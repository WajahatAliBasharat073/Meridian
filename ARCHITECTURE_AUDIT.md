# Architecture Audit

## 1. Backend layering

The pattern is consistent and, since the curriculum rework, explicit: `router → repository (DB I/O, user_id scoping) → engine (pure function, no I/O)`. `services.py` orchestrates the ones that combine multiple engines/repos for a single endpoint (e.g. `get_daily_theory_questions`). This is a genuinely good architecture for a solo-maintained app — engines are unit-testable without a database, in-memory, deterministic (seeded RNG keyed on `date.toordinal()` throughout), and every engine that would otherwise have to guess refuses instead (`recovery_score=None`, `enough_data=False`, `readiness_pct=None`) rather than fabricating a number from insufficient data. This discipline is documented in nearly every engine's own docstring.

## 2. Engine-by-engine (16 engines, all confirmed wired — none dead)

| Engine | Problem it solves | Notes |
|---|---|---|
| `bandwidth` | How much can today's plan hold given stated minutes/energy | pure |
| `block_lock` | Prevents dishonest time-block claims (can't start a block 70% through its window; can't complete with >5min left) | pure predicates |
| `daily_recap` | End-of-day deterministic summary, no LLM | pure |
| `daily_theory` | Ranks the 722-question interview bank for the day (tier, module priority, frequency, seeded shuffle, diversity caps) | now superseded for the curriculum-graph path by `engines/curriculum.py`, kept as legacy fallback in `services.py` |
| `prayer` | Solar-position prayer times, computed locally (never fetched externally) | pure math |
| `punctuality` | On-time-start %, refuses to report under 5 sessions | pure |
| `recommender` | Next-LeetCode-problem picker (failed→overdue→due→scheduled→pattern-gap ladder) | pure, seeded |
| `recovery` | Weighted recovery score from vitals, `None` if sleep missing | pure |
| `repetition` | Core spaced-repetition state machine, shared polymorphically across problem/vocab/ml_concept/mistake | pure |
| `scheduling` | Resolves absolute or prayer-relative time specs (`"asr+15m"`) into concrete times | pure, depends on `prayer` |
| `session_breakdown` | Turns a session's pause/resume trail into per-activity paused time | pure |
| `summary` | Cross-problem dashboard aggregate (mastery distribution, readiness %) | pure |
| `theory_pace` | Projects days-to-clear-backlog at a given daily count, refuses under 5 timed questions | pure |
| `topic_gate` | Build→defend verification-gate policy (coverage thresholds, 30-day TTL) | pure, LLM does judging elsewhere |
| `weekly_review` | 7-day rollup, same discipline as `daily_recap` | pure |
| `curriculum` / `placement` | The rebuilt knowledge-model engine (topics/phases/eligibility/ranking) and the placement estimator | pure, newest, most heavily tested |

## 3. Duplication found (real, not hypothetical)

- **Two independent readiness-% computations**: `engines/summary.py` (`l5_plus_total / total_problems`) and `routers/today.py`'s counters recompute the same DSA-curriculum readiness figure separately rather than one calling the other.
- **Two independent "not enough data" thresholds**: `punctuality.py` and `theory_pace.py` both hardcode their own `MIN_*_FOR_INSIGHT = 5` and near-identical refusal shape, defined twice instead of once.
- **Two independently-evolved recommendation rankers**: `recommender.py` (LeetCode) and `daily_theory.py` (theory questions) reimplement the same shape — tiered priority, per-day seeded shuffle, diversity cap — for two different content types, and neither shares code with the new `curriculum.py` ranking engine, which does the same job a third way (weighted score + reason codes) for the same theory-question domain `daily_theory.py` already covers.
- **`daily_recap.py` and `weekly_review.py`** duplicate category-breakdown / completion-% / reflection-text logic at different time windows with no shared "period rollup" helper.

