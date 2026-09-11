"""Pydantic request/response models — the only shape the API speaks in.
Validated at every boundary (build prompt 10 / design doc 11)."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, Field

# `date` as a *type* alias. A schema field named `date` with a default
# (`date: date | None = None`) binds the name `date` to None inside its own
# class body, so the annotation can no longer resolve — this alias is what
# such fields annotate against.
DateOnly = date

MasteryLevel = Literal["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
BlockStatus = Literal["DONE", "NOT DONE", "PARTIAL", "RESCHEDULED"]

# How much help an attempt actually took — a separate axis from
# MasteryLevel, which records confidence afterwards. Defined up here
# because ProblemOut (below) annotates with it.
SolveMethod = Literal[
    "independent",        # solved it alone, start to finish
    "recalled_pattern",   # recognised the pattern from earlier practice
    "after_hint",         # needed a nudge, then solved it
    "after_editorial",    # read the written solution
    "after_video",        # watched a video explanation
    "brute_force_only",   # working solution, but not the optimal one
    "not_solved",         # attempted, didn't get there
]


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
    # Whether a focus session has ever been started on this block, in any
    # state — the signal the block-lock rule needs (see
    # app/engines/block_lock.py). Not derived from `status`: a block can
    # be NOT DONE and still have an abandoned session on it.
    has_focus_session: bool = False


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
    # None for a classic algorithm with no LeetCode entry (Dijkstra, KMP,
    # Rat in a Maze) — never a stand-in number.
    lc_number: int | None = None
    title: str
    slug: str
    url: str | None = None
    pattern: str
    topic: str | None = None
    difficulty: str
    source: str = "leetcode"
    is_neetcode150: bool
    is_blind75: bool
    # Named companies from the source sheet, plus its own "+N" truncation
    # as a count rather than invented names.
    companies: list[str] = Field(default_factory=list)
    company_extra_count: int = 0
    current_mastery: MasteryLevel | None = None
    is_scheduled_today: bool = False
    # Progress detail, so the browser can distinguish "solved unaided" from
    # "solved after watching the video" without a second request.
    last_solve_method: SolveMethod | None = None
    attempt_count: int = 0
    last_attempted_at: datetime | None = None
    last_minutes: int | None = None
    last_key_insight: str | None = None
    last_notes: str | None = None


class TopicGuideTypeOut(BaseModel):
    name: str
    note: str


class TopicGuideOperationOut(BaseModel):
    op: str
    complexity: str
    note: str


class TopicGuideOut(BaseModel):
    """The "learn the structure first" material for one topic."""

    topic: str
    display_name: str
    seq: int
    one_liner: str
    learn_first: str
    types: list[TopicGuideTypeOut] = Field(default_factory=list)
    operations: list[TopicGuideOperationOut] = Field(default_factory=list)
    must_know: list[str] = Field(default_factory=list)
    pitfalls: list[str] = Field(default_factory=list)
    needs_revision: bool = False


class TopicSectionOut(BaseModel):
    """One topic: what to learn first, then its problems and the counts.

    Ordered by topic, never by the source sheet's day numbering — the plan
    is "understand arrays, then do the array problems", not "day 3".
    """

    topic: str
    display_name: str
    seq: int
    guide: TopicGuideOut | None = None
    problems: list[ProblemOut] = Field(default_factory=list)
    total: int = 0
    solved: int = 0
    unaided: int = 0
    remaining: int = 0
    by_difficulty: dict[str, int] = Field(default_factory=dict)
    # Every company named across this topic's problems, most-tagged first.
    companies: list[str] = Field(default_factory=list)
    # Whether the structure has been demonstrated. `problems` is empty while
    # this is locked or expired — see app/engines/topic_gate.py.
    gate: TopicGateOut | None = None


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


# The 0-7 interview mastery ladder. Seeing a question is not knowing it,
# which is why this is not a boolean.
MASTERY_LADDER: dict[int, str] = {
    0: "Never seen",
    1: "Recognize",
    2: "Can explain",
    3: "Can solve",
    4: "Can reason about trade-offs",
    5: "Can answer follow-ups",
    6: "Can design a production system",
    7: "Can teach it",
}


class InterviewModuleOut(BaseModel):
    code: str
    title: str
    summary: str | None
    priority: str
    submodules: list[str]
    target_seniority: list[str]
    question_count: int
    ready_count: int
    pct: float


#: A self-tag layered on top of the 0-7 mastery ladder — see
#: QuestionProgress.learning_status and migration 0021. "not_attempted" is
#: not a member: it is the absence of any status, which the frontend
#: renders from `learning_status is None` rather than a stored value.
LearningStatus = Literal[
    "already_know", "easy", "understood", "solved_with_help", "struggled", "no_idea",
]

LEARNING_STATUS_LABELS: dict[str, str] = {
    "already_know": "Already know",
    "easy": "Easy",
    "understood": "Understood",
    "solved_with_help": "Solved with help",
    "struggled": "Struggled",
    "no_idea": "No idea",
}


class QuestionOut(BaseModel):
    question_id: int
    category: str
    title: str
    source: str
    mastery: int

    module_code: str | None = None
    submodule: str | None = None
    question_type: str | None = None
    difficulty: str | None = None
    seniority: str | None = None
    priority: str | None = None
    frequency: str | None = None
    # See `Question.evidence` — a non-empty `companies` list is only legal
    # alongside evidence='reported' and a source_url.
    evidence: str | None = None
    source_url: str | None = None
    tests_for: str | None = None
    strong_signal: str | None = None
    weak_signal: str | None = None
    companies: list[str] = []
    answer_dimensions: list[str] = []
    follow_ups: list[str] = []
    common_mistakes: list[str] = []
    # A real reference implementation, for coding questions backed by an
    # actual source file (Module B). None for every other question type.
    reference_solution: str | None = None

    # Curriculum position (migration 0019/0020) — None until classified.
    topic: str | None = None
    phase: int | None = None
    cognitive_level: int | None = None

    # This user's self-tag and revisit flag (migration 0021). None/false
    # when the question has never been rated on this axis.
    learning_status: LearningStatus | None = None
    needs_review: bool = False


class DailyTheoryPickOut(QuestionOut):
    """One of today's recommended theory questions — the full QuestionOut
    record plus why it was picked today specifically."""

    is_case_study: bool
    pick_reason: str


class QuestionMasteryIn(BaseModel):
    mastery: int = Field(ge=0, le=7)
    notes: str | None = None
    # Optional, and cumulative server-side (see QuestionProgress.total_minutes)
    # — an untimed rating simply contributes nothing to the pace average
    # rather than being recorded as a zero-minute study session.
    minutes: int | None = Field(default=None, ge=0)


class QuestionMasteryOut(BaseModel):
    mastery: int
    label: str


#: Statuses that auto-set `needs_review` unless the caller explicitly
#: overrides it — "solved with help, so flag it for later" is the default
#: reading of that status, not something you have to ask for separately.
AUTO_REVIEW_STATUSES: frozenset[str] = frozenset({"solved_with_help", "struggled", "no_idea"})


def resolve_needs_review(learning_status: str | None, needs_review: bool | None) -> bool:
    """The stored value of `needs_review` for a status-update call.

    An explicit True/False always wins — the flag must stay independently
    toggleable, per "I solved it with help, so I want to revisit it later"
    being a default the learner can still override. Otherwise it derives
    from the status: solved-with-help / struggled / no-idea flag
    themselves for revisit; every other status (or clearing status
    entirely) clears the flag.
    """
    if needs_review is not None:
        return needs_review
    return bool(learning_status) and learning_status in AUTO_REVIEW_STATUSES


class QuestionStatusIn(BaseModel):
    learning_status: LearningStatus | None = None
    # None = derive from `learning_status` via AUTO_REVIEW_STATUSES; an
    # explicit True/False overrides that default, since the whole feature
    # exists so the flag can be toggled independently of status.
    needs_review: bool | None = None


class QuestionStatusOut(BaseModel):
    learning_status: LearningStatus | None = None
    needs_review: bool = False


class CategoryCoverageOut(BaseModel):
    category: str
    # "covered" is kept as the field name for compatibility; it means
    # ready (mastery >= 4). `started_count` is anything rated at all.
    covered_count: int
    started_count: int = 0
    total_count: int
    pct: float


class QuestionSummaryOut(BaseModel):
    by_category: list[CategoryCoverageOut]
    covered_count: int
    started_count: int = 0
    total_count: int
    pct: float | None


class TheoryPaceProjectionOut(BaseModel):
    daily_count: int
    daily_minutes: int
    days_to_clear_backlog: int | None
    minutes_delta_vs_baseline: int
    days_saved_vs_baseline: int | None


class TheoryPaceOut(BaseModel):
    enough_data: bool
    questions_with_data: int
    min_questions_needed: int
    avg_minutes_per_question: float | None
    backlog_count: int
    baseline_daily_count: int
    projections: list[TheoryPaceProjectionOut]


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
    # How much help the attempt actually took — a separate axis from
    # mastery_level, which records confidence afterwards.
    solve_method: SolveMethod | None = None
    understood_approach_independently: bool | None = None
    reached_optimal: bool | None = None
    # Long-form workings, kept separate from the short key_insight prompt.
    notes: str | None = None


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
    #: Set only when this goal is linked to a money goal (app/models/finance.py).
    #: Its progress is always computed from real transactions, never the
    #: manual slider progress_pct above -- the two coexist rather than one
    #: overriding the other, since they measure different things.
    finance_goal_id: int | None = None
    linked_finance_goal: FinanceGoalOut | None = None


class GoalCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    category: str | None = None
    target_date: date | None = None
    finance_goal_id: int | None = None


class GoalUpdate(BaseModel):
    progress_pct: int | None = Field(default=None, ge=0, le=100)
    status: GoalStatus | None = None
    #: None = no change (matches progress_pct/status above); 0 = clear an
    #: existing link (0 is never a real finance_goals.id); any other value
    #: = link to that finance goal.
    finance_goal_id: int | None = None


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


ReadingFormat = Literal["book", "paper", "article", "docs"]
ReadingStatus = Literal["to_read", "reading", "completed", "paused", "dropped"]

# Genre, not format — kept separate so a self-help title and a technical
# book can both be tracked without one field trying to mean two things.
# "self_help" is deliberately named to cover exactly the titles that
# prompted adding this list: The 5 AM Club, The 7 Habits of Highly
# Effective People, Atomic Habits, and the rest of that shelf.
ReadingCategory = Literal[
    "fiction",
    "non_fiction",
    "self_help",
    "business",
    "technical",
    "biography_memoir",
    "philosophy",
    "science",
    "history",
    "other",
]

READING_CATEGORY_LABELS: dict[str, str] = {
    "fiction": "Fiction",
    "non_fiction": "Non-Fiction",
    "self_help": "Self-Help / Personal Development",
    "business": "Business & Career",
    "technical": "Technical",
    "biography_memoir": "Biography & Memoir",
    "philosophy": "Philosophy",
    "science": "Science",
    "history": "History",
    "other": "Other",
}


class ReadingSessionOut(BaseModel):
    id: int
    book_id: int
    date: date
    page_reached: int | None = None
    minutes: int | None = None
    note: str | None = None


class ReadingSessionCreate(BaseModel):
    date: date
    page_reached: int | None = Field(default=None, ge=0)
    minutes: int | None = Field(default=None, gt=0)
    note: str | None = None


ReadingPriority = Literal["high", "medium", "low"]


class ReadingQuoteOut(BaseModel):
    text: str
    page: int | None = None


class ReadingQuoteCreate(BaseModel):
    text: str = Field(min_length=1)
    page: int | None = Field(default=None, ge=0)


class ReadingBookOut(BaseModel):
    id: int
    title: str
    author: str | None = None
    cover_url: str | None = None
    total_pages: int | None = None
    format: ReadingFormat
    category: ReadingCategory | None = None
    status: ReadingStatus
    rating: int | None = None
    started_date: date | None = None
    finished_date: date | None = None
    notes: str | None = None
    priority: ReadingPriority | None = None
    tags: list[str] = Field(default_factory=list)
    quotes: list[ReadingQuoteOut] = Field(default_factory=list)
    why_reading: str | None = None
    revisit_date: date | None = None

    # Computed from `reading_sessions`, never stored — see ReadingBook's
    # docstring. None until at least one session has logged a page.
    current_page: int | None = None
    progress_pct: float | None = None
    session_count: int = 0
    total_minutes_logged: int = 0
    last_session_date: date | None = None
    last_session_note: str | None = None


class ReadingBookCreate(BaseModel):
    title: str = Field(min_length=1)
    author: str | None = None
    cover_url: str | None = None
    total_pages: int | None = Field(default=None, gt=0)
    format: ReadingFormat = "book"
    category: ReadingCategory | None = None
    status: ReadingStatus = "reading"
    started_date: date | None = None
    priority: ReadingPriority | None = None
    tags: list[str] = Field(default_factory=list)
    why_reading: str | None = None


class ReadingBookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    cover_url: str | None = None
    total_pages: int | None = Field(default=None, gt=0)
    format: ReadingFormat | None = None
    category: ReadingCategory | None = None
    status: ReadingStatus | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    started_date: date | None = None
    finished_date: date | None = None
    notes: str | None = None
    priority: ReadingPriority | None = None
    tags: list[str] | None = None
    why_reading: str | None = None
    revisit_date: date | None = None


class ReadingStatsOut(BaseModel):
    completed_count: int
    reading_count: int
    to_read_count: int
    completed_this_month: int
    completed_this_year: int
    pages_read_this_month: int
    streak_days: int
    top_categories: list[tuple[str, int]] = Field(default_factory=list)


class FocusSessionOut(BaseModel):
    id: int
    block_id: int
    scheduled_start: time | None = None
    planned_minutes: int
    started_at: datetime
    ended_at: datetime | None = None
    elapsed_seconds: int
    start_delay_minutes: int | None = None
    state: Literal["in_progress", "paused", "completed", "abandoned"]
    focus_rating: int | None = None


class FocusSessionStart(BaseModel):
    block_id: int


class FocusSessionUpdate(BaseModel):
    state: Literal["in_progress", "paused", "completed", "abandoned"] | None = None
    elapsed_seconds: int | None = Field(default=None, ge=0)
    focus_rating: int | None = Field(default=None, ge=1, le=5)
    notes: str | None = None


class CategoryPunctualityOut(BaseModel):
    category: str
    sessions: int
    avg_delay_minutes: float
    on_time_pct: float


class PunctualityOut(BaseModel):
    enough_data: bool
    session_count: int
    min_sessions_needed: int
    on_time_pct: float | None
    avg_delay_minutes: float | None
    median_delay_minutes: float | None
    started_early_or_on_time: int
    started_late: int
    worst_category: CategoryPunctualityOut | None
    best_category: CategoryPunctualityOut | None
    by_category: list[CategoryPunctualityOut]
    observations: list[str]


class FocusSessionEventOut(BaseModel):
    id: int
    session_id: int
    event_type: Literal[
        "started", "paused", "resumed", "extended", "shortened", "completed", "abandoned"
    ]
    occurred_at: datetime
    elapsed_seconds_at_event: int
    note: str | None = None


class ActivityBreakdownOut(BaseModel):
    activity: str
    category: str
    sessions: int
    worked_minutes: int
    paused_minutes: int
    pause_count: int
    avg_pauses_per_session: float
    paused_pct_of_session: float | None


class SessionBreakdownOut(BaseModel):
    window_days: int
    total_sessions: int
    total_worked_minutes: int
    total_paused_minutes: int
    total_pause_count: int
    by_activity: list[ActivityBreakdownOut]
    observations: list[str]

class TopicGateOut(BaseModel):
    """Whether this topic's problems are open, and on what evidence."""

    topic: str
    state: str  # locked | unlocked | expired | unverified_override
    problems_visible: bool
    passed_at: datetime | None = None
    expires_at: datetime | None = None
    days_until_expiry: int | None = None
    attempt_count: int = 0
    overridden: bool = False


