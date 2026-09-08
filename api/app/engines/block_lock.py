"""Pure functions guarding a time block's DONE claim from both directions:
has its window mostly elapsed with focus never started at all (too late),
and is it being marked complete while most of its window is still ahead
(too early)?

Exists to stop dishonest actions: starting a "focus session" for a block
that's basically already over, marking a block DONE when no real work was
ever recorded against it, and marking a block DONE minutes after opening
it with most of the window still unused. All three would make
`actual_minutes` and every duration-derived figure downstream
(punctuality, session breakdown, pace projections) fiction rather than
data.

Deliberately narrow: a block that already has *any* focus session — even
one abandoned seconds after starting — is never locked by the 70% rule.
That rule is about never having engaged with the block at all, not about
how that first attempt went. The early-completion guard below is
independent of engagement — it fires purely on how much of the window is
still ahead, whether or not focus was ever started.
"""

from __future__ import annotations

from datetime import time

# 70%: enough of the window that "I'll still do this for real" is no
# longer a credible plan for the remaining time — not so aggressive that
# a block barely underway gets locked out from a late start.
LOCK_THRESHOLD = 0.7


def _minutes_between(a: time, b: time) -> int:
    return (b.hour * 60 + b.minute) - (a.hour * 60 + a.minute)


class BlockLockedError(Exception):
    """Raised when an action is attempted against a block whose window has
    mostly elapsed with no focus session ever started on it."""


def is_block_locked(
    scheduled_start: time | None,
    planned_minutes: int,
    now: time,
    has_any_focus_session: bool,
) -> bool:
    if has_any_focus_session or scheduled_start is None or planned_minutes <= 0:
        return False

    elapsed = _minutes_between(scheduled_start, now)
    if elapsed < 0:
        # The block hasn't even started yet by the clock - nothing to lock.
        return False
    return elapsed >= LOCK_THRESHOLD * planned_minutes


# 5 minutes: a block claimed DONE while most of its window is still ahead
# is the same kind of fiction the 70% lock above guards against, just at
# the opposite end — "I finished" said too early rather than too late.
EARLY_COMPLETION_GUARD_MINUTES = 5


class TooEarlyToCompleteError(Exception):
    """Raised when a block is marked DONE while more than
    `EARLY_COMPLETION_GUARD_MINUTES` remain before its scheduled end."""


def is_too_early_to_complete(scheduled_end: time | None, now: time) -> bool:
    """True once there's still more than the guard window left before the
    block's scheduled end — i.e. too early to honestly call it done.

    A block with no `scheduled_end`, or one already at/past its end (or
    within the last few minutes of it), is never too early — completion
    is only ever disallowed for time still clearly ahead."""
    if scheduled_end is None:
        return False
    remaining = _minutes_between(now, scheduled_end)
    return remaining > EARLY_COMPLETION_GUARD_MINUTES
