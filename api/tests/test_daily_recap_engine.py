from datetime import date

from app.domain import TimeBlockFixture
from app.engines.daily_recap import compute_daily_recap

DAY = date(2026, 9, 6)


def _block(category: str, tier: str, status: str, planned: int, actual: int | None = None) -> TimeBlockFixture:
    return TimeBlockFixture(category=category, tier=tier, status=status, planned_minutes=planned, actual_minutes=actual)


def test_empty_day_is_all_zero_not_a_different_shape() -> None:
    recap = compute_daily_recap([], 0, DAY)

    assert recap.total_blocks == 0
    assert recap.completion_pct is None
    assert recap.category_breakdown == []
    assert recap.suggestions == []
    assert recap.headline == "Nothing was scheduled that day."


def test_strong_day_has_no_low_completion_suggestion() -> None:
    blocks = [_block("Job", "T1", "DONE", 60, 60) for _ in range(9)] + [_block("Job", "T1", "NOT DONE", 60)]
    recap = compute_daily_recap(blocks, problems_attempted=1, recap_date=DAY)

    assert recap.completion_pct == 90.0
    assert "Under half" not in " ".join(recap.suggestions)
    assert recap.headline.startswith("Strong day")


def test_low_completion_triggers_bandwidth_suggestion() -> None:
    blocks = [_block("Job", "T1", "NOT DONE", 60) for _ in range(8)] + [_block("Job", "T1", "DONE", 60, 60) for _ in range(2)]
    recap = compute_daily_recap(blocks, problems_attempted=0, recap_date=DAY)

    assert recap.completion_pct == 20.0
    assert any("Under half" in s for s in recap.suggestions)


def test_rescheduled_threshold() -> None:
    blocks = [_block("Job", "T2", "RESCHEDULED", 30) for _ in range(3)] + [_block("Job", "T2", "DONE", 30, 30)]
    recap = compute_daily_recap(blocks, problems_attempted=0, recap_date=DAY)

    assert recap.rescheduled_count == 3
    assert any("rescheduled" in s for s in recap.suggestions)


def test_weakest_category_flagged() -> None:
    blocks = [
        _block("Prayer", "T1", "DONE", 15, 15),
        _block("Prayer", "T1", "DONE", 15, 15),
        _block("Thesis", "T2", "NOT DONE", 45),
        _block("Thesis", "T2", "NOT DONE", 45),
    ]
    recap = compute_daily_recap(blocks, problems_attempted=0, recap_date=DAY)

    breakdown = {c.category: c for c in recap.category_breakdown}
    assert breakdown["Thesis"].done == 0
    assert any("Thesis" in s for s in recap.suggestions)


def test_deep_work_shortfall_flagged() -> None:
    blocks = [_block("Job", "T1", "DONE", 180, 40)]
    recap = compute_daily_recap(blocks, problems_attempted=0, recap_date=DAY)

    assert recap.deep_work_planned_minutes == 180
    assert recap.deep_work_actual_minutes == 40
    assert any("Deep-work" in s for s in recap.suggestions)


def test_no_problems_attempted_despite_prep_scheduled() -> None:
    blocks = [_block("InterviewPrep", "T1", "NOT DONE", 90)]
    recap = compute_daily_recap(blocks, problems_attempted=0, recap_date=DAY)

    assert any("No problems attempted" in s for s in recap.suggestions)


def test_no_problems_attempted_without_prep_scheduled_is_silent() -> None:
    blocks = [_block("Job", "T1", "DONE", 90, 90)]
    recap = compute_daily_recap(blocks, problems_attempted=0, recap_date=DAY)

    assert not any("No problems attempted" in s for s in recap.suggestions)
