# Meridian — api

FastAPI backend. See the root [README.md](../README.md) and the design
docs for full context.

## Setup

```bash
python -m venv .venv
.venv/Scripts/Activate.ps1   # Windows; .venv/bin/activate on macOS/Linux
python -m pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env         # then fill in real values, see below
alembic upgrade head
python -m scripts.seed       # synthetic 4-week dev dataset
uvicorn app.main:app --reload --port 8000
```

## Environment

See `.env.example` for the full list. Notes on the non-obvious ones:

- `DATABASE_URL` — must use the `postgresql+asyncpg://` scheme. If pointed
  at Supabase, use the **pooler** connection (port 6543 or 5432 under
  Connection Pooling in the dashboard), not the direct connection — the
  direct host is IPv6-only and unreachable from some networks.
- `SUPABASE_JWT_SECRET` — leave unset for local dev; the API falls back to
  a single stub user (`app/deps.py`). Once set, every request requires a
  real bearer token (see `web/README.md` for how the frontend mints a dev
  one in the meantime).

## Architecture

Layered: `routers/` (FastAPI, thin) → `services.py` (composition) →
`engines/` (pure functions, no DB — prayer, scheduling, repetition,
recommender, bandwidth) + `repositories/` (SQLAlchemy, adapt ORM rows to
the engines' plain dataclasses in `domain.py`). The engines are the
tested core — see `tests/`.

## Commands

```
pytest -q --cov=app          # engine tests, 96-100% coverage
ruff check .
mypy app scripts
alembic revision -m "..."     # new migration
alembic upgrade head / downgrade -1
```
