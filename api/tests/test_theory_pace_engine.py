from app.engines.theory_pace import (
    MIN_QUESTIONS_FOR_INSIGHT,
    QuestionTiming,
    compute_theory_pace,
)

DAILY_COUNTS = [2, 3, 4, 5, 6]


def test_below_minimum_questions_refuses_to_estimate() -> None:
    timings = [QuestionTiming(i, total_minutes=10, rating_count=1) for i in range(1, 4)]
    assert len(timings) < MIN_QUESTIONS_FOR_INSIGHT

    report = compute_theory_pace(timings, backlog_count=100, daily_counts=DAILY_COUNTS)

    assert report.enough_data is False
    assert report.questions_with_data == 3
    assert report.avg_minutes_per_question is None
    assert report.projections == []
    # The backlog count itself is real and known even without a pace
    # estimate — it should still be surfaced, just with no projection.
    assert report.backlog_count == 100


def test_average_is_weighted_by_rating_events_not_by_question() -> None:
    # One question reviewed 9 times at 10 min/review, one seen once at
    # 100 min. Event-weighted average is 190/10 = 19, not the naive
    # per-question mean of (10+100)/2 = 55.
    timings = [
        QuestionTiming(1, total_minutes=90, rating_count=9),
        QuestionTiming(2, total_minutes=100, rating_count=1),
        *[QuestionTiming(i, total_minutes=20, rating_count=2) for i in range(3, 6)],
    ]
    report = compute_theory_pace(timings, backlog_count=0, daily_counts=DAILY_COUNTS)

    assert report.enough_data is True
    total_minutes = 90 + 100 + 20 * 3
    total_events = 9 + 1 + 2 * 3
    expected_avg = round(total_minutes / total_events, 1)
    assert report.avg_minutes_per_question == expected_avg


def test_zero_backlog_needs_no_days_projection() -> None:
    timings = [QuestionTiming(i, total_minutes=15, rating_count=1) for i in range(1, 6)]
    report = compute_theory_pace(timings, backlog_count=0, daily_counts=DAILY_COUNTS)

    assert report.enough_data is True
    assert all(p.days_to_clear_backlog == 0 for p in report.projections)
    assert all(p.days_saved_vs_baseline == 0 for p in report.projections)


def test_higher_daily_count_reduces_days_to_clear_and_costs_more_minutes() -> None:
    timings = [QuestionTiming(i, total_minutes=20, rating_count=1) for i in range(1, 6)]
    # avg = 20 min/question exactly
    report = compute_theory_pace(timings, backlog_count=60, daily_counts=[3, 4])
    by_count = {p.daily_count: p for p in report.projections}

    assert report.avg_minutes_per_question == 20.0
    assert by_count[3].daily_minutes == 60
    assert by_count[3].days_to_clear_backlog == 20  # 60 / 3
    assert by_count[4].daily_minutes == 80
    assert by_count[4].days_to_clear_backlog == 15  # 60 / 4, rounded up
    # Moving from the 3/day baseline to 4/day: +20 min/day, 5 days sooner.
    assert by_count[4].minutes_delta_vs_baseline == 20
    assert by_count[4].days_saved_vs_baseline == 5
    # The baseline itself nets to zero against its own projection.
    assert by_count[3].minutes_delta_vs_baseline == 0
    assert by_count[3].days_saved_vs_baseline == 0


def test_backlog_not_evenly_divisible_rounds_up_days() -> None:
    timings = [QuestionTiming(i, total_minutes=10, rating_count=1) for i in range(1, 6)]
    report = compute_theory_pace(timings, backlog_count=10, daily_counts=[3])
    # 10 questions at 3/day is 4 days (3+3+3+1), not 3.33 rounded down.
    assert report.projections[0].days_to_clear_backlog == 4


def test_exactly_minimum_questions_is_enough() -> None:
    timings = [
        QuestionTiming(i, total_minutes=10, rating_count=1) for i in range(1, MIN_QUESTIONS_FOR_INSIGHT + 1)
    ]
    report = compute_theory_pace(timings, backlog_count=50, daily_counts=[3])
    assert report.enough_data is True
    assert report.questions_with_data == MIN_QUESTIONS_FOR_INSIGHT
