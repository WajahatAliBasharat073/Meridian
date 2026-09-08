"""Pure functions: turn a focus session's event trail into pause/waste
figures, and roll those up per activity.

Paused time is *derived* from the paired pause→resume timestamps rather
than stored as its own column. One number kept in two places drifts; the
event trail is the source of truth, so a pause that was never resumed
(app closed mid-pause) is visible as exactly that instead of silently
inflating a stored total."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

PAUSE = "paused"
RESUME = "resumed"
TERMINAL = ("completed", "abandoned")


@dataclass(frozen=True)
class SessionEvent:
    event_type: str
    occurred_at: datetime


@dataclass(frozen=True)
class PauseStats:
    pause_count: int
    paused_seconds: int
    # A pause with no matching resume — still paused, or the session ended
    # while paused. Reported rather than folded into paused_seconds, since
    # its true length isn't known.
    unresolved_pause: bool


def compute_pause_stats(events: list[SessionEvent], now: datetime | None = None) -> PauseStats:
    """Pairs each `paused` with the next `resumed` (or a terminal event).

    `now` closes an open pause for a session that is still running; without
    it an open pause contributes nothing but is flagged.
    """
    ordered = sorted(events, key=lambda e: e.occurred_at)

    pause_count = 0
    paused_seconds = 0
    unresolved = False
    pause_started: datetime | None = None

    for e in ordered:
        if e.event_type == PAUSE:
            # Two pauses in a row shouldn't happen, but if they do, keep the
            # first (earliest) open pause rather than losing the interval.
            if pause_started is None:
                pause_started = e.occurred_at
                pause_count += 1
        elif e.event_type == RESUME and pause_started is not None:
            paused_seconds += max(0, int((e.occurred_at - pause_started).total_seconds()))
            pause_started = None
        elif e.event_type in TERMINAL and pause_started is not None:
            # Session finished while paused — the pause ends there.
            paused_seconds += max(0, int((e.occurred_at - pause_started).total_seconds()))
            pause_started = None

    if pause_started is not None:
        if now is not None:
            paused_seconds += max(0, int((now - pause_started).total_seconds()))
        else:
            unresolved = True

    return PauseStats(pause_count=pause_count, paused_seconds=paused_seconds, unresolved_pause=unresolved)


@dataclass(frozen=True)
class SessionForBreakdown:
    """One recorded session plus the block identity it belongs to."""

    activity: str
    category: str
    worked_seconds: int
    pause_stats: PauseStats


@dataclass(frozen=True)
class ActivityBreakdown:
    activity: str
    category: str
    sessions: int
    worked_seconds: int
    paused_seconds: int
    pause_count: int
    avg_pauses_per_session: float
    # Paused time as a share of the time the session was open at all.
    paused_pct_of_session: float | None


def compute_activity_breakdown(sessions: list[SessionForBreakdown]) -> list[ActivityBreakdown]:
    """Grouped by activity, not category — "Interview Prep — Coding" and
    "Interview Prep — Theory" are the same category but different work, and
    collapsing them would hide which one actually gets interrupted."""
    grouped: dict[str, list[SessionForBreakdown]] = {}
    for s in sessions:
        grouped.setdefault(s.activity, []).append(s)

    out: list[ActivityBreakdown] = []
    for activity, group in grouped.items():
        worked = sum(s.worked_seconds for s in group)
        paused = sum(s.pause_stats.paused_seconds for s in group)
        pauses = sum(s.pause_stats.pause_count for s in group)
        open_total = worked + paused

        out.append(
            ActivityBreakdown(
                activity=activity,
                category=group[0].category,
                sessions=len(group),
                worked_seconds=worked,
                paused_seconds=paused,
                pause_count=pauses,
                avg_pauses_per_session=round(pauses / len(group), 2),
                paused_pct_of_session=round(100 * paused / open_total, 1) if open_total else None,
            )
        )

    # Most-interrupted first — that's the actionable end of the list.
    return sorted(out, key=lambda b: -b.paused_seconds)
