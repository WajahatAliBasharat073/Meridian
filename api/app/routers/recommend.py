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
from app.engines.bandwidth import plan_bandwidth
from app.schemas import RecommendationOut
from app.services import get_recommendations, infer_bandwidth_input

router = APIRouter(prefix="/api", tags=["recommend"])


@router.get("/recommend", response_model=list[RecommendationOut])
async def get_recommend(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
    minutes: int | None = None,
    energy: int | None = None,
) -> list[RecommendationOut]:
    """Ranked list with reasons — never more than the bandwidth budget
    allows (build prompt 5.2/5.3)."""
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    bandwidth_input = await infer_bandwidth_input(
        session, user_id, today, settings, minutes_override=minutes, energy_override=energy
    )
    plan = plan_bandwidth(bandwidth_input)
    max_results = max(plan.max_new_problems, 1) if plan.include_reviews or plan.max_new_problems else 0
    if plan.band == "MINIMUM_VIABLE_DAY":
        max_results = 1

    recs = await get_recommendations(session, user_id, today, max_results=max_results or 1)
    return [
        RecommendationOut(
            problem_id=r.problem_id,
            title=r.title,
            pattern=r.pattern,
            difficulty=r.difficulty,
            reason=r.reason,
            queue=r.queue,
            is_review=r.is_review,
            prior_key_insight=r.prior_key_insight,
        )
        for r in recs
    ]
