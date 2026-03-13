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
