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
