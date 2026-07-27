from pydantic import BaseModel, Field


class MeetingBriefRequest(BaseModel):
    query: str = Field(..., example="Prepare me for tomorrow's Acme meeting")


class ContextPackageResponse(BaseModel):
    context_package: dict


class StructuredRetrievalResponse(BaseModel):
    meeting: dict
    client: dict
    pending_tasks: list[dict]
    meeting_notes: list[dict] = Field(default_factory=list)


class MeetingBriefResponse(BaseModel):
    context_package: dict
    meeting_brief: dict


class HealthResponse(BaseModel):
    status: str
    mode: str


class IngestResponse(BaseModel):
    indexed_documents: int
    indexed_chunks: int
