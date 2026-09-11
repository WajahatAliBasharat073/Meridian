# Implementation Roadmap

Sequential, not parallel — each phase produces something real before the next begins, per the audit's core instruction not to make one giant uncontrolled change.

## Phase 1 — Audit + Architecture (this deliverable set) — DONE

Produced: `PRODUCT_AUDIT.md`, `ARCHITECTURE_AUDIT.md`, `UX_AUDIT.md`, `FINANCE_MODULE_PROPOSAL.md`, `LEARNING_SYSTEM_AUDIT.md`, `DATA_MODEL_AUDIT.md`, `SECURITY_AUDIT.md`, this roadmap. No production code touched.

## Phase 2 — Foundation — DONE (2026-09-10)

1. ✅ Structured logging (`app/logging.py`, `structlog`) wired into app startup, every auth-failure path in `deps.py`, and both LLM-call failure paths in `coach.py`.
2. ✅ Cross-user isolation test suite (`tests/test_cross_user_isolation.py`) — 4 tests spanning `goals`, `time_budgets`, `thesis_log`, `question_progress`, run against the real database with full cleanup.
3. ✅ `curriculum_topics` RLS gap closed (migration `0022_curriculum_topics_rls`, applied).
4. ✅ `coach.py` extracted into `engines/coach.py` (`build_system_prompt`, `local_fallback_response`, both pure, both tested — `tests/test_coach_engine.py`). While extracting, found and fixed a real fabrication bug: the local fallback's catch-all and "thesis" branches unconditionally asserted a fixed fake date ("Monday, September 7, 2026"), a fixed fake block count ("21 scheduled blocks"), and a fixed fake schedule ("124 minutes... 04:41-06:45") regardless of what was actually scheduled — a direct violation of the same anti-invention rule the system prompt orders the LLM to follow. Both now describe only real data.
5. ✅ Consolidated the two duplicated "not enough data" thresholds (`app/engines/policy.py`, `MIN_SAMPLES_FOR_INSIGHT`, imported by both `punctuality.py` and `theory_pace.py`) and the two duplicated readiness-% computations (`app/domain.py`'s `readiness_pct()`, used by both `summary.py` and `today.py`).

186/186 tests passing, `ruff check` and `mypy` both clean across the full `app/` tree.

## Phase 3 — Finance — DONE (2026-09-11)

1. ✅ Migration `0023_finance` — `finance_accounts`, `finance_categories` (30 system-seeded rows, hierarchical: Education→{Courses,Books,Conferences,Certifications}, Research→{Papers,Conferences,Compute/GPU,APIs,Software,Books}), `finance_transactions`, `finance_recurring`, `finance_budgets`, `finance_goals`, `finance_net_worth_snapshots`. RLS on every table (hybrid read policy on `finance_categories` for system-vs-own rows), applied and verified live.
2. ✅ Engine (`app/engines/finance.py`, pure functions, 25 tests): month summary, income-change %, category breakdown, spending outliers (refuses below `MIN_MONTHS_FOR_TREND=2` prior months — same discipline as `engines/policy.py`), budget utilization, goal progress (required-monthly-contribution derived, never stored), upcoming commitments, `build_insights()` — the actual decision sentences, each only rendered when the underlying comparison means something.
3. ✅ Repository (`app/repositories/finance.py`) — account-balance maintenance is transactional and reversible (verified: creating/deleting a transaction moves/unmoves the exact right amount; `status='planned'` never touches a balance); `FinanceGoal.current_amount` is always `SUM()` of linked contributions, never a stored number (6 integration tests against the live DB, `tests/test_finance_integration.py`).
4. ✅ Routers — `finance_accounts.py` (+ `categories_router`), `finance_transactions.py`, `finance_recurring.py`, `finance_budgets.py`, `finance_goals.py`, `finance_dashboard.py`, all wired into `main.py`, all logging mutations via Phase 2's `structlog` setup, all following the existing `Depends(get_current_user_id)` pattern with zero exceptions.
5. ✅ Frontend — `finance` nav entry, `lib/types.ts`/`lib/api.ts`/`hooks/useFinance.ts` following the exact existing conventions, `lib/money.ts` formatter, five components under `components/finance/` (Accounts/Transactions/Budgets/Goals panels + Net-Worth/Category-Breakdown charts + an Insights card), one tabbed page at `/finance` mirroring `dashboard`'s tab pattern exactly. A transaction can optionally link to a goal — a "contribution" is just a normal transaction, not a separate feature.
6. ✅ Verified live: 211 backend tests passing, `ruff`/`mypy` clean; a full authenticated HTTP smoke test (real HS256 JWT signed with the configured secret) created an account, posted an income transaction, confirmed the balance moved by exactly the right amount, took a net-worth snapshot, and read a correct dashboard back — then cleaned up. Frontend: `tsc --noEmit`, `eslint`, and `next build` all clean, `/finance` registered as a route.
7. Manual entry only — no CSV import, no bank integration (both explicitly deferred, per the module's own phasing).

**Known verification gap**: the actual rendered browser UI was not click-tested — the app's Next.js API proxy requires a real authenticated Supabase session by design, and no test login credentials exist for this project. Recommend the user does one real click-through of `/finance` before relying on it.

## Phase 4 — Learning Intelligence — engineering half DONE (2026-09-11), content half NOT started

✅ `scripts/curriculum_gap_report.py` — automated per-topic gap report for every gated topic below a completeness threshold (a fixed six-angle rubric: intuition / mechanism-derivation / edge-cases / debugging / implementation / comparison, matched by keyword against existing question titles — deliberately generic rather than fabricating bespoke per-topic content it has no expertise to invent). Verified against the live bank: correctly reproduces the `backpropagation` example from `LEARNING_SYSTEM_AUDIT.md` and additionally flags `linear_algebra`, `probability`, `calculus_optimization` (too few questions to trust coverage), `numpy_vectorization`/`pandas_data`/`python_for_ml` (zero questions), plus every other thin/empty gated topic, each phase-prioritized.

Not started — genuine content-authoring work, distinct in kind from the engineering above and carrying real technical-accuracy risk if rushed:

1. Author the P0-Foundations content gap (python/numpy/pandas/backprop — zero questions each, per the gap report above).
2. Author debugging-format questions bank-wide (currently 11 of 722, 1.5%).
3. Formalize the LLM-judge duplicate/classification review used manually earlier this session into a repeatable script emitting the `question_a/question_b/relationship/reason/recommended_action/confidence` report format — human-approval gate preserved, never auto-delete. (The mechanics already exist in `find_duplicate_questions.py`; this would extend it with a `relationship` classification field.)

**Recommendation**: treat 1-2 as their own dedicated task — writing dozens of technically-correct new ML/DSA interview questions deserves focused attention and is a different kind of work than the schema/engine/API work in Phases 1-3.

**Update (2026-09-11): 1-2 done.** `scripts/author_p0_and_debugging_content.py` added 45 hand-classified questions (`classification_confidence="adjudicated"`): 6-7 each for `python_for_ml`, `numpy_vectorization`, `pandas_data` (all previously empty), 8 for `backpropagation` (previously empty), 2 each for `linear_algebra`/`calculus_optimization`/`probability`, and 10 bank-wide debugging-format questions. Every coding-question reference solution was executed and checked before insertion — the backprop one initially failed a numerical-gradient-check verification (a loss-averaging convention bug: dividing by `n` instead of `y.size`), caught and fixed before insertion, not after. P0 Foundations moved from INCOMPLETE (15 knowledge questions) to READY (39 knowledge, 9 entry points); debugging-format questions went from 11 to 26 (722 → 767 total questions). 226/226 backend tests pass.

## Unplanned addition (2026-09-11): English Vocabulary + configurable Focus routing

Requested mid-session, alongside continuing the phases above. Two independent pieces:

**Vocabulary** — the schema already had an unused `VocabWord` model (no router/repo/frontend ever built on it); extended rather than duplicated. Migration `0024_vocab_words_enrichment` added `pronunciation`, `part_of_speech`, `category`, `learning_status` (known/learning/difficult/need_to_revisit — one flat status, no separate mastery ladder needed here), and an import-tracking pair (`source`, `notion_page_id`) for safe re-import. A pure engine (`app/engines/vocab.py`) ranks the daily review batch (revisit-flagged first, then difficult, then unreviewed, then learning, then known, day-seeded jitter within a tier). Repository, schemas, router (`/api/vocab`, `/api/vocab/daily`, status/delete), and a `/vocabulary` page (today's-review flashcard flow + filterable browse, mirroring the existing `QuestionFlashcards` pattern) are all built and verified live (create → dedup-rejects a repeat word with 409 → status update → filter → delete, all over real HTTP).

**Notion**: the provided link (`app.notion.com/p/...`) is a private, authenticated URL. No Notion API key exists anywhere in this project, no Notion MCP tool is available, and `WebFetch` correctly returned nothing but a login shell — confirmed rather than assumed. No vocabulary content was fabricated. The supported path is Notion's own CSV export (`scripts/import_vocab_csv.py`), which needs no API key, flexibly matches common export column names, and dedups case-insensitively per user on re-import (verified: created 2 on first run, updated 0/2 on a re-run of the same file). **Vocabulary entries currently in the database: 0** — none have been imported, since importing means running that script against a real Notion export, which only the user can produce.

**Focus routing** — `web/lib/focusRouting.ts`: a `FOCUS_ROUTES` config array (`{category, activityIncludes?, destination, label}`) plus `resolveFocusDestination(category, activity)`, unit-tested (6 tests). Wired into both of `ActivityController.tsx`'s session-start actions (current-block "Start Activity" and upcoming-block "Start Focus Session") — after starting the timer (unchanged, global store, unaffected by navigation), it navigates to the configured destination if one exists, otherwise does nothing (graceful fallback, per spec). Currently mapped: Thesis→`/research`, English→`/vocabulary`, Reading→`/reading`, InterviewPrep→`/problems` when the activity text names a DSA topic (leetcode/two-pointer/sliding-window/etc.) else `/concepts`. Adding a new one (the spec's own example: System Design→`/system-design`) is one array entry, no component change.

Verified: full frontend suite (`tsc --noEmit`, `eslint`, `vitest run` — 25/25 passing including the 6 new routing tests, `next build`) all clean; `/vocabulary` registered as a route. Desktop/mobile navigation behavior is unchanged from the existing Next.js router (`router.push`), which already handles both — no separate mobile path exists to verify. The actual click-through (does Focus visibly land on the right page in a browser) was not visually confirmed for the same reason as the Finance module: no real login session available to this session.

## Phase 5 — Unified Personal OS

Only once Finance and the learning-content gaps are real:

1. Add an optional `finance_goal_id` link on `Goal` (or shared UI over the two models) — the narrow goal-linkage version from `PRODUCT_AUDIT.md`, not a full habit/task system.
2. Build a genuine cross-domain dashboard aggregator — a new engine that reaches into today/dashboard/finance/goals/research, closing the gap found in `ARCHITECTURE_AUDIT.md` where neither existing "control center" reaches outside its own domain.
3. Re-evaluate global search and the unified event/activity model **only if** real cross-domain data volume by this point justifies them — both are explicitly deferred, not committed, per `PRODUCT_AUDIT.md`.

## Phase 6 — AI Assistant

Last, deliberately — a contextual assistant is only as good as the data underneath it:

1. Confirm `coach.py`'s Phase-2 extraction into `engines/coach.py` is holding up under the new domains.
2. Extend the assistant's grounded context to goals, vitals, and finance data, using the exact same real-rows-only, explicit-"do not invent" system-prompt discipline already proven in production today.

## What this roadmap deliberately does not do

It does not build Career, a habit tracker, global search, or the unified event model on spec — none have a real consumer yet, and building them now would be exactly the unnecessary complexity this audit was charged to catch. Each is a one-line addition to a future phase if and when real usage creates the need.
