# Finance Module Proposal

Manual-first, privacy-first, single-user personal finance command center. No banking integrations, no double-entry accounting, no tax module, no crypto/trading, no payment processing — those are explicitly deferred (see §6). Every schema decision below follows the pattern this audit found already working in the rest of the app: a reference/definition table plus a per-user activity-log table, `user_id` + RLS on everything, `TimestampMixin`, hard-delete-only, and — the app's own repeatedly-stated ethos, seen in `research/page.tsx`'s comment about not inventing numbers when data is empty — **compute derived numbers from real rows, never store a number a user could type that drifts from reality.**

## 1. Schema

```
finance_accounts
  id, user_id, name, account_type (cash|bank|savings|investment|
    receivable|credit|loan|other), currency, opening_balance,
    current_balance (maintained by transaction triggers/repo logic,
    not user-edited directly), is_liability (bool, derived from
    account_type but stored for a simple net-worth query), is_active,
    created_at

finance_categories
  id, user_id (NULL for system-seeded defaults, set for a user's own
    custom category), parent_id (self-FK, for subcategories), name,
    kind (income|expense), is_system, created_at
  Seeded system defaults, hierarchical:
    Income: Salary, Freelance, Contract, Research Income, Bonus, One-time, Other
    Expense: Rent, Utilities, Food, Transportation, Subscriptions,
      Gym, Software, Entertainment, Shopping, Family/Personal, Misc,
      Education (-> Courses, Books, Conferences, Certifications),
      Research (-> Papers, Conferences, Compute/GPU, APIs, Software, Books)
  This hierarchy is what makes "$X on professional development this
  year" or "$X on research this year" a plain GROUP BY under
  Education/Research, not a new feature.

finance_transactions
  id, user_id, account_id (FK), category_id (FK), type (income|expense),
  amount (numeric, always positive; sign comes from `type`), currency,
  occurred_on (date), status (actual|planned — planned rows are
  "expected income" or a bill not yet paid, and are excluded from
  actual totals but included in projections), description, notes,
  is_recurring (bool), recurring_id (FK, nullable, -> finance_recurring
  if this row was generated from/linked to a template),
  goal_id (FK, nullable, -> finance_goals — a transaction can be a
  contribution toward a savings goal), created_at

finance_recurring
  id, user_id, description, account_id, category_id, type, amount,
  currency, interval (weekly|monthly|yearly), anchor_day, next_due_date,
  active, created_at
  Powers "upcoming expenses" projections and the Plan/Today integration
  (§3) without ever writing a phantom transaction row until it's real.

finance_budgets
  id, user_id, category_id (FK), monthly_amount, created_at
  Actual spend is computed at read time from finance_transactions
  (type=expense, status=actual, this month, this category) — exactly
  the pattern the existing time_budgets/actual_minutes split already
  uses for minutes. Deliberately NOT named `budgets` to avoid colliding
  with the existing `time_budgets` table (see DATA_MODEL_AUDIT.md §4).

finance_goals
  id, user_id, title, target_amount, currency, target_date, category
  (emergency_fund|short_term|long_term|custom), status, notes, created_at
  `current_amount` is NOT a stored column — it's
  SUM(finance_transactions.amount WHERE goal_id = this goal), so
  progress is always real, never a manually-typed number that can lie.

finance_net_worth_snapshots
  id, user_id, snapshot_date, total_assets, total_liabilities,
  net_worth, created_at
  A point-in-time capture (on-demand button, or nightly if a scheduler
  exists later) of SUM(finance_accounts.current_balance) split by
  is_liability — this is the only place a computed number gets
  persisted rather than recomputed live, and only because historical
  trend requires a time series that live balances alone don't provide.
```

All tables follow the existing RLS template exactly (`user_id = auth.uid()`), `finance_categories`' system rows get the existing reference-table read-only policy.

## 2. Integration with the existing product (not an isolated CRUD module)

