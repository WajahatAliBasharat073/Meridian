from __future__ import annotations

import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.engines.finance import (
    budget_utilization,
    build_insights,
    category_breakdown,
    goal_progress,
    income_change_pct,
    month_summary,
    net_worth_trend,
    shift_months,
    spending_outliers,
    upcoming_commitments,
)
from app.logging import get_logger
from app.repositories import finance as finance_repo
from app.schemas import (
    FinanceBudgetOut,
    FinanceDashboardOut,
    FinanceGoalOut,
    FinanceNetWorthPointOut,
    FinanceRecurringOut,
)

log = get_logger(__name__)

router = APIRouter(prefix="/api/finance/dashboard", tags=["finance"])

# Enough trailing history for a 2-3 month spending-outlier comparison
# without pulling a user's entire transaction history on every load.
_OUTLIER_LOOKBACK_MONTHS = 4


@router.get("", response_model=FinanceDashboardOut)
async def get_dashboard(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> FinanceDashboardOut:
    today = date.today()
    this_month = today.replace(day=1)
    last_month = shift_months(this_month, -1)
    since = shift_months(this_month, -_OUTLIER_LOOKBACK_MONTHS)

    transactions = await finance_repo.get_transaction_fixtures(session, user_id, since=since)
    this_month_summary = month_summary(transactions, this_month)
    last_month_summary = month_summary(transactions, last_month)
    change = income_change_pct(this_month_summary, last_month_summary)
    breakdown = category_breakdown(transactions, this_month)
    outliers = spending_outliers(transactions, this_month)

    budget_fixtures = await finance_repo.get_budget_fixtures(session, user_id, today)
    budgets = budget_utilization(budget_fixtures)

    goal_rows = {g.id: g for g in await finance_repo.list_goals(session, user_id)}
    goal_fixtures = await finance_repo.get_goal_fixtures(session, user_id)
    goals = [g for g in goal_progress(goal_fixtures, today) if goal_rows[g.id].status == "active"]

    recurring_fixtures = await finance_repo.get_recurring_fixtures(session, user_id)
    upcoming = upcoming_commitments(recurring_fixtures, today)
    recurring_rows = {r.id: r for r in await finance_repo.list_recurring(session, user_id)}

    net_worth_points = await finance_repo.get_net_worth_points(session, user_id)
    trend = net_worth_trend(net_worth_points)
    latest = trend[-1] if trend else None

    insights = build_insights(
        income_change=change, outliers=outliers, budgets=budgets, goals=goals, upcoming=upcoming
    )

    return FinanceDashboardOut(
        month=this_month,
        income=this_month_summary.income,
        expenses=this_month_summary.expenses,
        savings=this_month_summary.savings,
        savings_rate_pct=this_month_summary.savings_rate_pct,
        income_change_pct=change,
        category_breakdown=[{"category_name": c.category_name, "amount": c.amount} for c in breakdown],
        outliers=[
            {
                "category_name": o.category_name,
                "this_month": o.this_month,
                "trailing_avg": o.trailing_avg,
                "pct_diff": o.pct_diff,
            }
            for o in outliers
        ],
        budgets=[
            FinanceBudgetOut(
                id=s.id,
                category_id=f.category_id,
                category_name=s.category_name,
                planned=s.planned,
                actual=s.actual,
                remaining=s.remaining,
                utilization_pct=s.utilization_pct,
                over_budget=s.over_budget,
            )
            for f, s in zip(budget_fixtures, budgets, strict=True)
        ],
        goals=[
            FinanceGoalOut(
                id=g.id,
                title=g.title,
                target_amount=g.target_amount,
                current_amount=g.current_amount,
                remaining=g.remaining,
                progress_pct=g.progress_pct,
                required_monthly_contribution=g.required_monthly_contribution,
                currency=goal_rows[g.id].currency,
                target_date=goal_rows[g.id].target_date,
                category=goal_rows[g.id].category,
                status=goal_rows[g.id].status,
                notes=goal_rows[g.id].notes,
            )
            for g in goals
        ],
        upcoming_commitments=[
            FinanceRecurringOut(
                id=r.id,
                description=r.description,
                account_id=recurring_rows[r.id].account_id,
                category_id=recurring_rows[r.id].category_id,
                type=r.type,
                amount=r.amount,
                currency=recurring_rows[r.id].currency,
                interval=recurring_rows[r.id].interval,
                anchor_day=recurring_rows[r.id].anchor_day,
                next_due_date=r.next_due_date,
                active=recurring_rows[r.id].active,
            )
            for r in upcoming
        ],
        upcoming_total=sum(r.amount for r in upcoming),
        net_worth=FinanceNetWorthPointOut(
            snapshot_date=latest.snapshot_date,
            total_assets=latest.total_assets,
            total_liabilities=latest.total_liabilities,
            net_worth=latest.net_worth,
        )
        if latest
        else None,
        net_worth_trend=[
            FinanceNetWorthPointOut(
                snapshot_date=p.snapshot_date,
                total_assets=p.total_assets,
                total_liabilities=p.total_liabilities,
                net_worth=p.net_worth,
            )
            for p in trend
        ],
        insights=insights,
    )


@router.post("/snapshot", response_model=FinanceNetWorthPointOut)
async def take_net_worth_snapshot(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> FinanceNetWorthPointOut:
    snapshot = await finance_repo.compute_and_store_snapshot(session, user_id, date.today())
    log.info("finance_net_worth_snapshot_taken", user_id=str(user_id), net_worth=float(snapshot.net_worth))
    return FinanceNetWorthPointOut(
        snapshot_date=snapshot.snapshot_date,
        total_assets=float(snapshot.total_assets),
        total_liabilities=float(snapshot.total_liabilities),
        net_worth=float(snapshot.net_worth),
    )
