# Product Audit

## Vision test: can this become a Personal Operating System?

Yes, structurally — but not by adding Finance (or anything else) on top of the current surface area in one pass. The app already has the two things a "personal OS" actually needs underneath the feature list: a consistent security/isolation boundary (`user_id` threaded through every repository call, verified with zero exceptions — `SECURITY_AUDIT.md`) and a consistent engine discipline (pure functions, refuse-rather-than-fabricate — `ARCHITECTURE_AUDIT.md`). What it does not yet have is a layer *above* the individual domains that understands relationships between them — today's `dashboard` is DSA-mastery-shaped, `today` is schedule-shaped, and neither reaches into goals, vitals, or (soon) finance. Becoming a Personal OS is exactly that missing aggregation layer, and it should be built last (Phase 5), once there are enough real domains worth aggregating.

## What's already good

- The engine layer's discipline (pure functions, deterministic seeded randomness, explicit `None`/`enough_data=False` refusal over invented confidence) is unusually strong for a solo project and should be the standard every new domain — Finance included — is held to.
- `user_id`-from-JWT isolation is applied with perfect consistency across the entire router surface — this is the app's real security boundary and it holds.
- The frontend's centralized conventions (`lib/api.ts`, `lib/types.ts`, `lib/nav.ts`, the `Skeleton`/`QueryError`/`EmptyState` triad, one charting library behind `ChartCard`) mean the product actually feels coherent today, not glued-together.
- The curriculum rebuild (documented separately) is a working example of exactly the kind of rigor — reason-coded decisions, validator scripts, explicit known-gaps documentation — the rest of the product should aspire to.
- The existing AI assistant (`coach.py`) already proves the "grounded, not hallucinated" pattern the spec asks for in a future assistant — it's a foundation to extend, not build from scratch.

## What's weak

- Zero structured logging anywhere — no audit trail for auth failures, LLM-call outcomes, or (soon) financial mutations.
- No cross-user isolation test — the one place the app's actual security boundary is unverified by anything but manual reading.
- P0 Foundations in the learning system is measurably thin (15 questions, 3 entry topics with zero content), and debugging-format questions are a rounding error (11 of 722) — see `LEARNING_SYSTEM_AUDIT.md`.
- `coach.py` is the one part of the backend that isn't unit-testable the way everything else is — it mixes DB fetch, prompt assembly, and error handling in one router function.
- No account export/deletion endpoint — not urgent today, but a real gap ahead of storing financial data.

## What's redundant

- Two independently-computed "readiness %" figures (`summary.py` and `today.py`).
- Two independently-defined "not enough data yet" thresholds (`punctuality.py`, `theory_pace.py`).
- Two separately-evolved content rankers (`recommender.py` for DSA problems, `daily_theory.py` for theory questions) reimplementing the same tiered-priority/seeded-shuffle/diversity-cap shape that `curriculum.py`'s newer ranking engine also now covers for theory questions specifically.

None of this is broken; it's organic accumulation worth consolidating opportunistically (Phase 2), not urgent enough to block anything.

## Evaluating proposed new capabilities against the 7-question framework

| Candidate | Problem solved | Overlaps existing? | Produces reusable data? | Verdict |
|---|---|---|---|---|
| **Finance module** | Zero financial visibility today; `time_budgets` covers minutes, not money. | No real overlap — genuinely new domain. | Yes — feeds career income analytics, education/research spend reporting, goal funding, upcoming-bills planning, all for free via category rollups. | **Build.** High value, bounded complexity when kept manual-first. |
| **Unified event/activity model** (`QUESTION_SOLVED`, `EXPENSE_CREATED`, ...) | Claims to enable analytics without per-module analytics systems. | Yes, significantly — `dashboard.py`/`summary.py`/`weekly_review.py`/`daily_recap.py` already compute their own analytics directly from source tables with no observed problem at this data volume. | Speculative — a queryable unified timeline is only valuable once a real consumer (e.g. a cross-domain activity feed, or the AI assistant needing one) exists. | **Defer.** Building it now means every future write path must remember to dual-write to an event log with no proven consumer yet — exactly the "unnecessary complexity" this audit was charged to catch. Revisit when Phase 6's AI assistant creates real pull for a unified timeline. |
| **Global search** | Finding things across domains. | Minimal — additive. | Only valuable once there's enough cross-domain volume that per-page filters stop being sufficient (today: 722 questions have filters already; research/goals have a handful of rows each). | **Defer** to Phase 5, after Finance adds a genuinely search-worthy new corpus (transactions). |
| **Full unified goal↔task↔habit system** | Goals today are flat/manual; no habit-tracking or task-backlog subsystem exists at all in this codebase. | Building the full version means building two subsystems that don't exist yet just to serve "goals." | A narrower version (goal ↔ finance_goal link, lightweight milestone list) delivers most of the real value without inventing a habit tracker speculatively. | **Build the narrow version** (Phase 5); **defer** full habit/task linkage until those subsystems have independent justification. |
| **AI assistant expansion** (goals/vitals/finance awareness) | Real, directly requested use cases ("what should I study today," "how much can I safely save"). | Extends `coach.py`, doesn't duplicate it. | High — but only as good as the data underneath it (Finance/Goals need to exist and be trustworthy first). | **Build, but sequence last** (Phase 6), after `coach.py` is refactored into a testable engine and Finance/Goals data is real. |
| **LLM-as-judge for question/data quality** | Formalizing what was already done manually this session (duplicate detection, classification adjudication). | Overlaps the scripts already built (`find_duplicate_questions.py`, `curriculum_overrides.py`) — the process exists, just not as a standing repeatable tool. | Yes — a `question_a/question_b/relationship/reason/recommended_action/confidence` report format, matching the `ReasonCode` discipline already proven in `curriculum.py`. | **Formalize, don't rebuild.** Turn the existing manual process into a repeatable script with the same never-auto-delete guardrail already followed by hand. |

