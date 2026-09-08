"""Adapts `focus_sessions` ORM rows."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.block_lock import LOCK_THRESHOLD, BlockLockedError, is_block_locked
from app.models.core import TimeBlock
from app.models.sessions import FocusSession, FocusSessionEvent


def _record_event(
    session: AsyncSession,
    user_id: uuid.UUID,
    session_id: int,
    event_type: str,
    occurred_at: datetime,
    elapsed_seconds: int,
    note: str | None = None,
) -> None:
    """Appends one row to the audit trail. Called for every state change so
    the history can't drift from the session row it describes."""
    session.add(
        FocusSessionEvent(
            user_id=user_id,
            session_id=session_id,
            event_type=event_type,
            occurred_at=occurred_at,
            elapsed_seconds_at_event=elapsed_seconds,
            note=note,
        )
    )


async def get_open_session(session: AsyncSession, user_id: uuid.UUID) -> FocusSession | None:
    """The one session still running (or paused) for this user, if any."""
    result = await session.execute(
        select(FocusSession)
        .where(FocusSession.user_id == user_id, FocusSession.state.in_(["in_progress", "paused"]))
        .order_by(FocusSession.started_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def block_ids_with_any_session(
    session: AsyncSession, user_id: uuid.UUID, block_ids: list[int]
) -> set[int]:
    """Which of these blocks have ever had a focus session started on them
    — in any state, including abandoned. This is the "has ever engaged
    with it at all" signal the block-lock rule needs; a block's own
    status/actual_minutes can't answer that on their own."""
    if not block_ids:
        return set()
    rows = await session.execute(
        select(FocusSession.block_id)
        .where(FocusSession.user_id == user_id, FocusSession.block_id.in_(block_ids))
        .distinct()
    )
    return set(rows.scalars().all())


async def has_any_session_for_block(session: AsyncSession, user_id: uuid.UUID, block_id: int) -> bool:
    result = await session.execute(
        select(FocusSession.id)
        .where(FocusSession.user_id == user_id, FocusSession.block_id == block_id)
        .limit(1)
    )
    return result.first() is not None


async def start_session(
    session: AsyncSession, user_id: uuid.UUID, block_id: int, started_at: datetime
) -> FocusSession | None:
    """Records the moment work actually began on a block.

    Any previously open session is closed as 'abandoned' first — two
    concurrent focus sessions would make every downstream duration figure
    a guess about which one you were really doing.

    Raises BlockLockedError if most of the block's window has already
    passed with no focus session ever started on it — see
    app/engines/block_lock.py for why. Only enforced for today's blocks;
    a block from another date isn't something "now" can meaningfully lock.
    """
    block = await session.get(TimeBlock, block_id)
    if block is None or block.user_id != user_id:
        return None

    if block.date == started_at.date():
        already_engaged = await has_any_session_for_block(session, user_id, block_id)
        if is_block_locked(
            block.start_resolved, block.planned_minutes, started_at.time(), already_engaged
        ):
            raise BlockLockedError(
                f"{LOCK_THRESHOLD:.0%} of this block's window has passed without starting focus"
            )

    open_session = await get_open_session(session, user_id)
    if open_session is not None:
        open_session.state = "abandoned"
        open_session.ended_at = started_at

    delay: int | None = None
    if block.start_resolved is not None:
        scheduled_today = datetime.combine(started_at.date(), block.start_resolved)
        delay = round((started_at - scheduled_today).total_seconds() / 60)

    focus = FocusSession(
        user_id=user_id,
        block_id=block_id,
        scheduled_start=block.start_resolved,
        planned_minutes=block.planned_minutes,
        started_at=started_at,
        elapsed_seconds=0,
        start_delay_minutes=delay,
        state="in_progress",
    )
    session.add(focus)
    await session.flush()  # need focus.id before the event references it
    _record_event(session, user_id, focus.id, "started", started_at, 0)
    await session.commit()
    await session.refresh(focus)
    return focus


async def update_session(
    session: AsyncSession,
    user_id: uuid.UUID,
    session_id: int,
    state: str | None,
    elapsed_seconds: int | None,
    ended_at: datetime | None,
    focus_rating: int | None,
    notes: str | None,
) -> FocusSession | None:
    focus = await session.get(FocusSession, session_id)
    if focus is None or focus.user_id != user_id:
        return None

    previous_state = focus.state

    if state is not None:
        focus.state = state
    if elapsed_seconds is not None:
        focus.elapsed_seconds = elapsed_seconds
    if ended_at is not None:
        focus.ended_at = ended_at
    if focus_rating is not None:
        focus.focus_rating = focus_rating
    if notes is not None:
        focus.notes = notes

    # One event per real transition. Derived from the state change itself
    # rather than trusting the client to send a separate "log this" call,
    # so a dropped request can't silently leave a gap in the trail.
    if state is not None and state != previous_state:
        event_type = {
            "paused": "paused",
            "in_progress": "resumed",
            "completed": "completed",
            "abandoned": "abandoned",
        }.get(state)
        if event_type is not None:
            _record_event(
                session,
                user_id,
                focus.id,
                event_type,
                ended_at or datetime.now(),
                focus.elapsed_seconds,
                notes,
            )

    await session.commit()
    await session.refresh(focus)
    return focus


async def list_session_events(
    session: AsyncSession, user_id: uuid.UUID, session_id: int
) -> list[FocusSessionEvent]:
    result = await session.execute(
        select(FocusSessionEvent)
        .where(FocusSessionEvent.user_id == user_id, FocusSessionEvent.session_id == session_id)
        .order_by(FocusSessionEvent.occurred_at)
    )
    return list(result.scalars().all())


async def list_sessions_since(
    session: AsyncSession, user_id: uuid.UUID, since: date
) -> list[tuple[FocusSession, str]]:
    """(session, block category) pairs — the category comes from the block,
    which is where activity categorization actually lives."""
    result = await session.execute(
        select(FocusSession, TimeBlock.category)
        .join(TimeBlock, TimeBlock.id == FocusSession.block_id)
        .where(FocusSession.user_id == user_id, FocusSession.started_at >= datetime.combine(since, datetime.min.time()))
        .order_by(FocusSession.started_at)
    )
    return [(row[0], row[1]) for row in result.all()]


async def list_sessions_with_events_since(
    session: AsyncSession, user_id: uuid.UUID, since: date
) -> list[tuple[FocusSession, str, str, list[FocusSessionEvent]]]:
    """(session, block activity, block category, its events) for the window.

    Events are fetched in one query and grouped in memory rather than one
    query per session.
    """
    rows = (
        await session.execute(
            select(FocusSession, TimeBlock.activity, TimeBlock.category)
            .join(TimeBlock, TimeBlock.id == FocusSession.block_id)
            .where(
                FocusSession.user_id == user_id,
                FocusSession.started_at >= datetime.combine(since, datetime.min.time()),
            )
            .order_by(FocusSession.started_at)
        )
    ).all()

    session_ids = [r[0].id for r in rows]
    events_by_session: dict[int, list[FocusSessionEvent]] = {}
    if session_ids:
        events = (
            await session.execute(
                select(FocusSessionEvent)
                .where(FocusSessionEvent.session_id.in_(session_ids))
                .order_by(FocusSessionEvent.occurred_at)
            )
        ).scalars().all()
        for e in events:
            events_by_session.setdefault(e.session_id, []).append(e)

    return [(r[0], r[1], r[2], events_by_session.get(r[0].id, [])) for r in rows]
