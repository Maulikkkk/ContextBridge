import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from fastapi import FastAPI

from paths import ensure_runtime_dirs, log_startup_diagnostics
from embeddings import init_chroma_client, init_embedding_model, get_embedding_model_error
from routes.health import router as health_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

from routes.ingest import router as ingest_router
from routes.meeting_brief import router as meeting_brief_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_runtime_dirs()
    log_startup_diagnostics()
    init_chroma_client()
    model_ok = init_embedding_model()
    if not model_ok:
        logger.warning(
            "Embedding model failed to load at startup: %s — /ingest will return errors until resolved",
            get_embedding_model_error(),
        )
    yield


app = FastAPI(
    title="ContextBridge",
    description="A lightweight Context Engineering layer that prepares structured context for AI agents.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://contextbridge-w2fk.vercel.app",
        "https://contextbridge.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(meeting_brief_router)
