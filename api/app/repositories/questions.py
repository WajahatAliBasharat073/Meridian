"""Adapts `questions` / `question_coverage` ORM rows. Coverage is a
toggle (row exists iff covered), not a history log."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.questions import Question, QuestionCoverage


async def list_questions(
    session: AsyncSession, user_id: uuid.UUID, category: str | None = None
) -> list[tuple[Question, bool]]:
    query = select(Question)
    if category:
        query = query.where(Question.category == category)
    query = query.order_by(Question.category, Question.order_index)

    questions = list((await session.execute(query)).scalars().all())

    covered_ids: set[int] = set()
    if questions:
        result = await session.execute(
            select(QuestionCoverage.question_id).where(QuestionCoverage.user_id == user_id)
        )
        covered_ids = set(result.scalars().all())

    return [(q, q.id in covered_ids) for q in questions]


async def toggle_coverage(session: AsyncSession, user_id: uuid.UUID, question_id: int) -> bool:
    """Returns the new covered state."""
    existing = (
        await session.execute(
            select(QuestionCoverage).where(
                QuestionCoverage.user_id == user_id, QuestionCoverage.question_id == question_id
            )
        )
    ).scalar_one_or_none()

    if existing is not None:
        await session.execute(
            delete(QuestionCoverage).where(QuestionCoverage.id == existing.id)
        )
        await session.commit()
        return False

    session.add(QuestionCoverage(user_id=user_id, question_id=question_id, covered_at=datetime.now()))
    await session.commit()
    return True


async def get_coverage_summary(session: AsyncSession, user_id: uuid.UUID) -> list[tuple[str, int, int]]:
    """(category, covered_count, total_count) per category, ordered by category."""
    totals_result = await session.execute(
        select(Question.category, func.count()).group_by(Question.category)
    )
    totals: dict[str, int] = dict(totals_result.all())  # type: ignore[arg-type]

    covered_result = await session.execute(
        select(Question.category, func.count())
        .join(QuestionCoverage, QuestionCoverage.question_id == Question.id)
        .where(QuestionCoverage.user_id == user_id)
        .group_by(Question.category)
    )
    covered: dict[str, int] = dict(covered_result.all())  # type: ignore[arg-type]

    return [(category, covered.get(category, 0), total) for category, total in sorted(totals.items())]
