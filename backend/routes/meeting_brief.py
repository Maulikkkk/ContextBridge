import logging
import re
import uuid

from fastapi import APIRouter, HTTPException

from schemas import MeetingBriefRequest, MeetingBriefResponse
from services.calendar_service import CalendarService
from services.context_builder import ContextBuilder
from services.crm_service import CRMService
from services.llm_service import generate_meeting_brief
from services.notes_service import NotesService
from services.ranker import Ranker
from services.task_service import TaskService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["meeting-brief"])

calendar_service = CalendarService()
crm_service = CRMService()
task_service = TaskService()
notes_service = NotesService()
ranker = Ranker()
context_builder = ContextBuilder()


def parse_query(query: str, request_id: str) -> tuple[str, str | None]:
    client_match = re.search(r"\b(\w+)\s+meeting\b", query, re.IGNORECASE)
    if not client_match:
        logger.warning(f"[{request_id}] Unable to parse client from query: {query!r}")
        raise HTTPException(status_code=400, detail="Unable to parse client from query")

    date_match = re.search(r"\b(today|tomorrow)\b", query, re.IGNORECASE)
    client = client_match.group(1)
    date_str = date_match.group(1).lower() if date_match else None
    return client, date_str


@router.post("/meeting-brief", response_model=MeetingBriefResponse)
def meeting_brief(request: MeetingBriefRequest) -> MeetingBriefResponse:
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] Received meeting-brief request")

    client, date_str = parse_query(request.query, request_id)
    if date_str:
        logger.info(f"[{request_id}] Parsed query: client={client}, date={date_str}")
    else:
        logger.info(f"[{request_id}] Parsed query: client={client}, date=next scheduled")

    meeting = calendar_service.find_meeting_for_client(client, date_str)
    if meeting is None:
        logger.warning(f"[{request_id}] No meeting found for client={client}")
        raise HTTPException(
            status_code=404,
            detail=f"No meeting found for client '{client}'.",
        )

    logger.info(f"[{request_id}] Meeting found: {meeting['title']}")

    crm_record = crm_service.get_client(client)
    logger.info(f"[{request_id}] Retrieved CRM for client={client}")

    pending_tasks = task_service.get_pending_tasks(client)
    logger.info(f"[{request_id}] Retrieved {len(pending_tasks)} pending tasks")

    meeting_notes = notes_service.search_notes(client, request.query)
    logger.info(f"[{request_id}] Retrieved {len(meeting_notes)} meeting note chunks")

    logger.info(f"[{request_id}] Ranking started")
    ranked_notes = ranker.rank(request.query, meeting_notes)
    logger.info(f"[{request_id}] Ranking finished: {len(ranked_notes)} notes ranked")

    context_package = context_builder.build(
        meeting=meeting,
        client=crm_record or {},
        pending_tasks=pending_tasks,
        ranked_notes=ranked_notes,
    )
    logger.info(f"[{request_id}] Context package built")

    meeting_brief_data = generate_meeting_brief(context_package, request.query)
    logger.info(f"[{request_id}] Meeting brief generated")

    return MeetingBriefResponse(
        context_package=context_package,
        meeting_brief=meeting_brief_data,
    )
