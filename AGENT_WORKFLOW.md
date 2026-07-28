# ContextBridge – Agent Workflow

This document describes how AI-assisted development tools were used to build ContextBridge, what engineering decisions were made manually, and how a reviewer can audit the implementation. It is written for the Ninebar take-home assignment and is intended to be maintained as living documentation alongside the codebase.

---

## 1. Project Goal

**ContextBridge** is a lightweight Context Engineering layer that prepares structured context for AI agents before calling an LLM. The single supported use case is **meeting preparation**: given a natural-language request such as *"Prepare me for Globex meeting"*, the system retrieves relevant information from multiple sources, ranks it, assembles a **Context Package**, and generates a structured meeting brief.

The project exists to demonstrate a pattern that goes beyond simple RAG:

| Traditional RAG | ContextBridge |
|-----------------|---------------|
| Query → Vector Search → LLM | Query → Intent Parsing → Multi-source Retrieval → Ranking → Context Package → Prompt Builder → LLM |

Most agent prototypes stop at vector search. ContextBridge shows how an agent can combine **structured data** (calendar, CRM, tasks) with **semantic retrieval** (meeting notes in ChromaDB), apply explicit ranking logic, and pass the LLM a curated, auditable context object — not an unstructured pile of chunks.

The repository is deliberately scoped as an MVP: one intent, regex-based parsing, JSON mock data for structured sources, and ChromaDB only where semantic search adds value.

---

## 2. AI Development Workflow

Development was accelerated using three AI tools, with human review at every step:

### Cursor (primary implementation agent)

Cursor was used inside the IDE for:

- Scaffolding the FastAPI backend, service modules, and route handlers
- Implementing ChromaDB ingestion and semantic search
- Building the React dashboard (pipeline visualization, result cards, Context Envelope viewer)
- Writing the Dockerfile, docker-compose configuration, and deployment-related fixes
- Iterative debugging of production issues (CORS, memory limits, path resolution, environment variables)

All generated code was read, run locally, and adjusted before being kept.

### ChatGPT (planning and architecture)

ChatGPT was used earlier in the project for:

- Discussing the difference between RAG and Context Engineering
- Drafting initial folder structure and API shape
- Exploring deployment options (Render + Vercel)
- Reviewing trade-offs (JSON vs database, regex vs intent classifier)

Outputs from ChatGPT informed direction but were not copied verbatim into the repository without modification.

### Gemini (runtime LLM)

Gemini (`gemini-2.0-flash-lite` by default) is the production LLM when `GEMINI_API_KEY` is set. It was not used to write code; it is the **downstream consumer** of the Context Package. The prompt builder in `backend/services/llm_service.py` was written and tuned manually, with JSON-only output instructions to keep responses parseable.

### Verification principle

AI accelerated implementation, but **every architectural decision, deployment fix, and production behavior was manually verified**. No suggestion was merged because the model recommended it — it was merged because it worked in local runs, Docker builds, and deployed environments.

---

## 3. Development Timeline

The project evolved in roughly the following phases. Timings are approximate and reflect a focused take-home build rather than a multi-sprint product cycle.

```
Planning & requirements
        ↓
Architecture design (Context Engineering vs RAG)
        ↓
Backend scaffolding (FastAPI, routes, schemas)
        ↓
Structured data services (calendar, CRM, tasks)
        ↓
Meeting notes pipeline (ingest, ChromaDB, embeddings)
        ↓
Ranking + Context Package assembly
        ↓
LLM integration (Gemini + mock fallback)
        ↓
React frontend (dashboard, pipeline UI, Context Envelope)
        ↓
Docker + local container testing
        ↓
Production deployment (Render backend, Vercel frontend)
        ↓
Production debugging (localhost, OOM, CORS, paths, date logic)
        ↓
Documentation (README, AGENT_WORKFLOW)
```

Each phase included at least one manual test: `curl` against API endpoints, frontend smoke tests, Docker rebuilds, or live deployment verification.

---

## 4. Major AI-Assisted Tasks

