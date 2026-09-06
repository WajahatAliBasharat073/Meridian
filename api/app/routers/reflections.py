from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_session
from app.deps import get_current_user_id
from app.repositories import goals as goals_repo
from app.schemas import DailyReflectionOut, DailyReflectionUpsert

router = APIRouter(prefix="/api/reflections", tags=["reflections"])


@router.get("/today", response_model=DailyReflectionOut | None)
async def get_today_reflection(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DailyReflectionOut | None:
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    r = await goals_repo.get_reflection(session, user_id, today)
    if r is None:
        return None
    return DailyReflectionOut(
        date=r.date, mood=r.mood, what_got_in_the_way=r.what_got_in_the_way, what_went_well=r.what_went_well
    )


@router.put("/today", response_model=DailyReflectionOut)
async def upsert_today_reflection(
    payload: DailyReflectionUpsert,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DailyReflectionOut:
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    r = await goals_repo.upsert_reflection(
        session, user_id, today, payload.mood, payload.what_got_in_the_way, payload.what_went_well
    )
    return DailyReflectionOut(
        date=r.date, mood=r.mood, what_got_in_the_way=r.what_got_in_the_way, what_went_well=r.what_went_well
    )
