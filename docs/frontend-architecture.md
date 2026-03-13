# Frontend Architecture (Current State)

## Stack

- React 19 + TypeScript
- Vite 6
- Tailwind CSS (via `@tailwindcss/vite`)
- UI helper components in `Frontend/src/components/ui`
- Notifications with `sonner`

## High-Level Structure

- Single-page dashboard app.
- Main component: `Frontend/src/App.tsx`.
- API wrapper: `Frontend/src/lib/api.ts`.
- No routing layer yet.
- No auth flow yet.

## Key Product Flows

1. Initial page load:
- Calls history and insights in parallel for the current user.
- Renders skeleton loaders while fetching.

2. Analyze flow:
- User writes text and clicks "Analyze Emotion".
- Frontend calls analyze endpoint.
- Shows emotion, keywords, and summary in an analysis card.

3. Save flow:
- User clicks "Save Journal Entry".
- Frontend sends user id, ambience, and text.
- On success it clears input and refreshes history + insights.

## State Model (App.tsx)

- `ambience`: one of `forest | ocean | mountain`
- `text`: journal input text
- `analysisResult`: result from analysis endpoint
- `history`: journal entries list
- `insights`: computed summary metrics
- loading flags: `isAnalyzing`, `isSaving`, `isLoadingData`

## Important Runtime Assumptions

- Hardcoded user id is currently `123`.
- API base URL is `VITE_API_URL`; fallback is `http://localhost:8000`.
- Date rendering expects an ISO-parseable string for each journal entry (`entry.date`).

## Frontend-to-Backend Dependency Summary

The frontend expects the backend to provide:

- CRUD-ish write/read for journal entries
- Text analysis for emotion + themes + summary
- Aggregated user insights

Any mismatch in response field names will break rendering because fields are accessed directly.
