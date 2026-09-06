# MERIDIAN — System Design Document

**Version** 1.0 · **Date** 6 September 2026 · **Status** Design, pre-implementation
**Author role** Senior AI Architect / Full-Stack / UI-UX

---

## 1. NAME

**Meridian.**

The solar meridian — the sun's crossing of the local north-south line — is the astronomical anchor from which every prayer time in this system is computed. Solar noon plus declination plus the equation of time produces Fajr, Zuhr, Asr, Maghrib and Isha, and those five times shape the entire day's schedule. The name is literal, not decorative. It also carries the secondary sense of a peak, which is what the system exists to reach.

Alternatives considered: *Cadence* (rhythm, spaced repetition), *Lodestar* (navigation by a fixed point), *Trellis* (structure that supports growth). Meridian wins on the astronomical anchor being real rather than metaphorical.

Package namespace: `meridian`. Repo: `meridian`. Public URL: `meridian.<domain>`.

---

## 2. GOALS AND NON-GOALS

### Goals

| # | Goal | Success measure |
|---|---|---|
| G1 | Answer "what do I do right now" in under 3 seconds from app open | Time-to-first-action |
| G2 | Single source of truth for task completion | Zero divergence between any two rollups |
| G3 | Deterministic, explainable next-task recommendation | Every suggestion carries a one-line reason |
| G4 | Spaced repetition that survives contact with a real schedule | No silently dropped reviews; forecast breaches surfaced early |
| G5 | Learn the user's actual behaviour and adapt | Observations backed by stated sample size |
| G6 | Work offline for read and queue writes | Full Today view renders with no network |
| G7 | Never leak the LLM API key | Key exists only as a server env var |

### Non-goals

Multi-tenancy beyond correct auth · social features, sharing, leaderboards · a general-purpose task manager · mobile native apps · replacing the user's calendar or email · gamification beyond honest progress.

### Constraints

Single user. Fixed horizon 1 Sep – 31 Dec 2026, extensible. Free-tier hosting. Mobile-first usage at 04:30 and 22:00. Source data is a 25-sheet `.xlsx` that must migrate losslessly.

---

## 3. ARCHITECTURE

```
┌────────────────────────────────────────────────────────────┐
│  CLIENT — Next.js (Vercel)                                 │
│  React · TanStack Query · Recharts · Tailwind/shadcn       │
│  Service Worker + IndexedDB  ──►  offline read, write queue│
└───────────────┬────────────────────────────────────────────┘
                │ HTTPS, JWT (Supabase Auth)
┌───────────────▼────────────────────────────────────────────┐
│  API — FastAPI (Render / Railway), Python 3.12, venv       │
│                                                            │
│  ┌──────────────┬──────────────┬──────────────┬──────────┐ │
│  │ Scheduling   │ Repetition   │ Recommender  │ Pattern  │ │
│  │ Engine       │ Engine       │ Engine       │ Engine   │ │
│  └──────────────┴──────────────┴──────────────┴──────────┘ │
│  Groq client (server-side only) · Pydantic · SQLAlchemy    │
└───────────────┬────────────────────────────────────────────┘
                │ asyncpg
┌───────────────▼────────────────────────────────────────────┐
│  Supabase Postgres  ·  Row Level Security  ·  pg_cron      │
└────────────────────────────────────────────────────────────┘
                │
┌───────────────▼────────────────────────────────────────────┐
│  ETL — Python, same venv.  xlsx ──► Postgres, one-shot     │
└────────────────────────────────────────────────────────────┘
```

**Why FastAPI over Next.js route handlers.** The recommender and pattern engines do real numeric work (rolling aggregates, correlation, distribution fitting) that is natural in pandas/numpy and awkward in TypeScript. The xlsx importer requires openpyxl regardless. Python is the user's primary language. The cost is a second deployment target and CORS configuration; that is acceptable.

**Why not serverless Python on Vercel.** Cold starts on a numpy-carrying bundle are poor, and the nightly jobs want a persistent process. A small always-on container on Render or Railway free tier is simpler.

