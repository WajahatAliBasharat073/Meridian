from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_session
from app.deps import get_current_user_id
from app.repositories.questions import (
    get_coverage_summary,
    get_module_summary,
    list_modules,
    list_questions,
    set_learning_status,
    set_mastery,
)
from app.schemas import (
    MASTERY_LADDER,
    CategoryCoverageOut,
    DailyTheoryPickOut,
    InterviewModuleOut,
    QuestionMasteryIn,
    QuestionMasteryOut,
    QuestionOut,
    QuestionStatusIn,
    QuestionStatusOut,
    QuestionSummaryOut,
    TheoryPaceOut,
    TheoryPaceProjectionOut,
)
from app.services import get_daily_theory_questions, get_theory_pace

router = APIRouter(prefix="/api/questions", tags=["questions"])


def _to_out(q, mastery: int, progress=None) -> QuestionOut:  # type: ignore[no-untyped-def]
    return QuestionOut(
        question_id=q.id,
        category=q.category,
        title=q.title,
        source=q.source,
        mastery=mastery,
        module_code=q.module_code,
        submodule=q.submodule,
        question_type=q.question_type,
        difficulty=q.difficulty,
        seniority=q.seniority,
        priority=q.priority,
        frequency=q.frequency,
        evidence=q.evidence,
        source_url=q.source_url,
        tests_for=q.tests_for,
        strong_signal=q.strong_signal,
        weak_signal=q.weak_signal,
        companies=list(q.companies or []),
        answer_dimensions=list(q.answer_dimensions or []),
        follow_ups=list(q.follow_ups or []),
        common_mistakes=list(q.common_mistakes or []),
        reference_solution=q.reference_solution,
        topic=q.topic,
        phase=q.phase,
        cognitive_level=q.cognitive_level,
        learning_status=progress.learning_status if progress else None,
        needs_review=bool(progress.needs_review) if progress else False,
    )


@router.get("", response_model=list[QuestionOut])
async def get_questions(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    category: str | None = None,
    module: str | None = None,
    priority: str | None = None,
    company: str | None = None,
    topic: str | None = None,
    phase: int | None = None,
    difficulty: str | None = None,
    learning_status: str | None = None,
    needs_review: bool | None = None,
    attempted: bool | None = None,
) -> list[QuestionOut]:
    """Filters combine with AND — topic=nlp_tasks&phase=3&learning_status=struggled
    returns only questions matching every condition given."""
    rows = await list_questions(
        session,
        user_id,
        category=category,
        module_code=module,
        priority=priority,
        company=company,
        topic=topic,
        phase=phase,
        difficulty=difficulty,
        learning_status=learning_status,
        needs_review=needs_review,
        attempted=attempted,
    )
    return [_to_out(q, mastery, progress) for q, mastery, progress in rows]


@router.put("/{question_id}/status", response_model=QuestionStatusOut)
async def set_question_status(
    question_id: int,
    payload: QuestionStatusIn,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> QuestionStatusOut:
    """Set this user's self-tag (already_know / easy / understood /
    solved_with_help / struggled / no_idea) and/or the revisit flag.

    Independent of the 0-7 mastery ladder — this never touches
    `question_progress.mastery` and never feeds the curriculum engine's
    mastery-fraction calculation. It exists purely for the learner's own
    filtering: "show me what I struggled with."
    """
    row = await set_learning_status(
        session, user_id, question_id, payload.learning_status, payload.needs_review
    )
    return QuestionStatusOut(learning_status=row.learning_status, needs_review=row.needs_review)


@router.get("/modules", response_model=list[InterviewModuleOut])
async def get_modules(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[InterviewModuleOut]:
    """OUTPUT 1 — the master map, with this user's readiness per module."""
    modules = await list_modules(session)
    counts = {code: (ready, total) for code, ready, total in await get_module_summary(session, user_id)}
    out: list[InterviewModuleOut] = []
    for m in modules:
        ready, total = counts.get(m.code, (0, 0))
        out.append(
            InterviewModuleOut(
                code=m.code,
                title=m.title,
                summary=m.summary,
                priority=m.priority,
                submodules=list(m.submodules or []),
                target_seniority=list(m.target_seniority or []),
                question_count=total,
                ready_count=ready,
                pct=round(100 * ready / total, 1) if total else 0.0,
            )
        )
    return out


@router.put("/{question_id}/mastery", response_model=QuestionMasteryOut)
async def put_question_mastery(
    question_id: int,
    payload: QuestionMasteryIn,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> QuestionMasteryOut:
    if payload.mastery not in MASTERY_LADDER:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "mastery must be 0-7")
    stored = await set_mastery(
        session, user_id, question_id, payload.mastery, payload.notes, payload.minutes
    )
    return QuestionMasteryOut(mastery=stored, label=MASTERY_LADDER[stored])


@router.get("/summary", response_model=QuestionSummaryOut)
async def get_questions_summary(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> QuestionSummaryOut:
    rows = await get_coverage_summary(session, user_id)
    by_category = [
        CategoryCoverageOut(
            category=cat,
            covered_count=ready,
            started_count=started,
            total_count=total,
            pct=round(100 * ready / total, 1) if total else 0.0,
        )
        for cat, ready, started, total in rows
    ]
    total_ready = sum(c.covered_count for c in by_category)
    total_started = sum(c.started_count for c in by_category)
    total_all = sum(c.total_count for c in by_category)
    return QuestionSummaryOut(
        by_category=by_category,
        covered_count=total_ready,
        started_count=total_started,
        total_count=total_all,
        pct=round(100 * total_ready / total_all, 1) if total_all else None,
    )


@router.get("/daily", response_model=list[DailyTheoryPickOut])
async def get_daily_theory(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> list[DailyTheoryPickOut]:
    """Today's recommended theory questions — by default 1 case study plus
    2 others, picked by what's due for reinforcement, then what's never
    been seen, spread across modules. Meant for the Interview Prep —
    Theory block on Today."""
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    rows = await get_daily_theory_questions(session, user_id, today)
    return [
        DailyTheoryPickOut(
            **_to_out(q, mastery).model_dump(),
            is_case_study=pick.is_case_study,
            pick_reason=pick.reason,
        )
        for q, mastery, pick in rows
    ]


@router.get("/pace", response_model=TheoryPaceOut)
async def get_pace(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> TheoryPaceOut:
    """How long clearing the theory backlog takes at your actual recorded
    pace, and the marginal cost/benefit of studying more or fewer per day.
    Refuses to project until at least 5 questions have logged real time —
    see MIN_QUESTIONS_FOR_INSIGHT in app/engines/theory_pace.py."""
    report = await get_theory_pace(session, user_id)
    return TheoryPaceOut(
        enough_data=report.enough_data,
        questions_with_data=report.questions_with_data,
        min_questions_needed=report.min_questions_needed,
        avg_minutes_per_question=report.avg_minutes_per_question,
        backlog_count=report.backlog_count,
        baseline_daily_count=report.baseline_daily_count,
        projections=[
            TheoryPaceProjectionOut(
                daily_count=p.daily_count,
                daily_minutes=p.daily_minutes,
                days_to_clear_backlog=p.days_to_clear_backlog,
                minutes_delta_vs_baseline=p.minutes_delta_vs_baseline,
                days_saved_vs_baseline=p.days_saved_vs_baseline,
            )
            for p in report.projections
        ],
    )