LearningEntryKind = Literal["source", "note", "snippet", "requirement"]


class LearningEntryOut(BaseModel):
    """One thing logged while learning a topic.

    For a `source`, `url` is a bookmark only — nothing fetches or reads it —
    so `body` (the summary or transcript pasted in) is the only content that
    reaches the question generator. Pasting the transcript is therefore what
    makes the questions specific; a bare link barely moves them.
    """

    id: int
    topic: str
    kind: LearningEntryKind
    title: str
    url: str | None = None
    body: str | None = None
    created_at: datetime


class LearningEntryCreate(BaseModel):
    kind: LearningEntryKind
    title: str = Field(min_length=1)
    url: str | None = None
    body: str | None = None


class VerificationChecklistItemOut(BaseModel):
    text: str
    # Curated items can never be removed; self-added ones are additive only,
    # or the gate would be set by the person it is gating.
    self_added: bool = False
    entry_id: int | None = None


class VerificationChecklistOut(BaseModel):
    """What this topic requires you to have implemented: its curated gate
    list, plus anything you have added to it yourself."""

    topic: str
    display_name: str
    required: list[str] = Field(default_factory=list)
    items: list[VerificationChecklistItemOut] = Field(default_factory=list)


class BuildSubmissionIn(BaseModel):
    code: str = Field(min_length=1)
    notes: str = ""


