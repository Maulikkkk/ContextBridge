import logging
import os

from fastapi import APIRouter

from schemas import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    mode = "gemini" if os.getenv("GEMINI_API_KEY") else "mock"
    logger.info(f"Health check: mode={mode}")
    return HealthResponse(status="healthy", mode=mode)