| Task | AI Contribution | Manual Changes |
|------|-----------------|----------------|
| **FastAPI project scaffolding** | Generated `main.py`, route modules, Pydantic schemas, and CORS middleware | Added lifespan startup hooks, structured logging, path diagnostics in `paths.py`, and explicit CORS origins for Vercel |
| **ChromaDB integration** | Drafted ingest flow, collection setup, and query logic | Replaced `sentence-transformers`/PyTorch with **FastEmbed** (ONNX) after Render OOM; added singleton client/model in `embeddings.py`; build-time pre-index in Dockerfile |
| **Meeting brief pipeline** | Generated orchestration in `meeting_brief.py` | Removed implicit `"tomorrow"` default; added `find_meeting_for_client()` for date-free queries; added request ID logging |
| **Context Package design** | Suggested assembling retrieval results into one JSON object | Finalized schema in `context_builder.py`: metadata, meeting, client, tasks, top-3 ranked notes, summary counts |
| **React UI** | Generated dashboard layout, Tailwind styling, pipeline animation, result cards | Refined UX copy, error messages, API error handling, and removed date-dependent placeholder text |
| **Docker** | Generated initial Dockerfile and compose file | Added build-time model download, build-time ingest, path env vars, `--workers 1`, and data file existence checks |
| **Render deployment** | Suggested uvicorn CMD and PORT handling | Diagnosed 502/OOM manually; switched embedding stack; pre-indexed notes at build time so cold starts do not require `/ingest` |
| **Vercel deployment** | Suggested environment variable pattern | Confirmed `VITE_API_URL` must be set at **build time** (not runtime); removed localhost fallback in `frontend/src/config/api.js` |
| **README** | Drafted overview, architecture diagrams, setup steps | Edited for accuracy after production fixes; aligned terminology (Context Package vs Context Envelope in UI) |
| **API documentation** | FastAPI auto-generates OpenAPI at `/docs` | Example queries updated to reflect date-optional parsing (`"Prepare me for Globex meeting"`) |

---

## 5. Important Manual Decisions

These decisions were **not** blindly accepted from AI suggestions. They reflect deliberate engineering trade-offs for an MVP demo.

### Rejecting a chatbot-style UI

Early AI suggestions leaned toward a conversational chat interface. The final UI is an **enterprise dashboard** with a pipeline visualization, structured result cards, and an expandable Context Envelope — because the assignment is about Context Engineering, not chat UX.

### Introducing the Context Package abstraction

Rather than passing raw Chroma chunks directly to the LLM, retrieval results are assembled into a single JSON object in `context_builder.py`. This separates **retrieval** from **generation**, makes the pipeline auditable, and mirrors how production agent systems pass structured context to models.

### JSON for structured data, ChromaDB only for notes

Calendar, CRM, and task data live in `data/*.json`. Only meeting notes use vector search. AI initially suggested heavier stacks (SQLite, full RAG over everything). The simpler split keeps the demo focused and the architecture easy to explain.

### Gemini with mock fallback

`llm_service.py` runs in **mock mode** when no API key is present, and falls back to mock if Gemini fails at runtime. This was a manual decision so reviewers can run the project without credentials and so demos survive transient API errors.

### Ranking formula

The ranker uses a weighted score: `0.6 × semantic + 0.3 × freshness + 0.1 × source_priority`. Freshness is currently a placeholder (`1.0`) pending document timestamps — an intentional TODO documented in code rather than hidden.

### Date-optional query parsing

The parser originally defaulted missing dates to `"tomorrow"`, which broke demos when calendar dates did not align with the reviewer's clock. This was manually changed: queries like *"Prepare me for Globex meeting"* resolve to the **next scheduled meeting** for that client, with a demo fallback to any meeting if all dates are in the past.

### Production deployment fixes

- **`VITE_API_URL`**: Must be injected at Vercel build time; runtime env vars do not affect Vite bundles.
- **FastEmbed over sentence-transformers**: Manual swap after observing ~500MB+ RAM usage and 502 errors on Render's free tier.
- **Build-time ingest**: Notes are indexed during Docker build so the first production request does not trigger a memory-heavy ingest.
- **`DEMO_TODAY` env var**: Optional override in `calendar_service.py` for stable demo dates when needed.
- **CORS**: Explicit Vercel origins plus regex for preview deployments.

---

## 6. Example Prompt Used During Development

Below is a representative prompt used in Cursor during backend implementation:

> *"Build a Context Engineering layer that retrieves structured information from calendar, CRM, tasks, and semantic meeting notes before generating a meeting brief. Use FastAPI, ChromaDB for notes only, and return both the context package and the generated brief."*

### How that prompt became code

```
AI Output
   ↓  Initial FastAPI routes, service stubs, basic Chroma ingest
Manual Review
   ↓  Ran locally, verified data paths, tested /health and /meeting-brief
Refactoring
   ↓  Extracted paths.py, singleton embeddings, ContextBuilder, ranker weights
Final Implementation
   ↓  Production-hardened Dockerfile, date-optional parsing, mock/Gemini dual mode
```

The AI produced a workable skeleton. The final pipeline — including ranking, prompt construction, error handling, and deployment constraints — was shaped through multiple review cycles.

---

## 7. Debugging Sessions

