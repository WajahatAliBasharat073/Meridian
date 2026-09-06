from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_session
from app.deps import get_current_user_id
from app.repositories import goals as goals_repo
from app.schemas import GoalCreate, GoalOut, GoalUpdate

router = APIRouter(prefix="/api/goals", tags=["goals"])


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
        out.append(
            GoalOut(
                id=g.id,
                title=g.title,
                description=g.description,
                category=g.category,
                target_date=g.target_date,
                progress_pct=g.progress_pct,
                status=g.status,
                minutes_logged=minutes_logged,
            )
        )
    return out


@router.post("", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
async def create_goal(
    payload: GoalCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> GoalOut:
    g = await goals_repo.create_goal(
        session, user_id, payload.title, payload.description, payload.category, payload.target_date
    )
    return GoalOut(
        id=g.id,
        title=g.title,
        description=g.description,
        category=g.category,
        target_date=g.target_date,
        progress_pct=g.progress_pct,
        status=g.status,
        minutes_logged=None,
    )


@router.patch("/{goal_id}", response_model=GoalOut)
async def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> GoalOut:
    g = await goals_repo.update_goal(session, user_id, goal_id, payload.progress_pct, payload.status)
    if g is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return GoalOut(
        id=g.id,
        title=g.title,
        description=g.description,
        category=g.category,
        target_date=g.target_date,
        progress_pct=g.progress_pct,
        status=g.status,
        minutes_logged=None,
    )
