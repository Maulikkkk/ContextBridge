import logging
import uuid

from fastapi import APIRouter

from schemas import IngestResponse
from services.ingest_service import IngestService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ingest"])
ingest_service = IngestService()


@router.post("/ingest", response_model=IngestResponse)
def ingest() -> IngestResponse:
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] Starting meeting notes ingestion")

    result = ingest_service.ingest()

    logger.info(
        f"[{request_id}] Ingestion complete: "
        f"{result['indexed_documents']} documents, {result['indexed_chunks']} chunks"
    )

    return IngestResponse(**result)