---

## 4. LOCAL DEVELOPMENT — PYTHON VIRTUAL ENVIRONMENT

**Every Python dependency is installed inside a project-local virtual environment. Never install into the system interpreter, and never use `sudo pip`.**

### 4.1 Backend setup

```bash
git clone <repo> meridian && cd meridian/api

# create — python3.12 or newer
python3 -m venv .venv

# activate
source .venv/bin/activate            # macOS / Linux
# .venv\Scripts\Activate.ps1         # Windows PowerShell

# confirm you are inside it before installing anything
which python                          # must print .../meridian/api/.venv/bin/python
python -V

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt       # runtime
pip install -r requirements-dev.txt   # tests, lint, type-check
```

### 4.2 Rules

- `.venv/` is in `.gitignore`. It is never committed.
- Dependencies are **pinned** in `requirements.txt` (`fastapi==0.115.*`). Generate with `pip freeze > requirements.lock` and commit the lock.
- Runtime and dev dependencies are separate files. Test tooling never ships to production.
- Deactivate with `deactivate`. Rebuild from scratch with `rm -rf .venv` and repeat — this must always work, and CI proves it.
- The ETL scripts use **the same venv**, not a second one.
- If `uv` is available, `uv venv && uv pip install -r requirements.txt` is an acceptable faster substitute. `conda` is not — it complicates deployment.

### 4.3 requirements.txt

```
fastapi · uvicorn[standard] · pydantic · pydantic-settings
sqlalchemy · asyncpg · alembic
openpyxl · pandas · numpy · scipy
groq · httpx · tenacity
python-jose[cryptography] · structlog
```

### 4.4 requirements-dev.txt

```
pytest · pytest-asyncio · pytest-cov · httpx
ruff · mypy · types-python-dateutil · faker
```

### 4.5 Frontend

Node is separate and unrelated to the venv:

```bash
cd meridian/web && npm ci && npm run dev
```

### 4.6 Environment

`.env.example` is committed; `.env` never is.

```
DATABASE_URL=postgresql+asyncpg://...
SUPABASE_JWT_SECRET=...
GROQ_API_KEY=...            # server only — never reaches the browser
GROQ_MODEL=...
DAILY_TOKEN_BUDGET=200000
TZ=Asia/Karachi
```

### 4.7 Make targets

```
make venv · make install · make dev · make test · make lint
make typecheck · make migrate · make seed · make import-xlsx
```

---

## 5. DATA MODEL

Postgres. All timestamps `timestamptz`; all dates `date` in `Asia/Karachi`. RLS on every table keyed to `user_id`.

### 5.1 Core

```sql
users(id, email, created_at, settings jsonb)

-- computed once per date from lat/long/convention, cached
prayer_times(date PK, fajr, sunrise, zuhr, asr, maghrib, isha)

-- THE execution layer and the ONLY completion store
time_blocks(
  id, user_id, date, seq,
  start_spec  text,      -- '17:05'  |  'maghrib+15m'  |  'asr'
  end_spec    text,
  start_resolved time,   -- materialised on write/recompute
  end_resolved   time,
  activity text, tier text CHECK (tier IN ('T1','T2','T3','T4')),
  category text, planned_minutes int,
  status text CHECK (status IN ('DONE','NOT DONE','PARTIAL','RESCHEDULED')),
  actual_minutes int, energy_before int, focus int, deep_work int,
  location text, what_to_do text, notes text,
  UNIQUE(user_id, date, seq)
)
```

`start_spec` holds either a literal time or a prayer-relative expression. The resolver materialises `start_resolved` so queries stay simple, and recomputes when `prayer_times` or settings change. This is the one piece of the spreadsheet worth preserving exactly: the original workbook used array formulas to do this and it worked.

### 5.2 Interview prep

