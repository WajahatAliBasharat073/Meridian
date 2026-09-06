from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.repositories.questions import get_coverage_summary, list_questions, toggle_coverage
from app.schemas import CategoryCoverageOut, QuestionCoverageOut, QuestionOut, QuestionSummaryOut

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("", response_model=list[QuestionOut])
async def get_questions(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    category: str | None = None,
) -> list[QuestionOut]:
    rows = await list_questions(session, user_id, category=category)
    return [
        QuestionOut(
            question_id=q.id,
            category=q.category,
            title=q.title,
            source=q.source,
            covered=covered,
        )
        for q, covered in rows
    ]


@router.post("/{question_id}/toggle", response_model=QuestionCoverageOut)
async def toggle_question_coverage(
    question_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> QuestionCoverageOut:
    covered = await toggle_coverage(session, user_id, question_id)
    return QuestionCoverageOut(covered=covered)


@router.get("/summary", response_model=QuestionSummaryOut)
async def get_questions_summary(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> QuestionSummaryOut:
    rows = await get_coverage_summary(session, user_id)
    by_category = [
        CategoryCoverageOut(
            category=cat,
            covered_count=covered,
            total_count=total,
            pct=round(100 * covered / total, 1) if total else 0.0,
        )
        for cat, covered, total in rows
    ]
    total_covered = sum(c.covered_count for c in by_category)
    total_all = sum(c.total_count for c in by_category)
    return QuestionSummaryOut(
        by_category=by_category,
        covered_count=total_covered,
        total_count=total_all,
        pct=round(100 * total_covered / total_all, 1) if total_all else None,
    )
