from datetime import date, timedelta

from app.domain import TimeBlockFixture
from app.engines.weekly_review import compute_weekly_review

START = date(2026, 8, 31)
END = date(2026, 9, 6)


def _block(day_offset: int, category: str, tier: str, status: str, planned: int, actual: int | None = None):
    return (START + timedelta(days=day_offset)), TimeBlockFixture(
        category=category, tier=tier, status=status, planned_minutes=planned, actual_minutes=actual
    )


def _split(pairs):
    dates = [d for d, _ in pairs]
    blocks = [b for _, b in pairs]
    return blocks, dates


def test_empty_week_is_all_zero_not_a_different_shape() -> None:
    review = compute_weekly_review([], [], {}, START, END, 7)

    assert review.total_minutes_logged == 0
    assert review.days_active == 0
    assert review.completion_pct is None
    assert review.category_minutes == []
    assert review.what_went_well == []
    assert review.what_to_improve == []


def test_days_active_counts_distinct_dates_with_real_completion() -> None:
    blocks, dates = _split(
        [
            _block(0, "Job", "T1", "DONE", 60, 60),
            _block(0, "Job", "T1", "NOT DONE", 60),
            _block(1, "Job", "T1", "DONE", 60, 60),
            _block(2, "Job", "T1", "NOT DONE", 60),
        ]
    )
    review = compute_weekly_review(blocks, dates, {}, START, END, 7)

    assert review.days_active == 2  # day 0 and day 1 had a real completion; day 2 did not


def test_strong_week_flags_high_completion_and_active_days() -> None:
    blocks, dates = _split([_block(i, "Job", "T1", "DONE", 60, 60) for i in range(5)])
    review = compute_weekly_review(blocks, dates, {}, START, END, 7)

    assert review.completion_pct == 100.0
    assert any("Active 5 of 7" in s for s in review.what_went_well)
    assert any("Held 100.0%" in s for s in review.what_went_well)


def test_low_completion_flagged_as_improvement() -> None:
    blocks, dates = _split(
        [_block(0, "Job", "T1", "DONE", 60, 60)] + [_block(0, "Job", "T1", "NOT DONE", 60) for _ in range(4)]
    )
    review = compute_weekly_review(blocks, dates, {}, START, END, 7)

    assert review.completion_pct == 20.0
    assert any("Only" in s and "%" in s for s in review.what_to_improve)


def test_category_minutes_sums_only_completed_work() -> None:
    blocks, dates = _split(
        [
            _block(0, "Job", "T1", "DONE", 60, 55),
            _block(1, "Thesis", "T2", "DONE", 30, 30),
            _block(2, "Job", "T1", "NOT DONE", 60),
        ]
    )
    review = compute_weekly_review(blocks, dates, {}, START, END, 7)

    by_cat = {c.category: c.minutes for c in review.category_minutes}
    assert by_cat["Job"] == 55
    assert by_cat["Thesis"] == 30
    assert review.total_minutes_logged == 85


def test_rescheduled_threshold_flagged() -> None:
    blocks, dates = _split([_block(0, "Job", "T2", "RESCHEDULED", 30) for _ in range(5)])
    review = compute_weekly_review(blocks, dates, {}, START, END, 7)

    assert review.rescheduled_count == 5
    assert any("rescheduled" in s for s in review.what_to_improve)


def test_short_focus_sessions_flagged() -> None:
    blocks, dates = _split([_block(0, "Job", "T1", "DONE", 60, 15) for _ in range(3)])
    review = compute_weekly_review(blocks, dates, {}, START, END, 7)

    assert review.avg_focus_session_minutes == 15.0
    assert any("short for deep work" in s for s in review.what_to_improve)


def test_mood_distribution_passthrough() -> None:
    review = compute_weekly_review([], [], {"good": 3, "normal": 2}, START, END, 7)

    by_mood = {m.mood: m.count for m in review.mood_distribution}
    assert by_mood == {"good": 3, "normal": 2}
