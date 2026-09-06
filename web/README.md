# Meridian — web

Next.js (App Router) frontend for the Today view. See the root
[README.md](../README.md) and the design docs for full context.

## Setup

```bash
npm ci
cp .env.example .env.local   # then fill in API_DEV_TOKEN, see below
npm run dev                  # http://localhost:3000
```

The API (`../api`) must be running separately on `API_BASE_URL` (default
`http://localhost:8000`).

## Environment

| Variable | Required | Notes |
|---|---|---|
| `API_BASE_URL` | No (defaults `http://localhost:8000`) | Server-only — read by `app/api/[...path]/route.ts`, never exposed to the browser |
| `API_DEV_TOKEN` | Yes, until real Supabase Auth is wired in | A JWT signed with the same `SUPABASE_JWT_SECRET` as `../api/.env`, payload `{"sub": "<STUB_USER_ID>"}` |

Mint a dev token (from `../api`, with its venv active):
```bash
python -c "
from jose import jwt
from app.config import get_settings
from app.deps import STUB_USER_ID
print(jwt.encode({'sub': str(STUB_USER_ID)}, get_settings().supabase_jwt_secret, algorithm='HS256'))
"
```

## Architecture note: why a proxy route

`app/api/[...path]/route.ts` is a thin server-side proxy that forwards
browser requests to the FastAPI backend, attaching `API_DEV_TOKEN`
server-side. This keeps the token out of the client bundle — the same
discipline the build prompt requires for the Groq key (§2.1), applied
here since real Supabase Auth (browser-managed session tokens) isn't
built yet. Once it is, this proxy can be removed in favor of direct
client → FastAPI calls with the Supabase JS client attaching the user's
real session token, per the design doc's architecture diagram.

## What's built

Today view only: current block with a live countdown, the next-action
card with inline L0–L6 mastery buttons, the day's timeline (tap to mark
DONE/PARTIAL/NOT DONE/RESCHEDULED), a bandwidth control, and the three
leading counters. Dark-first (no light theme yet — see the design note
in `app/globals.css`). No Insights charts, no offline/PWA support, no
Groq-backed surfaces — none of that is built on the backend yet either.

## Scripts

`npm run dev` · `build` · `start` · `lint` · `typecheck`
