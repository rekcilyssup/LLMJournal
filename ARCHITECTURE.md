# Architecture and Scale Plan

## Current System Overview

### Frontend

- React SPA calls FastAPI over REST.
- Features include journaling, analysis, history, search/delete, and timeline insights.

### Backend

- FastAPI routes in `Backend/api/routes`.
- Service layer in `Backend/services` for business logic and LLM orchestration.
- LLM abstraction supports local/cloud providers.

### Data Layer

- PostgreSQL stores journal entries and analysis fields.
- Core table includes date, emotion, keywords_json, summary, text, and user_id.

## 1. How would you scale this to 100k users?

1. Split services by responsibility:
- API gateway + auth service
- journal CRUD service
- asynchronous analysis service (worker queue)

2. Add asynchronous processing for LLM tasks:
- Enqueue timeline and heavy analyses to background workers (Celery/RQ/Sidekiq style).
- Return job ids and stream status to frontend.

3. Scale API horizontally:
- Run multiple stateless backend instances behind a load balancer.
- Use autoscaling based on CPU, memory, and queue depth.

4. Improve database scalability:
- Add indexes on `user_id`, `date`, and search fields.
- Partition large journal tables by date or tenant/user hash.
- Add read replicas for history and insights reads.

5. Add observability and SLOs:
- Distributed tracing, centralized logs, metrics dashboards.
- Alert on latency, error rates, queue lag, and DB saturation.

## 2. How would you reduce LLM cost?

1. Route requests by complexity:
- Use smaller/cheaper model for basic entry analysis.
- Use larger model only for timeline summaries when needed.

2. Reduce token usage:
- Send only required fields (date, emotion, keywords) for timeline analysis.
- Cap historical window (for example last 30-90 days) or summarize in chunks.

3. Batch and summarize incrementally:
- Precompute daily/weekly summaries and compose final timeline from summaries.
- Avoid reprocessing full history each time.

4. Add cost controls:
- Per-user daily budgets and request throttling.
- Dynamic fallback to deterministic heuristic summaries under budget pressure.

## 3. How would you cache repeated analysis?

1. Cache key design:
- Key by hash of normalized input + model + prompt version.
- Example: `timeline:{userId}:{historyHash}:{promptVersion}:{model}`.

2. Use multi-layer cache:
- Redis for hot shared cache across instances.
- In-process short TTL cache for very frequent repeats.

3. Invalidate safely:
- Invalidate user timeline cache on create/delete/update entry.
- Keep entry-level analysis immutable where possible to maximize hit rate.

4. Persist reusable artifacts:
- Store analysis outputs in DB with input hash and model metadata.
- Serve from stored analysis when hash and version match.

## 4. How would you protect sensitive journal data?

1. Encrypt data end-to-end:
- TLS in transit.
- Encryption at rest for database and backups.
- Optional field-level encryption for `text` and `summary`.

2. Enforce strong access control:
- OAuth/JWT auth with per-user authorization checks.
- Row-level security so users access only their entries.

3. Minimize data sent to LLMs:
- Strip PII before provider calls when possible.
- Use self-hosted model for high-sensitivity deployments.
- Store provider prompts/responses with retention controls.

4. Security operations:
- Secrets in vault/KMS, never in source control.
- Audit logging for access and deletion events.
- Data retention and deletion policies aligned with compliance needs.
- Regular vulnerability scanning and dependency patching.

## Suggested Next Architecture Milestones

1. Introduce background job queue for timeline analysis.
2. Add Redis cache with history-hash invalidation.
3. Add authentication and row-level authorization.
4. Add prompt/versioned analysis artifacts for deterministic cache reuse.
