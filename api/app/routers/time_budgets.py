from __future__ import annotations

import uuid
from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.repositories import goals as goals_repo
from app.schemas import TimeBudgetOut, TimeBudgetUpsert

router = APIRouter(prefix="/api/time-budgets", tags=["time-budgets"])


@router.get("", response_model=list[TimeBudgetOut])
async def list_time_budgets(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[TimeBudgetOut]:
    budgets = await goals_repo.list_time_budgets(session, user_id)
    since = date.today() - timedelta(days=6)
    actuals = await goals_repo.actual_minutes_by_category(session, user_id, since)
    return [
        TimeBudgetOut(
            id=b.id,
            category=b.category,
            minutes_per_week=b.minutes_per_week,
            actual_minutes_this_week=actuals.get(b.category, 0),
        )
        for b in budgets
    ]


@router.put("", response_model=TimeBudgetOut)
async def upsert_time_budget(
    payload: TimeBudgetUpsert,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> TimeBudgetOut:
    b = await goals_repo.upsert_time_budget(session, user_id, payload.category, payload.minutes_per_week)
    since = date.today() - timedelta(days=6)
    actual = await goals_repo.minutes_logged_for_category(session, user_id, payload.category, since)
    return TimeBudgetOut(
        id=b.id, category=b.category, minutes_per_week=b.minutes_per_week, actual_minutes_this_week=actual
    )


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_budget(
    budget_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> None:
    deleted = await goals_repo.delete_time_budget(session, user_id, budget_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
