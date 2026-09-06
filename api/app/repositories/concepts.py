"""Adapts `concepts` / `concept_attempts` ORM rows — same shape as
app/repositories/problems.py, reusing the same repetition engine."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import AttemptFixture
from app.models.concepts import Concept, ConceptAttempt


async def list_concepts(
    session: AsyncSession,
    user_id: uuid.UUID,
    category: str | None = None,
    phase: str | None = None,
) -> list[tuple[Concept, str | None]]:
    query = select(Concept)
    if category:
        query = query.where(Concept.category == category)
    if phase:
        query = query.where(Concept.phase == phase)
    query = query.order_by(Concept.category, Concept.order_index)

    concepts = list((await session.execute(query)).scalars().all())

    concept_ids = [c.id for c in concepts]
    mastery_by_concept: dict[int, str] = {}
    if concept_ids:
        result = await session.execute(
            select(ConceptAttempt)
            .where(ConceptAttempt.user_id == user_id, ConceptAttempt.concept_id.in_(concept_ids))
            .order_by(ConceptAttempt.attempted_at)
        )
        for a in result.scalars().all():
            mastery_by_concept[a.concept_id] = a.mastery_level

    return [(c, mastery_by_concept.get(c.id)) for c in concepts]


async def get_latest_attempt_for_concept(
    session: AsyncSession, user_id: uuid.UUID, concept_id: int
) -> AttemptFixture | None:
    result = await session.execute(
        select(ConceptAttempt)
        .where(ConceptAttempt.user_id == user_id, ConceptAttempt.concept_id == concept_id)
        .order_by(ConceptAttempt.attempted_at.desc())
        .limit(1)
    )
    a = result.scalar_one_or_none()
    if a is None:
        return None
    return AttemptFixture(
        problem_id=a.concept_id,
        attempted_at=a.attempted_at,
        mastery_level=a.mastery_level,
        key_insight=a.notes,
    )


async def record_attempt(
    session: AsyncSession,
    user_id: uuid.UUID,
    concept_id: int,
    mastery_level: str,
    notes: str | None,
) -> ConceptAttempt:
    attempt = ConceptAttempt(
        user_id=user_id,
        concept_id=concept_id,
        attempted_at=datetime.now(),
        mastery_level=mastery_level,
        notes=notes,
    )
    session.add(attempt)
    await session.commit()
    await session.refresh(attempt)
    return attempt
