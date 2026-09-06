from app.domain import BandwidthInput
from app.engines.bandwidth import plan_bandwidth


def _input(**overrides) -> BandwidthInput:
    defaults = dict(
        minutes_available=60,
        energy=3,
        overdue_review_count=0,
        overdue_review_minutes=0,
        hour_of_day=10,
    )
    defaults.update(overrides)
    return BandwidthInput(**defaults)


def test_very_low_minutes_is_minimum_viable_day() -> None:
    plan = plan_bandwidth(_input(minutes_available=15))
    assert plan.band == "MINIMUM_VIABLE_DAY"
    assert plan.max_new_problems == 0
    assert plan.allow_new_hard is False


def test_high_energy_and_two_hours_allows_hard() -> None:
    plan = plan_bandwidth(_input(minutes_available=120, energy=5, hour_of_day=10))
    assert plan.band == "HIGH"
    assert plan.allow_new_hard is True
    assert plan.max_new_problems > 0


def test_high_minutes_but_low_energy_downgrades_band() -> None:
    plan = plan_bandwidth(_input(minutes_available=120, energy=1))
    assert plan.band != "HIGH"
    assert plan.allow_new_hard is False


def test_low_energy_short_window_excludes_new_hard() -> None:
    plan = plan_bandwidth(_input(minutes_available=30, energy=2))
    assert plan.band == "LOW"
    assert plan.allow_new_hard is False
    assert plan.max_new_problems == 0


def test_never_proposes_more_new_problems_than_time_allows() -> None:
    plan = plan_bandwidth(_input(minutes_available=65, energy=5, hour_of_day=10))
    from app.engines.bandwidth import MINUTES_PER_NEW_PROBLEM

    assert plan.max_new_problems * MINUTES_PER_NEW_PROBLEM <= 65


def test_large_overdue_backlog_overrides_energy() -> None:
    plan = plan_bandwidth(
        _input(minutes_available=120, energy=5, overdue_review_count=30, overdue_review_minutes=130)
    )
    assert plan.allow_new_hard is False
    assert plan.allow_new_medium is False
    assert plan.max_new_problems == 0
    assert plan.include_reviews is True


def test_late_night_softens_new_hard_even_at_high_band() -> None:
    plan = plan_bandwidth(_input(minutes_available=120, energy=5, hour_of_day=23))
    assert plan.band == "HIGH"
    assert plan.allow_new_hard is False


def test_spare_minutes_suggestion_is_concrete_not_vague() -> None:
    # 95 min leaves a 5-min remainder after 3 whole 30-min problem slots —
    # deliberately not a round multiple of MINUTES_PER_NEW_PROBLEM, so the
    # leftover that funds the suggestion actually exists.
    plan = plan_bandwidth(
        _input(minutes_available=95, energy=5, overdue_review_count=6, overdue_review_minutes=24, hour_of_day=10)
    )
    assert plan.spare_minutes_suggestion is not None
    assert "spare minutes" in plan.spare_minutes_suggestion
    assert "overdue" in plan.spare_minutes_suggestion


def test_no_spare_suggestion_when_nothing_left_over() -> None:
    plan = plan_bandwidth(_input(minutes_available=20, energy=1))
    assert plan.spare_minutes_suggestion is None


def test_mock_only_offered_at_high_band() -> None:
    medium = plan_bandwidth(_input(minutes_available=90, energy=5, hour_of_day=10))
    assert medium.band == "MEDIUM"
    assert medium.include_mock is False

    high = plan_bandwidth(_input(minutes_available=150, energy=5, hour_of_day=10))
    assert high.band == "HIGH"
    assert high.include_mock is True


def test_mock_excluded_when_backlog_override_wins_even_at_high_band_minutes() -> None:
    plan = plan_bandwidth(
        _input(minutes_available=125, energy=5, overdue_review_count=25, overdue_review_minutes=130, hour_of_day=10)
    )
    assert plan.include_mock is False
