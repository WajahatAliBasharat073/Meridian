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
from app.schemas import AttemptCreate, AttemptResult
from app.services import submit_attempt

router = APIRouter(prefix="/api/attempts", tags=["attempts"])


@router.post("", response_model=AttemptResult)
async def create_attempt(
    payload: AttemptCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AttemptResult:
    """One click, no forms (build prompt 5.2): mastery level in, next
    review date and a plain-English confirmation out."""
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    due_date_str, interval_days = await submit_attempt(
        session,
        user_id,
        payload.problem_id,
        payload.mastery_level,
        payload.minutes,
        payload.hint_used,
        payload.key_insight,
        today,
        payload.solve_method,
        payload.understood_approach_independently,
        payload.reached_optimal,
        payload.notes,
    )
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    if interval_days:
        # Avoid strftime's non-portable no-pad flag (%-d on POSIX, %#d on
        # Windows) — build the "14 Sep" form manually instead.
        pretty_date = f"{due_date.day} {due_date.strftime('%b')}"
        message = f"Next review: {pretty_date}, {interval_days} day{'s' if interval_days != 1 else ''}."
    else:
        message = "No review scheduled yet — mark real progress to start one."
    return AttemptResult(next_review_due=due_date, interval_days=interval_days, message=message)
