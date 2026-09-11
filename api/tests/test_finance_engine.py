from datetime import date

from app.engines.finance import (
    BudgetFixture,
    BudgetStatus,
    CategoryOutlier,
    GoalFixture,
    GoalStatus,
    RecurringFixture,
    TransactionFixture,
    budget_utilization,
    build_insights,
    category_breakdown,
    goal_progress,
    income_change_pct,
    month_summary,
    shift_months,
    spending_outliers,
    upcoming_commitments,
)


def _tx(
    category: str, type_: str, amount: float, on: date, status: str = "actual"
) -> TransactionFixture:
    return TransactionFixture(
        category_id=1, category_name=category, type=type_, amount=amount, status=status, occurred_on=on
    )


def test_month_summary_computes_income_expenses_savings_and_rate() -> None:
    txs = [
        _tx("Salary", "income", 5000, date(2026, 9, 1)),
        _tx("Rent", "expense", 2000, date(2026, 9, 5)),
        _tx("Food", "expense", 500, date(2026, 9, 10)),
    ]
    s = month_summary(txs, date(2026, 9, 15))

    assert s.income == 5000
    assert s.expenses == 2500
    assert s.savings == 2500
    assert s.savings_rate_pct == 50.0


def test_month_summary_ignores_other_months_and_planned_transactions() -> None:
    txs = [
        _tx("Salary", "income", 5000, date(2026, 8, 1)),  # wrong month
        _tx("Rent", "expense", 2000, date(2026, 9, 5), status="planned"),  # not actual yet
    ]
    s = month_summary(txs, date(2026, 9, 15))

    assert s.income == 0
    assert s.expenses == 0


def test_month_summary_reports_no_rate_when_there_is_no_income() -> None:
    s = month_summary([_tx("Food", "expense", 100, date(2026, 9, 1))], date(2026, 9, 15))
    assert s.savings_rate_pct is None


def test_income_change_pct_is_none_when_last_month_had_no_income() -> None:
    this_month = month_summary([_tx("Salary", "income", 1000, date(2026, 9, 1))], date(2026, 9, 1))
    last_month = month_summary([], date(2026, 8, 1))
    assert income_change_pct(this_month, last_month) is None


def test_income_change_pct_computes_a_real_percentage() -> None:
    this_month = month_summary([_tx("Salary", "income", 5600, date(2026, 9, 1))], date(2026, 9, 1))
    last_month = month_summary([_tx("Salary", "income", 5000, date(2026, 8, 1))], date(2026, 8, 1))
    assert income_change_pct(this_month, last_month) == 12.0


def test_category_breakdown_sums_and_sorts_descending() -> None:
    txs = [
        _tx("Food", "expense", 100, date(2026, 9, 1)),
        _tx("Food", "expense", 50, date(2026, 9, 2)),
        _tx("Rent", "expense", 2000, date(2026, 9, 1)),
        _tx("Salary", "income", 5000, date(2026, 9, 1)),  # income excluded
    ]
    breakdown = category_breakdown(txs, date(2026, 9, 15))

    assert [c.category_name for c in breakdown] == ["Rent", "Food"]
    assert breakdown[1].amount == 150


def test_spending_outliers_refuses_below_minimum_history() -> None:
    # Only one prior month on record -- not enough to call an "average".
    txs = [
        _tx("Food", "expense", 100, date(2026, 8, 1)),
        _tx("Food", "expense", 500, date(2026, 9, 1)),
    ]
    assert spending_outliers(txs, date(2026, 9, 15)) == []


def test_spending_outliers_flags_a_real_swing_with_enough_history() -> None:
    txs = [
        _tx("Food", "expense", 100, date(2026, 7, 1)),
        _tx("Food", "expense", 100, date(2026, 8, 1)),
        _tx("Food", "expense", 180, date(2026, 9, 1)),  # 80% above trailing avg of 100
    ]
    outliers = spending_outliers(txs, date(2026, 9, 15))

    assert len(outliers) == 1
    assert outliers[0].category_name == "Food"
    assert outliers[0].pct_diff == 80.0


def test_spending_outliers_ignores_small_swings() -> None:
    txs = [
        _tx("Food", "expense", 100, date(2026, 7, 1)),
        _tx("Food", "expense", 100, date(2026, 8, 1)),
        _tx("Food", "expense", 105, date(2026, 9, 1)),  # only 5% -- noise
    ]
    assert spending_outliers(txs, date(2026, 9, 15)) == []


def test_budget_utilization_flags_over_budget_and_computes_remaining() -> None:
    budgets = [
        BudgetFixture(id=1, category_id=1, category_name="Food", monthly_amount=400, actual_this_month=500),
        BudgetFixture(id=2, category_id=2, category_name="Gym", monthly_amount=100, actual_this_month=60),
    ]
    statuses = budget_utilization(budgets)

    food = next(s for s in statuses if s.category_name == "Food")
    gym = next(s for s in statuses if s.category_name == "Gym")
    assert food.over_budget is True
    assert food.remaining == -100
    assert food.utilization_pct == 125.0
    assert gym.over_budget is False
    assert gym.remaining == 40


