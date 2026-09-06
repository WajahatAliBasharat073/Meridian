# Meridian

Personal operating system for daily schedule, interview prep, thesis, health and
review tracking — 1 Sep – 31 Dec 2026. Named for the solar meridian: the
astronomical anchor prayer times (and therefore the schedule) are computed from.

Full design: [MERIDIAN_SYSTEM_DESIGN.md](MERIDIAN_SYSTEM_DESIGN.md) ·
[WEB_PLATFORM_BUILD_PROMPT.md](WEB_PLATFORM_BUILD_PROMPT.md)

## Layout

```
api/     FastAPI backend, Python 3.12, venv-only. Engines, schema, ETL.
web/     Next.js frontend, App Router, TypeScript, Tailwind. Today view only so far.
```

## Quickstart

```bash
make install   # api venv + web node_modules
make migrate   # apply schema (see api/README.md re: which DATABASE_URL)
make seed      # synthetic 4-week dataset for dev
make test      # api unit tests (engines)
make dev       # api on :8000; separately: cd web && npm run dev for :3000
```

See [api/README.md](api/README.md) and [web/README.md](web/README.md) for
environment setup — the frontend needs a dev auth token minted against the
same JWT secret as the API; both READMEs explain how.

## Status

Build order follows section 11 of the build prompt / section 14 of the
design doc. Complete so far:

- Full schema + hand-written migration + RLS policies (all 21 tables),
  applied and verified against a real Supabase project (not just offline
  SQL generation)
- The four engines — prayer, scheduling, spaced repetition, recommender,
  bandwidth — pure functions, 96–100% test coverage
- `/api/today`, `/blocks/{id}/status`, `/attempts`, `/recommend`,
  `/reviews/due` — verified end-to-end against real seeded data
- `scripts/seed.py` — deterministic synthetic 4-week dataset (real
  LeetCode problems, never fabricated)
- `web/` — the Today view: current block with a live countdown, the
  next-action card with inline mastery buttons, timeline, bandwidth
  control, leading counters. Dark-first, mobile-first, driven end-to-end
  against the real API and screenshot-verified

Not yet built: Insights charts, the Groq layer, the pattern engine,
offline/PWA support, remaining CRUD views (thesis/vocab/recovery/etc. have
schema and seed data but no UI or dedicated endpoints yet), and real
Supabase Auth in the frontend (currently a dev-only signed token — see
`web/README.md`).

**No source `.xlsx` workbook was ever supplied.** `scripts/import_xlsx.py`
is not yet written; it's blocked on the real workbook. `scripts/seed.py`
covers development and testing in the meantime.

## CI/CD

`.github/workflows/ci.yml` runs API (lint/typecheck/test) and web
(lint/build) on every push/PR, plus a docker-compose config check.
`.github/workflows/cd.yml` maps branches (`develop`/`staging`/`qa`/`uat`/
`main`) to environments but deploys nothing until `DEPLOY_ENABLED` and the
provider-specific secrets are configured — see `.github/CICD_SETUP.md`
for what's required before enabling real deploys.
