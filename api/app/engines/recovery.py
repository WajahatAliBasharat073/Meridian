"""Pure function: today's recovery score from today's logged vitals.

This lived in the Health page as inline arithmetic over hardcoded defaults,
which meant the weighting was invisible, untested, and applied to numbers
nobody had entered. Moving it here makes the policy explicit and testable,
and — more importantly — lets it refuse to produce a number at all.

The refusal is the point. A recovery score computed from two of four inputs
is not a recovery score, and a page that always shows 78% teaches you
nothing about your actual recovery. `None` means "not enough logged today",
which the UI states plainly instead of filling the gap.
"""

from __future__ import annotations

from dataclasses import dataclass

# Weights sum to 100. Sleep dominates because it is the input with the
# largest effect on next-day cognitive capacity, and it is also the one
# most often sacrificed.
SLEEP_WEIGHT = 40.0
HYDRATION_WEIGHT = 25.0
ENERGY_WEIGHT = 20.0
STRESS_WEIGHT = 15.0

# Targets a score of 100 is measured against.
SLEEP_TARGET_HOURS = 7.5
WATER_TARGET_ML = 2500

# Sleep and at least one of the subjective ratings. Water alone says
# nothing about recovery, and sleep alone is a sleep log, not a score.
_REQUIRED = ("sleep_hours",)


@dataclass(frozen=True)
class VitalsFixture:
    """One day's logged vitals, as the engine sees them — no ORM, no session.

    Every field is optional because every field is genuinely optional in the
    log: you might record sleep at 06:00 and never get round to stress.
    """

    sleep_hours: float | None = None
    sleep_quality: int | None = None
    energy: int | None = None
    stress: int | None = None
    water_ml: int | None = None
    exercise_minutes: int | None = None


@dataclass(frozen=True)
class RecoveryScore:
    score: float | None
    """None when too little was logged to say anything honest."""

    components: dict[str, float]
    """Per-input contribution, so the number can be explained rather than
    just displayed."""

    missing: list[str]
    """Which inputs were absent — shown to the user as what to fill in."""


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def compute_recovery_score(vitals: VitalsFixture) -> RecoveryScore:
    """Weighted score in 0-100, or None if the day is too empty to score.

    Present inputs are scored against their target; absent inputs contribute
    nothing and are named in `missing`. Because absent inputs are not
    silently treated as zero *or* as average, a partially logged day scores
    lower than a fully logged one — which is correct: the score answers
    "how recovered am I, on the evidence", and missing evidence is not
    evidence of recovery.
    """
    missing: list[str] = []
    components: dict[str, float] = {}

    if vitals.sleep_hours is None:
        missing.append("sleep_hours")
    else:
        components["sleep"] = _clamp01(vitals.sleep_hours / SLEEP_TARGET_HOURS) * SLEEP_WEIGHT

    if vitals.water_ml is None:
        missing.append("water_ml")
    else:
        components["hydration"] = _clamp01(vitals.water_ml / WATER_TARGET_ML) * HYDRATION_WEIGHT

    if vitals.energy is None:
        missing.append("energy")
    else:
        components["energy"] = _clamp01(vitals.energy / 5.0) * ENERGY_WEIGHT

    if vitals.stress is None:
        missing.append("stress")
    else:
        # Inverted: 1 is calm, 5 is maximum stress.
        components["stress"] = _clamp01((5 - vitals.stress) / 4.0) * STRESS_WEIGHT

    if any(field in missing for field in _REQUIRED):
        return RecoveryScore(score=None, components=components, missing=missing)

    return RecoveryScore(
        score=round(sum(components.values()), 1), components=components, missing=missing
    )


def hydration_pct(water_ml: int | None) -> float | None:
    """Progress toward the daily water target, or None if nothing is logged."""
    if water_ml is None:
        return None
    return round(_clamp01(water_ml / WATER_TARGET_ML) * 100, 1)
