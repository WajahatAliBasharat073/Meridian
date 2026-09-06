from datetime import date

from app.domain import LADDER_DAYS, ReviewState
from app.engines.repetition import apply_daily_cap, on_attempt, roll_forward_overdue

TODAY = date(2026, 9, 6)


def test_unattempted_schedules_no_review() -> None:
    outcome = on_attempt(None, "problem", 1, "L0", TODAY, engaged=False)
    assert outcome is None


def test_first_engaged_attempt_schedules_from_ladder() -> None:
    outcome = on_attempt(None, "problem", 1, "L2", TODAY, engaged=True)
    assert outcome is not None
    assert outcome.new_level == "L2"
    assert outcome.interval_days == LADDER_DAYS["L2"]
    assert outcome.due_date == date(2026, 9, 9)
    assert outcome.regressed is False


def test_regression_drops_exactly_one_level_and_resets_interval() -> None:
    previous = ReviewState(
        subject_type="problem",
        subject_id=1,
        due_date=TODAY,
        interval_days=LADDER_DAYS["L4"],
        current_level="L4",
        overdue_days=0,
        last_result="success",
        streak_at_level=1,
    )
    # Reported a big drop to L1 — the engine only demotes one level from L4.
    outcome = on_attempt(previous, "problem", 1, "L1", TODAY, engaged=True)
    assert outcome is not None
    assert outcome.new_level == "L3"
    assert outcome.interval_days == LADDER_DAYS["L3"]
    assert outcome.regressed is True
    assert outcome.streak_at_level == 0


def test_two_consecutive_successes_at_same_level_promote() -> None:
    previous = ReviewState(
        subject_type="problem",
        subject_id=1,
        due_date=TODAY,
        interval_days=LADDER_DAYS["L2"],
        current_level="L2",
        overdue_days=0,
        last_result="success",
        streak_at_level=1,  # already had one success at L2
    )
    outcome = on_attempt(previous, "problem", 1, "L2", TODAY, engaged=True)
    assert outcome is not None
    assert outcome.new_level == "L3"  # promoted
    assert outcome.streak_at_level == 0


def test_single_success_at_same_level_does_not_yet_promote() -> None:
    previous = ReviewState(
        subject_type="problem",
        subject_id=1,
        due_date=TODAY,
        interval_days=LADDER_DAYS["L2"],
        current_level="L2",
        overdue_days=0,
        last_result="success",
        streak_at_level=0,
    )
    outcome = on_attempt(previous, "problem", 1, "L2", TODAY, engaged=True)
    assert outcome is not None
    assert outcome.new_level == "L2"
    assert outcome.streak_at_level == 1


def test_explicit_jump_to_higher_level_is_trusted_and_resets_streak() -> None:
    previous = ReviewState(
        subject_type="problem",
        subject_id=1,
        due_date=TODAY,
        interval_days=LADDER_DAYS["L2"],
        current_level="L2",
        overdue_days=0,
        last_result="success",
        streak_at_level=1,
    )
    outcome = on_attempt(previous, "problem", 1, "L5", TODAY, engaged=True)
    assert outcome is not None
    assert outcome.new_level == "L5"
    assert outcome.streak_at_level == 0


def test_mastered_item_gets_60_day_interval() -> None:
    outcome = on_attempt(None, "problem", 1, "L6", TODAY, engaged=True)
    assert outcome is not None
    assert outcome.interval_days == 60


def test_roll_forward_increments_overdue_days_without_moving_due_date() -> None:
    reviews = [
        ReviewState(
            subject_type="problem",
            subject_id=1,
            due_date=date(2026, 9, 1),
            interval_days=7,
            current_level="L3",
            overdue_days=0,
        )
    ]
    rolled = roll_forward_overdue(reviews, TODAY)
    assert rolled[0].due_date == date(2026, 9, 1)
    assert rolled[0].overdue_days == 5


def test_roll_forward_leaves_not_yet_due_reviews_untouched() -> None:
    reviews = [
        ReviewState(
            subject_type="problem",
            subject_id=1,
            due_date=date(2026, 9, 10),
            interval_days=7,
            current_level="L3",
            overdue_days=0,
        )
    ]
    rolled = roll_forward_overdue(reviews, TODAY)
    assert rolled[0].overdue_days == 0


def test_daily_cap_prioritises_failed_then_oldest_overdue() -> None:
    reviews = [
        ReviewState("problem", 1, TODAY, 7, "L3", overdue_days=1, last_result="success"),
        ReviewState("problem", 2, TODAY, 7, "L2", overdue_days=5, last_result="regressed"),
        ReviewState("problem", 3, TODAY, 7, "L4", overdue_days=3, last_result="success"),
    ]
    kept, pushed = apply_daily_cap(reviews, cap=2, today=TODAY)
    assert [r.subject_id for r in kept] == [2, 3]  # failed first, then most overdue
    assert [r.subject_id for r in pushed] == [1]
    assert pushed[0].overdue_days == 2  # bumped, never dropped
    assert pushed[0].due_date == date(2026, 9, 7)


def test_daily_cap_never_drops_anything() -> None:
    reviews = [
        ReviewState("problem", i, TODAY, 7, "L3", overdue_days=i) for i in range(20)
    ]
    kept, pushed = apply_daily_cap(reviews, cap=12, today=TODAY)
    assert len(kept) == 12
    assert len(pushed) == 8
    assert len(kept) + len(pushed) == len(reviews)
