from datetime import datetime, timedelta

from app.engines.session_breakdown import (
    ActivityBreakdown,
    PauseStats,
    SessionEvent,
    SessionForBreakdown,
    compute_activity_breakdown,
    compute_pause_stats,
)

T0 = datetime(2026, 9, 7, 17, 0, 0)


def _e(kind: str, minutes: int) -> SessionEvent:
    return SessionEvent(event_type=kind, occurred_at=T0 + timedelta(minutes=minutes))


def test_no_pauses() -> None:
    stats = compute_pause_stats([_e("started", 0), _e("completed", 60)])

    assert stats.pause_count == 0
    assert stats.paused_seconds == 0
    assert stats.unresolved_pause is False


def test_single_pause_resume_pair_sums_the_gap() -> None:
    stats = compute_pause_stats([_e("started", 0), _e("paused", 10), _e("resumed", 25)])

    assert stats.pause_count == 1
    assert stats.paused_seconds == 15 * 60


def test_multiple_pauses_accumulate() -> None:
    stats = compute_pause_stats(
        [
            _e("started", 0),
            _e("paused", 10),
            _e("resumed", 15),  # 5 min
            _e("paused", 30),
            _e("resumed", 42),  # 12 min
            _e("completed", 60),
        ]
    )

    assert stats.pause_count == 2
    assert stats.paused_seconds == 17 * 60


def test_session_completed_while_paused_closes_the_pause() -> None:
    stats = compute_pause_stats([_e("started", 0), _e("paused", 20), _e("completed", 35)])

    assert stats.pause_count == 1
    assert stats.paused_seconds == 15 * 60
    assert stats.unresolved_pause is False


def test_open_pause_without_now_is_flagged_not_guessed() -> None:
    stats = compute_pause_stats([_e("started", 0), _e("paused", 20)])

    assert stats.pause_count == 1
    assert stats.paused_seconds == 0  # length unknown — not invented
    assert stats.unresolved_pause is True


def test_open_pause_closed_by_now_when_supplied() -> None:
    stats = compute_pause_stats([_e("started", 0), _e("paused", 20)], now=T0 + timedelta(minutes=50))

    assert stats.paused_seconds == 30 * 60
    assert stats.unresolved_pause is False


def test_events_out_of_order_are_sorted_before_pairing() -> None:
    stats = compute_pause_stats([_e("resumed", 25), _e("paused", 10), _e("started", 0)])

    assert stats.pause_count == 1
    assert stats.paused_seconds == 15 * 60


def _sfb(activity: str, category: str, worked_min: int, pauses: int, paused_min: int) -> SessionForBreakdown:
    return SessionForBreakdown(
        activity=activity,
        category=category,
        worked_seconds=worked_min * 60,
        pause_stats=PauseStats(pause_count=pauses, paused_seconds=paused_min * 60, unresolved_pause=False),
    )


def test_breakdown_keeps_activities_separate_within_one_category() -> None:
    rows = compute_activity_breakdown(
        [
            _sfb("Interview Prep — Coding", "InterviewPrep", 100, 3, 20),
            _sfb("Interview Prep — Theory", "InterviewPrep", 60, 0, 0),
            _sfb("Remote job — focused work", "Job", 180, 1, 5),
        ]
    )

    by = {r.activity: r for r in rows}
    # Same category, different work — must not be collapsed together.
    assert by["Interview Prep — Coding"].paused_seconds == 20 * 60
    assert by["Interview Prep — Theory"].paused_seconds == 0
    assert by["Interview Prep — Coding"].category == "InterviewPrep"
    assert by["Interview Prep — Theory"].category == "InterviewPrep"


def test_breakdown_aggregates_repeat_sessions_of_same_activity() -> None:
    rows = compute_activity_breakdown(
        [
            _sfb("Interview Prep — Coding", "InterviewPrep", 60, 2, 10),
            _sfb("Interview Prep — Coding", "InterviewPrep", 40, 1, 5),
        ]
    )

    assert len(rows) == 1
    r = rows[0]
    assert r.sessions == 2
    assert r.worked_seconds == 100 * 60
    assert r.paused_seconds == 15 * 60
    assert r.pause_count == 3
    assert r.avg_pauses_per_session == 1.5


def test_paused_pct_is_share_of_time_session_was_open() -> None:
    rows = compute_activity_breakdown([_sfb("Coding", "InterviewPrep", 90, 1, 10)])

    # 10 paused out of 100 minutes open.
    assert rows[0].paused_pct_of_session == 10.0


def test_breakdown_sorted_most_interrupted_first() -> None:
    rows = compute_activity_breakdown(
        [
            _sfb("Light", "A", 60, 1, 2),
            _sfb("Heavy", "B", 60, 5, 40),
            _sfb("Middle", "C", 60, 2, 12),
        ]
    )

    assert [r.activity for r in rows] == ["Heavy", "Middle", "Light"]


def test_empty_input_gives_empty_breakdown() -> None:
    assert compute_activity_breakdown([]) == []


def test_zero_open_time_reports_none_not_division_error() -> None:
    rows: list[ActivityBreakdown] = compute_activity_breakdown(
        [_sfb("Instant", "A", 0, 0, 0)]
    )

    assert rows[0].paused_pct_of_session is None
