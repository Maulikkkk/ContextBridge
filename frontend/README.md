# ContextBridge Frontend

React dashboard for the ContextBridge Context Engineering API.

## Setup

```bash
cd frontend
npm install
npm run dev
```

Runs at `http://localhost:5173`

## Backend

Ensure the API is running at `http://localhost:8001`:

```bash
cd backend
uvicorn main:app --reload --port 8001
curl -X POST http://localhost:8001/ingest
```

Override API URL with `.env`:

```
VITE_API_URL=http://localhost:8001
```
