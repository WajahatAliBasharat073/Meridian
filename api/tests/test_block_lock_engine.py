from datetime import time

from app.engines.block_lock import (
    EARLY_COMPLETION_GUARD_MINUTES,
    LOCK_THRESHOLD,
    is_block_locked,
    is_too_early_to_complete,
)


def test_not_locked_before_block_starts() -> None:
    assert is_block_locked(time(9, 0), 60, now=time(8, 59), has_any_focus_session=False) is False


def test_not_locked_just_after_start() -> None:
    assert is_block_locked(time(9, 0), 60, now=time(9, 5), has_any_focus_session=False) is False


def test_not_locked_right_at_threshold_minus_one_minute() -> None:
    # 60-minute block, threshold 70% = 42 minutes.
    assert is_block_locked(time(9, 0), 60, now=time(9, 41), has_any_focus_session=False) is False


def test_locked_at_exact_threshold() -> None:
    assert is_block_locked(time(9, 0), 60, now=time(9, 42), has_any_focus_session=False) is True


def test_locked_well_past_threshold() -> None:
    assert is_block_locked(time(9, 0), 60, now=time(10, 0), has_any_focus_session=False) is True


def test_never_locked_if_a_focus_session_already_exists() -> None:
    # Even long past the window, having ever engaged with it un-locks it.
    assert is_block_locked(time(9, 0), 60, now=time(12, 0), has_any_focus_session=True) is False


def test_zero_or_negative_planned_minutes_never_locks() -> None:
    assert is_block_locked(time(9, 0), 0, now=time(23, 0), has_any_focus_session=False) is False


def test_missing_scheduled_start_never_locks() -> None:
    assert is_block_locked(None, 60, now=time(23, 0), has_any_focus_session=False) is False


def test_threshold_is_seventy_percent() -> None:
    assert LOCK_THRESHOLD == 0.7


def test_too_early_well_before_end() -> None:
    # 60-minute block ending at 10:00 — 30 minutes still left.
    assert is_too_early_to_complete(time(10, 0), now=time(9, 30)) is True


def test_too_early_right_outside_guard_window() -> None:
    # 6 minutes left — one more than the 5-minute guard.
    assert is_too_early_to_complete(time(10, 0), now=time(9, 54)) is True


def test_not_too_early_at_exact_guard_boundary() -> None:
    # Exactly 5 minutes left — the guard window itself is completable.
    assert is_too_early_to_complete(time(10, 0), now=time(9, 55)) is False


def test_not_too_early_inside_guard_window() -> None:
    assert is_too_early_to_complete(time(10, 0), now=time(9, 58)) is False


def test_not_too_early_exactly_at_end() -> None:
    assert is_too_early_to_complete(time(10, 0), now=time(10, 0)) is False


def test_not_too_early_after_end() -> None:
    assert is_too_early_to_complete(time(10, 0), now=time(10, 30)) is False


def test_not_too_early_missing_scheduled_end() -> None:
    assert is_too_early_to_complete(None, now=time(9, 0)) is False


def test_early_completion_guard_is_five_minutes() -> None:
    assert EARLY_COMPLETION_GUARD_MINUTES == 5
