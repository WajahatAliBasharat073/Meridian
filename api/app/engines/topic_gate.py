"""Pure functions: is this topic's problem list unlocked, and did this
verification attempt pass?

The split that matters here — an LLM supplies the *judgement* (does this
code cover a circular list, is this answer about `prev` actually right), and
this module supplies the *policy* (what fraction counts as covered, what
score passes, how long a pass lasts). Policy in a pure function means the
thresholds are visible, testable and changeable without touching a prompt,
and a model that drifts can't quietly move the bar.

Verification expires on purpose. Understanding a structure once and then
forgetting it is the exact failure this whole gate exists for — the OOP
knowledge that lapsed did so because nothing ever re-checked it. So a pass
is valid for VERIFICATION_TTL_DAYS and then the topic needs defending again.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum

# Coverage: most of the topic's required items must be present. Not 100% —
# a checklist item can be arguably out of scope for one person's
# implementation, and a gate that never opens gets overridden every time,
# which teaches nothing.
BUILD_PASS_THRESHOLD = 0.8

# The closed-book stage is the real check, so it is stricter, but still
# short of perfect: one fumbled explanation out of five is a human being
# under a timer, not a lack of understanding.
DEFEND_PASS_THRESHOLD = 0.7

VERIFICATION_TTL_DAYS = 30


class GateState(StrEnum):
    LOCKED = "locked"
    """Never verified, or the last attempt failed."""

    UNLOCKED = "unlocked"
    """Verified, within its validity window."""

    EXPIRED = "expired"
    """Was verified, but the pass has aged out — defend it again."""

    UNVERIFIED_OVERRIDE = "unverified_override"
    """Opened via the escape hatch. Usable, and permanently marked as
    never actually demonstrated."""


@dataclass(frozen=True)
class AttemptFixture:
    """One verification attempt, as the engine sees it — no ORM, no session."""

    topic: str
    started_at: datetime
    passed: bool | None
    passed_at: datetime | None
    override: bool


@dataclass(frozen=True)
class TopicGate:
    topic: str
    state: GateState
    passed_at: datetime | None
    expires_at: datetime | None
    days_until_expiry: int | None
    attempt_count: int
    overridden: bool

    @property
    def problems_visible(self) -> bool:
        """An override unlocks the problems; it just never claims they were
        earned. Only LOCKED and EXPIRED actually hide them."""
        return self.state in (GateState.UNLOCKED, GateState.UNVERIFIED_OVERRIDE)


def compute_gate(
    topic: str,
    attempts: list[AttemptFixture],
    now: datetime,
    ttl_days: int = VERIFICATION_TTL_DAYS,
) -> TopicGate:
    """Current gate state for one topic from its attempt history.

    An override is deliberately checked *after* a live pass: if the topic was
    later verified for real, that pass is what should be reported, not the
    old bypass.
    """
    mine = [a for a in attempts if a.topic == topic]
    passes = [a for a in mine if a.passed and a.passed_at is not None]
    overridden = any(a.override for a in mine)

    if passes:
        latest = max(passes, key=lambda a: a.passed_at)  # type: ignore[arg-type,return-value]
        assert latest.passed_at is not None
        expires_at = latest.passed_at + timedelta(days=ttl_days)
        if now < expires_at:
            remaining = (expires_at - now).days
            return TopicGate(
                topic=topic,
                state=GateState.UNLOCKED,
                passed_at=latest.passed_at,
                expires_at=expires_at,
                days_until_expiry=remaining,
                attempt_count=len(mine),
                overridden=overridden,
            )
        # A stale pass does not fall back to an old override — the topic
        # needs defending again either way.
        return TopicGate(
            topic=topic,
            state=GateState.EXPIRED,
            passed_at=latest.passed_at,
            expires_at=expires_at,
            days_until_expiry=0,
            attempt_count=len(mine),
            overridden=overridden,
        )

    if overridden:
        return TopicGate(
            topic=topic,
            state=GateState.UNVERIFIED_OVERRIDE,
            passed_at=None,
            expires_at=None,
            days_until_expiry=None,
            attempt_count=len(mine),
            overridden=True,
        )

    return TopicGate(
        topic=topic,
        state=GateState.LOCKED,
        passed_at=None,
        expires_at=None,
        days_until_expiry=None,
        attempt_count=len(mine),
        overridden=False,
    )


def build_score(covered: int, required: int) -> float:
    """Fraction of the topic's required items the submission covers."""
    if required <= 0:
        return 0.0
    return min(1.0, max(0.0, covered / required))


def build_passes(score: float) -> bool:
    return score >= BUILD_PASS_THRESHOLD


# Per-question verdicts the grader may return, and what each is worth.
# "partial" earns half rather than nothing: an explanation that is right in
# substance but missed an edge case is not the same as not knowing.
VERDICT_WEIGHTS: dict[str, float] = {
    "correct": 1.0,
    "partial": 0.5,
    "wrong": 0.0,
}


def defend_score(verdicts: list[str]) -> float:
    if not verdicts:
        return 0.0
    total = sum(VERDICT_WEIGHTS.get(v, 0.0) for v in verdicts)
    return total / len(verdicts)


def defend_passes(score: float) -> bool:
    return score >= DEFEND_PASS_THRESHOLD


def attempt_passed(build: float, defend: float) -> bool:
    """Both stages must clear their own bar — a strong viva does not excuse
    an implementation that never covered half the structure, and complete
    code does not excuse being unable to explain it."""
    return build_passes(build) and defend_passes(defend)
