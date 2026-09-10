"""Adapts `curriculum_topics` / `questions` / `question_progress` into the
plain fixtures the curriculum engine takes.

The engine never sees a Session or an ORM row -- same rule as every other
engine here. This module is the only place that knows both shapes.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.curriculum import (
    CurriculumQuestion,
    ProgressFixture,
    TopicFixture,
)
from app.models.questions import CurriculumTopic, LearnerFrontier, Question, QuestionProgress


async def get_topic_fixtures(session: AsyncSession) -> list[TopicFixture]:
    rows = (
        await session.execute(select(CurriculumTopic).order_by(CurriculumTopic.order_index))
    ).scalars()
    return [
        TopicFixture(
            slug=t.slug,
            name=t.name,
            phase=t.phase,
            prereqs=tuple(t.prereqs or []),
            gated=t.gated,
            order_index=t.order_index,
        )
        for t in rows
    ]


async def get_curriculum_questions(session: AsyncSession) -> list[CurriculumQuestion]:
    rows = (await session.execute(select(Question))).scalars()
    return [
        CurriculumQuestion(
            question_id=q.id,
            topic=q.topic,
            phase=q.phase,
            axis=q.axis or "knowledge",
            cognitive_level=q.cognitive_level if q.cognitive_level is not None else 2,
            primary_format=q.primary_format or "concept",
            preview=bool(q.preview),
            # `priority` is *interview* priority. Passed through under a
            # name that says so, because conflating it with curriculum
            # position is the bug this rebuild exists to fix.
            interview_priority=q.priority,
        )
        for q in rows
    ]


async def get_progress_fixtures(
    session: AsyncSession, user_id: uuid.UUID
) -> dict[int, ProgressFixture]:
    rows = (
        await session.execute(
            select(QuestionProgress).where(QuestionProgress.user_id == user_id)
        )
    ).scalars()
    return {
        p.question_id: ProgressFixture(
            question_id=p.question_id,
            mastery=p.mastery,
            last_rated=p.updated_at.date() if p.updated_at else None,
        )
        for p in rows
    }


async def get_empty_topics(session: AsyncSession) -> frozenset[str]:
    """Gated topics with no knowledge questions.

    These are handed to the engine as already-satisfied so a content gap
    never walls off the curriculum (invariant 7). The gap itself is
    reported by scripts/validate_curriculum.py rather than silently
    swallowed here.
    """
    topics = {
        t.slug for t in (await session.execute(select(CurriculumTopic))).scalars() if t.gated
    }
    with_content = {
        row[0]
        for row in (
            await session.execute(
                select(Question.topic).where(
                    Question.axis == "knowledge", Question.topic.is_not(None)
                )
            )
        ).all()
    }
    return frozenset(topics - with_content)


async def get_frontier(session: AsyncSession, user_id: uuid.UUID) -> LearnerFrontier | None:
    return (
        await session.execute(
            select(LearnerFrontier).where(LearnerFrontier.user_id == user_id)
        )
    ).scalar_one_or_none()


async def upsert_frontier(
    session: AsyncSession, user_id: uuid.UUID, now: datetime, **fields: object
) -> LearnerFrontier:
    row = await get_frontier(session, user_id)
    if row is None:
        row = LearnerFrontier(user_id=user_id, updated_at=now)
        session.add(row)
    for k, v in fields.items():
        setattr(row, k, v)
    row.updated_at = now
    await session.commit()
    await session.refresh(row)
    return row