```sql
problems(id, lc_number UNIQUE, title, slug UNIQUE, url, pattern,
         difficulty, is_neetcode150 bool, is_blind75 bool,
         freq_meta int NULL, freq_amazon int NULL, freq_google int NULL)
         -- Netflix and OpenAI: no data exists. NULL, never invented.

curriculum(id, problem_id FK, scheduled_date, slot, phase)

problem_attempts(
  id, user_id, problem_id FK, attempted_at,
  minutes int, mastery_level text CHECK (mastery_level ~ '^L[0-6]$'),
  hint_used bool, key_insight text, mistake_id FK NULL
)
```

**Mastery is a property of the latest attempt, never a mutable column on `problems`.** Current mastery is a view:

```sql
CREATE VIEW current_mastery AS
SELECT DISTINCT ON (problem_id) problem_id, mastery_level, attempted_at
FROM problem_attempts ORDER BY problem_id, attempted_at DESC;
```

This preserves the full trajectory, makes the review engine auditable, and makes "did I regress on this?" answerable.

### 5.3 Repetition, mistakes, mocks

```sql
reviews(id, user_id, subject_type, subject_id, due_date,
        interval_days int, overdue_days int DEFAULT 0,
        last_result text, created_at)
-- subject_type: 'problem' | 'vocab' | 'ml_concept' | 'mistake'
-- polymorphic on purpose: one engine serves all four

mistakes(id, user_id, occurred_on, track, topic,
         what_went_wrong, root_cause, correct_thinking,
         memory_hook, redo_date, redo_result)

mocks(id, user_id, date, company_mode, round_type, prompt,
      score_coding, score_ml, score_sysdesign, score_comms,
      top_weakness, next_action)
```

`root_cause` is the field that matters. Repeat detection groups on its normalised form; three occurrences flags CRITICAL.

### 5.4 Life tracks

`thesis_log` · `vocab_words` · `recovery_log` · `nutrition_log` · `meals` · `meal_plan` · `reading_log` · `time_leaks` · `patterns` (the 18 DSA patterns and their cues) · `operating_rules` · `settings`.

### 5.5 Learned behaviour

```sql
observations(
  id, user_id, detected_at, kind, subject,
  claim text,                 -- 'completion drops 41% after <5.5h sleep'
  sample_size int,
  confidence text CHECK (confidence IN ('low','medium','high')),
  effect_size numeric,
  suggested_action text,
  status text  -- 'new' | 'accepted' | 'dismissed' | 'stale'
)
```

Dismissals are retained and suppress that observation kind for 30 days.

### 5.6 Migration

A Python ETL reads the workbook sheet by sheet and reports per-table row counts against expected values, aborting loudly on mismatch. Expected at time of writing: 2,534 time blocks · 270 curriculum rows · 122 prayer dates · 18 patterns · 488 meal-plan rows.

---

## 6. ENGINES

Four engines. Everything else is CRUD. All are pure functions over database state, unit-testable against fixtures, and none of them call an LLM.

### 6.1 Scheduling engine

Resolves `start_spec` / `end_spec` against `prayer_times` for a date. Detects overlaps and gaps. Recomputes when settings or prayer parameters change. Prayer times are computed from solar position (declination + equation of time; Islamabad 33.6844°N, 73.0479°E; Karachi convention, Fajr/Isha 18°, Hanafi Asr factor 2) with a **stated ±5–15 minute accuracy disclosed in the UI**. Never silently substitute an API.

### 6.2 Repetition engine

```
LADDER = {L0:1, L1:1, L2:3, L3:7, L4:14, L5:30, L6:60}   # days

on_attempt(subject, level, previous_level):
    if no prior attempt and level == L0 and no time logged:
        return  None                        # unattempted ≠ due
    if previous_level and level < previous_level:         # regression
        level = demote(previous_level)                    # drop one, reset
    due = today + LADDER[level]
    upsert review(subject, due, interval=LADDER[level], overdue_days=0)
```

Nightly job: any review with `due_date < today` has `overdue_days` incremented. **Nothing is ever dropped.**

**Capacity control.** Simulation over the seeded curriculum shows review load peaking near **15/day in November (~60 min)** on top of ~60 min of new problems — 120 of a 140-minute block, before any failures. Therefore:

