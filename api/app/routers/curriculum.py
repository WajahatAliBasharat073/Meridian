"""Curriculum endpoints: where the learner is, why, and whether the
curriculum itself is sound.

`/explain` exists because the old picker was impossible to debug -- it
returned three questions and no account of itself, so "why on earth is it
asking me this?" had no answer short of reading the ranking code. Every
selection now carries reason codes, and the rejections are inspectable
too.
"""

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
from app.engines.curriculum import build_daily_plan, build_learner_state
from app.engines.placement import (
    CONFIDENT_AT,
    estimate_from_history,
    estimate_from_probes,
    select_probe_questions,
)
from app.repositories import curriculum as curriculum_repo
from app.schemas import (
    CurriculumStateOut,
    PlacementApplyIn,
    PlacementOut,
    PlacementProbeOut,
    SelectionExplanationOut,
    TopicStateOut,
)

router = APIRouter(prefix="/api/curriculum", tags=["curriculum"])


async def _load(session: AsyncSession, user_id: uuid.UUID):  # type: ignore[no-untyped-def]
    topics = await curriculum_repo.get_topic_fixtures(session)
    questions = await curriculum_repo.get_curriculum_questions(session)
    progress = await curriculum_repo.get_progress_fixtures(session, user_id)
    empty = await curriculum_repo.get_empty_topics(session)
    return topics, questions, progress, empty


def _today(settings: Settings) -> datetime:
    return datetime.now(ZoneInfo(settings.timezone)).replace(tzinfo=None)


@router.get("/state", response_model=CurriculumStateOut)
async def get_state(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> CurriculumStateOut:
    """The learning frontier: what is mastered, open, and still locked."""
    topics, questions, progress, empty = await _load(session, user_id)
    if not topics:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The curriculum graph has not been seeded. Run scripts.ingest_curriculum_graph.",
        )
    frontier = await curriculum_repo.get_frontier(session, user_id)
    state = build_learner_state(
        topics, questions, progress, empty, frontier.current_topic if frontier else None
    )
    names = {t.slug: t for t in topics}
    return CurriculumStateOut(
        current_topic=state.current_topic,
        current_topic_name=(
            names[state.current_topic].name if state.current_topic in names else None
        ),
        reached_phase=state.reached_phase,
        placement_status=frontier.placement_status if frontier else "UNASSESSED",
        topics=[
            TopicStateOut(
                slug=t.slug,
                name=t.name,
                phase=t.phase,
                state=state.topic_states.get(t.slug, "LOCKED"),
                mastery=round(state.topic_mastery.get(t.slug, 0.0), 2),
                prereqs=list(t.prereqs),
                has_content=t.slug not in empty,
            )
            for t in topics
        ],
    )


@router.get("/explain", response_model=list[SelectionExplanationOut])
async def explain_today(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
    include_rejections: bool = False,
) -> list[SelectionExplanationOut]:
    """Why today's questions were chosen, with reason codes.

    Set `include_rejections` to also see a sample of what was excluded and
    on which rule -- the fastest way to find a mis-classified question.
    """
    topics, questions, progress, empty = await _load(session, user_id)
    frontier = await curriculum_repo.get_frontier(session, user_id)
    plan = build_daily_plan(
        topics,
        questions,
        progress,
        _today(settings).date(),
        current_topic=frontier.current_topic if frontier else None,
        empty_topics=empty,
    )
    out = [
        SelectionExplanationOut(
            question_id=s.question_id,
            selected=True,
            slot=s.slot,
            topic=s.topic,
            phase=s.phase,
            score=s.score,
            reason_codes=[r.value for r in s.reasons],
        )
        for s in plan.selections
    ]
    if include_rejections:
        out.extend(
            SelectionExplanationOut(
                question_id=r.question_id,
                selected=False,
                slot=None,
                topic=None,
                phase=None,
                score=None,
                reason_codes=[c.value for c in r.reasons],
            )
            for r in plan.sample_rejections
        )
    return out


@router.get("/placement/probes", response_model=list[PlacementProbeOut])
async def placement_probes(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[PlacementProbeOut]:
    """A short probe set spanning P0-P5.

    Deliberately not the whole bank: the objective is the highest reliable
    starting point, which a couple of dozen questions can establish.
    """
    topics, questions, _, _ = await _load(session, user_id)
    probes = select_probe_questions(topics, questions)
    phase_of = {t.slug: t.phase for t in topics}
    return [
        PlacementProbeOut(
            question_id=p.question_id,
            topic=p.topic or "",
            phase=phase_of.get(p.topic or "", 0),
            cognitive_level=p.cognitive_level,
        )
        for p in probes
    ]


@router.get("/placement", response_model=PlacementOut)
async def get_placement(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> PlacementOut:
    """Estimate placement from existing history, without asking anything.

    An existing user already has months of `question_progress`; making
    them sit an assessment to recover what the app already knows would be
    a poor trade.
    """
    topics, questions, progress, empty = await _load(session, user_id)
    est = estimate_from_history(topics, questions, progress, empty)
    frontier = await curriculum_repo.get_frontier(session, user_id)
    return PlacementOut(
        phase=est.phase,
        confidence=est.confidence,
        confident=est.confidence >= CONFIDENT_AT,
        method=est.method,
        clamped_by_prerequisites=est.clamped,
        evidence={f"P{k}": v for k, v in est.evidence.items()},
        known_topics=list(est.known_topics),
        status=frontier.placement_status if frontier else "UNASSESSED",
    )


@router.post("/placement", response_model=PlacementOut)
async def apply_placement(
    payload: PlacementApplyIn,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> PlacementOut:
    """Record a placement, from probe answers or from history."""
    topics, questions, progress, empty = await _load(session, user_id)
    if payload.answers:
        probes = select_probe_questions(topics, questions)
        est = estimate_from_probes(topics, probes, payload.answers)
    else:
        est = estimate_from_history(topics, questions, progress, empty)

    now = _today(settings)
    # Land on the first open topic of the estimated phase, never past it.
    state = build_learner_state(topics, questions, progress, empty)
    candidates = [
        t for t in topics if t.phase == est.phase and t.gated
        and state.topic_states.get(t.slug) != "LOCKED"
    ]
    current = candidates[0].slug if candidates else state.current_topic

    await curriculum_repo.upsert_frontier(
        session,
        user_id,
        now,
        current_topic=current,
        placement_status="PLACED",
        placement_phase=est.phase,
        placement_confidence=est.confidence,
        placed_at=now,
        placement_method=est.method,
    )
    return PlacementOut(
        phase=est.phase,
        confidence=est.confidence,
        confident=est.confidence >= CONFIDENT_AT,
        method=est.method,
        clamped_by_prerequisites=est.clamped,
        evidence={f"P{k}": v for k, v in est.evidence.items()},
        known_topics=list(est.known_topics),
        status="PLACED",
    )
