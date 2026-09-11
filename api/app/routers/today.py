from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_session
from app.deps import get_current_user_id
from app.domain import Recommendation, readiness_pct
from app.engines.bandwidth import plan_bandwidth
from app.models.core import TimeBlock
from app.models.sessions import FocusSession
from app.repositories import problems as problems_repo
from app.repositories import reviews as reviews_repo
from app.repositories import schedule as schedule_repo
from app.schemas import BandwidthOut, RecommendationOut, TimeBlockOut, TodayCounters, TodayOut
from app.services import get_current_block, get_recommendations, infer_bandwidth_input

router = APIRouter(prefix="/api", tags=["today"])


@router.get("/today", response_model=TodayOut)
async def get_today(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TodayOut:
    today = datetime.now(ZoneInfo(settings.timezone)).date()

    prayer_times = await schedule_repo.get_or_compute_prayer_times(session, today, settings)
    blocks = await schedule_repo.get_blocks_for_date(session, user_id, today, prayer_times)
    current = await get_current_block(session, blocks, settings)

    # One query for the whole day rather than one per block — the
    # block-lock rule (app/engines/block_lock.py) needs to know which
    # blocks have ever had a focus session started on them.
    engaged_block_ids: set[int] = set()
    if blocks:
        engaged_block_ids = set(
            (
                await session.execute(
                    select(FocusSession.block_id).where(
                        FocusSession.user_id == user_id,
                        FocusSession.block_id.in_([b.id for b in blocks]),
                    )
                )
            )
            .scalars()
            .all()
        )

    recs = await get_recommendations(session, user_id, today, max_results=1)
    next_action = recs[0] if recs else None

    bandwidth_input = await infer_bandwidth_input(session, user_id, today, settings)
    bandwidth_plan = plan_bandwidth(bandwidth_input)

    overdue_reviews = [r for r in await reviews_repo.get_due_or_overdue(session, user_id, today) if r.due_date < today]
    blocks_remaining = sum(1 for b in blocks if b.status == "NOT DONE")

    attempt_fixtures = await problems_repo.get_attempt_fixtures(session, user_id)
    latest_by_problem: dict[int, str] = {}
    for a in attempt_fixtures:
        latest_by_problem[a.problem_id] = a.mastery_level
    total_curriculum = len(await problems_repo.get_problem_fixtures(session))

    return TodayOut(
        date=today,
        blocks=[_block_to_out(b, current, engaged_block_ids) for b in blocks],
        current_block=_block_to_out(current, current, engaged_block_ids) if current else None,
        next_action=_rec_to_out(next_action) if next_action else None,
        bandwidth=BandwidthOut(**bandwidth_plan.__dict__),
        counters=TodayCounters(
            overdue_reviews=len(overdue_reviews),
            blocks_remaining=blocks_remaining,
            readiness_pct=readiness_pct(total_curriculum, latest_by_problem.values()),
        ),
    )


def _block_to_out(
    block: TimeBlock, current: TimeBlock | None, engaged_block_ids: set[int]
) -> TimeBlockOut:
    return TimeBlockOut(
        id=block.id,
        seq=block.seq,
        start=block.start_resolved,
        end=block.end_resolved,
        activity=block.activity,
        tier=block.tier,
        category=block.category,
        planned_minutes=block.planned_minutes,
        status=block.status,
        actual_minutes=block.actual_minutes,
        what_to_do=block.what_to_do,
        notes=block.notes,
        is_current=current is not None and block.id == current.id,
        has_focus_session=block.id in engaged_block_ids,
    )


def _rec_to_out(rec: Recommendation) -> RecommendationOut:
    return RecommendationOut(
        problem_id=rec.problem_id,
        title=rec.title,
        pattern=rec.pattern,
        difficulty=rec.difficulty,
        reason=rec.reason,
        queue=rec.queue,
        is_review=rec.is_review,
        prior_key_insight=rec.prior_key_insight,
    )