def test_goal_progress_computes_remaining_and_required_monthly_contribution() -> None:
    goal = GoalFixture(
        id=1,
        title="Emergency fund",
        target_amount=6000,
        current_amount=1500,
        target_date=date(2026, 12, 1),
        category="emergency_fund",
    )
    status = goal_progress([goal], date(2026, 9, 1))[0]

    assert status.remaining == 4500
    assert status.progress_pct == 25.0
    assert status.required_monthly_contribution == 1500.0  # 4500 / 3 months


def test_goal_progress_has_no_required_contribution_without_a_target_date() -> None:
    goal = GoalFixture(
        id=1, title="Laptop", target_amount=1000, current_amount=200, target_date=None, category="custom"
    )
    status = goal_progress([goal], date(2026, 9, 1))[0]
    assert status.required_monthly_contribution is None


def test_goal_progress_remaining_never_goes_negative_once_met() -> None:
    goal = GoalFixture(
        id=1, title="Laptop", target_amount=1000, current_amount=1200, target_date=None, category="custom"
    )
    status = goal_progress([goal], date(2026, 9, 1))[0]
    assert status.remaining == 0.0


def _recurring(days_from_today: int, today: date) -> RecurringFixture:
    from datetime import timedelta

    return RecurringFixture(
        id=1,
        description="Rent",
        amount=2000,
        type="expense",
        next_due_date=today + timedelta(days=days_from_today),
        category_name="Rent",
    )


def test_upcoming_commitments_filters_by_window_and_sorts_by_due_date() -> None:
    today = date(2026, 9, 1)
    items = [_recurring(45, today), _recurring(5, today), _recurring(20, today)]

    upcoming = upcoming_commitments(items, today, within_days=30)

    assert [ (r.next_due_date - today).days for r in upcoming ] == [5, 20]


def test_upcoming_commitments_excludes_already_overdue_items() -> None:
    today = date(2026, 9, 15)
    overdue = _recurring(-3, today)
    assert upcoming_commitments([overdue], today) == []


def test_build_insights_says_nothing_when_there_is_nothing_to_say() -> None:
    assert build_insights(income_change=None, outliers=[], budgets=[], goals=[], upcoming=[]) == []


def test_build_insights_states_income_change_direction_and_size() -> None:
    lines = build_insights(income_change=12.0, outliers=[], budgets=[], goals=[], upcoming=[])
    assert lines == ["Income increased 12% this month."]

    lines = build_insights(income_change=-8.0, outliers=[], budgets=[], goals=[], upcoming=[])
    assert lines == ["Income decreased 8% this month."]


def test_build_insights_omits_a_negligible_income_change() -> None:
    lines = build_insights(income_change=0.4, outliers=[], budgets=[], goals=[], upcoming=[])
    assert lines == []


def test_build_insights_names_the_outlier_category_and_direction() -> None:
    outlier = CategoryOutlier(category_name="Food", this_month=180, trailing_avg=100, pct_diff=80.0)
    lines = build_insights(income_change=None, outliers=[outlier], budgets=[], goals=[], upcoming=[])
    assert lines == ["Food spending is 80% above your trailing average."]


def test_build_insights_flags_over_budget_categories() -> None:
    over = BudgetStatus(
        id=1, category_name="Food", planned=400, actual=500, remaining=-100, utilization_pct=125.0, over_budget=True
    )
    under = BudgetStatus(
        id=2, category_name="Gym", planned=100, actual=60, remaining=40, utilization_pct=60.0, over_budget=False
    )
    lines = build_insights(income_change=None, outliers=[], budgets=[over, under], goals=[], upcoming=[])
    assert lines == ["You are $100 over budget on Food this month."]


def test_build_insights_states_required_monthly_saving_for_a_goal() -> None:
    goal = GoalStatus(
        id=1,
        title="Emergency fund",
        target_amount=6000,
        current_amount=1500,
        remaining=4500,
        progress_pct=25.0,
        required_monthly_contribution=1500.0,
    )
    lines = build_insights(income_change=None, outliers=[], budgets=[], goals=[goal], upcoming=[])
    assert lines == ['Save $1,500/month to reach "Emergency fund" on time.']


def test_build_insights_totals_upcoming_commitments() -> None:
    today = date(2026, 9, 1)
    lines = build_insights(
        income_change=None, outliers=[], budgets=[], goals=[], upcoming=[_recurring(5, today), _recurring(10, today)]
    )
    assert lines == ["You have $4,000 in recurring commitments due in the next 30 days."]


def test_shift_months_moves_back_within_the_same_year() -> None:
    assert shift_months(date(2026, 9, 15), -1) == date(2026, 8, 1)


def test_shift_months_crosses_a_year_boundary() -> None:
    assert shift_months(date(2026, 1, 10), -1) == date(2025, 12, 1)
    assert shift_months(date(2026, 1, 10), -4) == date(2025, 9, 1)


def test_shift_months_forward() -> None:
    assert shift_months(date(2026, 11, 1), 2) == date(2027, 1, 1)
