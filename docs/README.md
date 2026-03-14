# LLM Journal Docs (v2)

This folder defines the current frontend-backend contract for safe UI iteration.

## Purpose

- Keep frontend updates from breaking API integration.
- Define stable request/response schemas and endpoint rules.
- Document architecture boundaries between UI, API, service layer, and database.

## Docs Index

- frontend-architecture.md
	Current frontend behavior, user flow, runtime networking assumptions, and state model.

- backend-api-contract.md
	Authoritative endpoint contract, payloads, schema guarantees, and compatibility rules.

## Contract Governance

Before frontend changes are merged:

1. Confirm endpoint paths and field names are unchanged, or update both FE and BE together.
2. Confirm array/string/null behavior matches this contract.
3. Confirm date values remain ISO-compatible for JS Date parsing.
4. Confirm CORS and host behavior works for local and LAN access.

## Source of Truth

These docs are aligned with implementation in:

- Frontend/src/App.tsx
- Frontend/src/lib/api.ts
- Backend/api/routes/journal.py
- Backend/services/journal_service.py

## Run Locally

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL running locally

### 1) Start Backend

From project root:

1. Create virtual environment (first time only):
	python3.12 -m venv .venv
2. Activate virtual environment:
	source .venv/bin/activate
3. Install backend dependencies:
	.venv/bin/python -m pip install -r Backend/requirements.txt
4. Ensure Backend/.env has a valid DATABASE_URL and LLM settings.
5. Start API server:
	cd Backend
	../.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000

Health check:

- http://localhost:8000/health

### 2) Start Frontend

From project root:

1. Open another terminal.
2. Install frontend dependencies (first time only):
	cd Frontend
	npm install
3. Start Vite dev server:
	npm run dev

Frontend URLs:

- http://localhost:3000
- http://192.168.x.x:3000 (LAN)

### 3) Verify End-to-End

1. Open frontend URL.
2. Enter a user name in the onboarding modal.
3. Write text and click Analyze Emotion.
4. Save entry and confirm history/insights update.
