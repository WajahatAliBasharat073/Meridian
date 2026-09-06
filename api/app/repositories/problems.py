"""Adapts `problems` / `curriculum` / `problem_attempts` ORM rows to and
from the recommender and repetition engines' plain fixtures."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import AttemptFixture, ProblemFixture
from app.models.problems import Curriculum, Problem, ProblemAttempt


async def get_problem_fixtures(session: AsyncSession) -> list[ProblemFixture]:
    result = await session.execute(
        select(Problem, Curriculum.scheduled_date, Curriculum.slot).outerjoin(
            Curriculum, Curriculum.problem_id == Problem.id
        )
    )
    fixtures = []
    for problem, scheduled_date, slot in result.all():
        fixtures.append(
            ProblemFixture(
                problem_id=problem.id,
                title=problem.title,
                pattern=problem.pattern,
                difficulty=problem.difficulty,
                scheduled_date=scheduled_date,
                scheduled_slot=slot,
            )
        )
    return fixtures


async def get_attempt_fixtures(session: AsyncSession, user_id: uuid.UUID) -> list[AttemptFixture]:
    result = await session.execute(
        select(ProblemAttempt)
        .where(ProblemAttempt.user_id == user_id)
        .order_by(ProblemAttempt.attempted_at)
    )
    return [
        AttemptFixture(
            problem_id=a.problem_id,
            attempted_at=a.attempted_at,
            mastery_level=a.mastery_level,
            key_insight=a.key_insight,
        )
        for a in result.scalars().all()
    ]


async def get_latest_attempt_for_problem(
    session: AsyncSession, user_id: uuid.UUID, problem_id: int
) -> AttemptFixture | None:
    result = await session.execute(
        select(ProblemAttempt)
        .where(ProblemAttempt.user_id == user_id, ProblemAttempt.problem_id == problem_id)
        .order_by(ProblemAttempt.attempted_at.desc())
        .limit(1)
    )
    a = result.scalar_one_or_none()
    if a is None:
        return None
    return AttemptFixture(
        problem_id=a.problem_id,
        attempted_at=a.attempted_at,
        mastery_level=a.mastery_level,
        key_insight=a.key_insight,
    )


async def record_attempt(
    session: AsyncSession,
    user_id: uuid.UUID,
    problem_id: int,
    mastery_level: str,
    minutes: int | None,
    hint_used: bool,
    key_insight: str | None,
) -> ProblemAttempt:
    attempt = ProblemAttempt(
        user_id=user_id,
        problem_id=problem_id,
        attempted_at=datetime.now(),
        minutes=minutes,
        mastery_level=mastery_level,
        hint_used=hint_used,
        key_insight=key_insight,
    )
    session.add(attempt)
    await session.commit()
    await session.refresh(attempt)
    return attempt
