from app.engines.punctuality import (
    MIN_SESSIONS_FOR_INSIGHT,
    SessionDelay,
    compute_punctuality,
)


def _s(category: str, delay: int, hour: int = 18) -> SessionDelay:
    return SessionDelay(category=category, hour_of_day=hour, start_delay_minutes=delay)


def test_no_sessions_reports_not_enough_data_rather_than_zeroes() -> None:
    r = compute_punctuality([])

    assert r.enough_data is False
    assert r.session_count == 0
    assert r.on_time_pct is None
    assert r.avg_delay_minutes is None
    assert r.observations == []
    assert r.min_sessions_needed == MIN_SESSIONS_FOR_INSIGHT


def test_below_threshold_refuses_to_characterise() -> None:
    r = compute_punctuality([_s("InterviewPrep", 30), _s("InterviewPrep", 2)])

    assert r.enough_data is False
    assert r.session_count == 2
    assert r.on_time_pct is None  # no "50% on time" off two rows
    assert r.started_late == 1
    assert r.started_early_or_on_time == 1


def test_on_time_grace_window_counts_small_delays_as_on_time() -> None:
    r = compute_punctuality([_s("Job", d) for d in (0, 2, 5, 5, 4)])

    assert r.enough_data is True
    assert r.on_time_pct == 100.0
    assert r.started_late == 0


def test_late_starts_counted_and_averaged() -> None:
    r = compute_punctuality([_s("Job", d) for d in (0, 10, 20, 30, 40)])

    assert r.session_count == 5
    assert r.started_early_or_on_time == 1  # only the 0
    assert r.started_late == 4
    assert r.avg_delay_minutes == 20.0
    assert r.median_delay_minutes == 20.0


def test_median_preferred_in_copy_when_outliers_skew_mean() -> None:
    # Four punctual sessions and one catastrophic one.
    r = compute_punctuality([_s("Job", d) for d in (0, 1, 2, 3, 200)])

    assert r.median_delay_minutes == 2.0
    assert r.avg_delay_minutes == 41.2
    assert any("pulling it up" in o for o in r.observations)


def test_category_ranking_ignores_categories_with_too_few_sessions() -> None:
    sessions = [_s("Job", 1), _s("Job", 2), _s("Job", 0)] + [_s("Thesis", 90)] + [_s("Reading", 3)]
    r = compute_punctuality(sessions)

    ranked = {c.category for c in [r.worst_category, r.best_category] if c}
    # Thesis is late but has only 1 session — must not be crowned "worst".
    assert "Thesis" not in ranked
    assert r.worst_category is not None and r.worst_category.category == "Job"


def test_by_category_breakdown_is_per_category_real_numbers() -> None:
    sessions = [_s("Job", 10), _s("Job", 20), _s("Prep", 0), _s("Prep", 0), _s("Prep", 0)]
    r = compute_punctuality(sessions)

    by = {c.category: c for c in r.by_category}
    assert by["Job"].avg_delay_minutes == 15.0
    assert by["Job"].on_time_pct == 0.0
    assert by["Prep"].avg_delay_minutes == 0.0
    assert by["Prep"].on_time_pct == 100.0


def test_early_starts_are_not_penalised() -> None:
    # Negative delay = started before the scheduled time.
    r = compute_punctuality([_s("Job", d) for d in (-10, -5, 0, 1, 2)])

    assert r.on_time_pct == 100.0
    assert r.avg_delay_minutes == -2.4
