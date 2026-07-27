import logging
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

CHROMA_PATH = Path(__file__).resolve().parent.parent.parent / "chroma_db"
COLLECTION_NAME = "meeting_notes"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class NotesService:
    """
    Handles semantic retrieval of meeting notes from ChromaDB.
    """

    def __init__(self) -> None:
        self._model: SentenceTransformer | None = None

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(EMBEDDING_MODEL)
        return self._model

    def _get_collection(self):
        chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        return chroma_client.get_collection(COLLECTION_NAME)

    def search_notes(self, client: str, query: str, top_k: int = 5) -> list[dict]:
        try:
            collection = self._get_collection()
            if collection.count() == 0:
                logger.info("ChromaDB collection is empty, returning no notes")
                return []
        except Exception as exc:
            logger.info(f"ChromaDB unavailable or empty: {exc}")
            return []

        query_embedding = self._get_model().encode([query]).tolist()
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            where={"client": client},
        )

        notes: list[dict] = []
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        for content, distance, metadata in zip(documents, distances, metadatas):
            notes.append(
                {
                    "content": content,
                    "score": round(1 - distance, 4),
                    "metadata": metadata,
                }
            )

        return notes
