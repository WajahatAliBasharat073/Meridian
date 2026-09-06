from datetime import date, datetime, timedelta

from app.domain import AttemptFixture, ProblemFixture, ReviewState
from app.engines.summary import compute_dashboard_summary

TODAY = date(2026, 9, 6)


def test_empty_account_is_all_zero_not_a_different_shape() -> None:
    summary = compute_dashboard_summary([], [], [], TODAY, days_window=7)

    assert summary.total_problems == 0
    assert summary.attempted_count == 0
    assert all(m.count == 0 for m in summary.mastery_distribution)
    assert summary.pattern_coverage == []
    assert len(summary.attempts_by_day) == 7
    assert all(d.count == 0 for d in summary.attempts_by_day)
    assert summary.reviews_due_count == 0
    assert summary.reviews_overdue_count == 0
    assert summary.readiness_pct is None


def _problems() -> list[ProblemFixture]:
    return [
        ProblemFixture(1, "P1", "arrays_hashing", "Easy", scheduled_date=TODAY, scheduled_slot=1),
        ProblemFixture(2, "P2", "arrays_hashing", "Medium", scheduled_date=TODAY, scheduled_slot=2),
        ProblemFixture(3, "P3", "two_pointers", "Medium", scheduled_date=TODAY, scheduled_slot=3),
        ProblemFixture(4, "P4", "two_pointers", "Hard"),  # not in curriculum
    ]


def test_mastery_distribution_counts_only_attempted_problems() -> None:
    attempts = [
        AttemptFixture(1, datetime(2026, 9, 1), "L6"),
        AttemptFixture(2, datetime(2026, 9, 2), "L3"),
    ]
    summary = compute_dashboard_summary(_problems(), attempts, [], TODAY)

    counts = {m.level: m.count for m in summary.mastery_distribution}
    assert counts["L6"] == 1
    assert counts["L3"] == 1
    assert counts["L0"] == 0  # unattempted problems 3 and 4 never counted as L0
    assert summary.attempted_count == 2


def test_pattern_coverage_ratio_and_sort_weakest_first() -> None:
    attempts = [
        AttemptFixture(1, datetime(2026, 9, 1), "L6"),  # arrays_hashing: 1/2 at L5+
        AttemptFixture(3, datetime(2026, 9, 2), "L2"),  # two_pointers: 0/1 at L5+ (only P3 scheduled)
    ]
    summary = compute_dashboard_summary(_problems(), attempts, [], TODAY)

    by_pattern = {pc.pattern: pc for pc in summary.pattern_coverage}
    assert by_pattern["arrays_hashing"].scheduled_count == 2
    assert by_pattern["arrays_hashing"].l5_plus_count == 1
    assert by_pattern["arrays_hashing"].ratio == 0.5
    assert by_pattern["two_pointers"].scheduled_count == 1
    assert by_pattern["two_pointers"].l5_plus_count == 0
    assert by_pattern["two_pointers"].ratio == 0.0

    # weakest (lowest ratio) first
    assert summary.pattern_coverage[0].pattern == "two_pointers"


def test_attempts_by_day_includes_zero_days_and_is_chronological() -> None:
    attempts = [
        AttemptFixture(1, datetime(2026, 9, 6, 10, 0), "L2"),
        AttemptFixture(2, datetime(2026, 9, 6, 14, 0), "L1"),
        AttemptFixture(3, datetime(2026, 9, 4, 9, 0), "L3"),
    ]
    summary = compute_dashboard_summary(_problems(), attempts, [], TODAY, days_window=5)

    assert [d.day for d in summary.attempts_by_day] == [TODAY - timedelta(days=i) for i in (4, 3, 2, 1, 0)]
    by_day = {d.day: d.count for d in summary.attempts_by_day}
    assert by_day[TODAY] == 2
    assert by_day[TODAY - timedelta(days=2)] == 1
    assert by_day[TODAY - timedelta(days=1)] == 0


def test_reviews_due_and_overdue_counts() -> None:
    reviews = [
        ReviewState("problem", 1, TODAY, 7, "L3", last_result="success"),
        ReviewState("problem", 2, TODAY - timedelta(days=3), 7, "L2", overdue_days=3, last_result="success"),
        ReviewState("problem", 3, TODAY + timedelta(days=2), 7, "L4", last_result="success"),
        ReviewState("vocab", 1, TODAY, 1, "L0", last_result="success"),  # different subject_type, ignored
    ]
    summary = compute_dashboard_summary(_problems(), [], reviews, TODAY)

    assert summary.reviews_due_count == 1
    assert summary.reviews_overdue_count == 1


def test_readiness_pct_is_none_when_no_problems_exist() -> None:
    summary = compute_dashboard_summary([], [AttemptFixture(1, datetime(2026, 9, 1), "L6")], [], TODAY)
    assert summary.readiness_pct is None


def test_readiness_pct_computed_from_l5_plus_over_total() -> None:
    attempts = [
        AttemptFixture(1, datetime(2026, 9, 1), "L6"),
        AttemptFixture(2, datetime(2026, 9, 2), "L5"),
    ]
    summary = compute_dashboard_summary(_problems(), attempts, [], TODAY)
    assert summary.readiness_pct == 50.0  # 2 of 4 problems at L5+
