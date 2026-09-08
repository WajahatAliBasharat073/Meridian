"""Adapts `problems` / `curriculum` / `problem_attempts` ORM rows to and
from the recommender and repetition engines' plain fixtures."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import AttemptFixture, ProblemFixture, ProblemProgress
from app.models.problems import (
    Curriculum,
    Problem,
    ProblemAttempt,
    TopicGuide,
    TopicLearningEntry,
    TopicVerificationAttempt,
)


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


async def list_problems(
    session: AsyncSession,
    user_id: uuid.UUID,
    pattern: str | None = None,
    difficulty: str | None = None,
) -> list[tuple[Problem, date | None, ProblemProgress | None]]:
    """Every problem, its curriculum slot for `today` (if any), and the
    calling user's progress on it (if ever attempted) — the read model
    behind the Problems browser. Not an engine: no ranking or ladder
    logic, just a join and two optional filters."""
    query = select(Problem, Curriculum.scheduled_date).outerjoin(
        Curriculum, Curriculum.problem_id == Problem.id
    )
    if pattern:
        query = query.where(Problem.pattern == pattern)
    if difficulty:
        query = query.where(Problem.difficulty == difficulty)
    query = query.order_by(Problem.lc_number)

    result = await session.execute(query)
    rows = result.all()

    problem_ids = [p.id for p, _ in rows]
    progress_by_problem: dict[int, ProblemProgress] = {}
    if problem_ids:
        # Ascending, so the last row seen per problem is the latest attempt;
        # the count accumulates as we go.
        latest_result = await session.execute(
            select(ProblemAttempt)
            .where(ProblemAttempt.user_id == user_id, ProblemAttempt.problem_id.in_(problem_ids))
            .order_by(ProblemAttempt.attempted_at)
        )
        for a in latest_result.scalars().all():
            prior = progress_by_problem.get(a.problem_id)
            progress_by_problem[a.problem_id] = ProblemProgress(
                mastery_level=a.mastery_level,
                solve_method=a.solve_method,
                attempt_count=(prior.attempt_count + 1) if prior else 1,
                last_attempted_at=a.attempted_at,
                key_insight=a.key_insight,
                notes=a.notes,
                minutes=a.minutes,
            )

    return [(p, scheduled_date, progress_by_problem.get(p.id)) for p, scheduled_date in rows]


async def list_topic_guides(session: AsyncSession) -> list[TopicGuide]:
    """The "learn it first" guides, in study order."""
    result = await session.execute(select(TopicGuide).order_by(TopicGuide.seq))
    return list(result.scalars().all())


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


async def count_problems_attempted_on(session: AsyncSession, user_id: uuid.UUID, on_date: date) -> int:
    result = await session.execute(
        select(func.count(func.distinct(ProblemAttempt.problem_id))).where(
            ProblemAttempt.user_id == user_id,
            func.date(ProblemAttempt.attempted_at) == on_date,
        )
    )
    return result.scalar_one()


async def record_attempt(
    session: AsyncSession,
    user_id: uuid.UUID,
    problem_id: int,
    mastery_level: str,
    minutes: int | None,
    hint_used: bool,
    key_insight: str | None,
    solve_method: str | None = None,
    understood_approach_independently: bool | None = None,
    reached_optimal: bool | None = None,
    notes: str | None = None,
) -> ProblemAttempt:
    attempt = ProblemAttempt(
        user_id=user_id,
        problem_id=problem_id,
        attempted_at=datetime.now(),
        minutes=minutes,
        mastery_level=mastery_level,
        hint_used=hint_used,
        key_insight=key_insight,
        solve_method=solve_method,
        understood_approach_independently=understood_approach_independently,
        reached_optimal=reached_optimal,
        notes=notes,
    )
    session.add(attempt)
    await session.commit()
    await session.refresh(attempt)
    return attempt


async def get_verification_attempts(
    session: AsyncSession, user_id: uuid.UUID
) -> list[TopicVerificationAttempt]:
    """Every verification attempt for this user, all topics — the gate engine
    reads the whole history rather than a per-topic flag."""
    result = await session.execute(
        select(TopicVerificationAttempt)
        .where(TopicVerificationAttempt.user_id == user_id)
        .order_by(TopicVerificationAttempt.started_at)
    )
    return list(result.scalars().all())


async def get_verification_attempt(
    session: AsyncSession, user_id: uuid.UUID, attempt_id: int
) -> TopicVerificationAttempt | None:
    row = await session.get(TopicVerificationAttempt, attempt_id)
    return row if row is not None and row.user_id == user_id else None


async def create_verification_attempt(
    session: AsyncSession, user_id: uuid.UUID, topic: str, started_at: datetime
) -> TopicVerificationAttempt:
    attempt = TopicVerificationAttempt(
        user_id=user_id, topic=topic, started_at=started_at, stage="build"
    )
    session.add(attempt)
    await session.commit()
    await session.refresh(attempt)
    return attempt


async def save_verification_attempt(
    session: AsyncSession, attempt: TopicVerificationAttempt
) -> TopicVerificationAttempt:
    await session.commit()
    await session.refresh(attempt)
    return attempt


async def get_topic_guide(session: AsyncSession, topic: str) -> TopicGuide | None:
    result = await session.execute(select(TopicGuide).where(TopicGuide.topic == topic))
    return result.scalar_one_or_none()


async def list_learning_entries(
    session: AsyncSession, user_id: uuid.UUID, topic: str
) -> list[TopicLearningEntry]:
    result = await session.execute(
        select(TopicLearningEntry)
        .where(TopicLearningEntry.user_id == user_id, TopicLearningEntry.topic == topic)
        .order_by(TopicLearningEntry.created_at.desc())
    )
    return list(result.scalars().all())


async def create_learning_entry(
    session: AsyncSession,
    user_id: uuid.UUID,
    topic: str,
    kind: str,
    title: str,
    url: str | None,
    body: str | None,
    created_at: datetime,
) -> TopicLearningEntry:
    entry = TopicLearningEntry(
        user_id=user_id,
        topic=topic,
        kind=kind,
        title=title,
        url=url,
        body=body,
        created_at=created_at,
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


async def delete_learning_entry(session: AsyncSession, user_id: uuid.UUID, entry_id: int) -> bool:
    entry = await session.get(TopicLearningEntry, entry_id)
    if entry is None or entry.user_id != user_id:
        return False
    await session.delete(entry)
    await session.commit()
    return True
