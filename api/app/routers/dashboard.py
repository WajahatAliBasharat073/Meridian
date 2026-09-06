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
from app.schemas import (
    AttemptsByDayOut,
    DashboardSummaryOut,
    MasteryCountOut,
    PatternCoverageOut,
)
from app.services import get_dashboard_summary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryOut)
async def get_summary(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DashboardSummaryOut:
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    summary = await get_dashboard_summary(session, user_id, today)

    return DashboardSummaryOut(
        total_problems=summary.total_problems,
        attempted_count=summary.attempted_count,
        mastery_distribution=[
            MasteryCountOut(level=m.level, count=m.count) for m in summary.mastery_distribution
        ],
        pattern_coverage=[
            PatternCoverageOut(
                pattern=pc.pattern,
                scheduled_count=pc.scheduled_count,
                l5_plus_count=pc.l5_plus_count,
                ratio=pc.ratio,
            )
            for pc in summary.pattern_coverage
        ],
        attempts_by_day=[AttemptsByDayOut(day=d.day, count=d.count) for d in summary.attempts_by_day],
        reviews_due_count=summary.reviews_due_count,
        reviews_overdue_count=summary.reviews_overdue_count,
        readiness_pct=summary.readiness_pct,
    )