class BuildResultOut(BaseModel):
    attempt_id: int
    covered: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    notes: str = ""
    build_score: float
    build_passed: bool
    # Only present once the build stage clears — no questions to defend
    # against a submission that never covered the structure.
    questions: list[str] = Field(default_factory=list)


class DefendSubmissionIn(BaseModel):
    answers: list[str] = Field(default_factory=list)
    # Flight recorder, reported by the client. A browser cannot prevent tab
    # switching, so this records what happened instead of claiming it could
    # not happen.
    focus_losses: int = Field(default=0, ge=0)
    focus_lost_seconds: int = Field(default=0, ge=0)
    duration_seconds: int | None = Field(default=None, ge=0)


class DefendGradeOut(BaseModel):
    question: str
    answer: str
    verdict: str  # correct | partial | wrong
    feedback: str = ""


class DefendResultOut(BaseModel):
    attempt_id: int
    grades: list[DefendGradeOut] = Field(default_factory=list)
    defend_score: float
    passed: bool
    gate: TopicGateOut
    focus_losses: int = 0
    focus_lost_seconds: int = 0


class OverrideIn(BaseModel):
    reason: str = ""


class VitalsOut(BaseModel):
    """One day's vitals as logged, plus the derived score.

    `recovery_score` is null when too little was logged to compute one — the
    Health page previously showed a number derived from hardcoded defaults,
    which is worse than showing nothing. `missing` names what to fill in.
    """

    date: date
    sleep_hours: float | None = None
    sleep_quality: int | None = None
    energy: int | None = None
    mood: int | None = None
    stress: int | None = None
    exercise_minutes: int | None = None
    water_ml: int | None = None
    calories: int | None = None
    protein_g: float | None = None

    recovery_score: float | None = None
    score_components: dict[str, float] = Field(default_factory=dict)
    missing: list[str] = Field(default_factory=list)
    water_target_ml: int
    hydration_pct: float | None = None
    # False means literally nothing has been logged today, which the page
    # renders as an empty state rather than as zeroes.
    has_any_entry: bool = False


