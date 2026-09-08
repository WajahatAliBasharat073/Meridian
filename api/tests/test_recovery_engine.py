from app.engines.recovery import (
    ENERGY_WEIGHT,
    HYDRATION_WEIGHT,
    SLEEP_WEIGHT,
    STRESS_WEIGHT,
    VitalsFixture,
    compute_recovery_score,
    hydration_pct,
)


def test_nothing_logged_scores_nothing() -> None:
    result = compute_recovery_score(VitalsFixture())
    # The whole point: no invented number when the day is empty.
    assert result.score is None
    assert set(result.missing) == {"sleep_hours", "water_ml", "energy", "stress"}


def test_sleep_is_required_to_score_at_all() -> None:
    result = compute_recovery_score(VitalsFixture(water_ml=2500, energy=5, stress=1))
    assert result.score is None
    assert "sleep_hours" in result.missing


def test_a_perfect_day_scores_100() -> None:
    result = compute_recovery_score(
        VitalsFixture(sleep_hours=7.5, water_ml=2500, energy=5, stress=1)
    )
    assert result.score == 100.0
    assert result.missing == []


def test_targets_are_capped_not_extrapolated() -> None:
    # Ten hours of sleep does not earn more than the sleep weight.
    result = compute_recovery_score(
        VitalsFixture(sleep_hours=10.0, water_ml=9000, energy=5, stress=1)
    )
    assert result.score == 100.0


def test_worst_case_scores_zero() -> None:
    result = compute_recovery_score(
        VitalsFixture(sleep_hours=0.0, water_ml=0, energy=0, stress=5)
    )
    assert result.score == 0.0


def test_stress_is_inverted() -> None:
    calm = compute_recovery_score(VitalsFixture(sleep_hours=7.5, stress=1)).components["stress"]
    tense = compute_recovery_score(VitalsFixture(sleep_hours=7.5, stress=5)).components["stress"]
    assert calm == STRESS_WEIGHT
    assert tense == 0.0


def test_partial_day_scores_only_what_was_logged() -> None:
    result = compute_recovery_score(VitalsFixture(sleep_hours=7.5))
    # Sleep alone is present, so only the sleep weight is earned — a missing
    # input is neither zero-with-penalty-elsewhere nor a free average.
    assert result.score == SLEEP_WEIGHT
    assert set(result.missing) == {"water_ml", "energy", "stress"}


def test_components_explain_the_total() -> None:
    result = compute_recovery_score(
        VitalsFixture(sleep_hours=7.5, water_ml=2500, energy=5, stress=1)
    )
    assert result.components == {
        "sleep": SLEEP_WEIGHT,
        "hydration": HYDRATION_WEIGHT,
        "energy": ENERGY_WEIGHT,
        "stress": STRESS_WEIGHT,
    }
    assert round(sum(result.components.values()), 1) == result.score


def test_half_the_sleep_target_earns_half_the_sleep_weight() -> None:
    result = compute_recovery_score(VitalsFixture(sleep_hours=3.75))
    assert result.components["sleep"] == SLEEP_WEIGHT / 2


def test_weights_sum_to_one_hundred() -> None:
    assert SLEEP_WEIGHT + HYDRATION_WEIGHT + ENERGY_WEIGHT + STRESS_WEIGHT == 100.0


def test_hydration_pct_is_none_when_unlogged() -> None:
    assert hydration_pct(None) is None
    assert hydration_pct(0) == 0.0
    assert hydration_pct(1250) == 50.0
    assert hydration_pct(2500) == 100.0
    # Drinking more than the target is still 100%, not 140%.
    assert hydration_pct(3500) == 100.0
