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
from app.repositories.reviews import get_due_or_overdue
from app.schemas import ReviewDueOut

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("/due", response_model=list[ReviewDueOut])
async def list_due_reviews(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> list[ReviewDueOut]:
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    rows = await get_due_or_overdue(session, user_id, today)
    return [
        ReviewDueOut(
            subject_type=r.subject_type,
            subject_id=r.subject_id,
            due_date=r.due_date,
            overdue_days=r.overdue_days,
            interval_days=r.interval_days,
            last_result=r.last_result,
        )
        for r in rows
    ]