class RecoveryUpdateIn(BaseModel):
    """Patch semantics: only the fields sent are written, so entering sleep
    in the morning does not blank last night's stress rating."""

    date: DateOnly | None = None
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    sleep_quality: int | None = Field(default=None, ge=1, le=5)
    energy: int | None = Field(default=None, ge=1, le=5)
    mood: int | None = Field(default=None, ge=1, le=5)
    stress: int | None = Field(default=None, ge=1, le=5)
    exercise_minutes: int | None = Field(default=None, ge=0)


class NutritionUpdateIn(BaseModel):
    date: DateOnly | None = None
    water_ml: int | None = Field(default=None, ge=0)
    calories: int | None = Field(default=None, ge=0)
    protein_g: float | None = Field(default=None, ge=0)


class WaterAddIn(BaseModel):
    # One glass. Bounded so a stuck client cannot log a bathtub.
    ml: int = Field(default=250, gt=0, le=2000)


class TopicStateOut(BaseModel):
    slug: str
    name: str
    phase: int
    state: str  # LOCKED | AVAILABLE | IN_PROGRESS | MASTERED
    mastery: float
    prereqs: list[str] = Field(default_factory=list)
    #: False when the topic has no knowledge questions yet. Such a topic is
    #: transparent for unlocking (invariant 7) and reported as a gap.
    has_content: bool = True


