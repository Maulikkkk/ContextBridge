import logging
import traceback

from embeddings import COLLECTION_NAME, embed_query, get_chroma_client, is_embedding_model_ready

logger = logging.getLogger(__name__)


class NotesService:
    """
    Handles semantic retrieval of meeting notes from ChromaDB.
    """

    def search_notes(self, client: str, query: str, top_k: int = 5) -> list[dict]:
        if not is_embedding_model_ready():
            logger.warning("Embedding model not ready, skipping note search")
            return []

        try:
            collection = get_chroma_client().get_collection(COLLECTION_NAME)
            if collection.count() == 0:
                logger.info("ChromaDB collection is empty, returning no notes")
                return []
        except Exception as exc:
            logger.info("ChromaDB unavailable or empty: %s", exc)
            return []

        try:
            query_embedding = embed_query(query)
        except Exception as exc:
            logger.error("Query embedding failed: %s\n%s", exc, traceback.format_exc())
            return []

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
