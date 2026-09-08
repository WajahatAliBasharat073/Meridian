"""Pure function: at your actual recorded pace, how long does clearing the
theory backlog take — and what does changing the daily count actually buy?

Same discipline as `punctuality.py` — every figure is computed from real
logged minutes, and no claim is made until there is enough of them. A
single question timed at 40 minutes is not "your pace", it's one data
point; the caller gets `enough_data=False` and a count, not a confident
average built on two rows.

The average is deliberately *weighted by rating events, not by question*:
summing every question's `total_minutes` and dividing by the sum of every
question's `rating_count` means a question you reviewed five times
contributes five data points to the estimate, not one diluted by however
long ago you first saw it. The alternative (mean of each question's own
average) would let a single heavily-reviewed outlier and a single
once-seen question count equally, which is the wrong estimator for "how
long does a study session on one question actually take".
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# Below this many *distinct rated questions with logged time*, don't
# characterise pace at all — the same bar `punctuality.py` sets for focus
# sessions, and for the same reason.
MIN_QUESTIONS_FOR_INSIGHT = 5


@dataclass(frozen=True)
class QuestionTiming:
    """One question's cumulative logged time — a row from
    `question_progress` where `total_minutes > 0`."""

    question_id: int
    total_minutes: int
    rating_count: int


@dataclass(frozen=True)
class PaceProjection:
    daily_count: int
    daily_minutes: int
    days_to_clear_backlog: int | None  # None only when backlog_count == 0
    minutes_delta_vs_baseline: int
    days_saved_vs_baseline: int | None


@dataclass(frozen=True)
class TheoryPaceReport:
    enough_data: bool
    questions_with_data: int
    min_questions_needed: int
    avg_minutes_per_question: float | None
    backlog_count: int
    baseline_daily_count: int
    projections: list[PaceProjection]


def compute_theory_pace(
    timings: list[QuestionTiming],
    backlog_count: int,
    daily_counts: list[int],
    baseline_daily_count: int = 3,
) -> TheoryPaceReport:
    questions_with_data = len(timings)

    if questions_with_data < MIN_QUESTIONS_FOR_INSIGHT:
        return TheoryPaceReport(
            enough_data=False,
            questions_with_data=questions_with_data,
            min_questions_needed=MIN_QUESTIONS_FOR_INSIGHT,
            avg_minutes_per_question=None,
            backlog_count=backlog_count,
            baseline_daily_count=baseline_daily_count,
            projections=[],
        )

    total_minutes = sum(t.total_minutes for t in timings)
    total_events = sum(t.rating_count for t in timings)
    # rating_count is only ever incremented alongside a positive
    # total_minutes contribution when minutes are logged, so a timing row
    # existing at all guarantees total_events > 0 here.
    avg = total_minutes / total_events

    def _days_to_clear(count: int) -> int | None:
        if backlog_count <= 0:
            return 0
        if count <= 0:
            return None
        return math.ceil(backlog_count / count)

    baseline_minutes = round(avg * baseline_daily_count)
    baseline_days = _days_to_clear(baseline_daily_count)

    projections = []
    for count in daily_counts:
        daily_minutes = round(avg * count)
        days = _days_to_clear(count)
        days_saved = None
        if baseline_days is not None and days is not None:
            days_saved = baseline_days - days
        projections.append(
            PaceProjection(
                daily_count=count,
                daily_minutes=daily_minutes,
                days_to_clear_backlog=days,
                minutes_delta_vs_baseline=daily_minutes - baseline_minutes,
                days_saved_vs_baseline=days_saved,
            )
        )

    return TheoryPaceReport(
        enough_data=True,
        questions_with_data=questions_with_data,
        min_questions_needed=MIN_QUESTIONS_FOR_INSIGHT,
        avg_minutes_per_question=round(avg, 1),
        backlog_count=backlog_count,
        baseline_daily_count=baseline_daily_count,
        projections=projections,
    )