class CurriculumStateOut(BaseModel):
    """The learning frontier."""

    current_topic: str | None = None
    current_topic_name: str | None = None
    reached_phase: int = 0
    placement_status: str = "UNASSESSED"
    topics: list[TopicStateOut] = Field(default_factory=list)


class SelectionExplanationOut(BaseModel):
    """Why one question was chosen, or why it was not.

    Structured rather than prose so the curriculum can be debugged by
    query instead of by reading the ranking code.
    """

    question_id: int
    selected: bool
    slot: str | None = None
    topic: str | None = None
    phase: int | None = None
    score: float | None = None
    reason_codes: list[str] = Field(default_factory=list)


class PlacementProbeOut(BaseModel):
    question_id: int
    topic: str
    phase: int
    cognitive_level: int


class PlacementOut(BaseModel):
    phase: int
    confidence: float
    #: Below the threshold the estimate is shown but not acted on: thin
    #: evidence should not silently skip foundations.
    confident: bool
    method: str
    #: True when the graph pulled the estimate back -- advanced knowledge
    #: with a missing prerequisite underneath it.
    clamped_by_prerequisites: bool = False
    evidence: dict[str, float] = Field(default_factory=dict)
    known_topics: list[str] = Field(default_factory=list)
    status: str = "UNASSESSED"


