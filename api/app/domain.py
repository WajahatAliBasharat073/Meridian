"""Plain data shapes the four engines operate over.

Deliberately decoupled from the SQLAlchemy models: the build prompt requires
the engines be "pure functions over database state, unit-testable against
fixtures" (section 5) and the recommender specifically "testable: given a
fixture DB state, it returns a deterministic ranked list" (section 10). A
repository layer reads ORM rows and adapts them into these dataclasses;
engines never see a Session, so a test constructs fixtures with no DB at all.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

# Spaced-repetition ladder, in days (build prompt 5.1 / design doc 6.2).
MASTERY_LEVELS = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
LADDER_DAYS: dict[str, int] = {
    "L0": 1,
    "L1": 1,
    "L2": 3,
    "L3": 7,
    "L4": 14,
    "L5": 30,
    "L6": 60,
}


def level_index(level: str) -> int:
    return MASTERY_LEVELS.index(level)


def demote(level: str) -> str:
    idx = max(level_index(level) - 1, 0)
    return MASTERY_LEVELS[idx]


def promote(level: str) -> str:
    idx = min(level_index(level) + 1, len(MASTERY_LEVELS) - 1)
    return MASTERY_LEVELS[idx]


@dataclass(frozen=True)
class ReviewState:
    """One row of `reviews`, plus the mastery level it was scheduled at.
    `current_level` is not a design-doc column on `reviews` itself — it is
    carried here from the linked attempt (`current_mastery` for problems,
    the equivalent latest-result for other subject types) because the
    engine needs "what level was this reviewed at last" to detect
    regression and count same-level streaks."""

    subject_type: str
    subject_id: int
    due_date: date
    interval_days: int
    current_level: str
    overdue_days: int = 0
    last_result: str | None = None
    # Consecutive successes at the current level — drives promotion after 2.
    streak_at_level: int = 0


@dataclass(frozen=True)
class ReviewOutcome:
    """What `on_attempt` decides should happen to a review row."""

    subject_type: str
    subject_id: int
    new_level: str
    due_date: date
    interval_days: int
    overdue_days: int
    last_result: str
    streak_at_level: int
    regressed: bool


@dataclass(frozen=True)
class ProblemFixture:
    """A row from `problems` (+ optional curriculum slot for today)."""

    problem_id: int
    title: str
    pattern: str
    difficulty: str
    scheduled_date: date | None = None
    scheduled_slot: int | None = None


@dataclass(frozen=True)
class AttemptFixture:
    """A row from `problem_attempts`, reduced to what the recommender needs."""

    problem_id: int
    attempted_at: datetime
    mastery_level: str
    key_insight: str | None = None


@dataclass(frozen=True)
class Recommendation:
    problem_id: int
    title: str
    pattern: str
    difficulty: str
    reason: str
    queue: str  # 'FAILED_REVIEW' | 'OVERDUE_REVIEW' | 'DUE_REVIEW' | 'SCHEDULED' | 'PATTERN_GAP' | 'INTERLEAVE'
    is_review: bool
    prior_key_insight: str | None = None


@dataclass(frozen=True)
class BandwidthInput:
    minutes_available: int
    energy: int  # 1-5
    overdue_review_count: int
    overdue_review_minutes: int
    hour_of_day: int


@dataclass(frozen=True)
class BandwidthPlan:
    band: str  # 'HIGH' | 'MEDIUM' | 'LOW' | 'MINIMUM_VIABLE_DAY'
    allow_new_hard: bool
    allow_new_medium: bool
    max_new_problems: int
    include_reviews: bool
    include_mock: bool
    headline: str
    spare_minutes_suggestion: str | None = field(default=None)


@dataclass(frozen=True)
class MasteryCount:
    level: str  # L0-L6
    count: int


@dataclass(frozen=True)
class PatternCoverage:
    pattern: str
    scheduled_count: int
    l5_plus_count: int
    ratio: float  # l5_plus_count / scheduled_count, 0.0 if scheduled_count == 0


@dataclass(frozen=True)
class AttemptsByDay:
    day: date
    count: int


@dataclass(frozen=True)
class DashboardSummary:
    """Real aggregates only — every field is computed from actual rows,
    never a placeholder. A brand-new account gets all-zero values, not a
    different shape (build prompt: never fabricate; the UI decides how to
    present zero, this layer never pretends otherwise)."""

    total_problems: int
    attempted_count: int
    mastery_distribution: list[MasteryCount]
    pattern_coverage: list[PatternCoverage]
    attempts_by_day: list[AttemptsByDay]
    reviews_due_count: int
    reviews_overdue_count: int
    readiness_pct: float | None


@dataclass(frozen=True)
class TimeBlockFixture:
    """A row from `time_blocks`, reduced to what the daily-recap engine
    needs — the whole schedule (prayer, job, thesis, recovery, prep — not
    interview prep alone), not a subset of categories."""

    category: str
    tier: str
    status: str
    planned_minutes: int
    actual_minutes: int | None


@dataclass(frozen=True)
class CategoryBreakdown:
    category: str
    done: int
    total: int


@dataclass(frozen=True)
class DailyRecap:
    """A same-day, real-data-only look back at one day's schedule. No
    fabricated numbers, no invented advice — every suggestion is a plain
    restatement of a threshold crossed by an actual figure below."""

    recap_date: date
    total_blocks: int
    done_count: int
    partial_count: int
    not_done_count: int
    rescheduled_count: int
    completion_pct: float | None
    category_breakdown: list[CategoryBreakdown]
    problems_attempted: int
    deep_work_planned_minutes: int
    deep_work_actual_minutes: int
    headline: str
    suggestions: list[str]


@dataclass(frozen=True)
class WeeklyCategoryMinutes:
    category: str
    minutes: int


@dataclass(frozen=True)
class MoodCount:
    mood: str
    count: int


@dataclass(frozen=True)
class WeeklyReview:
    """A real-data-only look back at the last 7 days — same discipline as
    DailyRecap: every line in what_went_well / what_to_improve restates
    an actual figure, nothing inferred beyond what the numbers show."""

    window_start: date
    window_end: date
    total_minutes_logged: int
    days_active: int
    days_in_window: int
    completion_pct: float | None
    category_minutes: list[WeeklyCategoryMinutes]
    avg_focus_session_minutes: float | None
    rescheduled_count: int
    mood_distribution: list[MoodCount]
    what_went_well: list[str]
    what_to_improve: list[str]
