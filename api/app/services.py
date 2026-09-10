"""Composition layer: routers stay thin, repositories stay pure-adapter,
engines stay pure-function. This module is the only place that wires all
three together for a given use case."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.domain import (
    BandwidthInput,
    DailyRecap,
    DailyTheoryPick,
    DashboardSummary,
    Recommendation,
    TimeBlockFixture,
    WeeklyReview,
)
from app.engines.bandwidth import MINUTES_PER_REVIEW
from app.engines.curriculum import build_daily_plan
from app.engines.daily_recap import compute_daily_recap
from app.engines.daily_theory import pick_daily_theory
from app.engines.recommender import recommend
from app.engines.repetition import on_attempt
from app.engines.summary import compute_dashboard_summary
from app.engines.theory_pace import TheoryPaceReport, compute_theory_pace
from app.engines.weekly_review import compute_weekly_review
from app.models.core import TimeBlock
from app.models.questions import Question
from app.repositories import concepts as concepts_repo
from app.repositories import curriculum as curriculum_repo
from app.repositories import goals as goals_repo
from app.repositories import problems as problems_repo
from app.repositories import questions as questions_repo
from app.repositories import reviews as reviews_repo
from app.repositories import schedule as schedule_repo

DEFAULT_ENERGY = 3


async def infer_bandwidth_input(
    session: AsyncSession,
    user_id: uuid.UUID,
    today: date,
    settings: Settings,
    minutes_override: int | None = None,
    energy_override: int | None = None,
) -> BandwidthInput:
    """minutes/energy are explicit when the user states them (build prompt
    5.3); otherwise inferred from unclaimed blocks and last night's sleep."""
    overdue = [r for r in await reviews_repo.get_due_or_overdue(session, user_id, today) if r.due_date < today]
    overdue_count = len(overdue)
    overdue_minutes = overdue_count * MINUTES_PER_REVIEW

    if minutes_override is not None:
        minutes = minutes_override
    else:
        prayer_times = await schedule_repo.get_or_compute_prayer_times(session, today, settings)
        blocks = await schedule_repo.get_blocks_for_date(session, user_id, today, prayer_times)
        minutes = sum(b.planned_minutes for b in blocks if b.status == "NOT DONE")

    energy = energy_override if energy_override is not None else DEFAULT_ENERGY

    now_hour = datetime.now(ZoneInfo(settings.timezone)).hour

    return BandwidthInput(
        minutes_available=minutes,
        energy=energy,
        overdue_review_count=overdue_count,
        overdue_review_minutes=overdue_minutes,
        hour_of_day=now_hour,
    )


async def get_recommendations(
    session: AsyncSession,
    user_id: uuid.UUID,
    today: date,
    max_results: int = 1,
) -> list[Recommendation]:
    review_states = await reviews_repo.get_problem_reviews(session, user_id)
    problem_fixtures = await problems_repo.get_problem_fixtures(session)
    attempt_fixtures = await problems_repo.get_attempt_fixtures(session, user_id)
    return recommend(
        reviews=review_states,
        problems=problem_fixtures,
        attempts=attempt_fixtures,
        today=today,
        max_results=max_results,
    )


async def submit_attempt(
    session: AsyncSession,
    user_id: uuid.UUID,
    problem_id: int,
    mastery_level: str,
    minutes: int | None,
    hint_used: bool,
    key_insight: str | None,
    today: date,
    solve_method: str | None = None,
    understood_approach_independently: bool | None = None,
    reached_optimal: bool | None = None,
    notes: str | None = None,
) -> tuple[str, int]:
    """Writes the attempt, then advances (or creates) its review row.
    Returns (due_date, interval_days) for the one-line confirmation the UI
    shows immediately (build prompt 5.2: "Next review: 14 Sep, 7 days").

    The previous mastery level is read from the last attempt *before* this
    one is written — `reviews` deliberately has no level column of its own
    (design doc 5.2/5.3: mastery lives only on `problem_attempts`)."""
    previous_attempt = await problems_repo.get_latest_attempt_for_problem(session, user_id, problem_id)

    await problems_repo.record_attempt(
        session,
        user_id,
        problem_id,
        mastery_level,
        minutes,
        hint_used,
        key_insight,
        solve_method,
        understood_approach_independently,
        reached_optimal,
        notes,
    )

    existing_review = await reviews_repo.get_review_state(session, user_id, "problem", problem_id)
    previous_state = None
    if existing_review is not None and previous_attempt is not None:
        from app.domain import ReviewState

        previous_state = ReviewState(
            subject_type="problem",
            subject_id=problem_id,
            due_date=existing_review.due_date,
            interval_days=existing_review.interval_days,
            current_level=previous_attempt.mastery_level,
            overdue_days=existing_review.overdue_days,
            last_result=existing_review.last_result,
        )

    engaged = minutes is not None and minutes > 0
    outcome = on_attempt(previous_state, "problem", problem_id, mastery_level, today, engaged=engaged)
    if outcome is None:
        return today.isoformat(), 0

    await reviews_repo.upsert_review(session, user_id, outcome)
    return outcome.due_date.isoformat(), outcome.interval_days


