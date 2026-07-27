import logging
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from fastapi import FastAPI

from routes.health import router as health_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
from routes.ingest import router as ingest_router
from routes.meeting_brief import router as meeting_brief_router

app = FastAPI(
    title="ContextBridge",
    description="A lightweight Context Engineering layer that prepares structured context for AI agents.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(meeting_brief_router)
