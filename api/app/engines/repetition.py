"""Spaced-repetition engine (build prompt 5.1, design doc 6.2).

Serves problems, vocabulary, ML concepts and mistakes through one
polymorphic function — `subject_type` is opaque to this module. Pure: no
DB, no clock other than the `today` passed in, fully deterministic.
"""

from __future__ import annotations

from datetime import date, timedelta

from app.domain import LADDER_DAYS, ReviewOutcome, ReviewState, demote, level_index, promote

# Two consecutive successes at the same level promote it (build prompt 5.1).
PROMOTION_STREAK = 2


def on_attempt(
    previous: ReviewState | None,
    subject_type: str,
    subject_id: int,
    reported_level: str,
    today: date,
    engaged: bool = True,
) -> ReviewOutcome | None:
    """Decide the next review state after an attempt is recorded.

    `engaged` is False only for a bare "seen" with no time logged and no
    prior history — that does not schedule a review (unattempted != due).
    """
    if previous is None and reported_level == "L0" and not engaged:
        return None

    if previous is not None and level_index(reported_level) < level_index(previous.current_level):
        # Regression: always exactly one level down from where they were,
        # never adopted from the (possibly much lower) reported level.
        new_level = demote(previous.current_level)
        streak = 0
        result = "regressed"
    elif previous is not None and reported_level == previous.current_level:
        streak = previous.streak_at_level + 1
        if streak >= PROMOTION_STREAK:
            new_level = promote(reported_level)
            streak = 0
        else:
            new_level = reported_level
        result = "success"
    else:
        # First attempt, or the user explicitly jumped to a higher level —
        # trust the stated level; the streak toward the next promotion
        # starts fresh at this new level.
        new_level = reported_level
        streak = 0
        result = "success"

    interval = LADDER_DAYS[new_level]
    return ReviewOutcome(
        subject_type=subject_type,
        subject_id=subject_id,
        new_level=new_level,
        due_date=_add_days(today, interval),
        interval_days=interval,
        overdue_days=0,
        last_result=result,
        streak_at_level=streak,
        regressed=result == "regressed",
    )


def _add_days(d: date, days: int) -> date:
    return d + timedelta(days=days)


def roll_forward_overdue(reviews: list[ReviewState], today: date) -> list[ReviewState]:
    """Nightly job: never drop a review. Anything past due gets its
    `overdue_days` counter incremented; due date itself does not move so
    the true schedule stays visible, only how late it is grows."""
    rolled = []
    for r in reviews:
        if r.due_date < today:
            days_late = (today - r.due_date).days
            rolled.append(
                ReviewState(
                    subject_type=r.subject_type,
                    subject_id=r.subject_id,
                    due_date=r.due_date,
                    interval_days=r.interval_days,
                    current_level=r.current_level,
                    overdue_days=days_late,
                    last_result=r.last_result,
                    streak_at_level=r.streak_at_level,
                )
            )
        else:
            rolled.append(r)
    return rolled


def apply_daily_cap(
    reviews_due_or_overdue: list[ReviewState],
    cap: int,
    today: date,
) -> tuple[list[ReviewState], list[ReviewState]]:
    """Overflow policy (design doc 6.2): failed reviews first, then oldest
    overdue, then due-today. Remainder is pushed one day and its
    `overdue_days` still reflects real lateness — nothing is dropped.

    Returns (today's queue within cap, pushed-to-tomorrow with bumped due_date).
    """

    def sort_key(r: ReviewState) -> tuple[int, int, date]:
        failed_first = 0 if r.last_result == "regressed" else 1
        return (failed_first, -r.overdue_days, r.due_date)

    ordered = sorted(reviews_due_or_overdue, key=sort_key)
    kept = ordered[:cap]
    overflow = ordered[cap:]

    pushed = [
        ReviewState(
            subject_type=r.subject_type,
            subject_id=r.subject_id,
            due_date=_add_days(today, 1),
            interval_days=r.interval_days,
            current_level=r.current_level,
            overdue_days=r.overdue_days + 1,
            last_result=r.last_result,
            streak_at_level=r.streak_at_level,
        )
        for r in overflow
    ]
    return kept, pushed
