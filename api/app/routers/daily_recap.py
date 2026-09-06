from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_session
from app.deps import get_current_user_id
from app.schemas import CategoryBreakdownOut, DailyRecapOut
from app.services import get_daily_recap

router = APIRouter(prefix="/api", tags=["daily-recap"])


@router.get("/daily-recap", response_model=DailyRecapOut)
async def get_recap(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
    date_: Annotated[date | None, Query(alias="date")] = None,
) -> DailyRecapOut:
    """Defaults to yesterday — a recap of a day that has actually
    finished, not the one still in progress."""
    if date_ is None:
        today = datetime.now(ZoneInfo(settings.timezone)).date()
        date_ = today - timedelta(days=1)

    recap = await get_daily_recap(session, user_id, date_, settings)

    return DailyRecapOut(
        recap_date=recap.recap_date,
        total_blocks=recap.total_blocks,
        done_count=recap.done_count,
        partial_count=recap.partial_count,
        not_done_count=recap.not_done_count,
        rescheduled_count=recap.rescheduled_count,
        completion_pct=recap.completion_pct,
        category_breakdown=[
            CategoryBreakdownOut(category=c.category, done=c.done, total=c.total)
            for c in recap.category_breakdown
        ],
        problems_attempted=recap.problems_attempted,
        deep_work_planned_minutes=recap.deep_work_planned_minutes,
        deep_work_actual_minutes=recap.deep_work_actual_minutes,
        headline=recap.headline,
        suggestions=recap.suggestions,
    )
