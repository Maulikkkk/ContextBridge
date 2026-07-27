import logging
import traceback
import uuid

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from schemas import IngestResponse
from services.ingest_service import IngestService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ingest"])
ingest_service = IngestService()


@router.post("/ingest")
def ingest():
    request_id = uuid.uuid4().hex[:8]
    logger.info("[%s] Starting meeting notes ingestion", request_id)

    try:
        result = ingest_service.ingest()
        logger.info(
            "[%s] Ingestion complete: %s documents, %s chunks",
            request_id,
            result["indexed_documents"],
            result["indexed_chunks"],
        )
        return IngestResponse(**result)
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error("[%s] Ingestion failed: %s\n%s", request_id, exc, tb)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(exc),
                "traceback": tb,
            },
        )
