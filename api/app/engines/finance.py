"""Pure functions: the finance dashboard's actual decisions, not just its
charts. Same discipline as every other engine here — every figure is
computed from real rows passed in, and a comparison that doesn't have
enough history to mean anything is omitted rather than shown as a
confident-sounding percentage (FINANCE_MODULE_PROPOSAL.md §3).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

# A category's spend must differ from its trailing average by at least
# this fraction before it's worth interrupting the user about — smaller
# swings are noise, not a decision point.
OUTLIER_THRESHOLD_PCT = 20.0
# Need at least this many prior months of data before "your average" means
# anything — one prior month is one data point, not an average.
MIN_MONTHS_FOR_TREND = 2


@dataclass(frozen=True)
class TransactionFixture:
    category_id: int
    category_name: str
    type: str  # "income" | "expense"
    amount: float
    status: str  # "actual" | "planned"
    occurred_on: date


@dataclass(frozen=True)
class BudgetFixture:
    id: int
    category_id: int
    category_name: str
    monthly_amount: float
    actual_this_month: float


@dataclass(frozen=True)
class GoalFixture:
    id: int
    title: str
    target_amount: float
    current_amount: float
    target_date: date | None
    category: str


@dataclass(frozen=True)
class RecurringFixture:
    id: int
    description: str
    amount: float
    type: str
    next_due_date: date
    category_name: str


@dataclass(frozen=True)
class NetWorthPoint:
    snapshot_date: date
    total_assets: float
    total_liabilities: float
    net_worth: float


@dataclass(frozen=True)
class MonthSummary:
    income: float
    expenses: float
    savings: float
    savings_rate_pct: float | None  # None when income is 0 -- no rate to report


@dataclass(frozen=True)
class CategorySpend:
    category_name: str
    amount: float


@dataclass(frozen=True)
class CategoryOutlier:
    category_name: str
    this_month: float
    trailing_avg: float
    pct_diff: float  # positive = above average, negative = below


@dataclass(frozen=True)
class BudgetStatus:
    id: int
    category_name: str
    planned: float
    actual: float
    remaining: float
    utilization_pct: float
    over_budget: bool


@dataclass(frozen=True)
class GoalStatus:
    id: int
    title: str
    target_amount: float
    current_amount: float
    remaining: float
    progress_pct: float
    # None when there's no target_date (or it's already past) -- a
    # required monthly figure needs a real deadline to divide by.
    required_monthly_contribution: float | None


def _month_key(d: date) -> tuple[int, int]:
    return (d.year, d.month)


def _months_between(earlier: tuple[int, int], later: tuple[int, int]) -> int:
    return (later[0] - earlier[0]) * 12 + (later[1] - earlier[1])


def shift_months(d: date, months: int) -> date:
    """First-of-month, shifted by `months` (negative to go back). Plain
    arithmetic rather than a new dependency for something this small."""
    total = d.year * 12 + (d.month - 1) + months
    return date(total // 12, total % 12 + 1, 1)


def month_summary(transactions: list[TransactionFixture], month: date) -> MonthSummary:
    key = _month_key(month)
    actual = [t for t in transactions if t.status == "actual" and _month_key(t.occurred_on) == key]
    income = sum(t.amount for t in actual if t.type == "income")
    expenses = sum(t.amount for t in actual if t.type == "expense")
    savings = income - expenses
    savings_rate = round(100 * savings / income, 1) if income else None
    return MonthSummary(income=income, expenses=expenses, savings=savings, savings_rate_pct=savings_rate)


def income_change_pct(this_month: MonthSummary, last_month: MonthSummary) -> float | None:
    """None when last month had no income at all -- a "% change" from
    zero is undefined, not a very large number."""
    if not last_month.income:
        return None
    return round(100 * (this_month.income - last_month.income) / last_month.income, 1)


def category_breakdown(transactions: list[TransactionFixture], month: date) -> list[CategorySpend]:
    key = _month_key(month)
    totals: dict[str, float] = {}
    for t in transactions:
        if t.status == "actual" and t.type == "expense" and _month_key(t.occurred_on) == key:
            totals[t.category_name] = totals.get(t.category_name, 0.0) + t.amount
    return sorted(
        (CategorySpend(category_name=name, amount=amt) for name, amt in totals.items()),
        key=lambda c: -c.amount,
    )


def spending_outliers(transactions: list[TransactionFixture], month: date) -> list[CategoryOutlier]:
    """Categories where this month's actual spend is >= OUTLIER_THRESHOLD_PCT
    away from the trailing average of prior months with any data — refuses
    to flag a category with fewer than MIN_MONTHS_FOR_TREND prior months
    on record, per the same "not enough data" discipline as
    engines/policy.py."""
    this_key = _month_key(month)
    by_category_by_month: dict[str, dict[tuple[int, int], float]] = {}
    for t in transactions:
        if t.status != "actual" or t.type != "expense":
            continue
        k = _month_key(t.occurred_on)
        by_category_by_month.setdefault(t.category_name, {}).setdefault(k, 0.0)
        by_category_by_month[t.category_name][k] += t.amount

    outliers: list[CategoryOutlier] = []
    for category, months in by_category_by_month.items():
        this_month_amount = months.get(this_key, 0.0)
        prior_months = [amt for k, amt in months.items() if k != this_key]
        if len(prior_months) < MIN_MONTHS_FOR_TREND or this_month_amount == 0:
            continue
        trailing_avg = sum(prior_months) / len(prior_months)
        if trailing_avg == 0:
            continue
        pct_diff = round(100 * (this_month_amount - trailing_avg) / trailing_avg, 1)
        if abs(pct_diff) >= OUTLIER_THRESHOLD_PCT:
            outliers.append(
                CategoryOutlier(
                    category_name=category,
                    this_month=this_month_amount,
                    trailing_avg=round(trailing_avg, 2),
                    pct_diff=pct_diff,
                )
            )
    return sorted(outliers, key=lambda o: -abs(o.pct_diff))


def budget_utilization(budgets: list[BudgetFixture]) -> list[BudgetStatus]:
    return [
        BudgetStatus(
            id=b.id,
            category_name=b.category_name,
            planned=b.monthly_amount,
            actual=b.actual_this_month,
            remaining=b.monthly_amount - b.actual_this_month,
            utilization_pct=round(100 * b.actual_this_month / b.monthly_amount, 1)
            if b.monthly_amount
            else 0.0,
            over_budget=b.actual_this_month > b.monthly_amount,
        )
        for b in budgets
    ]


def goal_progress(goals: list[GoalFixture], today: date) -> list[GoalStatus]:
    statuses = []
    for g in goals:
        remaining = max(g.target_amount - g.current_amount, 0.0)
        pct = round(100 * g.current_amount / g.target_amount, 1) if g.target_amount else 0.0

        required_monthly = None
        if g.target_date and remaining > 0:
            months_left = _months_between(_month_key(today), _month_key(g.target_date))
            if months_left > 0:
                required_monthly = round(remaining / months_left, 2)

        statuses.append(
            GoalStatus(
                id=g.id,
                title=g.title,
                target_amount=g.target_amount,
                current_amount=g.current_amount,
                remaining=remaining,
                progress_pct=pct,
                required_monthly_contribution=required_monthly,
            )
        )
    return statuses


def upcoming_commitments(
    recurring: list[RecurringFixture], today: date, within_days: int = 30
) -> list[RecurringFixture]:
    due_soon = [r for r in recurring if 0 <= (r.next_due_date - today).days <= within_days]
    return sorted(due_soon, key=lambda r: r.next_due_date)


def net_worth_trend(snapshots: list[NetWorthPoint]) -> list[NetWorthPoint]:
    return sorted(snapshots, key=lambda s: s.snapshot_date)


def build_insights(
    *,
    income_change: float | None,
    outliers: list[CategoryOutlier],
    budgets: list[BudgetStatus],
    goals: list[GoalStatus],
    upcoming: list[RecurringFixture],
) -> list[str]:
    """The dashboard's actual decisions, in one sentence each
    (FINANCE_MODULE_PROPOSAL.md §3: "prioritize decisions, not just
    charts"). Every sentence names a real number computed above; nothing
    here is a template filled in when there's nothing to say -- an empty
    input to a section produces no sentence for it, not a filler line."""
    lines: list[str] = []

    if income_change is not None and abs(income_change) >= 1:
        direction = "increased" if income_change > 0 else "decreased"
        lines.append(f"Income {direction} {abs(income_change):.0f}% this month.")

    for o in outliers[:2]:
        direction = "above" if o.pct_diff > 0 else "below"
        lines.append(
            f"{o.category_name} spending is {abs(o.pct_diff):.0f}% {direction} your trailing average."
        )

    over = [b for b in budgets if b.over_budget]
    for b in over[:2]:
        lines.append(f"You are ${b.actual - b.planned:,.0f} over budget on {b.category_name} this month.")

    for g in goals:
        if g.required_monthly_contribution:
            lines.append(
                f"Save ${g.required_monthly_contribution:,.0f}/month to reach \"{g.title}\" on time."
            )

    if upcoming:
        total = sum(r.amount for r in upcoming)
        lines.append(f"You have ${total:,.0f} in recurring commitments due in the next 30 days.")

    return lines
