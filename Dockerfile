FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY data/ ./data/

ENV PROJECT_ROOT=/app
ENV DATA_DIR=/app/data
ENV CHROMA_PERSIST_DIR=/app/chroma_db
ENV OMP_NUM_THREADS=1
ENV TOKENIZERS_PARALLELISM=false
ENV FASTEMBED_CACHE_PATH=/app/.cache/fastembed

RUN mkdir -p /app/chroma_db /app/.cache/fastembed \
    && test -f /app/data/calendar.json \
    && test -f /app/data/crm.json \
    && test -f /app/data/tasks.json \
    && test -d /app/data/meeting_notes

# Pre-download ONNX embedding model (lightweight, ~80MB)
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='BAAI/bge-small-en-v1.5')"

# Pre-index meeting notes at build time so Render never needs to run /ingest on first request
WORKDIR /app/backend
RUN python -c "\
from embeddings import init_chroma_client, init_embedding_model; \
from services.ingest_service import IngestService; \
init_chroma_client(); \
init_embedding_model(); \
print('Build-time ingest:', IngestService().ingest())"

EXPOSE 10000

CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1"
