# LLM Journal Technical Docs

This folder documents the current frontend behavior so the backend can be built against a clear contract.

## Docs Index

- `frontend-architecture.md`: UI structure, state flow, and runtime assumptions.
- `backend-api-contract.md`: Required backend endpoints, payloads, response shapes, and implementation notes.

## Source of Truth

The contract here is derived from the current frontend code in `Frontend/src/App.tsx` and `Frontend/src/lib/api.ts`.
If frontend behavior changes, update these docs before backend changes.
