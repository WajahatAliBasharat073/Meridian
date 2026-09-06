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
from app.repositories.concepts import list_concepts
from app.schemas import (
    AttemptResult,
    ConceptAttemptCreate,
    ConceptOut,
    ConceptResourceOut,
)
from app.services import submit_concept_attempt

router = APIRouter(prefix="/api/concepts", tags=["concepts"])


@router.get("", response_model=list[ConceptOut])
async def get_concepts(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    category: str | None = None,
    phase: str | None = None,
) -> list[ConceptOut]:
    rows = await list_concepts(session, user_id, category=category, phase=phase)
    return [
        ConceptOut(
            concept_id=concept.id,
            category=concept.category,
            title=concept.title,
            summary=concept.summary,
            resources=[ConceptResourceOut(**r) for r in concept.resources],
            phase=concept.phase,
            current_mastery=mastery,
        )
        for concept, mastery in rows
    ]


@router.post("/attempts", response_model=AttemptResult)
async def create_concept_attempt(
    payload: ConceptAttemptCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AttemptResult:
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    due_date_str, interval_days = await submit_concept_attempt(
        session, user_id, payload.concept_id, payload.mastery_level, payload.notes, today
    )
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    if interval_days:
        pretty_date = f"{due_date.day} {due_date.strftime('%b')}"
        message = f"Next review: {pretty_date}, {interval_days} day{'s' if interval_days != 1 else ''}."
    else:
        message = "No review scheduled yet — mark real progress to start one."
    return AttemptResult(next_review_due=due_date, interval_days=interval_days, message=message)
