from __future__ import annotations

import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.engines.finance import GoalStatus, goal_progress
from app.logging import get_logger
from app.models.finance import FinanceGoal
from app.repositories import finance as finance_repo
from app.schemas import FinanceGoalCreate, FinanceGoalOut, FinanceGoalUpdate

log = get_logger(__name__)

router = APIRouter(prefix="/api/finance/goals", tags=["finance"])


def _out(status_row: FinanceGoal, goal_status: GoalStatus) -> FinanceGoalOut:
    return FinanceGoalOut(
        id=goal_status.id,
        title=goal_status.title,
        target_amount=goal_status.target_amount,
        current_amount=goal_status.current_amount,
        remaining=goal_status.remaining,
        progress_pct=goal_status.progress_pct,
        required_monthly_contribution=goal_status.required_monthly_contribution,
        currency=status_row.currency,
        target_date=status_row.target_date,
        category=status_row.category,
        status=status_row.status,
        notes=status_row.notes,
    )


@router.get("", response_model=list[FinanceGoalOut])
async def list_goals(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[FinanceGoalOut]:
    rows = await finance_repo.list_goals(session, user_id)
    fixtures = await finance_repo.get_goal_fixtures(session, user_id)
    statuses = {s.id: s for s in goal_progress(fixtures, date.today())}
    return [_out(r, statuses[r.id]) for r in rows if r.id in statuses]


@router.post("", response_model=FinanceGoalOut, status_code=status.HTTP_201_CREATED)
async def create_goal(
    payload: FinanceGoalCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> FinanceGoalOut:
    row = await finance_repo.create_goal(
        session,
        user_id,
        title=payload.title,
        target_amount=payload.target_amount,
        currency=payload.currency,
        target_date=payload.target_date,
        category=payload.category,
        notes=payload.notes,
    )
    fixtures = await finance_repo.get_goal_fixtures(session, user_id)
    fixture = next(f for f in fixtures if f.id == row.id)
    goal_status = goal_progress([fixture], date.today())[0]
    log.info("finance_goal_created", user_id=str(user_id), goal_id=row.id)
    return _out(row, goal_status)


@router.patch("/{goal_id}", response_model=FinanceGoalOut)
async def update_goal(
    goal_id: int,
    payload: FinanceGoalUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> FinanceGoalOut:
    row = await finance_repo.update_goal(session, user_id, goal_id, payload.status)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    fixtures = await finance_repo.get_goal_fixtures(session, user_id)
    fixture = next(f for f in fixtures if f.id == row.id)
    goal_status = goal_progress([fixture], date.today())[0]
    return _out(row, goal_status)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> None:
    deleted = await finance_repo.delete_goal(session, user_id, goal_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    log.info("finance_goal_deleted", user_id=str(user_id), goal_id=goal_id)