- `daily_review_cap` (default 12) in settings
- Overflow order: failed reviews → oldest overdue → due today
- Remainder pushes one day, `overdue_days` increments, and the UI shows the projected breach *before* it arrives

### 6.3 Recommender engine

Deterministic and explainable. Never an LLM.

```
rank(candidates):
  1 FAILED REVIEW     regressed, due today or earlier
  2 OVERDUE REVIEW    oldest overdue_days first
  3 DUE REVIEW        due today
  4 SCHEDULED         today's curriculum slot
  5 PATTERN GAP       min(L5+ count / scheduled count) per pattern
  6 INTERLEAVE        random earlier pattern, prevents blocked practice

constraints:
  - max 2 consecutive from the same pattern after the foundation phase
  - never exceed the bandwidth budget
  - every result carries a `reason` string
```

The interleave rule exists because blocked practice produces fluency that evaporates in an interview. The measured skill is recognising a pattern cold.

### 6.4 Pattern engine — learning the user

This is what "note my pattern and suggest on that basis" means. It is **statistical, with minimum sample sizes**, because a system that makes confident claims from four data points destroys its own credibility.

| Observation | Computation | Min n | Example output |
|---|---|---|---|
| Best hours | completion rate by hour bucket | 10/bucket | "Blocks at 05:00–07:00 complete 78% vs 41% at 19:00–21:00" |
| Weekday shape | completion by weekday | 4 weeks | "Thursday is your weakest day, 3 weeks running" |
| Drop order under load | which category is skipped first on overloaded days | 8 days | "Reading is dropped first, then Theory. Thesis never is" |
| Duration bias | actual ÷ planned per category | 15 blocks | "Coding blocks run 22% over. Plan 170 min, not 140" |
| Sleep threshold | completion vs sleep hours, changepoint | 20 nights | "Below 5.5h, next-day L4+ output halves" |
| Failure clustering | mistakes grouped by normalised root cause | 3 repeats | "Three misses this month were all 'missed the sorted-input signal'" |
| Difficulty velocity | median minutes by difficulty over time | 10/difficulty | "Medium solve time fell 31→24 min over 3 weeks" |
| Streak breakage | what preceded a missed day | 5 breaks | "Missed days follow nights under 5h in 4 of 5 cases" |

Rules:

1. **Never state a pattern without its sample size** in the UI.
2. Confidence is `low` (n at threshold), `medium` (2×), `high` (4× plus stable across two windows).
3. Every observation carries **one concrete suggested action** — "move the coding block to 05:00 on Saturdays", not "consider optimising your energy".
4. Suggestions are proposals. Accept applies a schedule or setting change; dismiss suppresses that kind for 30 days.
5. Observations expire. An unconfirmed one goes `stale` after 21 days.
6. **The engine computes; the LLM only phrases.** If Groq is down, a template renders the same claim.

Deliberately excluded: mood inference, productivity scoring of the person, anything that reads as judgement rather than observation.

---

## 7. API SURFACE

```
GET  /api/today                    resolved blocks + next action + bandwidth state
POST /api/blocks/{id}/status       one-tap completion, optimistic, undoable
GET  /api/recommend?minutes&energy ranked list with reasons
POST /api/attempts                 mastery → writes attempt, returns next review date
GET  /api/reviews/due
GET  /api/insights/{chart_key}     pre-aggregated series for one chart
GET  /api/observations             learned patterns, filterable by confidence
POST /api/observations/{id}/accept
POST /api/llm/{task}               streaming; task ∈ {followup, grade, narrative, cluster}
```

All request and response bodies are Pydantic models. `/api/llm/*` is the only path that touches Groq.

---

## 8. LLM LAYER

Server-side only. Key is an env var, never in a bundle.

**Use for judgement, never for facts.**