Production issues required human judgment and live environment testing. AI suggestions were starting points; fixes were validated in Render logs, browser network tabs, and Docker rebuilds.

### Frontend calling localhost in production

**Symptom:** Deployed Vercel app failed with network errors.  
**Root cause:** Frontend defaulted to `localhost:8000` or omitted `VITE_API_URL`.  
**AI suggestion:** Use environment variables.  
**Manual fix:** Created `frontend/src/config/api.js` with no localhost fallback; documented that Vercel must set `VITE_API_URL` at build time.

### Vercel environment variables

**Symptom:** Setting `VITE_API_URL` in Vercel dashboard did not update the live site.  
**Root cause:** Vite inlines env vars during `vite build`, not at request time.  
**Manual fix:** Rebuild/redeploy after setting the variable; added comments in `api.js` explaining this behavior.

### Render deployment (502 / OOM)

**Symptom:** `/ingest` and first `/meeting-brief` requests returned 502.  
**Root cause:** `sentence-transformers` pulled PyTorch and exceeded Render memory limits.  
**AI suggestion:** Try a smaller model or more workers.  
**Manual fix:** Replaced with **FastEmbed** (`BAAI/bge-small-en-v1.5`, ONNX ~80MB RAM); set `--workers 1`; moved ingest to Docker build step; added startup diagnostics in `paths.py`.

### Docker path issues

**Symptom:** Container could not find `data/` or wrote Chroma to unexpected locations.  
**Root cause:** Relative paths depended on working directory.  
**Manual fix:** Centralized paths in `paths.py` with `PROJECT_ROOT`, `DATA_DIR`, and `CHROMA_PERSIST_DIR` env vars; Dockerfile sets these explicitly.

### CORS debugging

**Symptom:** Browser blocked requests from Vercel preview URLs.  
**AI suggestion:** Allow all origins (`*`).  
**Manual fix:** Rejected wildcard; added specific production origins and `allow_origin_regex` for `*.vercel.app` in `main.py`.

### Embedding model loading

**Symptom:** Notes search returned empty results after restart.  
**Root cause:** Model not initialized before first query; ingest failing silently on small instances.  
**Manual fix:** Lifespan hook loads model and Chroma client at startup; `/health` reports readiness; ingest validates model state before indexing.

### Chroma indexing

**Symptom:** Empty collection on fresh Render deploy.  
**Manual fix:** Dockerfile runs ingest at build time; startup logs warn if collection is empty; frontend error handler mentions `POST /ingest` for local recovery.

### Date / "tomorrow" demo failure

**Symptom:** *"Prepare me for Globex meeting"* returned *"No meeting found … on tomorrow"* even though the user never mentioned a date.  
**Manual fix:** Removed tomorrow default; implemented `find_meeting_for_client()` with next-meeting and demo fallback logic.

---

## 8. AI Limitations Encountered

Honest assessment of where AI assistance fell short:

1. **Over-engineering suggestions** — AI occasionally proposed dependency injection frameworks, abstract base classes, or Redis caching inappropriate for an MVP. These were rejected in favor of plain service classes.
2. **Deployment blind spots** — Models suggested generic Docker and Render configs without accounting for Render free-tier memory, Vite build-time env vars, or cold-start ingest costs. Production verification was required.
3. **Environment-specific failures** — Path resolution, CORS on preview URLs, and calendar date drift could not be solved from code alone; they required testing against live URLs.
4. **Incorrect defaults** — Defaulting query dates to `"tomorrow"` seemed reasonable in isolation but broke real demos. Human review of user-facing behavior caught this.
5. **Stack recommendations** — Initial embedding library choice (`sentence-transformers`) was AI-suggested and worked locally but failed in production. Memory profiling and log analysis drove the FastEmbed migration.
6. **Terminology drift** — AI mixed "Context Envelope" and "Context Package" in UI copy vs backend naming. Terminology was aligned manually (backend: Context Package; UI label: Context Envelope for display).

Production readiness always required a human to run the deployed app, read logs, and confirm behavior end-to-end.

---

## 9. Validation Checklist

Use this checklist when verifying a fresh clone or deployment:

- [ ] **Backend runs** — `uvicorn main:app` from `backend/` or `docker compose up`
- [ ] **Frontend runs** — `npm run dev` in `frontend/` with `VITE_API_URL` pointing to backend
- [ ] **Health endpoint** — `GET /health` returns `{ "status": "healthy", "mode": "mock" \| "gemini" }`
- [ ] **Meeting brief generation** — `POST /meeting-brief` with `{"query": "Prepare me for Globex meeting"}` returns `context_package` and `meeting_brief`
- [ ] **Chroma indexing** — Build-time index in Docker, or `POST /ingest` locally; notes appear in brief sources
- [ ] **Docker build** — `docker compose up --build` completes without OOM; API responds on mapped port
- [ ] **Render deployment** — Backend URL responds to `/health`; logs show embedding model and Chroma ready
- [ ] **Vercel deployment** — Frontend loads; network tab shows requests to Render URL, not localhost
- [ ] **Mock mode** — Works without `GEMINI_API_KEY`; brief populated from context data
- [ ] **Gemini mode** — With `GEMINI_API_KEY` set on Render, `/health` reports `"mode": "gemini"` and briefs are LLM-generated

