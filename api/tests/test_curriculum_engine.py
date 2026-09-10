"""The eight acceptance tests from the curriculum rebuild spec.

These run against the *real* authored graph (scripts/curriculum_graph.py),
not a toy fixture, because the thing being tested is whether that graph
plus the engine actually sequences the curriculum. A synthetic three-topic
graph would pass while the real one still served a Google case study on
day one.

Questions are synthesised per test rather than read from the database:
the engine is pure, the tests must stay offline, and the shape of a
question is small enough to build honestly.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.engines.curriculum import (
    CLEARED_AT,
    CurriculumQuestion,
    ProgressFixture,
    ReasonCode,
    TopicFixture,
    TopicState,
    build_daily_plan,
    build_learner_state,
)
from scripts.curriculum_graph import TOPICS

TODAY = date(2026, 9, 10)


@pytest.fixture
def topics() -> list[TopicFixture]:
    return [
        TopicFixture(t.slug, t.name, t.phase, t.prereqs, t.gated, i)
        for i, t in enumerate(TOPICS)
    ]


def make_questions(topics: list[TopicFixture]) -> list[CurriculumQuestion]:
    """Four questions per topic at rising cognitive levels, plus a format
    question, so every topic can actually be worked through and mastered."""
    out: list[CurriculumQuestion] = []
    qid = 1
    for t in topics:
        for level in (1, 2, 3, 4):
            out.append(
                CurriculumQuestion(
                    question_id=qid,
                    topic=t.slug,
                    phase=t.phase,
                    axis="knowledge",
                    cognitive_level=level,
                    primary_format="concept",
                    interview_priority="P0",
                )
            )
            qid += 1
        out.append(
            CurriculumQuestion(
                question_id=qid,
                topic=t.slug,
                phase=t.phase,
                axis="format",
                cognitive_level=4,
                primary_format="case_study",
                interview_priority="P0",
            )
        )
        qid += 1
    return out


def master(
    questions: list[CurriculumQuestion], slugs: set[str], when: date
) -> dict[int, ProgressFixture]:
    """Mark every knowledge question in `slugs` as cleared."""
    return {
        q.question_id: ProgressFixture(q.question_id, CLEARED_AT + 1, when)
        for q in questions
        if q.topic in slugs and q.axis == "knowledge"
    }


def phases_of(plan, questions) -> set[int]:
    by_id = {q.question_id: q for q in questions}
    return {by_id[s.question_id].phase for s in plan.selections}


# ---------------------------------------------------------------- test 1 --


def test_1_beginner_gets_foundations_not_genai(topics):
    """A zero-progress learner must not receive advanced material."""
    questions = make_questions(topics)
    seen_phases: set[int] = set()
    seen_topics: set[str] = set()
    progress: dict[int, ProgressFixture] = {}

    for day in range(10):
        plan = build_daily_plan(topics, questions, progress, TODAY + timedelta(days=day))
        assert plan.selections, f"day {day + 1} produced nothing"
        if day == 0:
            assert {sel.phase for sel in plan.selections} == {0}, "day one left P0"
        for s in plan.selections:
            seen_phases.add(s.phase)
            seen_topics.add(s.topic)
            # Simulate the learner answering.
            progress[s.question_id] = ProgressFixture(
                s.question_id, CLEARED_AT + 1, TODAY + timedelta(days=day)
            )

    # Reaching P1 after clearing all of P0 is correct progression, not
    # leakage -- 10 days x 3 questions exhausts the foundations. What must
    # never happen is jumping past the next phase.
    assert seen_phases <= {0, 1}, f"a beginner reached phases {seen_phases}"
    for forbidden in ("genai_system_design", "transformers", "agent_loop", "rag_architecture"):
        assert forbidden not in seen_topics


def test_1b_beginner_never_sees_an_advanced_case_study(topics):
    questions = make_questions(topics)
    plan = build_daily_plan(topics, questions, {}, TODAY)
    by_id = {q.question_id: q for q in questions}
    for s in plan.selections:
        q = by_id[s.question_id]
        assert not (q.primary_format == "case_study" and (q.phase or 0) > 0)


# ---------------------------------------------------------------- test 2 --


def test_2_a_day_may_be_entirely_one_topic(topics):
    """The old engine forbade this. Coherence is the goal, not variety."""
    questions = make_questions(topics)
    # Everything before linear_regression is done; that topic is current.
    done = {
        "python_for_ml", "numpy_vectorization", "pandas_data", "linear_algebra",
        "probability", "statistics", "calculus_optimization", "what_is_ml",
        "train_val_test", "loss_functions", "gradient_descent",
    }
    progress = master(questions, done, TODAY - timedelta(days=1))
    plan = build_daily_plan(
        topics, questions, progress, TODAY, count=4, current_topic="linear_regression"
    )
    assert plan.current_topic == "linear_regression"
    topics_picked = [s.topic for s in plan.selections]
    # At least two of the day's questions come from the current topic --
    # impossible under a one-question-per-module rule.
    assert topics_picked.count("linear_regression") >= 2, topics_picked


# ---------------------------------------------------------------- test 3 --


def test_3_no_case_study_quota_for_a_beginner(topics):
    questions = make_questions(topics)
    for day in range(5):
        plan = build_daily_plan(topics, questions, {}, TODAY + timedelta(days=day))
        by_id = {q.question_id: q for q in questions}
        formats = [by_id[s.question_id].primary_format for s in plan.selections]
        assert "case_study" not in formats, f"day {day + 1}: {formats}"


def test_3b_case_studies_unlock_once_p1_is_reached(topics):
    questions = make_questions(topics)
    p0_and_p1 = {t.slug for t in topics if t.phase <= 1}
    progress = master(questions, p0_and_p1, TODAY - timedelta(days=30))
    state = build_learner_state(topics, questions, progress)
    assert state.reached_phase >= 1
    # The format is now permitted by policy; that is what unlocking means.
    from app.engines.curriculum import FORMAT_MIN_PHASE

    assert state.reached_phase >= FORMAT_MIN_PHASE["case_study"]


# ---------------------------------------------------------------- test 4 --


def test_4_placement_does_not_replay_mastered_foundations(topics):
    """A learner who has demonstrated P0/P1 starts near their frontier."""
    questions = make_questions(topics)
    known = {t.slug for t in topics if t.phase <= 1}
    progress = master(questions, known, TODAY - timedelta(days=60))
    state = build_learner_state(topics, questions, progress)

    assert state.reached_phase >= 1
    for slug in ("linear_regression", "logistic_regression", "what_is_ml"):
        assert state.topic_states[slug] is TopicState.MASTERED
    # Deep learning has opened up.
    assert state.topic_states["neural_networks"] in (
        TopicState.AVAILABLE,
        TopicState.IN_PROGRESS,
    )
    plan = build_daily_plan(topics, questions, progress, TODAY)
    assert all((s.phase or 0) >= 1 for s in plan.selections), [
        (s.topic, s.phase) for s in plan.selections
    ]


# ---------------------------------------------------------------- test 5 --


def test_5_prerequisite_violation_is_a_hard_exclusion(topics):
    """No score may buy past an unmet prerequisite."""
    questions = make_questions(topics)
    # Transformers is P0-priority and highly weighted, but attention is not
    # mastered, so it must never be selected.
    for day in range(20):
        plan = build_daily_plan(topics, questions, {}, TODAY + timedelta(days=day))
        for s in plan.selections:
            assert s.topic != "transformers"
            assert s.topic != "llm_architecture"


def test_5b_locked_topics_are_reported_as_locked(topics):
    questions = make_questions(topics)
    state = build_learner_state(topics, questions, {})
    assert state.topic_states["transformers"] is TopicState.LOCKED
    assert state.topic_states["rag_architecture"] is TopicState.LOCKED
    assert state.topic_states["python_for_ml"] is TopicState.AVAILABLE


# ---------------------------------------------------------------- test 6 --


def test_6_interview_priority_cannot_unlock_an_advanced_phase(topics):
    """P0 interview priority on a P5 topic must remain unavailable.

    This is the specific confusion that produced "Design an LLM chatbot at
    scale" on a beginner's day five.
    """
    questions = [
        CurriculumQuestion(
            question_id=1,
            topic="genai_system_design",
            phase=5,
            axis="format",
            cognitive_level=5,
            primary_format="system_design",
            interview_priority="P0",  # maximum interview priority
        ),
        CurriculumQuestion(
            question_id=2,
            topic="python_for_ml",
            phase=0,
            axis="knowledge",
            cognitive_level=1,
            primary_format="concept",
            interview_priority="P3",  # minimum interview priority
        ),
    ]
    plan = build_daily_plan(topics, questions, {}, TODAY)
    picked = [s.question_id for s in plan.selections]
    assert 1 not in picked, "a P5 question was served on interview priority alone"
    assert picked == [2]


# ---------------------------------------------------------------- test 7 --


def test_7_no_eligible_questions_is_explained_not_crashed(topics):
    plan = build_daily_plan(topics, [], {}, TODAY)
    assert plan.selections == ()
    assert plan.blocked_reason is not None
    assert "NO_ELIGIBLE" in plan.blocked_reason


def test_7b_every_selection_carries_reason_codes(topics):
    questions = make_questions(topics)
    plan = build_daily_plan(topics, questions, {}, TODAY)
    for s in plan.selections:
        assert s.reasons, "a selection had no explanation"
        assert ReasonCode.READY in s.reasons
        assert ReasonCode.PREREQUISITES_MET in s.reasons


def test_7c_rejections_are_explained(topics):
    questions = make_questions(topics)
    plan = build_daily_plan(topics, questions, {}, TODAY)
    assert plan.sample_rejections
    codes = {r.reasons[0] for r in plan.sample_rejections}
    assert ReasonCode.LOCKED_PREREQUISITE in codes


# ------------------------------------------------------------ invariants --


def test_empty_topic_does_not_wall_off_the_curriculum(topics):
    """Invariant 7. P0 has almost no real content; a learner must still be
    able to progress rather than being blocked on questions that do not
    exist."""
    questions = make_questions(topics)
    # Strip every question from one prerequisite topic, as if it were empty.
    questions = [q for q in questions if q.topic != "calculus_optimization"]
    # loss_functions requires BOTH what_is_ml and calculus_optimization, so
    # master the one that has content: the empty topic is then the only
    # thing that could still be blocking.
    progress = master(questions, {"what_is_ml"}, TODAY - timedelta(days=1))
    state = build_learner_state(
        topics, questions, progress, empty_topics=frozenset({"calculus_optimization"})
    )
    assert state.topic_mastery["calculus_optimization"] == 1.0
    assert state.topic_states["loss_functions"] is not TopicState.LOCKED


def test_preview_questions_never_count_toward_mastery(topics):
    """Invariant: a preview must not unlock its dependants."""
    qs = [
        CurriculumQuestion(1, "attention", 2, "knowledge", 1, "concept", preview=True),
        CurriculumQuestion(2, "attention", 2, "knowledge", 2, "concept", preview=True),
    ]
    progress = {
        1: ProgressFixture(1, 7, TODAY),
        2: ProgressFixture(2, 7, TODAY),
    }
    state = build_learner_state(topics, qs, progress)
    assert state.topic_mastery["attention"] == 0.0
    assert state.topic_states["transformers"] is TopicState.LOCKED


def test_plan_is_deterministic(topics):
    questions = make_questions(topics)
    a = build_daily_plan(topics, questions, {}, TODAY)
    b = build_daily_plan(topics, questions, {}, TODAY)
    assert [s.question_id for s in a.selections] == [s.question_id for s in b.selections]
