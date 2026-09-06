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
from app.schemas import MoodCountOut, WeeklyCategoryMinutesOut, WeeklyReviewOut
from app.services import get_weekly_review

router = APIRouter(prefix="/api/weekly-review", tags=["weekly-review"])


@router.get("", response_model=WeeklyReviewOut)
async def get_review(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> WeeklyReviewOut:
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    review = await get_weekly_review(session, user_id, today)
    return WeeklyReviewOut(
        window_start=review.window_start,
        window_end=review.window_end,
        total_minutes_logged=review.total_minutes_logged,
        days_active=review.days_active,
        days_in_window=review.days_in_window,
        completion_pct=review.completion_pct,
        category_minutes=[
            WeeklyCategoryMinutesOut(category=c.category, minutes=c.minutes) for c in review.category_minutes
        ],
        avg_focus_session_minutes=review.avg_focus_session_minutes,
        rescheduled_count=review.rescheduled_count,
        mood_distribution=[MoodCountOut(mood=m.mood, count=m.count) for m in review.mood_distribution],
        what_went_well=review.what_went_well,
        what_to_improve=review.what_to_improve,
    )