class PlacementApplyIn(BaseModel):
    #: question_id -> self-rated mastery on the existing 0-7 ladder. Empty
    #: means "estimate from my history instead".
    answers: dict[int, int] = Field(default_factory=dict)


# ------------------------------------------------------------- Finance

AccountType = Literal["cash", "bank", "savings", "investment", "receivable", "credit", "loan", "other"]
TransactionType = Literal["income", "expense"]
TransactionStatus = Literal["actual", "planned"]
RecurringInterval = Literal["weekly", "monthly", "yearly"]
FinanceGoalCategory = Literal["emergency_fund", "short_term", "long_term", "custom"]
FinanceGoalStatus = Literal["active", "completed", "abandoned"]


class FinanceAccountOut(BaseModel):
    id: int
    name: str
    account_type: AccountType
    currency: str
    opening_balance: float
    current_balance: float
    is_liability: bool
    is_active: bool


class FinanceAccountCreate(BaseModel):
    name: str = Field(min_length=1)
    account_type: AccountType
    currency: str = Field(default="AUD", min_length=3, max_length=3)
    opening_balance: float = Field(default=0)


class FinanceAccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    is_active: bool | None = None


class FinanceCategoryOut(BaseModel):
    id: int
    name: str
    kind: TransactionType
    parent_id: int | None = None
    is_system: bool


class FinanceCategoryCreate(BaseModel):
    name: str = Field(min_length=1)
    kind: TransactionType
    parent_id: int | None = None


class FinanceTransactionOut(BaseModel):
    id: int
    account_id: int
    category_id: int
    type: TransactionType
    amount: float
    currency: str
    occurred_on: DateOnly
    status: TransactionStatus
    description: str | None = None
    notes: str | None = None
    goal_id: int | None = None


class FinanceTransactionCreate(BaseModel):
    account_id: int
    category_id: int
    type: TransactionType
    amount: float = Field(gt=0)
    currency: str = Field(default="AUD", min_length=3, max_length=3)
    occurred_on: DateOnly
    status: TransactionStatus = "actual"
    description: str | None = None
    notes: str | None = None
    goal_id: int | None = None


class FinanceRecurringOut(BaseModel):
    id: int
    description: str
    account_id: int
    category_id: int
    type: TransactionType
    amount: float
    currency: str
    interval: RecurringInterval
    anchor_day: int
    next_due_date: DateOnly
    active: bool


class FinanceRecurringCreate(BaseModel):
    description: str = Field(min_length=1)
    account_id: int
    category_id: int
    type: TransactionType
    amount: float = Field(gt=0)
    currency: str = Field(default="AUD", min_length=3, max_length=3)
    interval: RecurringInterval
    anchor_day: int = Field(ge=0, le=31)
    next_due_date: DateOnly


class FinanceBudgetOut(BaseModel):
    id: int
    category_id: int
    category_name: str
    planned: float
    actual: float
    remaining: float
    utilization_pct: float
    over_budget: bool


class FinanceBudgetUpsert(BaseModel):
    category_id: int
    monthly_amount: float = Field(gt=0)


class FinanceGoalOut(BaseModel):
    id: int
    title: str
    target_amount: float
    #: Always SUM of this goal's linked contributions -- never a
    #: typed-in number (models/finance.py).
    current_amount: float
    remaining: float
    progress_pct: float
    required_monthly_contribution: float | None = None
    currency: str
    target_date: DateOnly | None = None
    category: FinanceGoalCategory
    status: FinanceGoalStatus
    notes: str | None = None


class FinanceGoalCreate(BaseModel):
    title: str = Field(min_length=1)
    target_amount: float = Field(gt=0)
    currency: str = Field(default="AUD", min_length=3, max_length=3)
    target_date: DateOnly | None = None
    category: FinanceGoalCategory = "custom"
    notes: str | None = None


class FinanceGoalUpdate(BaseModel):
    status: FinanceGoalStatus | None = None


class FinanceNetWorthPointOut(BaseModel):
    snapshot_date: DateOnly
    total_assets: float
    total_liabilities: float
    net_worth: float


