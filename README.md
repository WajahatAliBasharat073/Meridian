# Meridian

Personal operating system for daily schedule, interview prep, thesis, health and
review tracking — 1 Sep – 31 Dec 2026. Named for the solar meridian: the
astronomical anchor prayer times (and therefore the schedule) are computed from.

Full design: [MERIDIAN_SYSTEM_DESIGN.md](MERIDIAN_SYSTEM_DESIGN.md) ·
[WEB_PLATFORM_BUILD_PROMPT.md](WEB_PLATFORM_BUILD_PROMPT.md)

## Layout

```
api/     FastAPI backend, Python 3.12, venv-only. Engines, schema, ETL.
web/     Next.js frontend, App Router, TypeScript, Tailwind.
```

## Quickstart

```bash
make install   # api venv + web node_modules
make db-up     # local Postgres via docker compose
make migrate   # apply schema
make seed      # synthetic 4-week dataset for dev
make test      # api unit tests (engines)
make dev       # api on :8000, web on :3000
```

See `api/README.md` and `web/README.md` for details.

## Status

Build order follows section 11 of the build prompt / section 14 of the design
doc. Current phase: **0–5 — foundation through the recommender** (schema,
migrations, ETL + seed, Today view on real data, spaced-repetition engine,
recommender engine, bandwidth engine). Insights charts, the Groq layer, the
pattern engine and offline/PWA support are not yet built — see `NEXT.md`.

**No source `.xlsx` workbook was present at build time.** `scripts/import_xlsx.py`
is written against the sheet/column contract in the design doc (section 5.6)
and is ready to run once the real file is supplied; development and testing
until then use `scripts/seed.py`, which generates a realistic synthetic
4-week dataset as required by the quality bar.

This is local-only for now: docker-compose Postgres stands in for Supabase,
auth is a single stub user (no real Supabase Auth wiring yet), and the Groq
layer is not built — nothing in this phase calls an LLM.
