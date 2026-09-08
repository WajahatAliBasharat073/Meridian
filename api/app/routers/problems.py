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
from app.engines.topic_gate import AttemptFixture as GateAttemptFixture
from app.engines.topic_gate import compute_gate
from app.repositories.problems import (
    get_verification_attempts,
    list_problems,
    list_topic_guides,
)
from app.schemas import ProblemOut, TopicGateOut, TopicGuideOut, TopicSectionOut

router = APIRouter(prefix="/api/problems", tags=["problems"])

# Order within a topic: easiest first, then by title. Deliberately not the
# source sheet's day numbering — the plan is "learn the structure, then work
# through its problems", so a topic is one list, not a pile of day buckets.
_DIFFICULTY_RANK = {"Easy": 0, "Medium": 1, "Hard": 2}


def _to_out(  # type: ignore[no-untyped-def]
    problem,
    scheduled_today: bool,
    progress,
) -> ProblemOut:
    return ProblemOut(
        problem_id=problem.id,
        lc_number=problem.lc_number,
        title=problem.title,
        slug=problem.slug,
        url=problem.url,
        pattern=problem.pattern,
        topic=problem.topic,
        difficulty=problem.difficulty,
        source=problem.source,
        is_neetcode150=problem.is_neetcode150,
        is_blind75=problem.is_blind75,
        companies=list(problem.companies or []),
        company_extra_count=problem.company_extra_count,
        current_mastery=progress.mastery_level if progress else None,
        last_solve_method=progress.solve_method if progress else None,
        attempt_count=progress.attempt_count if progress else 0,
        last_attempted_at=progress.last_attempted_at if progress else None,
        last_minutes=progress.minutes if progress else None,
        last_key_insight=progress.key_insight if progress else None,
        last_notes=progress.notes if progress else None,
        is_scheduled_today=scheduled_today,
    )


@router.get("", response_model=list[ProblemOut])
async def get_problems(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
    pattern: str | None = None,
    difficulty: str | None = None,
) -> list[ProblemOut]:
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    rows = await list_problems(session, user_id, pattern=pattern, difficulty=difficulty)
    return [
        _to_out(problem, scheduled_date == today, progress)
        for problem, scheduled_date, progress in rows
    ]


@router.get("/by-topic", response_model=list[TopicSectionOut])
async def get_problems_by_topic(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> list[TopicSectionOut]:
    """The whole bank as topic sections: what to learn first, then that
    topic's problems, with per-topic totals and what's left.

    One request rather than one per topic — the page shows every section at
    once, and 369 problems is small enough that paging them would cost more
    than it saves.
    """
    now = datetime.now(ZoneInfo(settings.timezone)).replace(tzinfo=None)
    today = now.date()
    rows = await list_problems(session, user_id)
    guides = await list_topic_guides(session)
    gate_attempts = [
        GateAttemptFixture(
            topic=a.topic,
            started_at=a.started_at,
            passed=a.passed,
            passed_at=a.passed_at,
            override=a.override,
        )
        for a in await get_verification_attempts(session, user_id)
    ]

    grouped: dict[str, list[ProblemOut]] = {}
    for problem, scheduled_date, progress in rows:
        if problem.topic is None:
            continue
        grouped.setdefault(problem.topic, []).append(
            _to_out(problem, scheduled_date == today, progress)
        )

    sections: list[TopicSectionOut] = []
    for guide in guides:
        items = grouped.pop(guide.topic, [])
        items.sort(key=lambda p: (_DIFFICULTY_RANK.get(p.difficulty, 9), p.title))
        gate = compute_gate(guide.topic, gate_attempts, now)

        solved = sum(1 for p in items if p.attempt_count > 0 and p.last_solve_method != "not_solved")
        unaided = sum(
            1
            for p in items
            if p.last_solve_method is not None
            and p.last_solve_method
            not in ("not_solved", "after_hint", "after_editorial", "after_video", "brute_force_only")
        )
        by_difficulty: dict[str, int] = {}
        for p in items:
            by_difficulty[p.difficulty] = by_difficulty.get(p.difficulty, 0) + 1

        # Companies ranked by how many of this topic's problems name them —
        # "who asks this topic most" is the useful reading, not an A-Z list.
        tally: dict[str, int] = {}
        for p in items:
            for c in p.companies:
                tally[c] = tally.get(c, 0) + 1

        sections.append(
            TopicSectionOut(
                topic=guide.topic,
                display_name=guide.display_name,
                seq=guide.seq,
                guide=TopicGuideOut(
                    topic=guide.topic,
                    display_name=guide.display_name,
                    seq=guide.seq,
                    one_liner=guide.one_liner,
                    learn_first=guide.learn_first,
                    types=guide.types,
                    operations=guide.operations,
                    must_know=guide.must_know,
                    pitfalls=guide.pitfalls,
                    needs_revision=guide.needs_revision,
                ),
                # The counts are always honest; the list itself is withheld
                # while the topic is locked. Sending the problems and hiding
                # them client-side would make the gate a suggestion.
                problems=items if gate.problems_visible else [],
                total=len(items),
                solved=solved,
                unaided=unaided,
                remaining=len(items) - solved,
                by_difficulty=by_difficulty,
                companies=sorted(tally, key=lambda c: (-tally[c], c)),
                gate=TopicGateOut(
                    topic=gate.topic,
                    state=gate.state.value,
                    problems_visible=gate.problems_visible,
                    passed_at=gate.passed_at,
                    expires_at=gate.expires_at,
                    days_until_expiry=gate.days_until_expiry,
                    attempt_count=gate.attempt_count,
                    overridden=gate.overridden,
                ),
            )
        )

    # A topic with problems but no guide yet would otherwise vanish from the
    # page entirely — surface it rather than silently dropping it.
    for topic, items in grouped.items():
        items.sort(key=lambda p: (_DIFFICULTY_RANK.get(p.difficulty, 9), p.title))
        solved = sum(1 for p in items if p.attempt_count > 0 and p.last_solve_method != "not_solved")
        sections.append(
            TopicSectionOut(
                topic=topic,
                display_name=topic.replace("_", " ").title(),
                seq=999,
                guide=None,
                problems=items,
                total=len(items),
                solved=solved,
                remaining=len(items) - solved,
            )
        )

    return sections
