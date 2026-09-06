"""Adapts the `reviews` table to and from the repetition engine.

`ReviewState.current_level` is not a column on `reviews` (design doc 5.3
deliberately keeps mastery on `problem_attempts` only) — for subject_type
'problem' it is read from the latest attempt. Vocab/ml_concept/mistake
review subjects are not wired to a CRUD surface yet (build prompt phase 6),
so only 'problem' is fully supported here; the shape stays polymorphic so
adding them later does not touch the engine.
"""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import ReviewOutcome, ReviewState
from app.models.problems import ProblemAttempt
from app.models.repetition import Review


async def get_problem_reviews(session: AsyncSession, user_id: uuid.UUID) -> list[ReviewState]:
    result = await session.execute(select(Review).where(Review.user_id == user_id))
    reviews = list(result.scalars().all())

    problem_ids = [r.subject_id for r in reviews if r.subject_type == "problem"]
    current_levels: dict[int, str] = {}
    if problem_ids:
        latest_result = await session.execute(
            select(ProblemAttempt)
            .where(ProblemAttempt.user_id == user_id, ProblemAttempt.problem_id.in_(problem_ids))
            .order_by(ProblemAttempt.attempted_at)
        )
        for a in latest_result.scalars().all():
            current_levels[a.problem_id] = a.mastery_level

    states = []
    for r in reviews:
        if r.subject_type != "problem":
            continue
        level = current_levels.get(r.subject_id)
        if level is None:
            continue
        states.append(
            ReviewState(
                subject_type=r.subject_type,
                subject_id=r.subject_id,
                due_date=r.due_date,
                interval_days=r.interval_days,
                current_level=level,
                overdue_days=r.overdue_days,
                last_result=r.last_result,
            )
        )
    return states


async def get_review_state(
    session: AsyncSession, user_id: uuid.UUID, subject_type: str, subject_id: int
) -> Review | None:
    result = await session.execute(
        select(Review).where(
            Review.user_id == user_id,
            Review.subject_type == subject_type,
            Review.subject_id == subject_id,
        )
    )
    return result.scalar_one_or_none()


async def upsert_review(
    session: AsyncSession, user_id: uuid.UUID, outcome: ReviewOutcome
) -> Review:
    existing = await get_review_state(session, user_id, outcome.subject_type, outcome.subject_id)
    if existing is None:
        existing = Review(user_id=user_id, subject_type=outcome.subject_type, subject_id=outcome.subject_id)
        session.add(existing)

    existing.due_date = outcome.due_date
    existing.interval_days = outcome.interval_days
    existing.overdue_days = outcome.overdue_days
    existing.last_result = outcome.last_result
    await session.commit()
    await session.refresh(existing)
    return existing


async def get_due_or_overdue(session: AsyncSession, user_id: uuid.UUID, today: date) -> list[Review]:
    result = await session.execute(
        select(Review)
        .where(Review.user_id == user_id, Review.due_date <= today)
        .order_by(Review.due_date)
    )
    return list(result.scalars().all())
