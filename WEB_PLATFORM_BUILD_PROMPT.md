# BUILD PROMPT — MERIDIAN

*Personal operating system. Named for the solar meridian — the astronomical
anchor from which every prayer time, and therefore the whole daily schedule,
is computed.*

> Paste this whole document as the brief. It replaces the spreadsheet with a web application.

---

## 0. WHO YOU ARE

Act simultaneously as:

- **Senior AI Architect** — retrieval, LLM orchestration, prompt design, cost and latency control
- **Full-Stack Engineer** — Next.js, TypeScript, Postgres, serverless, auth, migrations
- **UI/UX Designer** — information architecture, visual hierarchy, interaction design, accessibility
- **Product Engineer** — you decide what NOT to build
- **Data Modeller** — normalise a 25-sheet spreadsheet into a relational schema without losing meaning

You are not decorating a spreadsheet. You are building the daily operating system for one person's life for the next four months.

---

## 1. WHAT THIS IS

This replaces an existing Excel workbook — a personal Productivity OS covering **1 Sep → 31 Dec 2026** for a single user (MS Computer Science researcher, Islamabad, remote job 09:00–17:00, preparing for ML/AI engineer interviews at Meta / Amazon / Netflix / Google / OpenAI while finishing a thesis).

**Scope is the entire life system, not just interview prep.** Interview prep is one track among many. Do not build an interview app with a calendar bolted on. Build the daily operating system; interview prep is its heaviest current workload.

Tracks the system covers:

| Track | Nature |
|---|---|
| Daily Schedule | ~21 time blocks/day, prayer-anchored, the execution layer |
| Interview Prep | 270 LeetCode problems + theory rotation + mocks |
| Thesis | Work log, milestones, deadlines, output-based |
| English vocabulary | 5 words/day with spaced repetition |
| Recovery & Energy | Sleep, energy, mood, stress, recovery score |
| Nutrition & meals | Rotating meal library, daily plan, water, nutrition score |
| Reading | Book/paper log |
| Time leakage | Unplanned minutes, triggers, root causes |
| Weekly / monthly review | Rollups and goal tracking |
| Rescheduling | Missed-work log with displacement rules |
| Reference | Settings, operating rules, glossary, DSA patterns |

---

## 2. NON-NEGOTIABLES — READ BEFORE ARCHITECTING

**2.1 The API key must never reach the browser.**
GitHub Pages is static hosting with no server runtime. If you put a Groq key in frontend code, environment variable or not, it ships in the bundle and gets scraped. All LLM calls go through a server-side route. If the deployment target genuinely cannot run server code, say so and stop — do not ship a client-side key.

**2.2 One source of truth for completion.**
The predecessor spreadsheet had three competing stores of "did I do this today" and they disagreed within a day of use. **Task completion lives in exactly one table.** Every rollup, score and streak derives from it. No denormalised completion counters that can drift.

**2.3 Never fabricate.**
No invented LeetCode numbers, URLs, company tags, interview questions, or statistics. If the LLM generates a problem reference, it must be validated against the seeded database before display. Unverifiable content is labelled, not guessed.

**2.4 Offline-tolerant.**
This is used first thing in the morning and last thing at night, often on mobile, sometimes on poor connectivity. The day's schedule and today's problems must render from cache. Writes queue and sync.

**2.5 Prayer times are computed, not fetched.**
Existing solar-position formulas (declination + equation of time, Islamabad 33.6844°N 73.0479°E, Karachi convention: Fajr/Isha 18°, Hanafi Asr factor 2) drive the schedule. Port them exactly. Accuracy is ±5–15 min and must be disclosed in the UI. Do not silently swap in an API.

---

## 3. STACK