async def submit_concept_attempt(
    session: AsyncSession,
    user_id: uuid.UUID,
    concept_id: int,
    mastery_level: str,
    notes: str | None,
    today: date,
) -> tuple[str, int]:
    """Same shape as `submit_attempt`, for the `ml_concept` subject type
    the repetition engine and `reviews` table already support."""
    previous_attempt = await concepts_repo.get_latest_attempt_for_concept(session, user_id, concept_id)

    await concepts_repo.record_attempt(session, user_id, concept_id, mastery_level, notes)

    existing_review = await reviews_repo.get_review_state(session, user_id, "ml_concept", concept_id)
    previous_state = None
    if existing_review is not None and previous_attempt is not None:
        from app.domain import ReviewState

        previous_state = ReviewState(
            subject_type="ml_concept",
            subject_id=concept_id,
            due_date=existing_review.due_date,
            interval_days=existing_review.interval_days,
            current_level=previous_attempt.mastery_level,
            overdue_days=existing_review.overdue_days,
            last_result=existing_review.last_result,
        )

    engaged = True
    outcome = on_attempt(previous_state, "ml_concept", concept_id, mastery_level, today, engaged=engaged)
    if outcome is None:
        return today.isoformat(), 0

    await reviews_repo.upsert_review(session, user_id, outcome)
    return outcome.due_date.isoformat(), outcome.interval_days


async def get_dashboard_summary(
    session: AsyncSession, user_id: uuid.UUID, today: date, days_window: int = 14
) -> DashboardSummary:
    review_states = await reviews_repo.get_problem_reviews(session, user_id)
    problem_fixtures = await problems_repo.get_problem_fixtures(session)
    attempt_fixtures = await problems_repo.get_attempt_fixtures(session, user_id)
    return compute_dashboard_summary(
        problems=problem_fixtures,
        attempts=attempt_fixtures,
        reviews=review_states,
        today=today,
        days_window=days_window,
    )


async def get_current_block(session: AsyncSession, blocks: list[TimeBlock], settings: Settings) -> TimeBlock | None:
    now = datetime.now(ZoneInfo(settings.timezone)).time()
    for b in blocks:
        if b.start_resolved and b.end_resolved and b.start_resolved <= now < b.end_resolved:
            return b
    return None


async def get_daily_recap(
    session: AsyncSession, user_id: uuid.UUID, recap_date: date, settings: Settings
) -> DailyRecap:
    prayer_times = await schedule_repo.get_or_compute_prayer_times(session, recap_date, settings)
    blocks = await schedule_repo.get_blocks_for_date(session, user_id, recap_date, prayer_times)
    block_fixtures = [
        TimeBlockFixture(
            category=b.category,
            tier=b.tier,
            status=b.status,
            planned_minutes=b.planned_minutes,
            actual_minutes=b.actual_minutes,
        )
        for b in blocks
    ]
    problems_attempted = await problems_repo.count_problems_attempted_on(session, user_id, recap_date)
    return compute_daily_recap(block_fixtures, problems_attempted, recap_date)


async def get_weekly_review(
    session: AsyncSession, user_id: uuid.UUID, window_end: date, days: int = 7
) -> WeeklyReview:

    window_start = window_end - timedelta(days=days - 1)
    blocks = await goals_repo.blocks_since(session, user_id, window_start)
    reflections = await goals_repo.list_reflections_since(session, user_id, window_start)

    block_fixtures = [
        TimeBlockFixture(
            category=b.category,
            tier=b.tier,
            status=b.status,
            planned_minutes=b.planned_minutes,
            actual_minutes=b.actual_minutes,
        )
        for b in blocks
    ]
    block_dates = [b.date for b in blocks]
    mood_counts: dict[str, int] = {}
    for r in reflections:
        mood_counts[r.mood] = mood_counts.get(r.mood, 0) + 1

    return compute_weekly_review(
        block_fixtures, block_dates, mood_counts, window_start, window_end, days
    )


