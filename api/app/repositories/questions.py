"""Adapts `interview_modules` / `questions` / `question_progress` rows.

Progress is a 0-7 ladder, not a toggle. A question with no row is mastery
0 ("never seen") — the absence of a row is a real answer here, so reads
default rather than requiring a row to exist.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import QuestionFixture, QuestionProgressFixture
from app.engines.theory_pace import QuestionTiming
from app.models.questions import InterviewModule, Question, QuestionProgress

# The bar at which a question counts as "prepared" in a readiness figure.
# 4 = can reason about trade-offs. Anything below that is recognition, and
# counting recognition as readiness is how a progress bar starts lying.
READY_MASTERY = 4


async def list_modules(session: AsyncSession) -> list[InterviewModule]:
    result = await session.execute(select(InterviewModule).order_by(InterviewModule.order_index))
    return list(result.scalars().all())


async def list_questions(
    session: AsyncSession,
    user_id: uuid.UUID,
    category: str | None = None,
    module_code: str | None = None,
    priority: str | None = None,
    company: str | None = None,
    topic: str | None = None,
    phase: int | None = None,
    difficulty: str | None = None,
    learning_status: str | None = None,
    needs_review: bool | None = None,
    attempted: bool | None = None,
) -> list[tuple[Question, int, QuestionProgress | None]]:
    """(question, mastery, progress row) for every question matching the
    filters. The progress row is returned alongside the mastery int (kept
    for compatibility with existing callers) so `learning_status` and
    `needs_review` are available without a second query.

    `attempted` filters on the *existence* of a progress row, independent
    of `learning_status` — a question can be attempted with no status set,
    and a status implies attempted but the reverse does not hold.
    """
    query = select(Question)
    if category:
        query = query.where(Question.category == category)
    if module_code:
        query = query.where(Question.module_code == module_code)
    if priority:
        query = query.where(Question.priority == priority)
    if company:
        # JSONB containment: the company appears in the tags array.
        query = query.where(Question.companies.contains([company]))
    if topic:
        query = query.where(Question.topic == topic)
    if phase is not None:
        query = query.where(Question.phase == phase)
    if difficulty:
        query = query.where(Question.difficulty == difficulty)
    query = query.order_by(Question.module_code, Question.order_index)

    questions = list((await session.execute(query)).scalars().all())

    progress_by_question: dict[int, QuestionProgress] = {}
    if questions:
        rows = await session.execute(
            select(QuestionProgress).where(QuestionProgress.user_id == user_id)
        )
        progress_by_question = {p.question_id: p for p in rows.scalars().all()}

    out: list[tuple[Question, int, QuestionProgress | None]] = []
    for q in questions:
        p = progress_by_question.get(q.id)
        if attempted is True and p is None:
            continue
        if attempted is False and p is not None:
            continue
        if learning_status is not None and (p is None or p.learning_status != learning_status):
            continue
        if needs_review is not None and bool(p and p.needs_review) != needs_review:
            continue
        out.append((q, p.mastery if p else 0, p))
    return out


async def set_learning_status(
    session: AsyncSession,
    user_id: uuid.UUID,
    question_id: int,
    learning_status: str | None,
    needs_review: bool | None,
) -> QuestionProgress:
    """Upsert this user's self-tag and revisit flag.

    A status-only call (mastery untouched) must not clobber an existing
    mastery rating, so a fresh row is created at mastery 0 only when none
    exists yet — the same "no row = never seen" convention `list_questions`
    already relies on.
    """
    from app.schemas import resolve_needs_review

    existing = (
        await session.execute(
            select(QuestionProgress).where(
                QuestionProgress.user_id == user_id,
                QuestionProgress.question_id == question_id,
            )
        )
    ).scalar_one_or_none()

    resolved_review = resolve_needs_review(learning_status, needs_review)

    if existing is not None:
        existing.learning_status = learning_status
        existing.needs_review = resolved_review
        existing.updated_at = datetime.now()
        row = existing
    else:
        row = QuestionProgress(
            user_id=user_id,
            question_id=question_id,
            mastery=0,
            updated_at=datetime.now(),
            learning_status=learning_status,
            needs_review=resolved_review,
        )
        session.add(row)

    await session.commit()
    await session.refresh(row)
    return row


async def set_mastery(
    session: AsyncSession,
    user_id: uuid.UUID,
    question_id: int,
    mastery: int,
    notes: str | None = None,
    minutes: int | None = None,
) -> int:
    """Upsert this user's ladder position. Returns the stored mastery.

    `rating_count` increments on every call (a re-rating is still a real
    study touch); `total_minutes` only increments when `minutes` is
    actually supplied, since an untimed rating shouldn't drag the pace
    average toward zero.
    """
    existing = (
        await session.execute(
            select(QuestionProgress).where(
                QuestionProgress.user_id == user_id,
                QuestionProgress.question_id == question_id,
            )
        )
    ).scalar_one_or_none()

    if existing is not None:
        existing.mastery = mastery
        existing.updated_at = datetime.now()
        existing.rating_count = (existing.rating_count or 0) + 1
        if minutes is not None:
            existing.total_minutes = (existing.total_minutes or 0) + minutes
        if notes is not None:
            existing.notes = notes
    else:
        session.add(
            QuestionProgress(
                user_id=user_id,
                question_id=question_id,
                mastery=mastery,
                notes=notes,
                updated_at=datetime.now(),
                rating_count=1,
                total_minutes=minutes or 0,
            )
        )
    await session.commit()
    return mastery


async def get_module_summary(
    session: AsyncSession, user_id: uuid.UUID
) -> list[tuple[str, int, int]]:
    """(module_code, ready_count, total_count) per module.

    "Ready" means mastery >= READY_MASTERY, not "has a row". Counting every
    touched question as progress is what made the old coverage percentage
    unusable as a readiness signal.
    """
    totals: dict[str, int] = dict(
        (
            await session.execute(
                select(Question.module_code, func.count())
                .where(Question.module_code.isnot(None))
                .group_by(Question.module_code)
            )
        ).all()  # type: ignore[arg-type]
    )

    ready: dict[str, int] = dict(
        (
            await session.execute(
                select(Question.module_code, func.count())
                .join(QuestionProgress, QuestionProgress.question_id == Question.id)
                .where(
                    QuestionProgress.user_id == user_id,
                    QuestionProgress.mastery >= READY_MASTERY,
                    Question.module_code.isnot(None),
                )
                .group_by(Question.module_code)
            )
        ).all()  # type: ignore[arg-type]
    )

    return [(code, ready.get(code, 0), total) for code, total in sorted(totals.items())]


async def get_coverage_summary(
    session: AsyncSession, user_id: uuid.UUID
) -> list[tuple[str, int, int, int]]:
    """(category, ready_count, started_count, total_count) per category.

    Two counts, not one, because they are different claims and collapsing
    them is what makes a progress bar dishonest:

      started  mastery >= 1 — you have rated it at all
      ready    mastery >= READY_MASTERY (4) — you can hold it under
               follow-up pressure

    A bar that shows only `started` says you have "done" 600 questions you
    can merely recognise; a bar that shows only `ready` hides the work in
    progress. The UI renders both segments.
    """
    totals: dict[str, int] = dict(
        (
            await session.execute(select(Question.category, func.count()).group_by(Question.category))
        ).all()  # type: ignore[arg-type]
    )

    async def _count_at_least(minimum: int) -> dict[str, int]:
        return dict(
            (
                await session.execute(
                    select(Question.category, func.count())
                    .join(QuestionProgress, QuestionProgress.question_id == Question.id)
                    .where(
                        QuestionProgress.user_id == user_id,
                        QuestionProgress.mastery >= minimum,
                    )
                    .group_by(Question.category)
                )
            ).all()  # type: ignore[arg-type]
        )

    ready = await _count_at_least(READY_MASTERY)
    started = await _count_at_least(1)

    return [
        (category, ready.get(category, 0), started.get(category, 0), total)
        for category, total in sorted(totals.items())
    ]


async def get_all_question_fixtures(session: AsyncSession) -> list[QuestionFixture]:
    """Every bank question, reduced to what the daily theory recommender
    needs. Deliberately the whole bank, not a filtered slice — the engine
    itself decides what is due, and it needs the full pool to do that."""
    rows = (
        await session.execute(
            select(
                Question.id,
                Question.module_code,
                Question.category,
                Question.question_type,
                Question.priority,
                Question.frequency,
            )
        )
    ).all()
    return [
        QuestionFixture(
            question_id=r[0],
            module_code=r[1],
            category=r[2],
            question_type=r[3],
            priority=r[4],
            frequency=r[5],
        )
        for r in rows
    ]


async def get_question_progress_fixtures(
    session: AsyncSession, user_id: uuid.UUID
) -> list[QuestionProgressFixture]:
    rows = (
        await session.execute(
            select(QuestionProgress.question_id, QuestionProgress.mastery, QuestionProgress.updated_at)
            .where(QuestionProgress.user_id == user_id)
        )
    ).all()
    return [
        QuestionProgressFixture(question_id=r[0], mastery=r[1], updated_at=r[2]) for r in rows
    ]


async def get_questions_by_ids(session: AsyncSession, ids: list[int]) -> dict[int, Question]:
    if not ids:
        return {}
    rows = (await session.execute(select(Question).where(Question.id.in_(ids)))).scalars().all()
    return {q.id: q for q in rows}


async def get_question_timing_fixtures(
    session: AsyncSession, user_id: uuid.UUID
) -> list[QuestionTiming]:
    """Every question this user has logged real minutes against — the
    input to the pace-projection engine. Untimed ratings (rating_count > 0
    but total_minutes == 0) are excluded: they'd silently drag the
    average toward zero for time nobody actually reported."""
    rows = (
        await session.execute(
            select(
                QuestionProgress.question_id,
                QuestionProgress.total_minutes,
                QuestionProgress.rating_count,
            ).where(
                QuestionProgress.user_id == user_id,
                QuestionProgress.total_minutes > 0,
            )
        )
    ).all()
    return [QuestionTiming(question_id=r[0], total_minutes=r[1], rating_count=r[2]) for r in rows]


async def get_backlog_count(session: AsyncSession, user_id: uuid.UUID) -> int:
    """Questions not yet at READY_MASTERY — the queue the pace projection
    is estimating time-to-clear for."""
    total = await session.scalar(select(func.count()).select_from(Question))
    ready = await session.scalar(
        select(func.count())
        .select_from(QuestionProgress)
        .where(QuestionProgress.user_id == user_id, QuestionProgress.mastery >= READY_MASTERY)
    )
    return max(0, (total or 0) - (ready or 0))
