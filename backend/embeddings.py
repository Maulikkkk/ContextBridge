import logging
from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer

from paths import CHROMA_PATH, ensure_runtime_dirs

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "meeting_notes"

_model: Optional[SentenceTransformer] = None
_model_load_error: Optional[str] = None
_chroma_client: Optional[chromadb.PersistentClient] = None
_cache_use_logged = False


def init_chroma_client() -> None:
    """Initialize ChromaDB PersistentClient once at startup."""
    global _chroma_client
    if _chroma_client is not None:
        return
    ensure_runtime_dirs()
    logger.info("Initializing ChromaDB client at %s", CHROMA_PATH)
    _chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    logger.info("ChromaDB client ready.")


def get_chroma_client() -> chromadb.PersistentClient:
    if _chroma_client is None:
        init_chroma_client()
    return _chroma_client


def init_embedding_model() -> bool:
    """
    Load SentenceTransformer once at startup.
    Returns True on success, False on failure (app continues running).
    """
    global _model, _model_load_error
    if _model is not None:
        logger.info("Using cached embedding model.")
        return True
    if _model_load_error is not None:
        return False

    logger.info("Loading embedding model...")
    try:
        ensure_runtime_dirs()
        _model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Embedding model loaded.")
        return True
    except Exception as exc:
        _model_load_error = str(exc)
        logger.error("Embedding model failed to load: %s", exc)
        return False


def get_embedding_model() -> SentenceTransformer:
    global _cache_use_logged
    if _model is not None:
        if not _cache_use_logged:
            logger.info("Using cached embedding model.")
            _cache_use_logged = True
        return _model
    if _model_load_error:
        raise RuntimeError(f"Embedding model unavailable: {_model_load_error}")
    raise RuntimeError("Embedding model not initialized — call init_embedding_model() at startup")


def is_embedding_model_ready() -> bool:
    return _model is not None


def get_embedding_model_error() -> Optional[str]:
    return _model_load_error


def embed_texts(texts: list[str]) -> list[list[float]]:
    return get_embedding_model().encode(texts).tolist()


def embed_query(query: str) -> list[list[float]]:
    return get_embedding_model().encode([query]).tolist()


def get_collection():
    """Return the meeting_notes collection, or None if it does not exist."""
    return get_chroma_client().get_collection(COLLECTION_NAME)


def recreate_collection():
    """Delete and recreate the meeting_notes collection for ingestion."""
    client = get_chroma_client()
    try:
        client.delete_collection(COLLECTION_NAME)
        logger.info("Removed existing collection: %s", COLLECTION_NAME)
    except Exception:
        pass
    return client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