| Permitted | Forbidden |
|---|---|
| Socratic follow-ups on a submitted answer | Generating LeetCode numbers or URLs |
| Grading a system-design answer to a rubric | Choosing the next problem |
| Clustering free-text mistake root causes | Computing review dates |
| Tightening a STAR story | Stating company interview processes |
| Weekly narrative from SQL results | Any unverifiable claim |

Streaming. JSON mode with schema validation and one repair retry. Response cache keyed on prompt hash. Per-day token budget with a visible counter. **Every LLM surface degrades to a useful non-LLM state.** Any model-produced problem reference is validated against `problems` before display or discarded.

---

## 9. FRONTEND

Next.js App Router. Server components for static shells, client components for interactive surfaces. TanStack Query with optimistic mutation and rollback. Service worker caches today and tomorrow; writes queue in IndexedDB and replay on reconnect with last-write-wins on `updated_at`.

**Today** is a decision surface, not a dashboard: current block with countdown, the Next Action card with inline L0–L6 buttons and its reason, the day timeline, a bandwidth control, and **three leading indicators only**. Charts live in **Insights**. Dark-first. Mastery colour-coded consistently and never colour alone. WCAG AA, full keyboard navigation, 44px touch targets, `prefers-reduced-motion` respected.

---

## 10. ANALYTICS

Fifteen charts grouped by the question each answers, each with a computed takeaway line beneath it. No pie charts, no dual axes. Leading indicators rank above lagging. Priority build order: **burn-up vs required pace**, **30-day review-load forecast with capacity line**, **pattern × mastery heatmap**. Full specification in the build prompt, section 8.

---

## 11. SECURITY

Key never client-side · RLS on every table · JWT verified server-side on every request · Pydantic validation at every boundary · parameterised queries only · rate limit on `/api/llm/*` · secrets in the platform secret store, `.env` gitignored · soft delete with undo on all destructive actions · nightly `pg_dump` retained 30 days.

---

## 12. OBSERVABILITY

Structured JSON logs (`structlog`). Request ID propagated client → API → DB. Tracked: recommender latency, LLM tokens and cost per day, cache hit rate, offline queue depth, review backlog, failed sync count. Alert on token budget at 80%, review backlog above 2× cap, sync failures over 5 minutes.

---

## 13. FAILURE MODES

| Failure | Behaviour |
|---|---|
| Groq down or over budget | Templated fallback; core app unaffected |
| Database unreachable | Cached today renders; writes queue |
| Prayer computation invalid (extreme latitude) | Fall back to last known, flag in UI |
| Review backlog exceeds cap | Overflow policy applies, breach shown |
| Clock/timezone drift | All dates computed server-side in `Asia/Karachi` |
| Import row-count mismatch | ETL aborts; no partial state |

---

## 14. DELIVERY PHASES

1. Repo, venv, CI, schema, migrations, xlsx ETL with verification
2. Auth, `/api/today`, Today view on real data
3. Scheduling engine + prayer resolver + tests
4. Repetition engine + capacity control + tests
5. Recommender + tests — **usable product from here**
6. Bandwidth engine
7. Remaining CRUD views
8. Insights: burn-up, review forecast, heatmap first
9. Pattern engine
10. Groq layer
11. Offline / PWA
12. Polish, Lighthouse, accessibility audit

Phases 1–5 must work before 6 begins. A polished shell over a broken recommender is worthless; a plain UI over a correct engine is usable on day one.

---

## 15. OPEN DECISIONS

| # | Decision | Default if unanswered |
|---|---|---|
| D1 | Render vs Railway vs Fly for the API | Render free tier |
| D2 | Daily review cap value | 12 |
| D3 | Does a failed review demote one level or reset to L0? | Demote one level |
| D4 | Keep the xlsx in sync, or is it retired at cutover? | Retired; export-only |
| D5 | Horizon past 31 Dec 2026 — extend or archive and restart? | Extend, same schema |
| D6 | Should the pattern engine be allowed to change the schedule automatically? | No — propose only, user accepts |

D6 matters most. An engine that silently rewrites your day is a system you stop trusting. Propose, explain, let the user accept.
