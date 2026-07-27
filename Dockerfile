FROM python:3.11-slim

WORKDIR /app

# System libs for torch / sentence-transformers on slim images
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY data/ ./data/

# Writable dirs for ChromaDB and HuggingFace model cache
ENV PROJECT_ROOT=/app
ENV DATA_DIR=/app/data
ENV CHROMA_PERSIST_DIR=/app/chroma_db
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence-transformers
ENV OMP_NUM_THREADS=1
ENV TOKENIZERS_PARALLELISM=false

RUN mkdir -p /app/chroma_db /app/.cache/huggingface /app/.cache/sentence-transformers \
    && test -f /app/data/calendar.json \
    && test -f /app/data/crm.json \
    && test -f /app/data/tasks.json \
    && test -d /app/data/meeting_notes

# Pre-download embedding model at build time (avoids runtime HF fetch + reduces first-request failures)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

WORKDIR /app/backend

EXPOSE 10000

CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"