---

## 10. How to Audit This Project

Reviewers should inspect the following areas to understand what the system does and how it was built.

### Entry points

| File | Purpose |
|------|---------|
| `README.md` | Architecture overview, setup, API list, design decisions |
| `Dockerfile` | Production image: model pre-download, build-time ingest, uvicorn CMD |
| `docker-compose.yml` | Local container wiring and env vars |

### Backend core

| Path | What to verify |
|------|----------------|
| `backend/routes/meeting_brief.py` | Full pipeline orchestration and query parsing |
| `backend/services/calendar_service.py` | Meeting lookup, date resolution, demo fallback |
| `backend/services/crm_service.py` | Client record retrieval |
| `backend/services/task_service.py` | Pending task filtering |
| `backend/services/notes_service.py` | Chroma semantic search with client filter |
| `backend/services/ranker.py` | Scoring weights and sort order |
| `backend/services/context_builder.py` | **Context Package** schema |
| `backend/services/llm_service.py` | Prompt builder, Gemini call, mock fallback |
| `backend/services/ingest_service.py` | Markdown chunking and Chroma indexing |
| `backend/embeddings.py` | Singleton FastEmbed model and Chroma client |
| `backend/paths.py` | Path resolution and startup diagnostics |

### Frontend

| Path | What to verify |
|------|----------------|
| `frontend/src/config/api.js` | `VITE_API_URL` — no silent localhost fallback |
| `frontend/src/hooks/useMeetingBrief.js` | API call, pipeline animation, error handling |
| `frontend/src/pages/Dashboard.jsx` | Result layout and Context Envelope display |
| `frontend/src/components/ContextEnvelope.jsx` | Inspectable JSON of the context package |

### Mock data

| Path | Purpose |
|------|---------|
| `data/calendar.json` | Meeting events for Acme and Globex |
| `data/crm.json` | Client records |
| `data/tasks.json` | Pending tasks per client |
| `data/meeting_notes/*.md` | Source documents for semantic retrieval |

### API routes (interactive docs at `/docs`)

- `GET /health`
- `POST /ingest`
- `POST /meeting-brief`

The most important audit artifact is the **Context Package** returned in every `/meeting-brief` response. It shows exactly what context was assembled before the LLM ran — the core of Context Engineering.

---

## 11. Lessons Learned

1. **Context Engineering is not RAG with extra steps.** Separating structured retrieval, semantic search, ranking, and prompt construction makes agent pipelines explainable and testable at each stage.

2. **Multi-source retrieval needs an explicit assembly step.** Without a Context Package, it is impossible to audit what the LLM actually saw. The JSON object in `context_builder.py` is the contract between retrieval and generation.

3. **Use vector search only where structure fails.** Calendar, CRM, and tasks are better served by deterministic lookups. ChromaDB adds value for unstructured meeting notes.

4. **AI accelerates scaffolding, not production judgment.** Deployment, memory limits, CORS, and environment variable semantics required hands-on debugging that models could not complete autonomously.

5. **Always verify in the target environment.** Code that passes locally may OOM on Render or call localhost from Vercel. Deploy early and test the full path.

6. **Mock modes are essential for demos and CI.** Gemini fallback and mock generation in `llm_service.py` keep the project runnable without API keys and resilient to transient LLM failures.

7. **Prompt engineering belongs in code, not in chat.** The `build_prompt()` function is version-controlled, reviewable, and specifies JSON output shape — unlike ad-hoc prompts in a chat window.

8. **Resist over-engineering from AI suggestions.** Plain service classes, JSON files, and regex parsing are appropriate for a single-intent MVP. Complexity can come later with real integrations.

9. **User-facing defaults matter for demos.** Implicit date assumptions (`tomorrow`) caused confusing 404 errors. Date-optional queries and demo fallbacks make the project robust for reviewers who do not know the mock calendar.

10. **Document the agent workflow, not just the code.** For take-home assignments and team projects alike, explaining how AI was used — and where humans intervened — is as important as the implementation itself.

---

*Last updated: July 2026. Maintained alongside the ContextBridge repository. *
