"""The curriculum engine: learner state -> frontier -> eligible -> daily plan.

Pure functions over plain fixtures. No session, no ORM, no clock of its
own -- everything time-dependent is passed in, so the whole thing is
testable and the simulation harness can drive it for 30 fictional days
without a database.

The failure this replaces (measured, see CURRICULUM_AUDIT.md): the old
picker served a zero-progress learner a Google case study, a chatbot
evaluation question and a behavioural question on day one. Three causes,
all addressed here:

  * module diversity was a *hard* rule, so a day could never sit inside
    one topic. Here coherence is the objective and variety is a soft
    tie-breaker.
  * a case study was forced every single day by quota. Here formats
    unlock from knowledge, and their share of the day is a function of
    how far the learner has actually got.
  * "P0 priority" meant *interview* priority, which correlates with
    advanced, and it was the primary sort key. Here readiness is a hard
    filter applied before priority is looked at at all.

The invariant that matters: a prerequisite violation is an exclusion, not
a penalty. No score can buy past it.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

# --------------------------------------------------------------------------
# Tunables. Collected here rather than scattered through the ranking so the
# curriculum's behaviour can be adjusted without reading the algorithm.
# --------------------------------------------------------------------------

#: Mastery on the existing 0-7 ladder at which a question counts as cleared.
#: 3 = "can solve". Below that the learner has seen it, not learned it.
CLEARED_AT = 3

#: Fraction of a topic's core questions that must be cleared to call it
#: mastered. Not 100%: a topic with one awkward question would never open
#: its dependants, and an unreachable gate gets overridden, which teaches
#: nothing.
TOPIC_MASTERY_THRESHOLD = 0.7

#: How much of the day is knowledge rather than format, by phase reached.
#: A beginner practising behavioural questions instead of gradient descent
#: is not preparing; an advanced learner drilling definitions is not either.
FORMAT_RATIO_BY_PHASE: dict[int, float] = {
    0: 0.10,
    1: 0.10,
    2: 0.25,
    3: 0.25,
    4: 0.40,
    5: 0.40,
}

#: Minimum phase the learner must have *reached* before a format becomes
#: eligible at all. This is the "knowledge mastery -> format unlock" rule:
#: a case study is a consolidation exercise and means nothing before there
#: is something to consolidate.
FORMAT_MIN_PHASE: dict[str, int] = {
    "concept": 0,
    "implementation": 0,
    "debugging": 1,
    "case_study": 1,
    "system_design": 2,
    "behavioral": 0,
    "project_deep_dive": 0,
}

#: Spaced review. Index is the 0-7 mastery; value is days until it is due.
REVIEW_INTERVAL_DAYS: dict[int, int] = {0: 0, 1: 1, 2: 2, 3: 4, 4: 7, 5: 14, 6: 30, 7: 60}


@dataclass(frozen=True)
class Weights:
    """Ranking weights. Readiness dominates by construction, and interview
    priority is worth less than every curriculum signal -- that ordering is
    the point, not the exact numbers."""

    current_topic: float = 100.0
    prerequisite_of_current: float = 60.0
    current_phase: float = 40.0
    review_due: float = 50.0
    mastery_gap: float = 30.0
    cognitive_fit: float = 25.0
    format_fit: float = 15.0
    interview_priority: float = 5.0
    cognitive_overreach_penalty: float = 20.0


#: Module-level singleton so the defaults are not constructed per call.
DEFAULT_WEIGHTS = Weights()


class TopicState(StrEnum):
    LOCKED = "LOCKED"
    AVAILABLE = "AVAILABLE"
    IN_PROGRESS = "IN_PROGRESS"
    MASTERED = "MASTERED"


class ReasonCode(StrEnum):
    # selected
    READY = "READY"
    PREREQUISITES_MET = "PREREQUISITES_MET"
    CURRENT_TOPIC = "CURRENT_TOPIC"
    CURRENT_PHASE = "CURRENT_PHASE"
    MASTERY_GAP = "MASTERY_GAP"
    REVIEW_DUE = "REVIEW_DUE"
    FORMAT_APPROPRIATE = "FORMAT_APPROPRIATE"
    COGNITIVE_FIT = "COGNITIVE_FIT"
    PREREQUISITE_REINFORCEMENT = "PREREQUISITE_REINFORCEMENT"
    # rejected
    LOCKED_PREREQUISITE = "LOCKED_PREREQUISITE"
    PHASE_TOO_ADVANCED = "PHASE_TOO_ADVANCED"
    ALREADY_MASTERED = "ALREADY_MASTERED"
    FORMAT_NOT_YET_UNLOCKED = "FORMAT_NOT_YET_UNLOCKED"
    COGNITIVE_TOO_ADVANCED = "COGNITIVE_TOO_ADVANCED"
    NOT_YET_DUE = "NOT_YET_DUE"
    NO_TOPIC = "NO_TOPIC"


@dataclass(frozen=True)
class TopicFixture:
    slug: str
    name: str
    phase: int
    prereqs: tuple[str, ...] = ()
    gated: bool = True
    order_index: int = 0


@dataclass(frozen=True)
class CurriculumQuestion:
    question_id: int
    topic: str | None
    phase: int | None
    axis: str  # knowledge | format
    cognitive_level: int
    primary_format: str
    preview: bool = False
    # Interview priority (P0..P3). Never a curriculum signal -- see the
    # module docstring. Carried only as a weak tie-breaker.
    interview_priority: str | None = None


@dataclass(frozen=True)
class ProgressFixture:
    question_id: int
    mastery: int
    last_rated: date | None


@dataclass(frozen=True)
class Selection:
    question_id: int
    slot: str  # new | reinforce | review
    score: float
    reasons: tuple[ReasonCode, ...]
    topic: str | None
    phase: int | None


@dataclass(frozen=True)
class Rejection:
    question_id: int
    reasons: tuple[ReasonCode, ...]


@dataclass(frozen=True)
class DailyPlan:
    selections: tuple[Selection, ...]
    current_topic: str | None
    current_phase: int | None
    #: Set when there is nothing legitimate to serve. The scheduler must
    #: say so rather than reaching past the frontier for filler.
    blocked_reason: str | None = None
    #: Sampled rejections, for the debug endpoint. Not the whole bank.
    sample_rejections: tuple[Rejection, ...] = ()
    eligible_count: int = 0


@dataclass(frozen=True)
class LearnerState:
    """Everything the engine needs to know about one learner."""

    topic_states: dict[str, TopicState] = field(default_factory=dict)
    topic_mastery: dict[str, float] = field(default_factory=dict)
    reached_phase: int = 0
    current_topic: str | None = None


# --------------------------------------------------------------------------
# Learner state
# --------------------------------------------------------------------------


def topic_mastery_fractions(
    topics: list[TopicFixture],
    questions: list[CurriculumQuestion],
    progress: dict[int, ProgressFixture],
) -> dict[str, float]:
    """Fraction of each topic's *core* questions that are cleared.

    Core means: knowledge axis, not a preview. Format questions exercise a
    topic but do not define whether it is understood, and a preview is
    explicitly excluded from counting toward mastery -- otherwise seeing
    "what is an LLM?" early would help unlock transformers.
    """
    totals: dict[str, int] = {t.slug: 0 for t in topics}
    cleared: dict[str, int] = {t.slug: 0 for t in topics}
    for q in questions:
        if q.topic is None or q.topic not in totals:
            continue
        if q.axis != "knowledge" or q.preview:
            continue
        totals[q.topic] += 1
        p = progress.get(q.question_id)
        if p is not None and p.mastery >= CLEARED_AT:
            cleared[q.topic] += 1
    return {
        slug: (cleared[slug] / totals[slug]) if totals[slug] else 0.0 for slug in totals
    }


def compute_topic_states(
    topics: list[TopicFixture],
    mastery: dict[str, float],
    threshold: float = TOPIC_MASTERY_THRESHOLD,
) -> dict[str, TopicState]:
    """LOCKED / AVAILABLE / IN_PROGRESS / MASTERED for every topic.

    A topic with no questions at all can never be mastered by this rule, so
    it would silently wall off everything downstream. Such a topic is
    treated as AVAILABLE and *transparent* for unlocking purposes -- the
    content gap is reported by the validator instead of quietly blocking
    the learner (invariant 7).
    """
    by_slug = {t.slug: t for t in topics}
    states: dict[str, TopicState] = {}

    def resolve(slug: str, seen: frozenset[str]) -> TopicState:
        if slug in states:
            return states[slug]
        if slug in seen:  # defensive; the graph is validated acyclic
            return TopicState.LOCKED
        topic = by_slug[slug]
        frac = mastery.get(slug, 0.0)

        if not topic.gated:
            state = TopicState.MASTERED if frac >= threshold else TopicState.AVAILABLE
            states[slug] = state
            return state

        for pre in topic.prereqs:
            if pre not in by_slug:
                continue
            # An empty prerequisite topic is handed in already at mastery
            # 1.0 by build_learner_state, so it resolves MASTERED and is
            # transparent here. That is invariant 7: a phase with no
            # content reports as a gap, it does not wall off the learner.
            if resolve(pre, seen | {slug}) is not TopicState.MASTERED:
                states[slug] = TopicState.LOCKED
                return TopicState.LOCKED

        if frac >= threshold:
            state = TopicState.MASTERED
        elif frac > 0:
            state = TopicState.IN_PROGRESS
        else:
            state = TopicState.AVAILABLE
        states[slug] = state
        return state

    for t in topics:
        resolve(t.slug, frozenset())
    return states


def build_learner_state(
    topics: list[TopicFixture],
    questions: list[CurriculumQuestion],
    progress: dict[int, ProgressFixture],
    empty_topics: frozenset[str] = frozenset(),
    current_topic: str | None = None,
) -> LearnerState:
    mastery = topic_mastery_fractions(topics, questions, progress)
    for slug in empty_topics:
        # An empty topic is vacuously satisfied for unlocking purposes.
        mastery[slug] = 1.0
    states = compute_topic_states(topics, mastery)

    reached = 0
    for t in topics:
        if states.get(t.slug) in (TopicState.MASTERED, TopicState.IN_PROGRESS):
            reached = max(reached, t.phase)

    if current_topic is None or states.get(current_topic) in (None, TopicState.LOCKED):
        current_topic = _pick_current_topic(topics, states)

    return LearnerState(
        topic_states=states,
        topic_mastery=mastery,
        reached_phase=reached,
        current_topic=current_topic,
    )


def _pick_current_topic(
    topics: list[TopicFixture], states: dict[str, TopicState]
) -> str | None:
    """The earliest topic that is started but not finished, else the
    earliest that is open. Curriculum order, never interview priority."""
    ordered = sorted(topics, key=lambda t: (t.phase, t.order_index))
    for t in ordered:
        if t.gated and states.get(t.slug) is TopicState.IN_PROGRESS:
            return t.slug
    for t in ordered:
        if t.gated and states.get(t.slug) is TopicState.AVAILABLE:
            return t.slug
    return None


# --------------------------------------------------------------------------
# Eligibility
# --------------------------------------------------------------------------


def evaluate(
    q: CurriculumQuestion,
    state: LearnerState,
    progress: dict[int, ProgressFixture],
    today: date,
    topic_phase: dict[str, int],
) -> tuple[bool, tuple[ReasonCode, ...]]:
    """Is this question servable, and why (or why not)?

    Hard exclusions first. A prerequisite violation can never be scored
    past -- that is invariant 5, and it is the difference between a
    curriculum and a weighted shuffle.
    """
    if q.topic is None:
        return False, (ReasonCode.NO_TOPIC,)

    ts = state.topic_states.get(q.topic)
    if ts is None:
        return False, (ReasonCode.NO_TOPIC,)
    if ts is TopicState.LOCKED:
        return False, (ReasonCode.LOCKED_PREREQUISITE,)

    phase = topic_phase.get(q.topic, 0)
    if phase > state.reached_phase + 1:
        # One phase of lookahead is deliberate: the frontier should be able
        # to spill into the start of the next phase, not the whole bank.
        return False, (ReasonCode.PHASE_TOO_ADVANCED,)

    if q.axis == "format":
        min_phase = FORMAT_MIN_PHASE.get(q.primary_format, 0)
        if state.reached_phase < min_phase:
            return False, (ReasonCode.FORMAT_NOT_YET_UNLOCKED,)

    p = progress.get(q.question_id)
    if p is not None:
        if p.mastery >= 7:
            return False, (ReasonCode.ALREADY_MASTERED,)
        if p.last_rated is not None:
            due_in = REVIEW_INTERVAL_DAYS.get(p.mastery, 60)
            if (today - p.last_rated).days < due_in:
                return False, (ReasonCode.NOT_YET_DUE,)

    reasons: list[ReasonCode] = [ReasonCode.READY, ReasonCode.PREREQUISITES_MET]
    if q.topic == state.current_topic:
        reasons.append(ReasonCode.CURRENT_TOPIC)
    if phase == state.reached_phase:
        reasons.append(ReasonCode.CURRENT_PHASE)
    if p is None:
        reasons.append(ReasonCode.MASTERY_GAP)
    else:
        reasons.append(ReasonCode.REVIEW_DUE)
    if q.cognitive_level <= _target_level(state, q.topic):
        reasons.append(ReasonCode.COGNITIVE_FIT)
    if q.axis == "format":
        reasons.append(ReasonCode.FORMAT_APPROPRIATE)
    return True, tuple(reasons)


def _target_level(state: LearnerState, topic: str) -> int:
    """Cognitive level the learner should be working at in this topic.

    Rises with topic mastery: definitions first, synthesis last. The +1
    keeps one rung of stretch available rather than capping at exactly
    what has been demonstrated.
    """
    frac = state.topic_mastery.get(topic, 0.0)
    return min(5, 1 + int(frac * 5) + 1)


def score(
    q: CurriculumQuestion,
    state: LearnerState,
    reasons: tuple[ReasonCode, ...],
    topic_phase: dict[str, int],
    current_prereqs: frozenset[str],
    rotation_seed: int = 0,
    w: Weights = DEFAULT_WEIGHTS,
) -> float:
    s = 0.0
    if ReasonCode.CURRENT_TOPIC in reasons:
        s += w.current_topic
    elif q.topic in current_prereqs:
        s += w.prerequisite_of_current
    if ReasonCode.CURRENT_PHASE in reasons:
        s += w.current_phase
    if ReasonCode.REVIEW_DUE in reasons:
        s += w.review_due
    if ReasonCode.MASTERY_GAP in reasons:
        s += w.mastery_gap
    if ReasonCode.COGNITIVE_FIT in reasons:
        s += w.cognitive_fit
    else:
        s -= w.cognitive_overreach_penalty
    if ReasonCode.FORMAT_APPROPRIATE in reasons:
        s += w.format_fit

    # Interview priority enters last and small. It answers "how often does
    # this come up", never "is this next".
    rank = {"P0": 3, "P1": 2, "P2": 1, "P3": 0}.get(q.interview_priority or "P3", 0)
    s += w.interview_priority * rank / 3.0

    # Tie-break: deterministic within a day, rotating across days.
    #
    # Without the day term, a learner who does not rate anything sees the
    # identical three questions tomorrow -- the top of the ranking never
    # moves, because nothing about their state moved. Mixing the date in
    # shuffles only among near-equal candidates: the weights above are
    # whole numbers apart, so this can reorder ties without ever
    # promoting a less-ready question over a more-ready one.
    jitter = ((q.question_id * 31 + rotation_seed * 17) % 97) / 97.0
    return s - jitter * 0.9


# --------------------------------------------------------------------------
# The daily plan
# --------------------------------------------------------------------------


def build_daily_plan(
    topics: list[TopicFixture],
    questions: list[CurriculumQuestion],
    progress: dict[int, ProgressFixture],
    today: date,
    count: int = 3,
    current_topic: str | None = None,
    empty_topics: frozenset[str] = frozenset(),
    weights: Weights = DEFAULT_WEIGHTS,
) -> DailyPlan:
    """Slot-based: new learning, reinforcement, review.

    Slots are roles, not quotas on *topics*. All three can legitimately be
    the same topic -- a day of nothing but linear regression is a good day
    when linear regression is what you are learning. That is the direct
    replacement for the module-diversity rule.
    """
    state = build_learner_state(topics, questions, progress, empty_topics, current_topic)
    topic_phase = {t.slug: t.phase for t in topics}
    by_slug = {t.slug: t for t in topics}
    cur = by_slug.get(state.current_topic) if state.current_topic else None
    current_prereqs = frozenset(cur.prereqs) if cur else frozenset()

    eligible: list[tuple[CurriculumQuestion, float, tuple[ReasonCode, ...]]] = []
    rejections: list[Rejection] = []
    for q in questions:
        ok, reasons = evaluate(q, state, progress, today, topic_phase)
        if ok:
            eligible.append(
                (
                    q,
                    score(
                        q,
                        state,
                        reasons,
                        topic_phase,
                        current_prereqs,
                        today.toordinal(),
                        weights,
                    ),
                    reasons,
                )
            )
        elif len(rejections) < 200:
            rejections.append(Rejection(q.question_id, reasons))

    if not eligible:
        return DailyPlan(
            selections=(),
            current_topic=state.current_topic,
            current_phase=state.reached_phase,
            blocked_reason=(
                "NO_ELIGIBLE_QUESTIONS: nothing is both unlocked and due today. "
                "This usually means the current phase has no content yet -- run "
                "the curriculum validator."
            ),
            sample_rejections=tuple(rejections[:50]),
            eligible_count=0,
        )

    eligible.sort(key=lambda t: -t[1])
    format_ratio = FORMAT_RATIO_BY_PHASE.get(state.reached_phase, 0.25)
    max_format = max(0, round(count * format_ratio))

    picks: list[Selection] = []
    used: set[int] = set()
    format_used = 0

    Predicate = Callable[[CurriculumQuestion, tuple[ReasonCode, ...]], bool]

    def take(pred: Predicate, slot: str) -> bool:
        nonlocal format_used
        for q, sc, reasons in eligible:
            if q.question_id in used:
                continue
            if q.axis == "format" and format_used >= max_format:
                continue
            if not pred(q, reasons):
                continue
            used.add(q.question_id)
            if q.axis == "format":
                format_used += 1
            picks.append(
                Selection(q.question_id, slot, round(sc, 2), reasons, q.topic, q.phase)
            )
            return True
        return False

    # Slot 1: forward progress on the current topic.
    take(lambda q, r: ReasonCode.CURRENT_TOPIC in r and ReasonCode.MASTERY_GAP in r, "new") or \
        take(lambda q, r: ReasonCode.MASTERY_GAP in r, "new")

    # Slot 2: reinforcement -- a prerequisite, or the current topic lower down.
    take(lambda q, r: q.topic in current_prereqs, "reinforce") or \
        take(lambda q, r: ReasonCode.CURRENT_TOPIC in r, "reinforce") or \
        take(lambda q, r: True, "reinforce")

    # Slot 3+: spaced review, else application, else anything eligible.
    while len(picks) < count:
        if take(lambda q, r: ReasonCode.REVIEW_DUE in r, "review"):
            continue
        if take(lambda q, r: q.axis == "format", "review"):
            continue
        if take(lambda q, r: True, "review"):
            continue
        break

    return DailyPlan(
        selections=tuple(picks),
        current_topic=state.current_topic,
        current_phase=state.reached_phase,
        blocked_reason=None,
        sample_rejections=tuple(rejections[:50]),
        eligible_count=len(eligible),
    )
