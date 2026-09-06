"""Pydantic request/response models — the only shape the API speaks in.
Validated at every boundary (build prompt 10 / design doc 11)."""

from __future__ import annotations

from datetime import date, time
from typing import Literal

from pydantic import BaseModel, Field

MasteryLevel = Literal["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
BlockStatus = Literal["DONE", "NOT DONE", "PARTIAL", "RESCHEDULED"]


class TimeBlockOut(BaseModel):
    id: int
    seq: int
    start: time
    end: time
    activity: str
    tier: str
    category: str
    planned_minutes: int
    status: BlockStatus
    actual_minutes: int | None = None
    what_to_do: str | None = None
    notes: str | None = None
    is_current: bool = False


class BlockStatusUpdate(BaseModel):
    status: BlockStatus
    actual_minutes: int | None = None


class BlockCreate(BaseModel):
    date: date
    # Absolute ("17:05") or prayer-relative ("maghrib+15m", "asr") — same
    # grammar app/engines/scheduling.py already resolves for seeded blocks.
    start_spec: str = Field(min_length=1)
    end_spec: str = Field(min_length=1)
    activity: str = Field(min_length=1)
    tier: Literal["T1", "T2", "T3", "T4"] = "T2"
    category: str = Field(min_length=1)
    planned_minutes: int = Field(gt=0)
    what_to_do: str | None = None
    notes: str | None = None


class ProblemOut(BaseModel):
    problem_id: int
    lc_number: int
    title: str
    slug: str
    url: str
    pattern: str
    difficulty: str
    is_neetcode150: bool
    is_blind75: bool
    current_mastery: MasteryLevel | None = None
    is_scheduled_today: bool = False


class ConceptResourceOut(BaseModel):
    label: str
    url: str | None = None


class ConceptOut(BaseModel):
    concept_id: int
    category: str
    title: str
    summary: str
    resources: list[ConceptResourceOut]
    phase: str
    current_mastery: MasteryLevel | None = None


class ConceptAttemptCreate(BaseModel):
    concept_id: int
    mastery_level: MasteryLevel
    notes: str | None = None


class QuestionOut(BaseModel):
    question_id: int
    category: str
    title: str
    source: str
    covered: bool


class QuestionCoverageOut(BaseModel):
    covered: bool


class CategoryCoverageOut(BaseModel):
    category: str
    covered_count: int
    total_count: int
    pct: float


class QuestionSummaryOut(BaseModel):
    by_category: list[CategoryCoverageOut]
    covered_count: int
    total_count: int
    pct: float | None


class RecommendationOut(BaseModel):
    problem_id: int
    title: str
    pattern: str
    difficulty: str
    reason: str
    queue: str
    is_review: bool
    prior_key_insight: str | None = None


class AttemptCreate(BaseModel):
    problem_id: int
    mastery_level: MasteryLevel
    minutes: int | None = None
    hint_used: bool = False
    key_insight: str | None = None


class AttemptResult(BaseModel):
    next_review_due: date
    interval_days: int
    message: str


class ReviewDueOut(BaseModel):
    subject_type: str
    subject_id: int
    due_date: date
    overdue_days: int
    interval_days: int
    last_result: str | None = None


class BandwidthOut(BaseModel):
    band: Literal["HIGH", "MEDIUM", "LOW", "MINIMUM_VIABLE_DAY"]
    allow_new_hard: bool
    allow_new_medium: bool
    max_new_problems: int
    include_reviews: bool
    include_mock: bool
    headline: str
    spare_minutes_suggestion: str | None = None


class TodayCounters(BaseModel):
    overdue_reviews: int
    blocks_remaining: int
    readiness_pct: float | None = None


class TodayOut(BaseModel):
    date: date
    blocks: list[TimeBlockOut]
    current_block: TimeBlockOut | None = None
    next_action: RecommendationOut | None = None
    bandwidth: BandwidthOut | None = None
    counters: TodayCounters
    prayer_accuracy_minutes: tuple[int, int] = Field(default=(5, 15))


class MasteryCountOut(BaseModel):
    level: MasteryLevel
    count: int


class PatternCoverageOut(BaseModel):
    pattern: str
    scheduled_count: int
    l5_plus_count: int
    ratio: float


class AttemptsByDayOut(BaseModel):
    day: date
    count: int


class DashboardSummaryOut(BaseModel):
    total_problems: int
    attempted_count: int
    mastery_distribution: list[MasteryCountOut]
    pattern_coverage: list[PatternCoverageOut]
    attempts_by_day: list[AttemptsByDayOut]
    reviews_due_count: int
    reviews_overdue_count: int
    readiness_pct: float | None = None


class CategoryBreakdownOut(BaseModel):
    category: str
    done: int
    total: int


class DailyRecapOut(BaseModel):
    recap_date: date
    total_blocks: int
    done_count: int
    partial_count: int
    not_done_count: int
    rescheduled_count: int
    completion_pct: float | None
    category_breakdown: list[CategoryBreakdownOut]
    problems_attempted: int
    deep_work_planned_minutes: int
    deep_work_actual_minutes: int
    headline: str
    suggestions: list[str]


class ProfileOut(BaseModel):
    birth_date: date | None = None
    life_expectancy_years: int | None = None


class ProfileUpdate(BaseModel):
    birth_date: date
    life_expectancy_years: int = Field(ge=1, le=120)


GoalStatus = Literal["active", "completed", "abandoned"]


class GoalOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    category: str | None = None
    target_date: date | None = None
    progress_pct: int
    status: GoalStatus
    minutes_logged: int | None = None


class GoalCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    category: str | None = None
    target_date: date | None = None


class GoalUpdate(BaseModel):
    progress_pct: int | None = Field(default=None, ge=0, le=100)
    status: GoalStatus | None = None


class TimeBudgetOut(BaseModel):
    id: int
    category: str
    minutes_per_week: int
    actual_minutes_this_week: int


class TimeBudgetUpsert(BaseModel):
    category: str = Field(min_length=1)
    minutes_per_week: int = Field(gt=0)


Mood = Literal["difficult", "normal", "good", "excellent"]


class DailyReflectionOut(BaseModel):
    date: date
    mood: Mood
    what_got_in_the_way: str | None = None
    what_went_well: str | None = None


class DailyReflectionUpsert(BaseModel):
    mood: Mood
    what_got_in_the_way: str | None = None
    what_went_well: str | None = None


class WeeklyCategoryMinutesOut(BaseModel):
    category: str
    minutes: int


class MoodCountOut(BaseModel):
    mood: str
    count: int


class WeeklyReviewOut(BaseModel):
    window_start: date
    window_end: date
    total_minutes_logged: int
    days_active: int
    days_in_window: int
    completion_pct: float | None
    category_minutes: list[WeeklyCategoryMinutesOut]
    avg_focus_session_minutes: float | None
    rescheduled_count: int
    mood_distribution: list[MoodCountOut]
    what_went_well: list[str]
    what_to_improve: list[str]


class GroqModelOut(BaseModel):
    id: str
    label: str
    description: str
    enabled: bool


class AISettingsOut(BaseModel):
    api_key_set: bool
    active_model: str
    models: list[GroqModelOut]


class AISettingsUpdate(BaseModel):
    # None = leave unchanged; "" = clear the stored key.
    api_key: str | None = None
    active_model: str | None = None
    enabled_model_ids: list[str] | None = None


class ThesisLogOut(BaseModel):
    id: int
    milestone: str | None = None
    work_summary: str
    minutes: int | None = None
    output_type: str | None = None
    deadline: date | None = None
    status: str | None = None
    date: date


class ThesisLogCreate(BaseModel):
    work_summary: str = Field(min_length=1)
    milestone: str | None = None
    minutes: int | None = Field(default=None, gt=0)
    output_type: str | None = None
    deadline: date | None = None
    status: str | None = None
    date: date


class ReadingLogOut(BaseModel):
    id: int
    date: date
    title: str
    author: str | None = None
    kind: str
    progress_note: str | None = None
    status: str | None = None


class ReadingLogCreate(BaseModel):
    date: date
    title: str = Field(min_length=1)
    author: str | None = None
    kind: str = "book"
    progress_note: str | None = None
    status: str | None = "in_progress"


class ReadingLogUpdate(BaseModel):
    status: str | None = None
    progress_note: str | None = None
