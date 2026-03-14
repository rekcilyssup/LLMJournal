# LLM Journal

LLM Journal is a full-stack journaling app with AI-assisted emotion analysis, timeline insights, searchable history, and record deletion.

## Tech Stack

- Frontend: React + TypeScript + Vite
- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL
- LLM Providers: Local or cloud-backed provider via backend abstraction

## Core Features

- Create journal entries with ambience tags
- AI analysis for each entry (emotion, keywords, summary)
- Insights dashboard with timeline analysis over historical entries
- Search records by text/emotion/summary/keywords
- Delete records safely by user and entry id

## Project Structure

- `Frontend/` UI application
- `Backend/` API, services, data models
- `docs/` detailed contract and architecture notes

## LLM Provider Setup

The backend supports **local** and **cloud** LLM providers. Copy the example env file first:

```
cp Backend/.env.example Backend/.env
```

**Option A — Cloud (OpenAI / any OpenAI-compatible API):**

Set these values in `Backend/.env`:

```
LLM_PROVIDER=cloud
CLOUD_LLM_API_KEY=sk-your-api-key-here
```

Defaults use `gpt-4o-mini` via `https://api.openai.com/v1`. To use a different model or provider:

```
CLOUD_LLM_BASE_URL=https://api.openai.com/v1
CLOUD_LLM_MODEL=gpt-4o-mini
```

**Option B — Local (Ollama / LM Studio):**

```
LLM_PROVIDER=local
LOCAL_LLM_BASE_URL=http://localhost:11434/v1
LOCAL_LLM_MODEL=llama3.1:8b
```

Ensure your local model server is running before starting the backend.

## Docker Run (Recommended)

The easiest way to run everything:

1. Configure your LLM provider (see above):

```
cp Backend/.env.example Backend/.env
# Edit Backend/.env — set LLM_PROVIDER and API key
```

2. Start all services:

```
docker compose up --build
```

This launches PostgreSQL, the backend, and the frontend together.

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000/health`

To stop: `docker compose down`

To reset the database: `docker compose down -v`

## Local Run (Without Docker)

### Backend

From repository root:

1. `python3.12 -m venv .venv`
2. `. .venv/bin/activate`
3. `.venv/bin/python -m pip install -r Backend/requirements.txt`
4. Configure `Backend/.env` (see LLM Provider Setup above)
5. `cd Backend`
6. `../.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000`

Health:

- `http://localhost:8000/health`

### Frontend

From repository root in a second terminal:

1. `cd Frontend`
2. `npm install`
3. `npm run dev`

Frontend URL:

- `http://localhost:3000`

## API Summary

- `POST /api/journal` create entry
- `POST /api/journal/analyze` analyze free text
- `GET /api/journal/{userId}` list history
- `GET /api/journal/{userId}?q=...` search history
- `DELETE /api/journal/{userId}/{entryId}` delete entry
- `GET /api/journal/insights/{userId}` aggregate insights
- `POST /api/journal/insights/{userId}/analyze-timeline` timeline analysis