async def get_daily_theory_questions(
    session: AsyncSession,
    user_id: uuid.UUID,
    today: date,
    count: int = 3,
    case_study_count: int = 1,
) -> list[tuple[Question, int, DailyTheoryPick]]:
    """The day's questions, chosen by the curriculum engine.

    Replaces the old module-diversity + case-study-quota picker. That one
    drew from all 724 questions and served a zero-progress learner a
    Google case study on day one; this one draws only from the learner's
    frontier. See CURRICULUM_AUDIT.md and app/engines/curriculum.py.

    `case_study_count` is retained in the signature for callers that still
    pass it, but is deliberately ignored: an unconditional daily case
    study is precisely the behaviour being removed. Format share is now a
    function of how far the learner has actually got.
    """
    topics = await curriculum_repo.get_topic_fixtures(session)
    if not topics:
        # The graph has not been seeded yet. Fall back to the legacy picker
        # rather than returning nothing, so an un-migrated database still
        # serves questions.
        return await _legacy_daily_theory(session, user_id, today, count, case_study_count)

    questions = await curriculum_repo.get_curriculum_questions(session)
    progress = await curriculum_repo.get_progress_fixtures(session, user_id)
    empty = await curriculum_repo.get_empty_topics(session)
    frontier = await curriculum_repo.get_frontier(session, user_id)

    plan = build_daily_plan(
        topics,
        questions,
        progress,
        today,
        count=count,
        current_topic=frontier.current_topic if frontier else None,
        empty_topics=empty,
    )
    if not plan.selections:
        return []

    questions_by_id = await questions_repo.get_questions_by_ids(
        session, [s.question_id for s in plan.selections]
    )
    out: list[tuple[Question, int, DailyTheoryPick]] = []
    for sel in plan.selections:
        q = questions_by_id.get(sel.question_id)
        if q is None:
            continue
        mastery = progress[sel.question_id].mastery if sel.question_id in progress else 0
        out.append(
            (
                q,
                mastery,
                DailyTheoryPick(
                    question_id=sel.question_id,
                    # Kept for the existing UI, which renders a badge from
                    # it. It is now a description of the question, not a
                    # quota that forced it into the day.
                    is_case_study=(q.question_type == "case_study"),
                    reason=_describe(sel),
                ),
            )
        )
    return out


def _describe(sel) -> str:  # type: ignore[no-untyped-def]
    """Human-readable version of the structured reason codes."""
    slot = {
        "new": "New in your current topic",
        "reinforce": "Reinforcing a prerequisite",
        "review": "Spaced review",
    }.get(sel.slot, sel.slot)
    codes = {r.value for r in sel.reasons}
    extra = []
    if "REVIEW_DUE" in codes:
        extra.append("due for review")
    if "MASTERY_GAP" in codes:
        extra.append("not yet attempted")
    if "CURRENT_TOPIC" in codes:
        extra.append("current topic")
    return f"{slot}" + (f" - {', '.join(extra)}" if extra else "")


async def _legacy_daily_theory(
    session: AsyncSession,
    user_id: uuid.UUID,
    today: date,
    count: int,
    case_study_count: int,
) -> list[tuple[Question, int, DailyTheoryPick]]:
    """The pre-curriculum picker. Only reachable before the topic graph is
    seeded; kept so a database mid-migration still works."""
    fixtures = await questions_repo.get_all_question_fixtures(session)
    progress = await questions_repo.get_question_progress_fixtures(session, user_id)
    picks = pick_daily_theory(
        fixtures, progress, today, count=count, case_study_count=case_study_count
    )
    if not picks:
        return []
    questions_by_id = await questions_repo.get_questions_by_ids(
        session, [p.question_id for p in picks]
    )
    progress_by_id = {p.question_id: p for p in progress}
    out: list[tuple[Question, int, DailyTheoryPick]] = []
    for pick in picks:
        q = questions_by_id.get(pick.question_id)
        if q is None:
            continue
        mastery = (
            progress_by_id[pick.question_id].mastery if pick.question_id in progress_by_id else 0
        )
        out.append((q, mastery, pick))
    return out


async def get_theory_pace(
    session: AsyncSession,
    user_id: uuid.UUID,
    daily_counts: list[int] | None = None,
    baseline_daily_count: int = 3,
) -> TheoryPaceReport:
    """How long clearing the theory backlog takes at your actual recorded
    pace, and what changing the daily count buys — composes real timing
    data with the pure `compute_theory_pace` engine."""
    timings = await questions_repo.get_question_timing_fixtures(session, user_id)
    backlog = await questions_repo.get_backlog_count(session, user_id)
    return compute_theory_pace(
        timings,
        backlog_count=backlog,
        daily_counts=daily_counts or [2, 3, 4, 5, 6],
        baseline_daily_count=baseline_daily_count,
    )
