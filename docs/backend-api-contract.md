# Backend API Contract (Required by Current Frontend)

## Base URL

- `VITE_API_URL` if set
- otherwise defaults to `http://localhost:8000`

All endpoints are under `/api/journal`.

## Data Types

### JournalEntry

```ts
{
  id: string;
  userId: string;
  ambience: string; // expected values today: forest | ocean | mountain
  text: string;
  date: string; // ISO date string recommended
  emotion?: string;
  keywords?: string[];
  summary?: string;
}
```

### AnalysisResult

```ts
{
  emotion: string;
  keywords: string[];
  summary: string;
}
```

### Insights

```ts
{
  totalEntries: number;
  topEmotion: string;
  mostUsedAmbience: string;
  recentKeywords: string[];
}
```

## Endpoints

Critical routing note:

- If using Express (or similar), define static routes before dynamic parameter routes.
- Register `/api/journal/analyze` and `/api/journal/insights/:userId` before `/api/journal/:userId`.
- Otherwise `/api/journal/analyze` can be incorrectly treated as `userId = "analyze"`.

## 1) Save Journal Entry

- Method: `POST`
- Path: `/api/journal`
- Request body:

```json
{
  "userId": "123",
  "ambience": "forest",
  "text": "Today I felt better after a walk."
}
```

- Success response: `200` or `201` with full `JournalEntry` JSON.
- Frontend behavior on failure: shows "Failed to save entry" toast.

Implementation notes:

- Validate non-empty `text` server-side too.
- Populate `id` and `date` on the server.
- Optional: enrich saved entry with `emotion`, `keywords`, `summary` if analysis runs on save.

## 2) Get Journal History

- Method: `GET`
- Path: `/api/journal/:userId`
- Success response: array of `JournalEntry`.

Example response:

```json
[
  {
    "id": "e1",
    "userId": "123",
    "ambience": "ocean",
    "text": "I felt calm today.",
    "date": "2026-03-12T10:15:00.000Z",
    "emotion": "calm"
  }
]
```

Implementation notes:

- Return newest-first if possible; UI labels section as "Recent History".
- Keep date field parseable by JavaScript `Date`.

## 3) Analyze Journal Text

- Method: `POST`
- Path: `/api/journal/analyze`
- Request body:

```json
{
  "text": "I am nervous but hopeful about tomorrow."
}
```

- Success response: `AnalysisResult`.

Example response:

```json
{
  "emotion": "hopeful",
  "keywords": ["nervous", "future", "growth"],
  "summary": "The entry reflects anxiety mixed with optimism about upcoming events."
}
```

Implementation notes:

- Always return all three fields (`emotion`, `keywords`, `summary`).
- Return an empty array for `keywords` instead of null.

## 4) Get User Insights

- Method: `GET`
- Path: `/api/journal/insights/:userId`
- Success response: `Insights`.

Example response:

```json
{
  "totalEntries": 18,
  "topEmotion": "calm",
  "mostUsedAmbience": "forest",
  "recentKeywords": ["gratitude", "focus", "family"]
}
```

Implementation notes:

- `recentKeywords` should always be an array (can be empty).
- `mostUsedAmbience` should align with known ambience values when possible.

## Error Shape Recommendation

The frontend currently only checks HTTP status and does not parse error JSON.
Recommended standard for future-proofing:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Text is required"
  }
}
```

## Backend Build Priorities

1. Implement the 4 endpoints with exact response fields.
2. Ensure CORS allows frontend origin (Vite dev server, typically `http://localhost:3000`).
3. Use stable date serialization (ISO 8601).
4. Keep nulls out of array fields expected by UI (`keywords`, `recentKeywords`).

## Gaps To Address Soon

- Replace hardcoded user id with real authentication/session identity.
- Decide whether analysis is synchronous or async during save.
- Add pagination/filtering for history when volume grows.
