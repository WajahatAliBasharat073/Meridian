"""Focus sessions — when work on a block *actually* started and ended,
as distinct from when it was scheduled to.

`time_blocks` holds the plan (start_spec/end_spec resolved to
start_resolved/end_resolved). This table holds what really happened, so
"scheduled 17:05, started 17:34" is a recorded fact rather than something
inferred after the fact. Punctuality analytics read the gap between the
two; nothing here is derived or guessed."""

import uuid
from datetime import datetime
from datetime import time as time_

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FocusSession(Base):
    __tablename__ = "focus_sessions"
    __table_args__ = (
        CheckConstraint(
            "state IN ('in_progress','paused','completed','abandoned')",
            name="ck_focus_sessions_state",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    block_id: Mapped[int] = mapped_column(ForeignKey("time_blocks.id"), index=True)

    # Copied from the block at start time so a later reschedule of the
    # block can't silently rewrite history for an already-recorded session.
    scheduled_start: Mapped[time_ | None] = mapped_column(nullable=True)
    planned_minutes: Mapped[int] = mapped_column(Integer)

    started_at: Mapped[datetime] = mapped_column(index=True)
    ended_at: Mapped[datetime | None] = mapped_column(nullable=True)
    elapsed_seconds: Mapped[int] = mapped_column(Integer, default=0)

    # Positive = started after the scheduled time. Stored rather than
    # recomputed so it survives the block being edited afterwards.
    start_delay_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    state: Mapped[str] = mapped_column(String, default="in_progress")
    focus_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)


class FocusSessionEvent(Base):
    """Append-only audit trail for one focus session: every start, pause,
    resume, extension and finish, with the wall-clock time it happened and
    how much work time had accumulated by then.

    Kept separate from `focus_sessions` on purpose — that table holds the
    session's current state, this one holds the history that produced it.
    Overwriting a single `paused_at` column would lose the second, third
    and fourth pause of a session, which is exactly the detail needed to
    see *when* focus actually breaks down."""

    __tablename__ = "focus_session_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('started','paused','resumed','extended','shortened','completed','abandoned')",
            name="ck_focus_session_events_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("focus_sessions.id"), index=True)
    event_type: Mapped[str] = mapped_column(String)
    occurred_at: Mapped[datetime] = mapped_column(index=True)
    # Accumulated work seconds at the moment of the event — lets a pause's
    # duration be derived from the next resume without storing a duration
    # that could disagree with the timestamps.
    elapsed_seconds_at_event: Mapped[int] = mapped_column(Integer, default=0)
    note: Mapped[str | None] = mapped_column(String, nullable=True)