- **Goals**: `finance_goals` is new (§1), not a retrofit of `goals` — the existing `Goal.progress_pct` is explicitly manual-only by design (`DATA_MODEL_AUDIT.md` §3) and a money goal's progress must be computed. Reuse the goal **card UI** (progress bar, badge, "update" affordance) for finance goals; don't reuse the **table**.
- **Career**: no career module exists yet (`UX_AUDIT.md` §1). Career income analytics need nothing new beyond consistent categorization — group `finance_transactions` by category (Salary/Freelance/Contract) over time. If a Career module is ever built (deferred, `PRODUCT_AUDIT.md`), it should read from Finance, not duplicate income tracking.
- **Calendar / Planning**: `finance_recurring.next_due_date` surfaces as a read-only "upcoming bills" widget on `today`/`plan` — deliberately **not** auto-injected as `time_blocks` rows (that model is the execution schedule, and mixing "a bill exists" with "a scheduled activity" would be exactly the kind of unnecessary coupling this audit is watching for). A due recurring item can offer a one-click "add to today's schedule" action reusing `today`'s existing "Add block" flow — the user decides, the system doesn't assume.
- **Productivity**: same reasoning — a "pay rent" task from a due recurring item is a suggested schedule addition, not a new parallel task system (none exists today to hang it on).
- **Learning / Research**: come free from the category hierarchy (§1) — no new schema. "You spent $X this year on professional development" is `SUM(amount) WHERE category IN (Education subtree)`.
- **AI Assistant** (Phase 6, deferred): once built, it reads Finance the same way `coach.py` already reads schedule/prayer/recommendation data — real rows only, with the same explicit "do not invent" system-prompt discipline already proven in production.

## 3. Financial Dashboard — decisions, not charts

Following the same discipline `ChartCard` already enforces elsewhere ("every chart states a written takeaway, never a shrug"):

- Current-month income / expenses / savings / savings rate — plain numbers, computed.
- Net worth trend — line chart from `finance_net_worth_snapshots`, `recharts` + `ChartCard`.
- Category spending breakdown — bar chart, current month, with a computed "N% above/below your trailing-3-month average" sentence per category that's meaningfully off (not every category, only outliers — avoids noise).
- Upcoming recurring commitments next 30 days — a plain list from `finance_recurring`, total dollar figure stated up front.
- Budget utilization — one row per `finance_budgets` category: planned vs. actual vs. remaining vs. %, with `--danger` token applied only when actual > planned (reusing the existing semantic-color convention, not inventing a new one).
- Goal progress — one card per active `finance_goals` row: target, current (computed), remaining, and — genuinely useful, not decorative — `required_monthly_contribution = remaining / months_until(target_date)`.

Sentences like "Income increased 12% this month" or "You're on track to reach your emergency-fund target by X" are computed comparisons over real rows (this month vs. last month, current pace vs. required pace) — not templated filler; each only renders when the underlying comparison is actually meaningful (enough history exists), matching the "refuse rather than fabricate" discipline found throughout the engine layer (`ARCHITECTURE_AUDIT.md` §2).

## 4. Currency

Single base currency per user (a `default_currency` setting), stored per-transaction/account for display, **no automatic FX conversion in this phase** — net worth and totals assume single-currency use unless the user genuinely operates in multiple currencies, in which case totals are computed per-currency and shown separately rather than silently mixed. Multi-currency conversion is a Phase-3+-or-later concern, not a blocker for shipping.

## 5. API surface (new routers, matching the existing fine-grained-per-domain convention already used for `goals.py`/`time_budgets.py`/`vitals.py`)

`routers/finance_accounts.py`, `finance_transactions.py`, `finance_budgets.py`, `finance_goals.py`, `finance_dashboard.py` — each following the existing `Depends(get_current_user_id)` pattern with zero exceptions (this is the app's actual security boundary, per `SECURITY_AUDIT.md`), plus structured logging on every mutation (new for this module specifically, ahead of the rest of the app getting it — see `SECURITY_AUDIT.md`).

## 6. Explicitly deferred (do not build now)

Bank/account integrations (Plaid-style scraping), double-entry accounting, tax computation, cryptocurrency portfolio tracking, investment/trading features, payment processing, multi-currency FX conversion, CSV import/export (genuinely useful, Phase 2 of Finance itself once manual entry is proven, not Phase 1).

## 7. Phased rollout within the Finance module

1. **Manual entry**: accounts, transactions, categories, budgets, goals, dashboard — the full schema above, manual-entry only.
2. **CSV import/export** once manual entry has real usage data to validate the category taxonomy against.
3. **Bank integration** — only if manual entry proves the taxonomy/workflow are right and the user still wants it; not assumed.
