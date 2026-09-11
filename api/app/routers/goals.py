from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_session
from app.deps import get_current_user_id
from app.engines.finance import GoalFixture, goal_progress
from app.models.goals import Goal
from app.repositories import finance as finance_repo
from app.repositories import goals as goals_repo
from app.schemas import FinanceGoalOut, GoalCreate, GoalOut, GoalUpdate

router = APIRouter(prefix="/api/goals", tags=["goals"])


def _linked_finance_out(fixture: GoalFixture, category: str, status_: str, today: date) -> FinanceGoalOut:
    s = goal_progress([fixture], today)[0]
    return FinanceGoalOut(
        id=s.id,
        title=s.title,
        target_amount=s.target_amount,
        current_amount=s.current_amount,
        remaining=s.remaining,
        progress_pct=s.progress_pct,
        required_monthly_contribution=s.required_monthly_contribution,
        currency="AUD",
        target_date=fixture.target_date,
        category=category,
        status=status_,
        notes=None,
    )


async def _goal_out(
    session: AsyncSession, user_id: uuid.UUID, g: Goal, minutes_logged: int | None
) -> GoalOut:
    linked = None
    if g.finance_goal_id is not None:
        finance_rows = {r.id: r for r in await finance_repo.list_goals(session, user_id)}
        fg_row = finance_rows.get(g.finance_goal_id)
        if fg_row is not None:
            fixtures = await finance_repo.get_goal_fixtures(session, user_id)
            fixture = next((f for f in fixtures if f.id == g.finance_goal_id), None)
            if fixture is not None:
                linked = _linked_finance_out(fixture, fg_row.category, fg_row.status, date.today())

    return GoalOut(
        id=g.id,
        title=g.title,
        description=g.description,
        category=g.category,
        target_date=g.target_date,
        progress_pct=g.progress_pct,
        status=g.status,
        minutes_logged=minutes_logged,
        finance_goal_id=g.finance_goal_id,
        linked_finance_goal=linked,
    )


async def _validate_finance_goal_ownership(
    session: AsyncSession, user_id: uuid.UUID, finance_goal_id: int | None
) -> None:
    if not finance_goal_id:
        return
    owned_ids = {r.id for r in await finance_repo.list_goals(session, user_id)}
    if finance_goal_id not in owned_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Finance goal not found"
        )


@router.get("", response_model=list[GoalOut])
async def list_goals(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
    status_filter: str | None = None,
) -> list[GoalOut]:
    goals = await goals_repo.list_goals(session, user_id, status=status_filter)
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    out = []
    for g in goals:
        minutes_logged = None
        if g.category:
            since = g.target_date if g.target_date and g.target_date < today else today.replace(day=1)
            minutes_logged = await goals_repo.minutes_logged_for_category(
                session, user_id, g.category, min(since, today)
            )
        out.append(await _goal_out(session, user_id, g, minutes_logged))
    return out


@router.post("", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
async def create_goal(
    payload: GoalCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> GoalOut:
    await _validate_finance_goal_ownership(session, user_id, payload.finance_goal_id)
    g = await goals_repo.create_goal(
        session,
        user_id,
        payload.title,
        payload.description,
        payload.category,
        payload.target_date,
        payload.finance_goal_id,
    )
    return await _goal_out(session, user_id, g, None)


@router.patch("/{goal_id}", response_model=GoalOut)
async def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> GoalOut:
    await _validate_finance_goal_ownership(session, user_id, payload.finance_goal_id)
    g = await goals_repo.update_goal(
        session, user_id, goal_id, payload.progress_pct, payload.status, payload.finance_goal_id
    )
    if g is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return await _goal_out(session, user_id, g, None)
