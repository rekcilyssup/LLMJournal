# Frontend Architecture (v2)

## Stack

- React 19 + TypeScript
- Vite 6
- Tailwind CSS
- Sonner for toasts
- Internal API client in Frontend/src/lib/api.ts

## Application Shape

- Single-page dashboard in Frontend/src/App.tsx
- No route-level auth yet
- Username is captured in UI and used as backend userId

## User Identity Flow

1. User enters a name in onboarding card.
2. Name is stored in localStorage as journalUserName.
3. Name is reused as userId for all journal/history/insight requests.
4. User can switch identity from the header switch action.

## Data Flows

### 1) Initial Data Load

- When user identity is ready, frontend fetches in parallel:
	- GET /api/journal/{userId}
	- GET /api/journal/insights/{userId}

### 2) Analyze-Only Flow

- Analyze button calls:
	- POST /api/journal/analyze
- Result is shown immediately in UI card.

### 3) Save Flow

- Save button calls:
	- POST /api/journal
- Payload includes userId, ambience, text.
- Backend persists entry and AI fields.
- Frontend refreshes history + insights after save.

## Runtime Networking Behavior

- API base URL selection order:

1. VITE_API_URL if provided.
2. Else runtime host with backend port 8000:
	 window.location.protocol + // + window.location.hostname + :8000

This prevents LAN breakage when frontend is accessed via 192.168.x.x.

## Frontend Contract Assumptions

- JournalEntry.date is ISO-parseable.
- analysis keywords is always an array.
- insights recentKeywords is always an array.
- Field names are case-sensitive and mapped directly in UI.

## Break-Safety Rules For UI Changes

1. Do not rename API fields without backend update.
2. Keep endpoint paths unchanged unless docs + backend are updated together.
3. Do not assume null-safe arrays; backend should return empty arrays where required.
4. Preserve userId strategy unless auth/session model is introduced.
