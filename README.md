# Meridian

Personal operating system for daily schedule, interview prep, thesis, health
and review tracking from 1 Sep to 31 Dec 2026. Named for the solar meridian:
the astronomical anchor prayer times, and therefore the schedule, are computed
from.

Full design: [MERIDIAN_SYSTEM_DESIGN.md](MERIDIAN_SYSTEM_DESIGN.md) and
[WEB_PLATFORM_BUILD_PROMPT.md](WEB_PLATFORM_BUILD_PROMPT.md)

## Layout

```text
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
environment setup. The frontend needs a dev auth token minted against the same
JWT secret as the API; both READMEs explain how.

## Status

Build order follows section 11 of the build prompt / section 14 of the design
doc. Complete so far:

- Full schema + hand-written migration + RLS policies (all 21 tables),
  applied and verified against a real Supabase project.
- The four engines: prayer, scheduling, spaced repetition, recommender,
  bandwidth; pure functions, 96-100% test coverage.
- `/api/today`, `/blocks/{id}/status`, `/attempts`, `/recommend`,
  `/reviews/due`; verified end-to-end against real seeded data.
- `scripts/seed.py`; deterministic synthetic 4-week dataset with real
  LeetCode problems.
- `web/`; the Today view: current block with a live countdown, the next-action
  card with inline mastery buttons, timeline, bandwidth control, and leading
  counters.

Not yet built: Insights charts, the Groq layer, the pattern engine,
offline/PWA support, remaining CRUD views, and complete production Supabase
Auth wiring in the frontend.

No source `.xlsx` workbook was ever supplied. `scripts/import_xlsx.py` is not
yet written; it is blocked on the real workbook. `scripts/seed.py` covers
development and testing in the meantime.

## CI/CD

Release engineering is trunk-based: short-lived work branches merge into the
protected `main` branch, staging is deployed from `main`, and production is
released from version tags such as `v0.1.0`.

GitHub Actions are split by concern so frontend-only changes do not run backend
checks unnecessarily:

- `Pull Request Quality Gate`
- `Security Scanning`
- `Deploy Staging`
- `Deploy Production`

See [.github/CICD_SETUP.md](.github/CICD_SETUP.md) for the branch strategy,
environment setup, required secrets, and rollback process.
