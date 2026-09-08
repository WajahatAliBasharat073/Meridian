from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_session
from app.deps import get_current_user_id
from app.engines.block_lock import BlockLockedError
from app.engines.punctuality import SessionDelay, compute_punctuality
from app.engines.session_breakdown import (
    SessionEvent,
    SessionForBreakdown,
    compute_activity_breakdown,
    compute_pause_stats,
)
from app.repositories import sessions as sessions_repo
from app.schemas import (
    ActivityBreakdownOut,
    CategoryPunctualityOut,
    FocusSessionEventOut,
    FocusSessionOut,
    FocusSessionStart,
    FocusSessionUpdate,
    PunctualityOut,
    SessionBreakdownOut,
)

router = APIRouter(prefix="/api/focus-sessions", tags=["focus-sessions"])


def _to_out(s) -> FocusSessionOut:  # type: ignore[no-untyped-def]
    return FocusSessionOut(
        id=s.id,
        block_id=s.block_id,
        scheduled_start=s.scheduled_start,
        planned_minutes=s.planned_minutes,
        started_at=s.started_at,
        ended_at=s.ended_at,
        elapsed_seconds=s.elapsed_seconds,
        start_delay_minutes=s.start_delay_minutes,
        state=s.state,
        focus_rating=s.focus_rating,
    )


@router.get("/open", response_model=FocusSessionOut | None)
async def get_open(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> FocusSessionOut | None:
    s = await sessions_repo.get_open_session(session, user_id)
    return _to_out(s) if s else None


@router.get("/breakdown", response_model=SessionBreakdownOut)
async def breakdown(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
    days: int = 30,
) -> SessionBreakdownOut:
    """Per-activity pause/waste breakdown: how often each activity gets
    interrupted and how much time those pauses actually cost.

    Grouped by activity rather than category, so "Interview Prep — Coding"
    and "Interview Prep — Theory" are reported separately.
    """
    now = datetime.now(ZoneInfo(settings.timezone)).replace(tzinfo=None)
    since = now.date() - timedelta(days=days - 1)
    rows = await sessions_repo.list_sessions_with_events_since(session, user_id, since)

    for_breakdown = []
    for focus, activity, category, events in rows:
        stats = compute_pause_stats(
            [SessionEvent(event_type=e.event_type, occurred_at=e.occurred_at) for e in events],
            # Only an in-flight session gets its open pause closed at "now";
            # a finished one keeps its trail as recorded.
            now=now if focus.state in ("in_progress", "paused") else None,
        )
        for_breakdown.append(
            SessionForBreakdown(
                activity=activity,
                category=category,
                worked_seconds=focus.elapsed_seconds,
                pause_stats=stats,
            )
        )

    rolled = compute_activity_breakdown(for_breakdown)

    total_worked = sum(b.worked_seconds for b in rolled)
    total_paused = sum(b.paused_seconds for b in rolled)
    total_pauses = sum(b.pause_count for b in rolled)

    observations: list[str] = []
    if rolled:
        worst = rolled[0]
        # At least a full minute before calling it lost time — "lost the most
        # time to pauses — 0m" is true and useless.
        if worst.paused_seconds >= 60:
            observations.append(
                f"{worst.activity} lost the most time to pauses — "
                f"{worst.paused_seconds // 60}m across {worst.sessions} session(s)."
            )
        clean = [b for b in rolled if b.pause_count == 0 and b.sessions >= 2]
        if clean:
            observations.append(
                f"{clean[0].activity} ran without a single pause across {clean[0].sessions} sessions."
            )
    else:
        observations.append("No focus sessions recorded in this window yet.")

    return SessionBreakdownOut(
        window_days=days,
        total_sessions=len(for_breakdown),
        total_worked_minutes=total_worked // 60,
        total_paused_minutes=total_paused // 60,
        total_pause_count=total_pauses,
        by_activity=[
            ActivityBreakdownOut(
                activity=b.activity,
                category=b.category,
                sessions=b.sessions,
                worked_minutes=b.worked_seconds // 60,
                paused_minutes=b.paused_seconds // 60,
                pause_count=b.pause_count,
                avg_pauses_per_session=b.avg_pauses_per_session,
                paused_pct_of_session=b.paused_pct_of_session,
            )
            for b in rolled
        ],
        observations=observations,
    )


@router.post("", response_model=FocusSessionOut, status_code=status.HTTP_201_CREATED)
async def start(
    payload: FocusSessionStart,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> FocusSessionOut:
    """Records when work on a block *actually* started — this is the moment
    'Focus' was pressed, not the block's scheduled time."""
    now = datetime.now(ZoneInfo(settings.timezone)).replace(tzinfo=None)
    try:
        s = await sessions_repo.start_session(session, user_id, payload.block_id, now)
    except BlockLockedError as exc:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=str(exc)) from exc
    if s is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")
    return _to_out(s)


@router.patch("/{session_id}", response_model=FocusSessionOut)
async def update(
    session_id: int,
    payload: FocusSessionUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> FocusSessionOut:
    now = datetime.now(ZoneInfo(settings.timezone)).replace(tzinfo=None)
    ended_at = now if payload.state in ("completed", "abandoned") else None
    s = await sessions_repo.update_session(
        session,
        user_id,
        session_id,
        payload.state,
        payload.elapsed_seconds,
        ended_at,
        payload.focus_rating,
        payload.notes,
    )
    if s is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return _to_out(s)


@router.get("/punctuality", response_model=PunctualityOut)
async def punctuality(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
    days: int = 30,
) -> PunctualityOut:
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    since = today - timedelta(days=days - 1)
    rows = await sessions_repo.list_sessions_since(session, user_id, since)

    delays = [
        SessionDelay(
            category=category,
            hour_of_day=s.started_at.hour,
            start_delay_minutes=s.start_delay_minutes,
        )
        for s, category in rows
        if s.start_delay_minutes is not None
    ]
    report = compute_punctuality(delays)

    def cat(c) -> CategoryPunctualityOut | None:  # type: ignore[no-untyped-def]
        if c is None:
            return None
        return CategoryPunctualityOut(
            category=c.category,
            sessions=c.sessions,
            avg_delay_minutes=c.avg_delay_minutes,
            on_time_pct=c.on_time_pct,
        )

    return PunctualityOut(
        enough_data=report.enough_data,
        session_count=report.session_count,
        min_sessions_needed=report.min_sessions_needed,
        on_time_pct=report.on_time_pct,
        avg_delay_minutes=report.avg_delay_minutes,
        median_delay_minutes=report.median_delay_minutes,
        started_early_or_on_time=report.started_early_or_on_time,
        started_late=report.started_late,
        worst_category=cat(report.worst_category),
        best_category=cat(report.best_category),
        by_category=[c for c in (cat(x) for x in report.by_category) if c is not None],
        observations=report.observations,
    )


@router.get("/{session_id}/events", response_model=list[FocusSessionEventOut])
async def list_events(
    session_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[FocusSessionEventOut]:
    """Full audit trail for one session — every pause and resume, in order,
    with the work time accumulated at each point."""
    events = await sessions_repo.list_session_events(session, user_id, session_id)
    return [
        FocusSessionEventOut(
            id=e.id,
            session_id=e.session_id,
            event_type=e.event_type,
            occurred_at=e.occurred_at,
            elapsed_seconds_at_event=e.elapsed_seconds_at_event,
            note=e.note,
        )
        for e in events
    ]