## Prioritized recommendations

| Priority | Feature | Problem | Current state | Proposed solution | Value | Complexity | Dependencies | Risk |
|---|---|---|---|---|---|---|---|---|
| P0 | Structured logging | No audit trail anywhere | Zero logging in the whole codebase | Add `structlog` (already a pinned, unused dependency) at repo-write layer + LLM-call paths | High — required before Finance's mutations are trustworthy | Low | none | Low |
| P0 | Cross-user isolation test | The app's actual security boundary is untested | 18 test files, all engine unit tests, none cross-user | One integration suite: two users, assert zero cross-contamination on every list/get endpoint | High — this is the app's real security guarantee | Low-Med | none | Low |
| P0 | `curriculum_topics` RLS gap | Only reference table without a read policy | Missing since `0019` | One-line migration adding the standard reference-table policy | Low blast radius, but closes an inconsistency before it's copy-pasted elsewhere | Trivial | none | None |
| P1 | Finance module (manual-first) | No financial visibility | Doesn't exist | Full proposal in `FINANCE_MODULE_PROPOSAL.md` | High — directly requested, integrates cleanly | Med | P0 items done first (logging must cover money mutations from day one) | Med — real data, needs care, but manual-first bounds scope |
| P1 | P0-Foundations content gap | Curriculum's own validator flags P0 INCOMPLETE; python/numpy/pandas/backprop topics have zero questions | 15 knowledge questions total in P0 | Author 20-30 new questions targeting the specific empty topics identified in `LEARNING_SYSTEM_AUDIT.md` | High for any true-beginner learner | Low (content, not engineering) | none | Low |
| P1 | Account export / deletion | No GDPR-style data lifecycle endpoints | Doesn't exist | `GET /api/account/export`, `DELETE /api/account`, cascading through every user-scoped table | Med, becomes higher once Finance holds real financial data | Low-Med | none | Low |
| P2 | `coach.py` → `engines/coach.py` refactor | Only untestable part of the business-logic layer | Prompt assembly + DB fetch + error handling in one router function | Extract prompt assembly into a pure engine, matching every other engine's shape | Med — pays off directly when Phase 6 extends the assistant | Low-Med | none | Low |
| P2 | Debugging-question gap | 11 of 722 questions are debugging-format (1.5%) | Bank is 58% definition-style | Author debugging-format questions across P1-P5 | Med — a real interview skill gap in the bank | Low (content) | none | Low |
| P2 | Formalize LLM-judge duplicate/classification review | Currently a manual, one-off agent process | `find_duplicate_questions.py` + `curriculum_overrides.py` already do the mechanics | Wrap into a repeatable script emitting the reason-coded report format, human-approval gate preserved | Med | Low | none | Low |
| P2 | Automated per-topic gap-detection report | Demonstrated by hand for 2 topics in `LEARNING_SYSTEM_AUDIT.md` | `validate_curriculum.py` reports phase-level completeness only | Extend it to emit the topic-level "current vs. recommended vs. missing sub-aspects" report for every gated topic | Med | Low-Med | none | Low |
| P2 | Engine duplication consolidation | Two readiness-% computations, two "not enough data" thresholds, two content rankers | Documented in `ARCHITECTURE_AUDIT.md` §3 | Consolidate into single owners | Low-Med, code-health only | Low | none | Low |
| P2 | Narrow goal↔finance linkage | Goals can't represent a money target today | `Goal.progress_pct` is manual-only by design | Add `finance_goal_id` FK option on `Goal`, or reuse `finance_goals` with shared UI | Med | Low | Finance module shipped | Low |
| P3 | Unified event/activity model | Speculative cross-domain analytics infrastructure | N/A | Defer until a real consumer exists (Phase 6 candidate) | Unproven today | High if built now | — | Building it now = premature complexity |
| P3 | Global search | Cross-domain search | N/A | Defer until Finance adds real searchable volume | Low today | Med | Finance shipped | Low if deferred |
| P3 | Generic `Table`/`Dialog` UI primitives | Each page hand-rolls its own | 0 generic primitives today | Extract when the *third* consumer needs one (Finance will likely be the second) | Low today | Low | — | None if deferred |
| P3 | Career module (applications/portfolio) | No career-tracking surface exists | N/A | No demand signal from this audit beyond the original prompt listing it — defer until Finance's income-by-category view proves insufficient | Unproven | Med | — | Low if deferred |
| P3 | Habit-tracking subsystem | No habit model exists | N/A | Defer — no existing surface to extend, and the "goals" ask doesn't require it | Unproven | Med-High | — | Low if deferred |

## Bottom line

Optimize for usefulness × simplicity × integration × reliability, exactly as instructed: fix the three P0 foundation items first (they're small and they're what makes everything after them trustworthy), ship Finance as its own bounded phase, then only afterward build the connective tissue (unified dashboard, goal linkage) and the AI assistant that depends on all of it being real. Do not build the unified event model or global search speculatively — both are real ideas without a real consumer yet, and adding them now is exactly the kind of feature-for-its-own-sake this audit was charged to reject.
