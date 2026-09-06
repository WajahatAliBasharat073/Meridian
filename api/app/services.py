"""Composition layer: routers stay thin, repositories stay pure-adapter,
engines stay pure-function. This module is the only place that wires all
three together for a given use case."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.domain import BandwidthInput, DashboardSummary, Recommendation
from app.engines.bandwidth import MINUTES_PER_REVIEW
from app.engines.recommender import recommend
from app.engines.repetition import on_attempt
from app.engines.summary import compute_dashboard_summary
from app.models.core import TimeBlock
from app.repositories import problems as problems_repo
from app.repositories import reviews as reviews_repo
from app.repositories import schedule as schedule_repo

DEFAULT_ENERGY = 3


async def infer_bandwidth_input(
    session: AsyncSession,
    user_id: uuid.UUID,
    today: date,
    settings: Settings,
    minutes_override: int | None = None,
    energy_override: int | None = None,
) -> BandwidthInput:
    """minutes/energy are explicit when the user states them (build prompt
    5.3); otherwise inferred from unclaimed blocks and last night's sleep."""
    overdue = [r for r in await reviews_repo.get_due_or_overdue(session, user_id, today) if r.due_date < today]
    overdue_count = len(overdue)
    overdue_minutes = overdue_count * MINUTES_PER_REVIEW

    if minutes_override is not None:
        minutes = minutes_override
    else:
        prayer_times = await schedule_repo.get_or_compute_prayer_times(session, today, settings)
        blocks = await schedule_repo.get_blocks_for_date(session, user_id, today, prayer_times)
        minutes = sum(b.planned_minutes for b in blocks if b.status == "NOT DONE")

    energy = energy_override if energy_override is not None else DEFAULT_ENERGY

    now_hour = datetime.now(ZoneInfo(settings.timezone)).hour

    return BandwidthInput(
        minutes_available=minutes,
        energy=energy,
        overdue_review_count=overdue_count,
        overdue_review_minutes=overdue_minutes,
        hour_of_day=now_hour,
    )


async def get_recommendations(
    session: AsyncSession,
    user_id: uuid.UUID,
    today: date,
    max_results: int = 1,
) -> list[Recommendation]:
    review_states = await reviews_repo.get_problem_reviews(session, user_id)
    problem_fixtures = await problems_repo.get_problem_fixtures(session)
    attempt_fixtures = await problems_repo.get_attempt_fixtures(session, user_id)
    return recommend(
        reviews=review_states,
        problems=problem_fixtures,
        attempts=attempt_fixtures,
        today=today,
        max_results=max_results,
    )


async def submit_attempt(
    session: AsyncSession,
    user_id: uuid.UUID,
    problem_id: int,
    mastery_level: str,
    minutes: int | None,
    hint_used: bool,
    key_insight: str | None,
    today: date,
) -> tuple[str, int]:
    """Writes the attempt, then advances (or creates) its review row.
    Returns (due_date, interval_days) for the one-line confirmation the UI
    shows immediately (build prompt 5.2: "Next review: 14 Sep, 7 days").

    The previous mastery level is read from the last attempt *before* this
    one is written — `reviews` deliberately has no level column of its own
    (design doc 5.2/5.3: mastery lives only on `problem_attempts`)."""
    previous_attempt = await problems_repo.get_latest_attempt_for_problem(session, user_id, problem_id)

    await problems_repo.record_attempt(
        session, user_id, problem_id, mastery_level, minutes, hint_used, key_insight
    )

    existing_review = await reviews_repo.get_review_state(session, user_id, "problem", problem_id)
    previous_state = None
    if existing_review is not None and previous_attempt is not None:
        from app.domain import ReviewState

        previous_state = ReviewState(
            subject_type="problem",
            subject_id=problem_id,
            due_date=existing_review.due_date,
            interval_days=existing_review.interval_days,
            current_level=previous_attempt.mastery_level,
            overdue_days=existing_review.overdue_days,
            last_result=existing_review.last_result,
        )

    engaged = minutes is not None and minutes > 0
    outcome = on_attempt(previous_state, "problem", problem_id, mastery_level, today, engaged=engaged)
    if outcome is None:
        return today.isoformat(), 0

    await reviews_repo.upsert_review(session, user_id, outcome)
    return outcome.due_date.isoformat(), outcome.interval_days


async def get_dashboard_summary(
    session: AsyncSession, user_id: uuid.UUID, today: date, days_window: int = 14
) -> DashboardSummary:
    review_states = await reviews_repo.get_problem_reviews(session, user_id)
    problem_fixtures = await problems_repo.get_problem_fixtures(session)
    attempt_fixtures = await problems_repo.get_attempt_fixtures(session, user_id)
    return compute_dashboard_summary(
        problems=problem_fixtures,
        attempts=attempt_fixtures,
        reviews=review_states,
        today=today,
        days_window=days_window,
    )


async def get_current_block(session: AsyncSession, blocks: list[TimeBlock], settings: Settings) -> TimeBlock | None:
    now = datetime.now(ZoneInfo(settings.timezone)).time()
    for b in blocks:
        if b.start_resolved and b.end_resolved and b.start_resolved <= now < b.end_resolved:
            return b
    return None
