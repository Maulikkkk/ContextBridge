# ContextBridge Frontend

React dashboard for the ContextBridge Context Engineering API.

## Setup

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Runs at `http://localhost:5173`

## Environment

Create `.env` for local development:

```
VITE_API_URL=http://localhost:8001
```

All API calls use `import.meta.env.VITE_API_URL` via `src/config/api.js`.

## Backend (local)

```bash
cd backend
uvicorn main:app --reload --port 8001
curl -X POST http://localhost:8001/ingest
```

## Vercel deployment

**Important:** `VITE_API_URL` must be set in Vercel **before** the build runs. Vite bakes env vars in at build time — runtime-only variables will not work.

In Vercel → Project → Settings → Environment Variables:

| Name | Value | Environments |
|------|-------|--------------|
| `VITE_API_URL` | `https://contextbridge-w2fk.onrender.com` | Production, Preview |

Redeploy after adding or changing this variable.

Ensure the Render backend allows CORS from your Vercel domain.
