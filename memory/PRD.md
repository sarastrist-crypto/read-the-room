# Room Reader - Product Requirements Document

## Original Problem Statement
A pre-talk prep tool that turns event context into an engagement strategy in under 60 seconds. User enters: event type, room size, audience context. Returns: room energy read, opening move, engagement anchor, recovery move, one thing to avoid. Direct, practical tone. Single-screen, mobile-friendly. No user accounts.

## Architecture
- **Backend**: FastAPI with Claude Sonnet 4.5 via Emergent LLM key
- **Frontend**: React with Neo-Brutalist UI (Clash Display + IBM Plex Mono fonts)
- **Database**: MongoDB (for status checks, no user data stored)

## User Personas
- Speakers preparing for keynotes/presentations
- Workshop facilitators
- Meeting leaders prepping for team/client meetings
- Anyone presenting to a room who needs quick tactical advice

## Core Requirements (Static)
1. Single-screen input form (event type, room size, audience context)
2. AI-generated engagement strategy with 5 sections
3. Mobile-friendly, fast interface
4. No authentication required
5. Results appear on same page without reload

## Implementation Status (Jan 2026)
- [x] Backend API with /api/generate-strategy endpoint
- [x] Claude Sonnet 4.5 integration via Emergent integrations
- [x] Frontend form with validation
- [x] Neo-Brutalist UI design
- [x] Loading states and error handling
- [x] All 15 event types pre-populated
- [x] Input validation (min_length=1)

## Prioritized Backlog
### P0 (Critical) - DONE
- Core form functionality
- AI strategy generation
- Basic error handling

### P1 (Important) - Future
- Copy-to-clipboard for strategy output
- Share strategy via link
- Print-friendly view

### P2 (Nice to have) - Future
- Strategy history (local storage)
- Quick presets for common scenarios
- Dark mode toggle

## Next Tasks
1. Add copy-to-clipboard functionality
2. Consider adding "Save to PDF" option
3. Analytics for most common event types
