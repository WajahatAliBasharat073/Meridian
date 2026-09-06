"""Pure function: turns 7 real days of schedule + reflections into a
review. Same discipline as daily_recap.py — every line is a plain
restatement of an actual number, never an inferred claim."""

from __future__ import annotations

from datetime import date

from app.domain import MoodCount, TimeBlockFixture, WeeklyCategoryMinutes, WeeklyReview

DONE_STATUSES = {"DONE", "PARTIAL"}
MIN_DAYS_FOR_STRONG_CLAIM = 4


def compute_weekly_review(
    blocks: list[TimeBlockFixture],
    block_dates: list[date],
    mood_counts: dict[str, int],
    window_start: date,
    window_end: date,
    days_in_window: int,
) -> WeeklyReview:
    total = len(blocks)
    done_or_partial = sum(1 for b in blocks if b.status in DONE_STATUSES)
    rescheduled = sum(1 for b in blocks if b.status == "RESCHEDULED")
    completion_pct = round(100 * done_or_partial / total, 1) if total else None

    days_active = len({d for d, b in zip(block_dates, blocks, strict=True) if b.status in DONE_STATUSES})

    minutes_by_category: dict[str, int] = {}
    total_minutes = 0
    for b in blocks:
        if b.status not in DONE_STATUSES:
            continue
        minutes = b.actual_minutes if b.actual_minutes is not None else b.planned_minutes
        if b.status == "PARTIAL" and b.actual_minutes is None:
            minutes = b.planned_minutes // 2
        minutes_by_category[b.category] = minutes_by_category.get(b.category, 0) + minutes
        total_minutes += minutes

    category_minutes = [
        WeeklyCategoryMinutes(category=cat, minutes=mins)
        for cat, mins in sorted(minutes_by_category.items(), key=lambda kv: -kv[1])
    ]

    deep_work_sessions = [
        b.actual_minutes for b in blocks if b.tier == "T1" and b.status == "DONE" and b.actual_minutes
    ]
    avg_focus = round(sum(deep_work_sessions) / len(deep_work_sessions), 1) if deep_work_sessions else None

    mood_distribution = [
        MoodCount(mood=m, count=c) for m, c in sorted(mood_counts.items(), key=lambda kv: -kv[1])
    ]

    went_well, to_improve = _reflect(
        total=total,
        completion_pct=completion_pct,
        days_active=days_active,
        days_in_window=days_in_window,
        rescheduled=rescheduled,
        category_minutes=category_minutes,
        avg_focus=avg_focus,
    )

    return WeeklyReview(
        window_start=window_start,
        window_end=window_end,
        total_minutes_logged=total_minutes,
        days_active=days_active,
        days_in_window=days_in_window,
        completion_pct=completion_pct,
        category_minutes=category_minutes,
        avg_focus_session_minutes=avg_focus,
        rescheduled_count=rescheduled,
        mood_distribution=mood_distribution,
        what_went_well=went_well,
        what_to_improve=to_improve,
    )


def _reflect(
    *,
    total: int,
    completion_pct: float | None,
    days_active: int,
    days_in_window: int,
    rescheduled: int,
    category_minutes: list[WeeklyCategoryMinutes],
    avg_focus: float | None,
) -> tuple[list[str], list[str]]:
    went_well: list[str] = []
    to_improve: list[str] = []

    if total == 0:
        return went_well, to_improve

    if days_active >= MIN_DAYS_FOR_STRONG_CLAIM:
        went_well.append(f"Active {days_active} of {days_in_window} days this week.")
    elif days_active > 0:
        to_improve.append(f"Only active {days_active} of {days_in_window} days this week.")

    if completion_pct is not None:
        if completion_pct >= 75:
            went_well.append(f"Held {completion_pct}% of scheduled blocks.")
        elif completion_pct < 50:
            to_improve.append(f"Only {completion_pct}% of scheduled blocks were completed.")

    if category_minutes:
        top = category_minutes[0]
        went_well.append(f"Most time went to {top.category} ({top.minutes} min).")

    if rescheduled >= 5:
        to_improve.append(f"{rescheduled} blocks were rescheduled this week — worth a closer look.")

    if avg_focus is not None and avg_focus < 25:
        to_improve.append(f"Average focus session was {avg_focus} min — short for deep work.")

    return went_well, to_improve
