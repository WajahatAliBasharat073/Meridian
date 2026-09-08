"""Endpoints for the topic gate: prove the structure, then the problems open.

Two stages, and the order is what makes it work — build (implement the
topic's required operations) then defend (closed-book questions, several of
them about the code just submitted). Pasted code passes stage one and fails
stage two, which is the only authorship check that actually holds up.

Everything that decides pass/fail lives in app/engines/topic_gate.py; the
LLM's judgement lives in app/grading.py. This router only sequences them and
records what happened.
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
from app.engines.topic_gate import (
    AttemptFixture,
    TopicGate,
    attempt_passed,
    build_passes,
    build_score,
    compute_gate,
    defend_score,
)
from app.grading import (
    GradingUnavailableError,
    check_build_submission,
    generate_defend_questions,
    grade_defend_answers,
    required_items,
)
from app.repositories import problems as problems_repo
from app.schemas import (
    BuildResultOut,
    BuildSubmissionIn,
    DefendGradeOut,
    DefendResultOut,
    DefendSubmissionIn,
    LearningEntryCreate,
    LearningEntryOut,
    OverrideIn,
    TopicGateOut,
    VerificationChecklistItemOut,
    VerificationChecklistOut,
)

router = APIRouter(prefix="/api/topics", tags=["verification"])


def _gate_out(gate: TopicGate) -> TopicGateOut:
    return TopicGateOut(
        topic=gate.topic,
        state=gate.state.value,
        problems_visible=gate.problems_visible,
        passed_at=gate.passed_at,
        expires_at=gate.expires_at,
        days_until_expiry=gate.days_until_expiry,
        attempt_count=gate.attempt_count,
        overridden=gate.overridden,
    )


def _fixtures(rows: list) -> list[AttemptFixture]:  # type: ignore[type-arg]
    return [
        AttemptFixture(
            topic=r.topic,
            started_at=r.started_at,
            passed=r.passed,
            passed_at=r.passed_at,
            override=r.override,
        )
        for r in rows
    ]


async def _now(settings: Settings) -> datetime:
    return datetime.now(ZoneInfo(settings.timezone)).replace(tzinfo=None)


def _entry_out(e) -> LearningEntryOut:  # type: ignore[no-untyped-def]
    return LearningEntryOut(
        id=e.id,
        topic=e.topic,
        kind=e.kind,
        title=e.title,
        url=e.url,
        body=e.body,
        created_at=e.created_at,
    )


def _checklist(guide, entries) -> list[VerificationChecklistItemOut]:  # type: ignore[no-untyped-def]
    """Curated items first, then anything the user added. Additive only —
    no path here drops a curated item, or the gate would be set by the
    person it is gating."""
    items = [
        VerificationChecklistItemOut(text=t, self_added=False)
        for t in required_items(guide.gate_requirements)
    ]
    for e in entries:
        if e.kind == "requirement":
            items.append(
                VerificationChecklistItemOut(text=e.title, self_added=True, entry_id=e.id)
            )
    return items


# A pasted transcript is the whole point of the `source` kind, so it gets a
# real budget rather than a token gesture — but still a bounded one, since a
# two-hour transcript would otherwise crowd out the code and the checklist.
_PER_ENTRY_CHARS = 6000
_STUDIED_TOTAL_CHARS = 16000


def _studied_context(entries) -> str:  # type: ignore[no-untyped-def]
    """The learning log as prose for the question generator.

    A `source` contributes whatever the user pasted — their summary, or a
    full transcript. Nothing here fetches the URL: the link is a bookmark,
    and the pasted text is the only content that exists. That is also why
    pasting the transcript materially improves the questions, and why a bare
    link barely changes them.
    """
    parts: list[str] = []
    for e in entries:
        body = (e.body or "")[:_PER_ENTRY_CHARS]
        truncated = " […truncated]" if e.body and len(e.body) > _PER_ENTRY_CHARS else ""
        if e.kind == "source":
            head = f"[studied from] {e.title}" + (f" ({e.url})" if e.url else "")
            parts.append(
                head
                + (
                    f"\n  what they pasted from it: {body}{truncated}"
                    if body
                    else "\n  (link only — no summary or transcript pasted, so this says "
                    "nothing about what was actually learned)"
                )
            )
        elif e.kind == "note":
            parts.append(f"[their note] {e.title}" + (f": {body}{truncated}" if body else ""))
        elif e.kind == "snippet":
            parts.append(f"[code they kept] {e.title}\n```\n{body}{truncated}\n```")
        elif e.kind == "requirement":
            parts.append(f"[they added this requirement themselves] {e.title}")
    out = "\n\n".join(parts)
    return out[:_STUDIED_TOTAL_CHARS]


@router.get("/{topic}/learning", response_model=list[LearningEntryOut])
async def list_learning(
    topic: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[LearningEntryOut]:
    entries = await problems_repo.list_learning_entries(session, user_id, topic)
    return [_entry_out(e) for e in entries]


@router.post(
    "/{topic}/learning", response_model=LearningEntryOut, status_code=status.HTTP_201_CREATED
)
async def add_learning(
    topic: str,
    payload: LearningEntryCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> LearningEntryOut:
    """Log a source (with its summary or transcript pasted in), a note, a
    code snippet, or a requirement you are adding to this topic yourself."""
    guide = await problems_repo.get_topic_guide(session, topic)
    if guide is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown topic")
    entry = await problems_repo.create_learning_entry(
        session,
        user_id,
        topic,
        payload.kind,
        payload.title.strip(),
        (payload.url or "").strip() or None,
        (payload.body or "").strip() or None,
        await _now(settings),
    )
    return _entry_out(entry)


@router.delete("/{topic}/learning/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_learning(
    topic: str,
    entry_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> None:
    if not await problems_repo.delete_learning_entry(session, user_id, entry_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")


@router.get("/gates", response_model=list[TopicGateOut])
async def get_gates(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> list[TopicGateOut]:
    """Gate state for every topic that has a guide."""
    now = await _now(settings)
    attempts = _fixtures(await problems_repo.get_verification_attempts(session, user_id))
    guides = await problems_repo.list_topic_guides(session)
    return [_gate_out(compute_gate(g.topic, attempts, now)) for g in guides]


@router.get("/{topic}/checklist", response_model=VerificationChecklistOut)
async def get_checklist(
    topic: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> VerificationChecklistOut:
    """What this topic asks you to have implemented — its guide's own types
    and operations, so the bar is visible before you start."""
    guide = await problems_repo.get_topic_guide(session, topic)
    if guide is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown topic")
    entries = await problems_repo.list_learning_entries(session, user_id, topic)
    items = _checklist(guide, entries)
    return VerificationChecklistOut(
        topic=guide.topic,
        display_name=guide.display_name,
        required=[i.text for i in items],
        items=items,
    )


@router.post("/{topic}/verify/build", response_model=BuildResultOut)
async def submit_build(
    topic: str,
    payload: BuildSubmissionIn,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> BuildResultOut:
    """Stage 1: check the submission covers the topic's checklist, and if it
    does, generate the closed-book questions for stage 2."""
    guide = await problems_repo.get_topic_guide(session, topic)
    if guide is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown topic")

    entries = await problems_repo.list_learning_entries(session, user_id, topic)
    required = [i.text for i in _checklist(guide, entries)]
    studied = _studied_context(entries)
    now = await _now(settings)
    attempt = await problems_repo.create_verification_attempt(session, user_id, topic, now)

    try:
        coverage = check_build_submission(
            settings, guide.display_name, required, payload.code, payload.notes
        )
    except GradingUnavailableError as exc:
        # Nothing was assessed, so nothing is recorded as pass or fail — the
        # attempt is abandoned rather than left looking like a failure the
        # user earned.
        attempt.stage = "abandoned"
        await problems_repo.save_verification_attempt(session, attempt)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc

    score = build_score(len(coverage.covered), coverage.required_count)
    attempt.code_submission = payload.code
    attempt.notes_submission = payload.notes
    attempt.coverage = {
        "covered": coverage.covered,
        "missing": coverage.missing,
        "concerns": coverage.concerns,
        "notes": coverage.notes,
        "required": required,
    }
    attempt.build_score = score

    questions_out: list[str] = []
    if build_passes(score):
        try:
            generated = generate_defend_questions(
                settings,
                guide.display_name,
                guide.must_know,
                guide.pitfalls,
                payload.code,
                required=required,
                studied=studied,
            )
        except GradingUnavailableError as exc:
            attempt.stage = "abandoned"
            await problems_repo.save_verification_attempt(session, attempt)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
            ) from exc
        attempt.questions = [
            {"question": q.question, "kind": q.kind, "expects": q.expects} for q in generated
        ]
        # `expects` is the grading key — never sent to the client, or the
        # closed-book stage is open-book.
        questions_out = [q.question for q in generated]
        attempt.stage = "defend"
    else:
        # Nothing to defend against a submission that missed the structure.
        attempt.stage = "failed"
        attempt.passed = False

    await problems_repo.save_verification_attempt(session, attempt)
    return BuildResultOut(
        attempt_id=attempt.id,
        covered=coverage.covered,
        missing=coverage.missing,
        concerns=coverage.concerns,
        notes=coverage.notes,
        build_score=score,
        build_passed=build_passes(score),
        questions=questions_out,
    )


@router.post("/{topic}/verify/{attempt_id}/defend", response_model=DefendResultOut)
async def submit_defend(
    topic: str,
    attempt_id: int,
    payload: DefendSubmissionIn,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DefendResultOut:
    """Stage 2: grade the closed-book answers and settle the gate."""
    attempt = await problems_repo.get_verification_attempt(session, user_id, attempt_id)
    if attempt is None or attempt.topic != topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    if attempt.stage != "defend":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This attempt is not awaiting answers.",
        )

    guide = await problems_repo.get_topic_guide(session, topic)
    if guide is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown topic")

    questions = list(attempt.questions or [])
    # Pad rather than reject: a blank answer is an answer, and it grades as
    # wrong. Rejecting the submission would let a hard question be dodged by
    # simply not filling it in.
    answers = list(payload.answers) + [""] * max(0, len(questions) - len(payload.answers))
    answers = answers[: len(questions)]

    try:
        graded = grade_defend_answers(settings, guide.display_name, questions, answers)
    except GradingUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc

    verdicts = [g.verdict for g in graded]
    d_score = defend_score(verdicts)
    b_score = attempt.build_score or 0.0
    passed = attempt_passed(b_score, d_score)

    now = await _now(settings)
    attempt.answers = answers
    attempt.grades = [{"verdict": g.verdict, "feedback": g.feedback} for g in graded]
    attempt.defend_score = d_score
    attempt.passed = passed
    attempt.passed_at = now if passed else None
    attempt.stage = "passed" if passed else "failed"
    attempt.focus_losses = payload.focus_losses
    attempt.focus_lost_seconds = payload.focus_lost_seconds
    attempt.duration_seconds = payload.duration_seconds
    await problems_repo.save_verification_attempt(session, attempt)

    all_attempts = _fixtures(await problems_repo.get_verification_attempts(session, user_id))
    gate = compute_gate(topic, all_attempts, now)

    return DefendResultOut(
        attempt_id=attempt.id,
        grades=[
            DefendGradeOut(
                question=str(q.get("question", "")),
                answer=a,
                verdict=g.verdict,
                feedback=g.feedback,
            )
            for q, a, g in zip(questions, answers, graded, strict=False)
        ],
        defend_score=d_score,
        passed=passed,
        gate=_gate_out(gate),
        focus_losses=payload.focus_losses,
        focus_lost_seconds=payload.focus_lost_seconds,
    )


@router.post("/{topic}/override", response_model=TopicGateOut)
async def override_gate(
    topic: str,
    payload: OverrideIn,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TopicGateOut:
    """The escape hatch: open the problems without verifying.

    Recorded as an attempt with `override=True`, so the topic carries a
    permanent "unlocked without verifying" mark. A gate with no exit gets
    resented and abandoned; an exit that costs an honest mark does not.
    """
    guide = await problems_repo.get_topic_guide(session, topic)
    if guide is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown topic")

    now = await _now(settings)
    attempt = await problems_repo.create_verification_attempt(session, user_id, topic, now)
    attempt.override = True
    attempt.override_reason = payload.reason
    attempt.stage = "override"
    await problems_repo.save_verification_attempt(session, attempt)

    all_attempts = _fixtures(await problems_repo.get_verification_attempts(session, user_id))
    return _gate_out(compute_gate(topic, all_attempts, now))