```
Frontend    Next.js (App Router) + TypeScript + Tailwind + shadcn/ui
State       TanStack Query + optimistic updates
Charts      Recharts
Backend     FastAPI · Python 3.12 · Pydantic · SQLAlchemy + asyncpg
Database    Supabase Postgres + Row Level Security
Auth        Supabase Auth (single user, but do it properly)
LLM         Groq Python SDK, server-side only
Hosting     Vercel (web) · Render or Railway (api) · repo on GitHub
Cron        pg_cron / Supabase scheduled functions
Offline     Service worker + IndexedDB write queue
```

**Backend is Python, not TypeScript.** The recommender and pattern engines do real
numeric work — rolling aggregates, correlation, changepoint detection — which is
natural in pandas/numpy and awkward in TS. The xlsx importer needs openpyxl
regardless. Python is the user's primary language and a Python service is the
better portfolio artifact for ML-engineer interviews. Cost: a second deploy target
and CORS config. Accepted.

Justify any substitution. Do not add a state library, ORM layer or component kit
beyond this without a stated reason.

### 3.1 PYTHON VIRTUAL ENVIRONMENT — MANDATORY

**Every Python dependency installs into a project-local venv. Never the system
interpreter. Never `sudo pip`.**

```bash
cd meridian/api
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
which python                        # MUST print .../meridian/api/.venv/bin/python
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Rules:

- `.venv/` is gitignored and never committed.
- Dependencies **pinned**; commit a lockfile. Runtime and dev requirements are
  separate files — test tooling never ships to production.
- `rm -rf .venv` then rebuild must always work. CI proves it on every push.
- The ETL scripts use the **same** venv. Do not create a second one.
- `uv venv` / `uv pip` is an acceptable faster substitute. `conda` is not.
- Node is separate and unrelated: `cd meridian/web && npm ci`.
- `.env.example` is committed; `.env` is not. `GROQ_API_KEY` lives only in the
  API's server environment.
- Provide a `Makefile`: `venv install dev test lint typecheck migrate seed
  import-xlsx`.

---

## 4. DATA MODEL

Design the full schema. These are the load-bearing tables — get their grain right.

**`time_blocks`** — the execution layer. One row per scheduled block per day (~21/day × 122 days). Columns: date, start, end, activity, tier (T1–T4), category, planned_minutes, status (`DONE | NOT DONE | PARTIAL | RESCHEDULED`), actual_minutes, energy_before, focus, deep_work, location, what_to_do, notes.
Start/end may be **absolute** (`17:05`) or **prayer-relative** (`maghrib + 15min`). Model both. Resolve relative times at read time from the computed prayer table.

**`problems`** — the seeded LeetCode curriculum. lc_number, title, slug, url, pattern, difficulty, is_neetcode150, is_blind75, company frequencies (Meta/Amazon/Google as integers; Netflix and OpenAI have no data — allow null, never invent).

**`problem_attempts`** — one row per attempt, not per problem. attempted_at, minutes, mastery_level (L0–L6), hint_used, key_insight, mistake_id.
Mastery is a property of the latest attempt, not a mutable field on `problems`. This preserves history and makes the review engine auditable.

**`reviews`** — the spaced-repetition queue. subject_type (`problem | vocab | ml_concept | mistake`), subject_id, due_date, interval_days, ease, last_result. Polymorphic, because problems, English words, ML concepts and mistakes all need the same engine.

**`mistakes`** — date, track, topic, what_went_wrong, **root_cause**, correct_thinking, memory_hook, redo_date, redo_result. Root cause is the field that matters; repeat detection groups on it.

**`mocks`** — date, company_mode, round_type, prompt, scores (coding/ml/system_design/communication), top_weakness, next_action.

Plus: `thesis_log`, `vocab_words`, `recovery_log`, `nutrition_log`, `meals`, `reading_log`, `time_leaks`, `settings`, `patterns`, `operating_rules`.

**Migration:** write an importer that reads the existing `.xlsx` and populates every table. Report row counts per table and refuse to proceed silently on mismatch.

---

## 5. THE FOUR ENGINES

This is the actual product. Everything else is CRUD. All four are pure functions
over database state, unit-testable against fixtures. **None of them call an LLM.**

### 5.1 Spaced repetition engine

Ladder by mastery, in days:

```
L0 Seen               → 1
L1 Understood         → 1
L2 Solved with help   → 3
L3 Solved independently → 7
L4 Can explain        → 14
L5 Interview ready    → 30
L6 Mastered           → 60
```

Rules:
- An item with no recorded attempt schedules **no review**. Unattempted ≠ due.
- Failing a review **drops mastery one level and resets the interval** — it does not simply repeat.
- Two consecutive successes at the same level promote it.
- Overdue items never silently vanish. A nightly job rolls them forward and increments an `overdue_days` counter that the UI surfaces.
- Same engine serves problems, vocabulary, ML concepts and mistakes.

### 5.2 Next-problem recommender

**This is the feature the user asked for. It must be deterministic, not LLM-generated.**

When the user opens the app or finishes a problem, produce the next single problem by ranked priority:

```
1. FAILED REVIEW      mastery dropped, due today or overdue
2. OVERDUE REVIEW     due_date < today, oldest first
3. DUE REVIEW         due_date = today
4. TODAY'S SCHEDULED  from the pre-assigned curriculum
5. PATTERN GAP        weakest pattern by (L5+ count ÷ scheduled count)
6. INTERLEAVE         a random earlier pattern, to prevent block-practice illusion
```

Never serve more than **2 consecutive problems from the same pattern** once past the foundation phase — pattern recognition is the skill, and blocked practice inflates it.

**Interaction:** the user clicks a mastery level on the problem card. The system immediately writes the attempt, computes the next review date from the ladder, shows a confirmation (*"Next review: 14 Sep, 7 days"*), and serves the next recommendation. **One click, no forms.** When that date arrives the problem reappears at the top of the queue, tagged `REVIEW`, with the key insight the user wrote last time hidden behind a "reveal" control — recall first, then check.

Explain *why* each recommendation was made in one line: *"Overdue 3 days — you rated this L2 on 12 Sep."* Never a black box.

### 5.3 Bandwidth engine

The user reports today's capacity; the system fits work to it. Inputs:

- minutes available (explicit, or inferred from unclaimed blocks)
- energy 1–5 (explicit, or last night's sleep from `recovery_log`)
- current overdue backlog
- time of day

Behaviour:

| Situation | Response |
|---|---|
| High energy, ≥2h | New Hard/Medium problems, unfamiliar system design, timed mock |
| Medium energy, ~1h | Scheduled Medium problems, theory topic, ML coding |
| Low energy, ~30min | Reviews, vocabulary, flashcards, reading a solution — no new Hard problems |
| Very low / <20min | Minimum Viable Day only. Say so plainly and stop suggesting |
| Large overdue backlog | Reviews outrank new problems regardless of energy |

**Never propose more than the stated budget.** Padding a 30-minute window with 90 minutes of work is how the system gets abandoned. When the user has bandwidth, offer *specific* extra work — *"You have 40 spare minutes and 6 overdue reviews; clearing them takes ~35"* — not "you could do more."

### 5.4 Pattern engine — learning the user's own behaviour

Distinct from DSA patterns. This engine observes how *this person* actually works
and adapts suggestions. It is **statistical with minimum sample sizes**, because a
system making confident claims from four data points destroys its own credibility.

| Observation | Computation | Min n | Example output |
|---|---|---|---|
| Best hours | completion rate by hour bucket | 10/bucket | "05:00–07:00 blocks complete 78% vs 41% at 19:00–21:00" |
| Weekday shape | completion by weekday | 4 weeks | "Thursday weakest, 3 weeks running" |
| Drop order under load | first category skipped on overloaded days | 8 days | "Reading drops first, then Theory. Thesis never does" |
| Duration bias | actual ÷ planned per category | 15 blocks | "Coding runs 22% over — plan 170 min, not 140" |
| Sleep threshold | completion vs sleep, changepoint | 20 nights | "Below 5.5h, next-day L4+ output halves" |
| Failure clustering | mistakes grouped by normalised root cause | 3 repeats | "Three misses were all 'missed the sorted-input signal'" |
| Difficulty velocity | median minutes by difficulty over time | 10/difficulty | "Medium solve time 31→24 min over 3 weeks" |
| Streak breakage | what preceded a missed day | 5 breaks | "Missed days follow <5h nights in 4 of 5 cases" |

Rules:

1. **Never state a pattern without its sample size shown in the UI.**
2. Confidence: `low` at threshold n, `medium` at 2×, `high` at 4× and stable
   across two windows.
3. Every observation carries **one concrete action** — "move Saturday coding to
   05:00", not "consider optimising your energy".
4. Propose only. Accept applies a change; dismiss suppresses that kind 30 days.
5. Observations go `stale` after 21 days unconfirmed.
6. **The engine computes; the LLM only phrases it.** Groq down → template renders
   the identical claim.
7. Do not build: mood inference, productivity scoring of the person, or anything
   that reads as judgement rather than observation.

**The engine must never silently rewrite the schedule.** A system that changes your
day without asking is one you stop trusting. Propose, explain, let the user accept.

---

## 6. GROQ / LLM LAYER

Server-side only. Every call goes through a route handler with the key in an env var.

**Use the LLM for judgement, not for facts.**

| Good use | Why |
|---|---|
| Socratic follow-ups on a submitted answer | Interviewer-attack mode |
| Grading a system-design answer against a rubric | Structured, reviewable |
| Clustering free-text mistake root causes | Finds patterns the user can't see |
| Rewriting a rambling STAR story tighter | Language, not fact |
| Weekly narrative from the week's actual numbers | Numbers come from SQL, prose from the LLM |

| Bad use | Why |
|---|---|
| Generating LeetCode problems or numbers | Hallucinates; DB is seeded and authoritative |
| Deciding the next problem | Must be deterministic and explainable |
| Computing review dates | Arithmetic belongs in code |
| Stating company interview processes | No verified source |

Requirements: streaming responses; JSON-mode with schema validation and a repair retry; cache identical prompts; per-day token budget with a visible counter; **every LLM surface degrades to a useful non-LLM state** when the API is down or the budget is spent.

---

## 7. UI / UX

**Design principle: the home screen answers one question — *what do I do right now?*** Everything else is one tap away.

### Home ("Today")
- Current block, large, with a live countdown to its end
- **Next Action card**: the recommended problem or task, with its one-line reason, and mastery buttons L0–L6 inline
- Compact timeline of the day; tap a block to mark DONE / PARTIAL / NOT DONE
- Bandwidth control: a single "How much time and energy do you have?" input that reshapes suggestions
- Three counters only: overdue reviews, blocks remaining, readiness %

Do **not** put twelve KPI tiles on the home screen. The spreadsheet's failure mode was information without direction.

### Other views
Problems (filterable table + card mode) · Patterns (recognition cues) · Mistakes (grouped by root cause, repeats flagged) · Mocks · Thesis · Health (sleep/energy/nutrition trends) · Review (weekly + monthly) · Settings.

### Visual
- Dark-first; this is used at 04:30 and 22:00
- Type scale with real hierarchy — one page, one primary element
- Mastery colour-coded consistently everywhere (L0 red → L6 green), and **never colour alone** — always a label too
- Prayer blocks visually distinct and never presented as skippable
- Mobile-first: thumb-reachable primary actions, no horizontal scroll, 44px minimum touch targets
- Respect `prefers-reduced-motion`; WCAG AA contrast; full keyboard navigation
- Empty states teach the system rather than showing a shrug

### Interaction rules
- Marking a task complete: **one tap, optimistic, undoable**
- No confirmation dialogs for reversible actions
- Every destructive action is soft-delete with undo
- Loading states are skeletons, not spinners
- The app never blocks on the network

---

## 8. ANALYTICS & DASHBOARD

**Where charts live.** Not on Today. Today answers *what do I do now*; adding twelve tiles to it recreates the spreadsheet's failure — information without direction. Charts live in a dedicated **Insights** view, with at most **three** summary numbers surfaced on Today.

### 8.1 Rules for every chart

1. **Each chart answers one written question.** Put the question in the chart title, not a noun phrase. "Am I on pace?" beats "Progress Overview."
2. **Every chart carries a computed takeaway line** underneath, generated from the data — *"You are 23 problems behind pace; at your current 2.4/day you finish 6 days late."* A chart without a conclusion is decoration.
3. **No pie or donut charts.** No dual y-axes. No 3D. No stacked area for anything that isn't a true part-to-whole over time.
4. **Never colour alone.** Every colour-encoded series also carries a label, shape or direct annotation. Colour-blind users and greyscale printing both matter.
5. **Show the target.** A progress chart without the required-pace reference line cannot tell you whether you're behind.
6. **Empty states teach.** Before data exists, show the chart's shape with sample data, greyed, plus one line explaining what it will tell you.
7. **Mobile:** charts reflow to a single column, minimum 240px tall, touch tooltips, no hover-only information. If a chart can't work at 380px wide, replace it with a sorted table on mobile.
8. **Time range control** is global to the view: 7d / 30d / phase / all.

### 8.2 The charts

Grouped by the question they answer.

**AM I ON PACE?**

- **Burn-up: problems at L5+ vs plan.** Line chart, cumulative. Two series: actual L5+ count, and the required-pace reference line from today to 270 by 31 Dec. Annotate the projection where actual velocity extrapolates. This is the single most important chart in the app.
- **Thesis burn-down to deadline.** Same treatment against Thesis Tracker milestones. Thesis and prep compete for the same hours — showing them adjacent makes the trade-off visible instead of discovered in December.

**WHAT IS MY REAL WEAKNESS?**

- **Pattern × mastery heatmap.** 18 patterns down, L0–L6 across, cell = count. Instantly shows which patterns are stuck at L2–L3. Sort rows by weakest. This replaces guessing at what to practise.
- **Mistake root-cause Pareto.** Horizontal bar, descending, cumulative % line. Groups `mistakes.root_cause`. The point is that ~3 root causes usually explain most failures — surface them, don't average them away.
- **Difficulty mix at L5+ vs target.** Grouped bar: Easy/Medium/Hard achieved against the curriculum's mix. Catches the classic self-deception of grinding Easy problems to inflate the count.

**IS MY REVIEW LOAD SUSTAINABLE?**

- **Review load forecast — 30 days forward.** Bar chart of scheduled reviews per upcoming day, with a horizontal capacity line at the daily review budget in minutes. **This is a forward-looking chart and most systems don't build one.** Modelled on the current curriculum, load peaks around **15 reviews/day in November (~60 min)** on top of ~60 min for three new problems — 120 of a 140-minute block, with no slack for failures, and every failed review resets an interval and adds more.
  - Therefore: implement a **daily review cap** (default 12) with an explicit overflow policy — oldest-overdue first, remainder pushed one day, `overdue_days` incremented and shown. Never silently drop a review. Surface the projected breach *before* it happens.

**DOES MY BODY PREDICT MY OUTPUT?**

- **Sleep vs next-day performance scatter.** X = sleep hours, Y = problems reaching L4+ that day. Point colour = energy rating. Fit a trend line only when n ≥ 20, and label the correlation coefficient honestly — including when it's weak. Do not imply causation.
- **Energy heatmap: hour × weekday.** Cell = mean focus/energy from `time_blocks`. Reveals whether the 17:05 coding block is actually a good slot or whether weekend mornings genuinely outperform it. This chart can justify moving the schedule.

**WHERE DID THE TIME GO?**

- **Planned vs actual minutes by tier.** Diverging bar per tier (T1–T4), planned left, actual right. Catches the gap between intention and execution.
- **Time leakage by trigger.** Horizontal bar from `time_leaks`, with a 7-day sparkline per trigger to show whether it's improving.
- **Weekly completion by category.** Stacked bar, one column per week, segments = category. 18 weeks fits comfortably.

**AM I INTERVIEW READY?**

- **Readiness radar.** Six axes: DSA mastery, mock coding, mock ML, mock system design, mock communication, weakness closure. Overlay the previous month's shape in outline to show movement. Radar is normally a bad chart — it's justified here only because the axes are genuinely commensurate (all 0–100) and shape-change over time is the message.
- **Mock score trend.** Multi-line, one per dimension, x = mock number. Small n, so show points and connect them; don't smooth.
- **Readiness band gauge.** The five bands (NOT READY → HIGHLY PREPARED) as a segmented horizontal bar with a marker. Label it clearly as an internal preparation threshold, **not** a prediction of a hiring outcome.

### 8.3 Leading vs lagging

Mark each metric in the UI:

- **Lagging** (outcome): readiness %, L5+ count, mock scores. Reassuring, but you cannot act on them today.
- **Leading** (behaviour): review backlog, blocks completed, sleep hours, overdue days, time leaked. These predict the lagging ones and are the only ones you can change this morning.

Put leading indicators *above* lagging ones. The Today view shows **leading only**.

### 8.4 Weekly narrative

One LLM-generated paragraph per week, built from SQL results — never from the model's own recollection. It states what moved, what slipped, the single biggest lever for next week, and it names a specific action. If the Groq call fails, fall back to a templated version from the same numbers. The numbers are always computed in SQL; only the prose is generated.

---

## 9. WHAT NOT TO BUILD

- Social, sharing, leaderboards, streak-shaming
- Gamification beyond honest progress
- A second planner competing with the schedule
- Configurable dashboards — you decide the layout, that's the job
- An LLM chat window as the primary interface
- Anything that makes the user feel worse for a bad day. The Operating Rules define a Minimum Viable Day; honour it

---

## 10. QUALITY BAR

- TypeScript strict, no `any`
- Zod validation at every boundary
- Unit tests for the four engines — they are the product
- Chart aggregations tested against fixture data; a wrong chart is worse than no chart
- CI recreates the venv from scratch and runs lint, mypy and pytest
- The recommender must be **testable**: given a fixture DB state, it returns a deterministic ranked list
- Seed script producing a realistic 4-week dataset for development
- Lighthouse ≥ 90 on mobile
- Migrations versioned and reversible

---

## 11. DELIVER IN THIS ORDER

0. **Repo, venv, CI, Makefile** — `rm -rf .venv && make install && make test` green
1. **Schema + migration + xlsx importer**, with row-count verification
2. **Today view** reading real data — no engines yet
3. **Spaced repetition engine** + tests
4. **Next-problem recommender** + tests
5. **Bandwidth engine**
6. Remaining CRUD views
7. **Insights view** — build the burn-up and the review-load forecast first; they change decisions. The rest follow
8. Groq layer
9. **Pattern engine**
10. Offline + PWA
11. Polish

Ship 1–4 working before starting 5. A beautiful shell over a broken recommender is worthless; a plain UI over a correct engine is usable on day one.

---

## 12. BEFORE YOU WRITE CODE

State:
- Your schema, with the grain of every table
- Where completion lives, and how every rollup derives from it
- How prayer-relative times are stored and resolved
- The recommender's ranking function in pseudocode
- Which LLM calls you'll make and what each degrades to
- The daily review cap and your overflow policy when it is breached
- For each chart: the question it answers, the SQL behind it, and its empty state
- What you're deliberately not building

Then flag every assumption you had to make, and ask before guessing.
