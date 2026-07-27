import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# backend/ directory
BACKEND_DIR = Path(__file__).resolve().parent
# Repository root (parent of backend/)
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", BACKEND_DIR.parent))

DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))
NOTES_DIR = DATA_DIR / "meeting_notes"
CHROMA_PATH = Path(os.getenv("CHROMA_PERSIST_DIR", PROJECT_ROOT / "chroma_db"))

CALENDAR_FILE = DATA_DIR / "calendar.json"
CRM_FILE = DATA_DIR / "crm.json"
TASKS_FILE = DATA_DIR / "tasks.json"

# Reduce memory pressure on small Render instances
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HOME", str(PROJECT_ROOT / ".cache" / "huggingface"))
os.environ.setdefault("TRANSFORMERS_CACHE", os.environ["HF_HOME"])
os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(PROJECT_ROOT / ".cache" / "sentence-transformers"))


def ensure_runtime_dirs() -> None:
    """Create writable directories required for ChromaDB and model caches."""
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    Path(os.environ["HF_HOME"]).mkdir(parents=True, exist_ok=True)
    Path(os.environ["SENTENCE_TRANSFORMERS_HOME"]).mkdir(parents=True, exist_ok=True)


def log_startup_diagnostics() -> None:
    logger.info("=== ContextBridge startup diagnostics ===")
    logger.info("Python version: %s", sys.version.replace("\n", " "))
    logger.info("CWD: %s", os.getcwd())
    logger.info("BACKEND_DIR: %s (exists=%s)", BACKEND_DIR, BACKEND_DIR.exists())
    logger.info("PROJECT_ROOT: %s (exists=%s)", PROJECT_ROOT, PROJECT_ROOT.exists())
    logger.info("DATA_DIR: %s (exists=%s)", DATA_DIR, DATA_DIR.exists())
    logger.info("NOTES_DIR: %s (exists=%s)", NOTES_DIR, NOTES_DIR.exists())
    logger.info("CHROMA_PATH: %s (exists=%s)", CHROMA_PATH, CHROMA_PATH.exists())
    logger.info("HF_HOME: %s", os.environ.get("HF_HOME"))

    for label, path in [
        ("calendar.json", CALENDAR_FILE),
        ("crm.json", CRM_FILE),
        ("tasks.json", TASKS_FILE),
    ]:
        logger.info("  %s: %s (exists=%s)", label, path, path.exists())

    if NOTES_DIR.exists():
        notes = sorted(NOTES_DIR.glob("*.md"))
        logger.info("  meeting notes: %d files in %s", len(notes), NOTES_DIR)
        for note in notes:
            logger.info("    - %s", note.name)
    else:
        logger.warning("  meeting notes directory missing: %s", NOTES_DIR)

    logger.info("=== end startup diagnostics ===")
