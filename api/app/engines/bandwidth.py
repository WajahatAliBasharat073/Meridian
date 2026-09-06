"""Bandwidth engine (build prompt 5.3): fits work to today's stated
capacity instead of padding a short window with more than fits.

Thresholds below (minute buckets, energy cutoffs, minutes-per-review) are
this module's reading of the build prompt's behaviour table — the docs
give bucket examples ("~1h", "~30min") rather than exact boundaries, so
they are named constants, tunable in one place, not scattered magic
numbers. `hour_of_day` softening new-Hard problems late at night is this
module's own addition (not stated in the docs) since the build prompt
lists time-of-day as an input without giving its rule; flagged here for
confirmation.

Reviews are always a baseline activity (`include_reviews` is true
whenever any are due) and are not subtracted from the new-problem time
budget — new-problem capacity is sized off the full stated minutes. The
one exception is a large backlog, which outranks new problems entirely
(build prompt 5.3's table). This keeps "spare minutes" meaningful: it is
time left over *after* the core plan, which can then be offered against
the *whole* overdue count — exactly the "40 spare minutes, 6 overdue
reviews, ~35 min to clear" example in the build prompt, not some already
-partially-cleared remainder.
"""

from __future__ import annotations

from app.domain import BandwidthInput, BandwidthPlan

MVD_MINUTES_CEILING = 20
LOW_MINUTES_CEILING = 45
MEDIUM_MINUTES_CEILING = 120

LOW_ENERGY_CEILING = 2
HIGH_ENERGY_FLOOR = 4

MINUTES_PER_NEW_PROBLEM = 30
MINUTES_PER_REVIEW = 4  # matches the ~60min/15-review November forecast

# Backlog is "large" once clearing it alone would consume the whole budget.
BACKLOG_OVERRIDE_RATIO = 1.0

LATE_HOUR_CUTOFF = 22
EARLY_HOUR_FLOOR = 5


def plan_bandwidth(inp: BandwidthInput) -> BandwidthPlan:
    if inp.minutes_available < MVD_MINUTES_CEILING:
        return BandwidthPlan(
            band="MINIMUM_VIABLE_DAY",
            allow_new_hard=False,
            allow_new_medium=False,
            max_new_problems=0,
            include_reviews=inp.overdue_review_count > 0,
            include_mock=False,
            headline=(
                f"Very low bandwidth ({inp.minutes_available} min) — "
                "Minimum Viable Day only."
            ),
        )

    backlog_overrides = (
        inp.overdue_review_count > 0
        and inp.overdue_review_minutes >= inp.minutes_available * BACKLOG_OVERRIDE_RATIO
    )
    if backlog_overrides:
        return BandwidthPlan(
            band=_band_from_minutes_and_energy(inp),
            allow_new_hard=False,
            allow_new_medium=False,
            max_new_problems=0,
            include_reviews=True,
            include_mock=False,
            headline=(
                f"Overdue backlog is large ({inp.overdue_review_count} reviews, "
                f"~{inp.overdue_review_minutes} min) — clearing it outranks new "
                "problems today, regardless of energy."
            ),
        )

    band = _band_from_minutes_and_energy(inp)
    is_late_or_early = inp.hour_of_day >= LATE_HOUR_CUTOFF or inp.hour_of_day < EARLY_HOUR_FLOOR
    max_new = inp.minutes_available // MINUTES_PER_NEW_PROBLEM

    if band == "LOW":
        return BandwidthPlan(
            band=band,
            allow_new_hard=False,
            allow_new_medium=False,
            max_new_problems=0,
            include_reviews=True,
            include_mock=False,
            headline=(
                f"Low energy, {inp.minutes_available} min — reviews, vocabulary, "
                "flashcards, or reading a solution. No new Hard problems."
            ),
        )

    if band == "MEDIUM":
        plan = BandwidthPlan(
            band=band,
            allow_new_hard=False,
            allow_new_medium=True,
            max_new_problems=max_new,
            include_reviews=True,
            include_mock=False,
            headline=(
                f"Medium energy, {inp.minutes_available} min — scheduled Medium "
                "problems, a theory topic, or ML coding."
            ),
        )
    else:  # HIGH
        # HIGH already requires >=120 min (see _band_from_minutes_and_energy),
        # comfortably enough for a mock — it's an alternative to new
        # problems, not stacked on top, so it isn't gated on `max_new`.
        plan = BandwidthPlan(
            band=band,
            allow_new_hard=not is_late_or_early,
            allow_new_medium=True,
            max_new_problems=max_new,
            include_reviews=True,
            include_mock=True,
            headline=(
                f"High energy, {inp.minutes_available} min — a new Hard/Medium "
                "problem, unfamiliar system design, or a timed mock."
            ),
        )

    return _attach_spare_minutes_suggestion(plan, inp, max_new)


def _band_from_minutes_and_energy(inp: BandwidthInput) -> str:
    if inp.minutes_available < LOW_MINUTES_CEILING:
        band = "LOW"
    elif inp.minutes_available < MEDIUM_MINUTES_CEILING:
        band = "MEDIUM"
    else:
        band = "HIGH" if inp.energy >= HIGH_ENERGY_FLOOR else "MEDIUM"

    if inp.energy <= LOW_ENERGY_CEILING and band == "HIGH":
        band = "MEDIUM"
    if inp.energy <= LOW_ENERGY_CEILING and band == "MEDIUM":
        band = "LOW"
    return band


def _attach_spare_minutes_suggestion(
    plan: BandwidthPlan, inp: BandwidthInput, max_new: int
) -> BandwidthPlan:
    """Never "you could do more" — a concrete number or nothing (build
    prompt 5.3)."""
    spare = inp.minutes_available - max_new * MINUTES_PER_NEW_PROBLEM
    if spare < MINUTES_PER_REVIEW or inp.overdue_review_count <= 0:
        return plan

    clearable = min(inp.overdue_review_count, spare // MINUTES_PER_REVIEW)
    if clearable <= 0:
        return plan

    suggestion = (
        f"You have {spare} spare minutes and {inp.overdue_review_count} overdue "
        f"reviews; clearing {clearable} takes ~{clearable * MINUTES_PER_REVIEW} min."
    )
    return BandwidthPlan(**{**plan.__dict__, "spare_minutes_suggestion": suggestion})