class FinanceDashboardOut(BaseModel):
    month: DateOnly
    income: float
    expenses: float
    savings: float
    savings_rate_pct: float | None = None
    income_change_pct: float | None = None
    category_breakdown: list[dict[str, float | str]] = Field(default_factory=list)
    outliers: list[dict[str, float | str]] = Field(default_factory=list)
    budgets: list[FinanceBudgetOut] = Field(default_factory=list)
    goals: list[FinanceGoalOut] = Field(default_factory=list)
    upcoming_commitments: list[FinanceRecurringOut] = Field(default_factory=list)
    upcoming_total: float = 0
    net_worth: FinanceNetWorthPointOut | None = None
    net_worth_trend: list[FinanceNetWorthPointOut] = Field(default_factory=list)
    insights: list[str] = Field(default_factory=list)


# --------------------------------------------------------------- Vocabulary

VocabLearningStatus = Literal["known", "learning", "difficult", "need_to_revisit"]
VocabCefrLevel = Literal["A1", "A2", "B1", "B2", "C1", "C2"]


class VocabWordOut(BaseModel):
    id: int
    word: str
    definition: str | None = None
    example_sentence: str | None = None
    pronunciation: str | None = None
    part_of_speech: str | None = None
    category: str | None = None
    cefr_level: VocabCefrLevel | None = None
    synonyms: str | None = None
    antonyms: str | None = None
    word_patterns: str | None = None
    paraphrase: str | None = None
    dictionary_link: str | None = None
    notes: str | None = None
    date_introduced: DateOnly
    learning_status: VocabLearningStatus | None = None
    source: str


class VocabWordCreate(BaseModel):
    word: str = Field(min_length=1)
    definition: str | None = None
    example_sentence: str | None = None
    pronunciation: str | None = None
    part_of_speech: str | None = None
    category: str | None = None
    cefr_level: VocabCefrLevel | None = None
    synonyms: str | None = None
    antonyms: str | None = None
    word_patterns: str | None = None
    paraphrase: str | None = None
    dictionary_link: str | None = None
    notes: str | None = None


class VocabWordUpdate(BaseModel):
    definition: str | None = None
    example_sentence: str | None = None
    pronunciation: str | None = None
    part_of_speech: str | None = None
    category: str | None = None
    cefr_level: VocabCefrLevel | None = None
    synonyms: str | None = None
    antonyms: str | None = None
    word_patterns: str | None = None
    paraphrase: str | None = None
    dictionary_link: str | None = None
    notes: str | None = None


class VocabStatusUpdate(BaseModel):
    learning_status: VocabLearningStatus | None = None


class VocabImportResultOut(BaseModel):
    created: int
    updated: int
    total_rows: int


class VocabSummaryOut(BaseModel):
    """Same shape as the ML/DSA bank summaries -- total, attempted (any
    learning_status set), not attempted (no row touched yet), and a
    breakdown so the bar can show more than one number."""

    total_words: int
    attempted_count: int
    not_attempted_count: int
    known_count: int
    learning_count: int
    difficult_count: int
    need_to_revisit_count: int
    by_level: list[tuple[str, int]] = Field(default_factory=list)


# --------------------------------------------------------------- Overview

class OverviewOut(BaseModel):
    """The cross-domain "Personal OS" summary — every number here is a
    read of an already-computed engine result (readiness_pct,
    month_summary, ...), never a new calculation invented for this
    endpoint alone."""

    readiness_pct: float | None = None
    reviews_due_today: int
    reviews_overdue: int
    active_goal_count: int
    finance_income_this_month: float | None = None
    finance_expenses_this_month: float | None = None
    finance_savings_this_month: float | None = None
    research_minutes_this_week: int
    highlights: list[str] = Field(default_factory=list)


# ------------------------------------------------- Research command center

ResearchTopicStatus = Literal["active", "paused", "completed", "abandoned"]
ResearchPaperStatus = Literal["to_read", "reading", "read"]
ResearchNoteKind = Literal["idea", "question", "hypothesis", "methodology", "note"]
ResearchExperimentStatus = Literal["planned", "running", "completed", "abandoned"]
ResearchMilestoneStatus = Literal["pending", "in_progress", "completed", "missed"]
ResearchVenueType = Literal["conference", "journal", "workshop"]
ResearchRelevance = Literal["high", "medium", "low"]
ResearchOpportunityStatus = Literal[
    "interested", "shortlisted", "preparing", "submitted", "accepted", "rejected", "not_relevant"
]


class ResearchTopicOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: ResearchTopicStatus
    current_blocker: str | None = None


class ResearchTopicCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None


class ResearchTopicUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: ResearchTopicStatus | None = None
    current_blocker: str | None = None


class ResearchPaperOut(BaseModel):
    id: int
    topic_id: int | None = None
    title: str
    authors: str | None = None
    year: int | None = None
    venue: str | None = None
    url: str | None = None
    status: ResearchPaperStatus
    summary: str | None = None
    relevance_note: str | None = None


class ResearchPaperCreate(BaseModel):
    topic_id: int | None = None
    title: str = Field(min_length=1)
    authors: str | None = None
    year: int | None = None
    venue: str | None = None
    url: str | None = None
    status: ResearchPaperStatus = "to_read"
    summary: str | None = None
    relevance_note: str | None = None


class ResearchPaperUpdate(BaseModel):
    topic_id: int | None = None
    title: str | None = None
    authors: str | None = None
    year: int | None = None
    venue: str | None = None
    url: str | None = None
    status: ResearchPaperStatus | None = None
    summary: str | None = None
    relevance_note: str | None = None


class ResearchNoteOut(BaseModel):
    id: int
    topic_id: int | None = None
    paper_id: int | None = None
    kind: ResearchNoteKind
    content: str


class ResearchNoteCreate(BaseModel):
    topic_id: int | None = None
    paper_id: int | None = None
    kind: ResearchNoteKind = "note"
    content: str = Field(min_length=1)


class ResearchExperimentOut(BaseModel):
    id: int
    topic_id: int | None = None
    title: str
    description: str | None = None
    dataset: str | None = None
    methodology_note: str | None = None
    status: ResearchExperimentStatus
    result_summary: str | None = None
    started_date: date | None = None
    completed_date: date | None = None


class ResearchExperimentCreate(BaseModel):
    topic_id: int | None = None
    title: str = Field(min_length=1)
    description: str | None = None
    dataset: str | None = None
    methodology_note: str | None = None
    status: ResearchExperimentStatus = "planned"
    started_date: date | None = None


class ResearchExperimentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    dataset: str | None = None
    methodology_note: str | None = None
    status: ResearchExperimentStatus | None = None
    result_summary: str | None = None
    started_date: date | None = None
    completed_date: date | None = None


class ResearchMilestoneOut(BaseModel):
    id: int
    topic_id: int | None = None
    title: str
    description: str | None = None
    target_date: date | None = None
    status: ResearchMilestoneStatus


class ResearchMilestoneCreate(BaseModel):
    topic_id: int | None = None
    title: str = Field(min_length=1)
    description: str | None = None
    target_date: date | None = None
    status: ResearchMilestoneStatus = "pending"


class ResearchMilestoneUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    target_date: date | None = None
    status: ResearchMilestoneStatus | None = None


class ResearchOpportunityOut(BaseModel):
    id: int
    venue_name: str
    venue_type: ResearchVenueType
    research_area: str | None = None
    submission_deadline: date | None = None
    notification_date: date | None = None
    event_date: date | None = None
    location: str | None = None
    links: list[str] = Field(default_factory=list)
    submission_type: str | None = None
    relevance: ResearchRelevance | None = None
    priority: ResearchRelevance | None = None
    status: ResearchOpportunityStatus
    notes: str | None = None


class ResearchOpportunityCreate(BaseModel):
    venue_name: str = Field(min_length=1)
    venue_type: ResearchVenueType
    research_area: str | None = None
    submission_deadline: date | None = None
    notification_date: date | None = None
    event_date: date | None = None
    location: str | None = None
    links: list[str] = Field(default_factory=list)
    submission_type: str | None = None
    relevance: ResearchRelevance | None = None
    priority: ResearchRelevance | None = None
    notes: str | None = None


class ResearchOpportunityUpdate(BaseModel):
    submission_deadline: date | None = None
    notification_date: date | None = None
    event_date: date | None = None
    location: str | None = None
    relevance: ResearchRelevance | None = None
    priority: ResearchRelevance | None = None
    status: ResearchOpportunityStatus | None = None
    notes: str | None = None


class ResearchAtAGlanceOut(BaseModel):
    active_topic: ResearchTopicOut | None = None
    papers_to_read_count: int
    next_milestone: ResearchMilestoneOut | None = None
    next_opportunity: ResearchOpportunityOut | None = None
    highlights: list[str] = Field(default_factory=list)
