# Backend API Contract (v2)

All endpoints are under /api/journal.

## Compatibility Objective

Frontend can evolve UI freely as long as this API contract remains stable.
Any contract change must update both frontend and backend in the same release.

## Database Context

- Primary store: PostgreSQL
- Journal table includes:
  id, user_id, ambience, text, date, emotion, keywords_json, summary

## Core Schemas

### JournalEntry

{
  id: string,
  userId: string,
  ambience: string,
  text: string,
  date: string,
  emotion?: string,
  keywords?: string[],
  summary?: string
}

### AnalysisResult

{
  emotion: string,
  keywords: string[],
  summary: string
}

### Insights

{
  totalEntries: number,
  topEmotion: string,
  mostUsedAmbience: string,
  recentKeywords: string[]
}

## Endpoints

### 1) Save Journal Entry (AI Persisted)

- Method: POST
- Path: /api/journal
- Request:

{
  "userId": "Aravind",
  "ambience": "forest",
  "text": "I feel anxious but hopeful."
}

- Behavior:

1. Validates text is non-empty.
2. Calls LLM analysis during save.
3. Persists emotion, keywords_json, summary with base entry.

- Response: 201 JournalEntry

### 2) Analyze Text Only

- Method: POST
- Path: /api/journal/analyze
- Request:

{
  "text": "I feel anxious but hopeful."
}

- Response: AnalysisResult

### 3) Get History

- Method: GET
- Path: /api/journal/{userId}
- Response: JournalEntry[] (newest first)

### 4) Get Insights

- Method: GET
- Path: /api/journal/insights/{userId}
- Response: Insights

## Non-Breaking Rules

1. Do not rename userId, ambience, text, date, emotion, keywords, summary.
2. keywords and recentKeywords should be arrays, not null.
3. date must stay ISO-parseable for JS clients.
4. Preserve endpoint paths exactly.

## CORS and Networking

- Backend allows localhost and LAN origins for port 3000 via allow_origins + allow_origin_regex.
- This supports frontend access from local and 192.168.x.x clients.

## Error Contract (Recommended)

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Text is required"
  }
}

## Change Checklist Before Frontend Merge

1. Save endpoint still returns JournalEntry with optional AI fields.
2. History and insights paths unchanged.
3. Analyze endpoint unchanged.
4. Regression test from browser and LAN URL passes.
