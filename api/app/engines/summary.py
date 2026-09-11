"""Dashboard aggregation — pure function, same shape as the other four
engines (no DB, no clock but the `today` passed in). Every number here is
a real aggregate over `problems`/`problem_attempts`/`reviews`; a
brand-new account simply produces all-zero fields, never a fabricated
placeholder shape.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from app.domain import (
    L5_PLUS,
    MASTERY_LEVELS,
    AttemptFixture,
    AttemptsByDay,
    DashboardSummary,
    MasteryCount,
    PatternCoverage,
    ProblemFixture,
    ReviewState,
    readiness_pct,
)


def _latest_attempt_by_problem(attempts: list[AttemptFixture]) -> dict[int, AttemptFixture]:
    latest: dict[int, AttemptFixture] = {}
    for a in sorted(attempts, key=lambda x: x.attempted_at):
        latest[a.problem_id] = a
    return latest


def compute_dashboard_summary(
    problems: list[ProblemFixture],
    attempts: list[AttemptFixture],
    reviews: list[ReviewState],
    today: date,
    days_window: int = 14,
) -> DashboardSummary:
    latest = _latest_attempt_by_problem(attempts)

    mastery_counts = {level: 0 for level in MASTERY_LEVELS}
    for a in latest.values():
        if a.mastery_level in mastery_counts:
            mastery_counts[a.mastery_level] += 1
    mastery_distribution = [MasteryCount(level=lv, count=mastery_counts[lv]) for lv in MASTERY_LEVELS]

    by_pattern: dict[str, list[ProblemFixture]] = defaultdict(list)
    for p in problems:
        by_pattern[p.pattern].append(p)

    pattern_coverage: list[PatternCoverage] = []
    for pattern, plist in by_pattern.items():
        scheduled_count = sum(1 for p in plist if p.scheduled_date is not None)
        l5_plus_count = 0
        for p in plist:
            attempt = latest.get(p.problem_id)
            if attempt is not None and attempt.mastery_level in L5_PLUS:
                l5_plus_count += 1
        ratio = (l5_plus_count / scheduled_count) if scheduled_count else 0.0
        pattern_coverage.append(
            PatternCoverage(
                pattern=pattern, scheduled_count=scheduled_count, l5_plus_count=l5_plus_count, ratio=ratio
            )
        )
    pattern_coverage.sort(key=lambda pc: (pc.ratio, pc.pattern))

    attempts_per_day: dict[date, int] = defaultdict(int)
    for a in attempts:
        attempts_per_day[a.attempted_at.date()] += 1
    attempts_by_day = [
        AttemptsByDay(day=today - timedelta(days=offset), count=attempts_per_day.get(today - timedelta(days=offset), 0))
        for offset in range(days_window - 1, -1, -1)
    ]

    problem_reviews = [r for r in reviews if r.subject_type == "problem"]
    reviews_due_count = sum(1 for r in problem_reviews if r.due_date == today)
    reviews_overdue_count = sum(1 for r in problem_reviews if r.due_date < today)

    total_problems = len(problems)

    return DashboardSummary(
        total_problems=total_problems,
        attempted_count=len(latest),
        mastery_distribution=mastery_distribution,
        pattern_coverage=pattern_coverage,
        attempts_by_day=attempts_by_day,
        reviews_due_count=reviews_due_count,
        reviews_overdue_count=reviews_overdue_count,
        readiness_pct=readiness_pct(total_problems, (a.mastery_level for a in latest.values())),
    )
