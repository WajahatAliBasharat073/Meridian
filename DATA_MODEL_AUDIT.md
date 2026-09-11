# Data Model Audit

Scope: every table in the schema except the curriculum/question-bank subsystem
(`questions`, `question_progress`, `curriculum_topics`, `learner_frontier`,
`interview_modules`), which is already fully documented in
`CURRICULUM_ARCHITECTURE.md` and is not re-litigated here.

## 1. Full table inventory

**Core**
- `users` — `id` uuid PK, `email`, `settings` JSONB (`{}` default), `created_at`.
- `prayer_times` — reference table, no `user_id` (global solar-time data, keyed by `date`).

**Schedule / execution**
- `time_blocks` — the day's plan: `date`, `seq`, `start_spec`/`end_spec` (raw specs — `"17:05"` or `"maghrib+15m"`), `start_resolved`/`end_resolved`, `activity`, `tier`, `category`, `planned_minutes`/`actual_minutes`, `status`, `deep_work`, `notes`. Unique `(user_id, date, seq)`.
- `focus_sessions` / `focus_session_events` — timer state machine and its pause/resume/complete event trail.
- `daily_reflections` — one row per day, `mood` + free-text.

**Goals & time allocation**
- `goals` — `title`, `description`, `category` (free-text, loosely matched against `time_blocks.category`), `target_date`, `progress_pct` (0–100, **manually entered, never computed** — `app/models/goals.py:1-6` states this is deliberate), `status`. Flat, single-row, no milestones table, nothing references it as a foreign key.
- `time_budgets` — `category`, `minutes_per_week`. Unique `(user_id, category)`. A real "planned allocation vs. computed actual" concept, but scoped entirely to **minutes**, not money.

**Life logs**
- `thesis_log`, `vocab_words`, `recovery_log`, `nutrition_log`, `meals` (reference)/`meal_plan`, `reading_books`/`reading_sessions`, `time_leaks`, `patterns` (reference), `operating_rules` (reference), `settings` (per-user key/value, distinct from `users.settings`).

**DSA / interview practice**
- `problems` (reference), `curriculum` (the DSA daily schedule — no `user_id`, shared), `problem_attempts`, `current_mastery` (view, `security_invoker=true`), `topic_verification_attempts`, `topic_learning_entries`, `topic_guides` (reference).

**Concepts**
- `concepts` (reference), `concept_attempts`.

**Spaced review / mistakes / mocks**
- `reviews` — polymorphic (`subject_type` ∈ problem/vocab/ml_concept/mistake, `subject_id` int, **no FK constraint enforced** on `subject_id` — integrity depends entirely on the check constraint on `subject_type`).
- `mistakes`, `mocks`.

**No money/finance vocabulary exists anywhere.** A repo-wide search for `amount|budget|currency|expense|cost|price|salary|payment|invoice|transaction` returns only `time_budgets`/`TimeBudget`, which is exclusively minutes-per-week. There is no `currency`, `amount`, or `balance` column in the entire schema.

## 2. User isolation pattern

Consistent across every in-scope table: a `user_id` FK to `users.id`, plus RLS policies (`SELECT/INSERT/UPDATE/DELETE ... USING/WITH CHECK (user_id = auth.uid())`) templated identically for all 15 user-scoped tables in `0002_enable_rls.py`. Reference tables (no owner) get a single permissive read policy. The `current_mastery` view is explicitly `security_invoker=true` to stop it running with elevated privilege and silently bypassing RLS — a real gap the original author clearly anticipated and closed.

**Caveat, stated in the migration's own docstring**: the FastAPI backend connects as the base `postgres` role and bypasses RLS entirely. RLS here is defense-in-depth for any *other* client, not the API's actual enforcement mechanism — real isolation today is 100% the repository layer threading `user_id` from the JWT into every query (confirmed correct everywhere by the security audit — see `SECURITY_AUDIT.md`).

**One real gap found**: `curriculum_topics` (added in `0019_curriculum_graph.py`) is a reference table that never gets RLS enabled at all — inconsistent with every other reference table, which do get an explicit read-only policy. Low severity (it's non-sensitive reference data and the API bypasses RLS anyway) but worth a one-line migration to close for consistency.

## 3. The existing Goal model — can Finance plug into it?

No, not cleanly. `Goal` supports `target_date` + a manually-dragged `progress_pct` slider — there is no `target_amount`, `current_amount`, or `currency`, and the module's own docstring explicitly forbids auto-computed progress (progress is "never computed," by design, for the activity-tracking use case it was built for). A savings goal's natural progress (`current_amount / target_amount`, computed from real transactions) directly conflicts with that design decision.

Recommendation: don't retrofit `Goal`. Add a `finance_goals` table (or extend `goals` with nullable `target_amount`/`current_amount`/`currency` columns used only when `category = 'finance'`) — see `FINANCE_MODULE_PROPOSAL.md` §2 for the concrete shape. Reuse the goals **UI** (card, progress bar, badge) even where the backend model differs.

## 4. Naming inconsistencies / schema smells

- **`created_at` handled three different ways**: `TimestampMixin` (tz-aware, DB `server_default=now()`) on `User`/`Goal`/`Review`; a plain `Mapped[datetime]` with no default at all (app must set it, tz-naive) on `ReadingBook`/`ReadingSession`/`TopicLearningEntry`; and no `created_at` column at all on most other tables (`time_budgets`, `daily_reflections`, `mistakes`, `mocks`, `focus_sessions`, `observations`, `concept_attempts`, `time_leaks`).
- **Date column naming drifts**: most daily logs use `date`, but `Mistake.occurred_on` and `VocabWord.date_introduced` break the pattern.
- **`TimeBudget` already owns the word "budget."** A Finance "Budget" concept must be named to avoid collision (`finance_budgets`, not `budgets`).
- **No soft-delete anywhere** — consistently hard-delete throughout. Not a smell, just worth knowing before Finance data (where "undo a deleted transaction" is a real user want) is added — plan for it deliberately rather than retrofitting later.
- **`reviews.subject_id`** is an unenforced polymorphic FK. If a future "review a stale budget category" feature ever wanted to hook into this table, the integrity gap becomes relevant; today it's a pre-existing, contained risk.

## 5. Verdict

The schema is trustworthy on the dimension that matters most for adding financial data — `user_id` + RLS scoping is applied with zero exceptions found, and hard-delete-only is consistent. It is not uniform on cosmetic conventions (`created_at`, date-column naming). Finance should be **new tables**, not a retrofit of `Goal`/`TimeBudget`, should follow the `TimestampMixin` + RLS + reference/attempt-log-split pattern exactly (the pattern used by `problems`/`problem_attempts` and `reading_books`/`reading_sessions` is the right template — a reference/definition table plus a per-user activity table), and must pick names that don't collide with `time_budgets`.
