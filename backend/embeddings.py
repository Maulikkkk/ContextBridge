import logging
from typing import Optional

import chromadb
from fastembed import TextEmbedding

from paths import CHROMA_PATH, ensure_runtime_dirs

logger = logging.getLogger(__name__)

# Lightweight ONNX model (~80MB RAM vs ~500MB+ for sentence-transformers/torch)
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
COLLECTION_NAME = "meeting_notes"

_model: Optional[TextEmbedding] = None
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
    Load embedding model once at startup (FastEmbed ONNX — low memory).
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
        _model = TextEmbedding(model_name=EMBEDDING_MODEL)
        logger.info("Embedding model loaded.")
        return True
    except Exception as exc:
        _model_load_error = str(exc)
        logger.error("Embedding model failed to load: %s", exc)
        return False


def get_embedding_model() -> TextEmbedding:
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


def chroma_has_notes() -> bool:
    try:
        collection = get_chroma_client().get_collection(COLLECTION_NAME)
        return collection.count() > 0
    except Exception:
        return False


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    return [vec.tolist() for vec in model.embed(texts)]


def embed_query(query: str) -> list[list[float]]:
    model = get_embedding_model()
    return [vec.tolist() for vec in model.embed([query])]


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
