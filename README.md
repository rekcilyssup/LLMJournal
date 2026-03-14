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

## Local Run

### Backend

From repository root:

1. `python3.12 -m venv .venv`
2. `. .venv/bin/activate`
3. `.venv/bin/python -m pip install -r Backend/requirements.txt`
4. Ensure `Backend/.env` is configured
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
