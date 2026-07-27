import logging
import os

from fastapi import APIRouter

from embeddings import chroma_has_notes, get_embedding_model_error, is_embedding_model_ready
from schemas import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    mode = "gemini" if os.getenv("GEMINI_API_KEY") else "mock"
    embeddings_ready = is_embedding_model_ready()
    notes_indexed = chroma_has_notes()

    logger.info(
        "Health check: mode=%s embeddings=%s notes_indexed=%s",
        mode,
        embeddings_ready,
        notes_indexed,
    )

    if not embeddings_ready:
        logger.warning("Embeddings not ready: %s", get_embedding_model_error())

    return HealthResponse(status="healthy", mode=mode)
