from __future__ import annotations

import uuid
from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.domain import readiness_pct
from app.engines.finance import month_summary
from app.engines.overview import OverviewInputs, build_overview_highlights
from app.repositories import finance as finance_repo
from app.repositories import goals as goals_repo
from app.repositories import life_logs as life_logs_repo
from app.repositories import problems as problems_repo
from app.repositories import reviews as reviews_repo
from app.schemas import OverviewOut

router = APIRouter(prefix="/api/overview", tags=["overview"])


@router.get("", response_model=OverviewOut)
async def get_overview(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> OverviewOut:
    today = date.today()
    week_start = today - timedelta(days=6)

    attempt_fixtures = await problems_repo.get_attempt_fixtures(session, user_id)
    latest_by_problem: dict[int, str] = {}
    for a in attempt_fixtures:
        latest_by_problem[a.problem_id] = a.mastery_level
    total_curriculum = len(await problems_repo.get_problem_fixtures(session))
    dsa_readiness = readiness_pct(total_curriculum, latest_by_problem.values())

    reviews = await reviews_repo.get_due_or_overdue(session, user_id, today)
    reviews_due_today = sum(1 for r in reviews if r.due_date == today)
    reviews_overdue = sum(1 for r in reviews if r.due_date < today)

    active_goals = await goals_repo.list_goals(session, user_id, status="active")

    this_month = today.replace(day=1)
    transactions = await finance_repo.get_transaction_fixtures(session, user_id, since=this_month)
    # Zero real transactions this month is a real answer ("nothing logged
    # yet"), not "unknown" -- month_summary already returns zeros rather
    # than fabricating anything for an empty list, so there's no need to
    # special-case it away here.
    finance_summary = month_summary(transactions, this_month)

    thesis_logs = await life_logs_repo.list_thesis_logs(session, user_id, limit=200)
    research_minutes_this_week = sum(
        (log.minutes or 0) for log in thesis_logs if log.date >= week_start
    )

    highlights = build_overview_highlights(
        OverviewInputs(
            readiness_pct=dsa_readiness,
            reviews_overdue=reviews_overdue,
            active_goal_count=len(active_goals),
            finance_savings_this_month=finance_summary.savings,
            research_minutes_this_week=research_minutes_this_week,
        )
    )

    return OverviewOut(
        readiness_pct=dsa_readiness,
        reviews_due_today=reviews_due_today,
        reviews_overdue=reviews_overdue,
        active_goal_count=len(active_goals),
        finance_income_this_month=finance_summary.income,
        finance_expenses_this_month=finance_summary.expenses,
        finance_savings_this_month=finance_summary.savings,
        research_minutes_this_week=research_minutes_this_week,
        highlights=highlights,
    )
