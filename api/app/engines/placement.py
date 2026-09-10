"""Placement: find the highest starting point the evidence actually supports.

The problem this exists for, stated plainly in the audit: *no recorded
progress does not mean beginner*. An experienced engineer opening the app
for the first time has an empty history, and sending them to "what is
supervised learning?" is how a tool gets abandoned in a week.

Two rules keep it honest.

**Conservative.** One right answer on a hard question is not evidence of a
phase. A phase is only credited when several of its topics show
independent evidence, and confidence is reported alongside the estimate so
a thin result can be treated as thin.

**Prerequisite-safe** (invariant 8). Placement may skip material the
learner demonstrably knows; it may never place them somewhere whose
prerequisites are unmet. Skipping ahead is a claim about what they already
know, not permission to ignore the graph -- so the estimate is always
clamped back to what the dependency graph allows.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.engines.curriculum import (
    CLEARED_AT,
    CurriculumQuestion,
    ProgressFixture,
    TopicFixture,
    TopicState,
    build_learner_state,
)

#: Topics within a phase that must show evidence before the phase counts as
#: known. One topic is an anecdote.
MIN_TOPICS_FOR_PHASE = 3

#: Fraction of a topic's probed questions that must be cleared for that
#: topic to count as evidence.
TOPIC_EVIDENCE_THRESHOLD = 0.6

#: Below this, the estimate is reported but not acted on automatically.
CONFIDENT_AT = 0.6

#: How many questions to probe per phase in an interactive placement.
PROBES_PER_PHASE = 4


@dataclass(frozen=True)
class PlacementEstimate:
    phase: int
    confidence: float
    #: Per-phase evidence, for showing the learner why they landed where
    #: they did rather than asserting a number at them.
    evidence: dict[int, float] = field(default_factory=dict)
    known_topics: tuple[str, ...] = ()
    method: str = "history"
    #: True when the graph pulled the estimate back below what the raw
    #: evidence suggested -- i.e. they know advanced material but are
    #: missing something underneath it.
    clamped: bool = False


def estimate_from_history(
    topics: list[TopicFixture],
    questions: list[CurriculumQuestion],
    progress: dict[int, ProgressFixture],
    empty_topics: frozenset[str] = frozenset(),
) -> PlacementEstimate:
    """Estimate a starting phase from whatever progress already exists.

    This is the zero-friction path: an existing user has months of
    `question_progress` and should never be asked to sit an assessment to
    recover what the app already knows about them.
    """
    state = build_learner_state(topics, questions, progress, empty_topics)
    by_phase: dict[int, list[str]] = {}
    for t in topics:
        if t.gated:
            by_phase.setdefault(t.phase, []).append(t.slug)

    evidence: dict[int, float] = {}
    known: list[str] = []
    for phase, slugs in sorted(by_phase.items()):
        # Only count topics that actually have content -- an empty topic
        # proves nothing about the learner either way.
        real = [s for s in slugs if s not in empty_topics]
        if not real:
            evidence[phase] = 0.0
            continue
        strong = [s for s in real if state.topic_mastery.get(s, 0.0) >= TOPIC_EVIDENCE_THRESHOLD]
        known.extend(strong)
        evidence[phase] = len(strong) / len(real)

    # Highest phase with enough independent evidence.
    raw_phase = 0
    for phase in sorted(evidence):
        strong_count = sum(
            1
            for s in by_phase.get(phase, [])
            if s not in empty_topics
            and state.topic_mastery.get(s, 0.0) >= TOPIC_EVIDENCE_THRESHOLD
        )
        if strong_count >= MIN_TOPICS_FOR_PHASE or evidence[phase] >= 0.8:
            raw_phase = max(raw_phase, phase)

    # Invariant 8: never place past what the graph permits. The highest
    # phase with an actually-unlocked topic is the ceiling.
    reachable = 0
    for t in topics:
        if not t.gated:
            continue
        if state.topic_states.get(t.slug) is not TopicState.LOCKED:
            reachable = max(reachable, t.phase)
    phase = min(raw_phase, reachable)

    confidence = evidence.get(phase, 0.0) if phase else (0.9 if not progress else 0.5)
    if not progress:
        # No history at all: this is not "beginner", it is "unknown". Say
        # so with a low confidence rather than asserting P0.
        confidence = 0.0

    return PlacementEstimate(
        phase=phase,
        confidence=round(min(1.0, confidence), 2),
        evidence={k: round(v, 2) for k, v in evidence.items()},
        known_topics=tuple(sorted(known)),
        method="history",
        clamped=raw_phase > phase,
    )


def select_probe_questions(
    topics: list[TopicFixture],
    questions: list[CurriculumQuestion],
    per_phase: int = PROBES_PER_PHASE,
) -> list[CurriculumQuestion]:
    """A short, representative probe set spanning P0..P5.

    Deliberately not the whole bank: the objective is to find the highest
    reliable starting point, which takes a handful of well-chosen
    questions, not 724. Picks mid-level knowledge questions -- a
    definition proves too little, a synthesis question too much.
    """
    phase_of = {t.slug: t.phase for t in topics}
    buckets: dict[int, list[CurriculumQuestion]] = {}
    for q in questions:
        if q.axis != "knowledge" or q.topic is None or q.preview:
            continue
        if not (2 <= q.cognitive_level <= 4):
            continue
        buckets.setdefault(phase_of.get(q.topic, 0), []).append(q)

    out: list[CurriculumQuestion] = []
    for phase in sorted(buckets):
        pool = sorted(buckets[phase], key=lambda q: (q.cognitive_level, q.question_id))
        # Spread across distinct topics so a phase is not judged on one.
        seen: set[str] = set()
        chosen: list[CurriculumQuestion] = []
        for q in pool:
            if q.topic in seen:
                continue
            seen.add(q.topic or "")
            chosen.append(q)
            if len(chosen) >= per_phase:
                break
        out.extend(chosen)
    return out


def estimate_from_probes(
    topics: list[TopicFixture],
    probes: list[CurriculumQuestion],
    answers: dict[int, int],
) -> PlacementEstimate:
    """Estimate from an interactive placement run.

    `answers` maps question_id -> self-rated mastery on the existing 0-7
    ladder, so placement uses the same scale as everything else rather
    than inventing a second one.
    """
    phase_of = {t.slug: t.phase for t in topics}
    per_phase_total: dict[int, int] = {}
    per_phase_ok: dict[int, int] = {}
    known: set[str] = set()

    for q in probes:
        phase = phase_of.get(q.topic or "", 0)
        per_phase_total[phase] = per_phase_total.get(phase, 0) + 1
        if answers.get(q.question_id, 0) >= CLEARED_AT:
            per_phase_ok[phase] = per_phase_ok.get(phase, 0) + 1
            if q.topic:
                known.add(q.topic)

    evidence = {
        p: (per_phase_ok.get(p, 0) / n if n else 0.0) for p, n in per_phase_total.items()
    }

    # Walk up while each phase is convincingly cleared, and stop at the
    # first that is not. Contiguity matters: strength at P4 with a hole at
    # P2 is exactly the uneven learner, and they belong at the hole.
    phase = 0
    for p in sorted(evidence):
        if evidence[p] >= TOPIC_EVIDENCE_THRESHOLD:
            phase = p
        else:
            break

    answered = len(answers)
    confidence = 0.0
    if answered:
        coverage = min(1.0, answered / max(1, len(probes)))
        confidence = round(min(1.0, evidence.get(phase, 0.0) * coverage), 2)

    return PlacementEstimate(
        phase=phase,
        confidence=confidence,
        evidence={k: round(v, 2) for k, v in evidence.items()},
        known_topics=tuple(sorted(known)),
        method="probe",
    )
