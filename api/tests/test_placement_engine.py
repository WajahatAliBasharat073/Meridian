"""Placement tests. The rule under test is invariant 8: placement may skip
what the learner demonstrably knows, and may never skip a prerequisite."""

from __future__ import annotations

from datetime import date

from app.engines.curriculum import CLEARED_AT, CurriculumQuestion, ProgressFixture, TopicFixture
from app.engines.placement import (
    CONFIDENT_AT,
    estimate_from_history,
    estimate_from_probes,
    select_probe_questions,
)
from scripts.curriculum_graph import TOPICS

TODAY = date(2026, 9, 10)


def topics() -> list[TopicFixture]:
    return [TopicFixture(t.slug, t.name, t.phase, t.prereqs, t.gated, i)
            for i, t in enumerate(TOPICS)]


def questions(ts: list[TopicFixture]) -> list[CurriculumQuestion]:
    out, qid = [], 1
    for t in ts:
        for level in (1, 2, 3, 4):
            out.append(CurriculumQuestion(qid, t.slug, t.phase, "knowledge", level, "concept"))
            qid += 1
    return out


def cleared(qs, slugs):
    return {q.question_id: ProgressFixture(q.question_id, CLEARED_AT + 1, TODAY)
            for q in qs if q.topic in slugs}


def test_no_history_is_unknown_not_beginner():
    """The distinction the whole feature exists for."""
    ts = topics()
    est = estimate_from_history(ts, questions(ts), {})
    assert est.phase == 0
    # Confidence 0 means "we do not know", which is what an empty history
    # actually tells us -- not "this person is a beginner".
    assert est.confidence == 0.0
    assert est.confidence < CONFIDENT_AT


def test_mastered_foundations_place_past_them():
    ts = topics()
    qs = questions(ts)
    known = {t.slug for t in ts if t.phase <= 1}
    est = estimate_from_history(ts, qs, cleared(qs, known))
    assert est.phase >= 1
    assert est.confidence > 0
    assert "linear_regression" in est.known_topics


def test_one_lucky_answer_does_not_place_a_phase():
    """Conservative: a single topic is not evidence of a phase."""
    ts = topics()
    qs = questions(ts)
    est = estimate_from_history(ts, qs, cleared(qs, {"transformers"}))
    assert est.phase == 0


def test_placement_is_clamped_by_the_prerequisite_graph():
    """Invariant 8. Knowing advanced material with a hole underneath it
    must not place the learner past the hole."""
    ts = topics()
    qs = questions(ts)
    # Strong on everything in P3-P5, nothing underneath.
    advanced = {t.slug for t in ts if t.phase >= 3}
    est = estimate_from_history(ts, qs, cleared(qs, advanced))
    assert est.clamped, "an unreachable phase was not clamped"
    assert est.phase < 3


def test_probe_set_is_small_and_spans_the_phases():
    ts = topics()
    probes = select_probe_questions(ts, questions(ts), per_phase=4)
    assert len(probes) <= 6 * 4
    phase_of = {t.slug: t.phase for t in ts}
    assert len({phase_of[p.topic] for p in probes}) >= 5
    # Never a definition, never a synthesis question.
    assert all(2 <= p.cognitive_level <= 4 for p in probes)


def test_probe_stops_at_the_first_gap():
    """The uneven learner: strong at P0-P1, weak at P2, strong at P4.
    They belong at the gap, not at P4."""
    ts = topics()
    probes = select_probe_questions(ts, questions(ts))
    phase_of = {t.slug: t.phase for t in ts}
    answers = {}
    for p in probes:
        ph = phase_of[p.topic]
        answers[p.question_id] = CLEARED_AT + 1 if ph in (0, 1, 4) else 0
    est = estimate_from_probes(ts, probes, answers)
    assert est.phase == 1, est.evidence


def test_probe_confidence_scales_with_how_much_was_answered():
    ts = topics()
    probes = select_probe_questions(ts, questions(ts))
    full = {p.question_id: CLEARED_AT + 1 for p in probes}
    partial = dict(list(full.items())[:3])
    assert (
        estimate_from_probes(ts, probes, full).confidence
        > estimate_from_probes(ts, probes, partial).confidence
    )
