# ContextBridge

A lightweight Context Engineering layer that prepares structured context for AI agents.

## Project Overview

ContextBridge demonstrates how an AI agent can gather, rank, and assemble context from multiple data sources before calling an LLM — going beyond simple vector search.

## Why This Isn't Just RAG

**Traditional RAG**

```
Query
  │
  ▼
Vector Search
  │
  ▼
LLM
```

**ContextBridge**

```
Query
  │
  ▼
Intent Parsing
  │
  ▼
Calendar ─┐
CRM       │
Tasks     ├── (multi-source retrieval)
Meeting Notes ─┘
  │
  ▼
Ranking
  │
  ▼
Context Package
  │
  ▼
Prompt Builder
  │
  ▼
LLM
```

Most agents stop at vector search. ContextBridge gathers structured and unstructured context, ranks it, builds a **Context Package**, and passes the LLM a curated prompt — not a random pile of chunks.

## Architecture

```
                 User Query
                      │
                      ▼
               Query Parser
                      │
                      ▼
        ┌─────────────────────────┐
        │ Structured Retrieval    │
        ├─────────────────────────┤
        │ Calendar                │
        │ CRM                     │
        │ Tasks                   │
        └─────────────────────────┘
                      │
                      ▼
          Meeting Notes (ChromaDB)
                      │
                      ▼
                 Rank Notes
                      │
                      ▼
             Context Package
                      │
                      ▼
              Prompt Builder
                      │
                      ▼
            Gemini / Mock LLM
                      │
                      ▼
               Meeting Brief
```

## Request Flow

```
User
 │
 │ POST /meeting-brief
 ▼
FastAPI
 │
 ├── Parse Query
 ├── Calendar Service
 ├── CRM Service
 ├── Task Service
 ├── Notes Service
 ├── Ranker
 ├── Context Builder
 ├── Prompt Builder
 ├── Gemini / Mock
 ▼
Response
```

## Folder Structure

```
ContextBridge/
├── backend/
│   ├── main.py
│   ├── schemas.py
│   ├── routes/
│   │   ├── health.py
│   │   ├── ingest.py
│   │   └── meeting_brief.py
│   └── services/
│       ├── calendar_service.py
│       ├── crm_service.py
│       ├── task_service.py
│       ├── notes_service.py
│       ├── ranker.py
│       ├── context_builder.py
│       ├── llm_service.py
│       └── ingest_service.py
├── data/
│   ├── calendar.json
│   ├── crm.json
│   ├── tasks.json
│   └── meeting_notes/
│       ├── Acme.md
│       └── Globex.md
├── README.md
├── AGENT_WORKFLOW.md
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Setup Instructions

### Local

```bash
cd ContextBridge
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Index meeting notes first
cd backend
uvicorn main:app --reload --port 8000
# In another terminal:
curl -X POST http://localhost:8000/ingest
```

### Docker

```bash
cd ContextBridge
cp .env.example .env
docker compose up --build
curl -X POST http://localhost:8000/ingest
```

API available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

Optional: set `GEMINI_API_KEY` in `.env` to use Gemini instead of mock mode.

## API List

| Method | Endpoint           | Description                              |
|--------|--------------------|------------------------------------------|
| GET    | `/health`          | Health check and runtime mode            |
| POST   | `/ingest`          | Index meeting notes into ChromaDB        |
| POST   | `/meeting-brief`   | Generate a meeting preparation brief     |

### Example

```bash
curl -X POST http://localhost:8000/meeting-brief \
  -H "Content-Type: application/json" \
  -d '{"query": "Prepare me for tomorrow'\''s Acme meeting"}'
```

## Design Decisions

| Decision | Why |
|----------|-----|
| JSON for structured data | Simpler MVP; avoids unnecessary database complexity |
| ChromaDB only for notes | Demonstrates semantic retrieval where it matters |
| Context Package | Separates retrieval from generation and makes the pipeline auditable |
| Mock mode | Allows the project to run without API keys |
| Regex parsing | Appropriate for a single, constrained use case |

## Future Improvements

- Support multiple meeting intents
- Learn ranking weights from feedback
- Add document timestamps to freshness scoring
- Replace regex parsing with an intent classifier
- Add Redis caching for embeddings and retrieval
- Introduce observability and metrics
- Add authentication and real integrations