None of this is broken — it's accumulated organic duplication, worth consolidating opportunistically (Phase 2), not urgent enough to block Finance.

## 4. `coach.py` — the one weak link in an otherwise disciplined layer

`coach.py` is the only file in the business-logic surface that mixes DB fetches, prompt construction, LLM-call error handling, and a hardcoded fallback-text generator in one router function — not unit-testable the way every engine is. It already grounds itself in real schedule/prayer/recommendation/rule data with an explicit anti-hallucination system prompt, but it does not yet see goals, time budgets, vitals, or dashboard data, and its `except Exception:` swallows LLM failures with no logging at all (see `SECURITY_AUDIT.md` §5-6). This is the natural extraction point before Phase 6 (AI Assistant) extends what the assistant can see — recommend pulling prompt-assembly into `engines/coach.py` first, matching the rest of the layer's pattern.

## 5. Frontend architecture

Also consistent: a flat `lib/api.ts` (one `request<T>()` wrapper handling `ApiError`, always `cache: "no-store"`) backing a flat `lib/types.ts` (`*Out`/`*CreateInput`/`*UpdateInput` triples per domain, mirroring backend Pydantic schemas 1:1), consumed through React Query hooks in `hooks/`. Navigation is fully data-driven (`lib/nav.ts`'s `NAV_GROUPS`), so adding a new top-level section is a config change, not a structural one. Design tokens are centralized in `globals.css` (dark-only, CSS custom properties, `--status-done`/`--danger`/`--warning` semantic aliases already exist and are reused everywhere rather than raw color literals). `recharts` is the only charting library, wrapped by a shared `ChartCard` that enforces "every chart states a written takeaway, never just a shrug."

Gap: no generic `Table`, `Dialog`/`Modal`, or `Tabs` primitive exists — each page that needs one hand-rolls it (dashboard's tabs are inline buttons; `problems/page.tsx` has its own one-off dialog). Not urgent, but the third page that needs a data table or modal should trigger extracting a shared primitive rather than a fourth hand-rolled copy.

## 6. Keep / Refactor / Remove / Merge / Add / Defer

**Keep** — the router→repository→engine layering; the pure-function/no-fabricated-confidence engine discipline; the RLS+`user_id` isolation pattern; the flat `api.ts`/`types.ts`/`nav.ts` frontend conventions; the `Skeleton`/`QueryError`/`EmptyState` UI triad; `recharts` + `ChartCard`; the curriculum engine's reason-code explainability model (`ReasonCode` on every selection/rejection) — this is the right pattern to extend to Finance decisions later (e.g. "why is this flagged over budget").

**Refactor** — extract `coach.py`'s prompt assembly into `engines/coach.py`; consolidate the two "not enough data" thresholds into one shared constant/helper; consider whether `daily_theory.py`'s legacy ranking can be fully retired now that `curriculum.py` covers the same ground (currently kept as a fallback for un-seeded data — reasonable short-term, revisit once the curriculum graph has been live long enough to trust as the sole path).

**Remove** — nothing identified as genuinely dead code; everything audited is wired to a live route.

**Merge** — `summary.py`'s readiness % and `today.py`'s duplicate readiness computation should have one owner; `recommender.py` and `daily_theory.py`'s shared ranking shape (tiered priority + seeded shuffle + diversity cap) is a candidate for a shared low-level utility even though the domains differ.

**Add** — structured logging (currently absent everywhere — see `SECURITY_AUDIT.md`); a cross-user isolation integration test; a generic `Table`/`Dialog` UI primitive once Finance needs one; a `finance_*` schema following the reference+RLS+`TimestampMixin` pattern.

**Defer** — retiring `daily_theory.py` outright; a shared `Table`/`Dialog` component before there's a second real consumer beyond Finance; unifying `recommender`/`daily_theory`/`curriculum` ranking into one engine (real value, but risky to do at the same time as adding a new domain — do it as its own focused pass).
