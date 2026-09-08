from datetime import datetime, timedelta

from app.engines.topic_gate import (
    BUILD_PASS_THRESHOLD,
    DEFEND_PASS_THRESHOLD,
    VERIFICATION_TTL_DAYS,
    AttemptFixture,
    GateState,
    attempt_passed,
    build_passes,
    build_score,
    compute_gate,
    defend_passes,
    defend_score,
)

NOW = datetime(2026, 9, 8, 12, 0)


def _passed(topic: str, when: datetime) -> AttemptFixture:
    return AttemptFixture(topic=topic, started_at=when, passed=True, passed_at=when, override=False)


def _failed(topic: str, when: datetime) -> AttemptFixture:
    return AttemptFixture(topic=topic, started_at=when, passed=False, passed_at=None, override=False)


def _override(topic: str, when: datetime) -> AttemptFixture:
    return AttemptFixture(topic=topic, started_at=when, passed=None, passed_at=None, override=True)


def test_no_attempts_is_locked() -> None:
    gate = compute_gate("linked_list", [], NOW)
    assert gate.state is GateState.LOCKED
    assert gate.problems_visible is False
    assert gate.attempt_count == 0


def test_failed_attempt_stays_locked() -> None:
    gate = compute_gate("linked_list", [_failed("linked_list", NOW - timedelta(hours=1))], NOW)
    assert gate.state is GateState.LOCKED
    assert gate.problems_visible is False
    assert gate.attempt_count == 1


def test_recent_pass_unlocks() -> None:
    gate = compute_gate("linked_list", [_passed("linked_list", NOW - timedelta(days=3))], NOW)
    assert gate.state is GateState.UNLOCKED
    assert gate.problems_visible is True
    assert gate.days_until_expiry == VERIFICATION_TTL_DAYS - 3


def test_pass_expires_after_ttl() -> None:
    stale = NOW - timedelta(days=VERIFICATION_TTL_DAYS + 1)
    gate = compute_gate("linked_list", [_passed("linked_list", stale)], NOW)
    assert gate.state is GateState.EXPIRED
    assert gate.problems_visible is False


def test_pass_still_valid_on_the_last_day() -> None:
    edge = NOW - timedelta(days=VERIFICATION_TTL_DAYS) + timedelta(minutes=1)
    gate = compute_gate("linked_list", [_passed("linked_list", edge)], NOW)
    assert gate.state is GateState.UNLOCKED


def test_override_unlocks_but_is_marked_unverified() -> None:
    gate = compute_gate("linked_list", [_override("linked_list", NOW)], NOW)
    assert gate.state is GateState.UNVERIFIED_OVERRIDE
    # Usable — the escape hatch exists so the app never becomes a jail.
    assert gate.problems_visible is True
    assert gate.overridden is True


def test_a_real_pass_supersedes_an_earlier_override() -> None:
    attempts = [
        _override("linked_list", NOW - timedelta(days=10)),
        _passed("linked_list", NOW - timedelta(days=1)),
    ]
    gate = compute_gate("linked_list", attempts, NOW)
    assert gate.state is GateState.UNLOCKED
    # The bypass still happened, and the record still says so.
    assert gate.overridden is True


def test_expired_pass_does_not_fall_back_to_an_old_override() -> None:
    attempts = [
        _override("linked_list", NOW - timedelta(days=90)),
        _passed("linked_list", NOW - timedelta(days=VERIFICATION_TTL_DAYS + 5)),
    ]
    gate = compute_gate("linked_list", attempts, NOW)
    assert gate.state is GateState.EXPIRED
    assert gate.problems_visible is False


def test_latest_pass_wins() -> None:
    attempts = [
        _passed("linked_list", NOW - timedelta(days=VERIFICATION_TTL_DAYS + 10)),
        _passed("linked_list", NOW - timedelta(days=2)),
    ]
    gate = compute_gate("linked_list", attempts, NOW)
    assert gate.state is GateState.UNLOCKED


def test_other_topics_attempts_are_ignored() -> None:
    gate = compute_gate("linked_list", [_passed("graphs", NOW)], NOW)
    assert gate.state is GateState.LOCKED
    assert gate.attempt_count == 0


def test_build_score_is_a_fraction_of_required_items() -> None:
    assert build_score(8, 10) == 0.8
    assert build_score(0, 10) == 0.0
    assert build_score(10, 10) == 1.0
    # Never above 1, and never divides by zero.
    assert build_score(12, 10) == 1.0
    assert build_score(3, 0) == 0.0


def test_build_threshold_boundary() -> None:
    assert build_passes(BUILD_PASS_THRESHOLD) is True
    assert build_passes(BUILD_PASS_THRESHOLD - 0.01) is False


def test_defend_score_weights_partial_as_half() -> None:
    assert defend_score(["correct", "correct"]) == 1.0
    assert defend_score(["correct", "wrong"]) == 0.5
    assert defend_score(["partial", "partial"]) == 0.5
    assert defend_score(["correct", "correct", "partial", "wrong"]) == 0.625
    assert defend_score([]) == 0.0


def test_unknown_verdict_scores_zero_rather_than_crashing() -> None:
    assert defend_score(["correct", "banana"]) == 0.5


def test_defend_threshold_boundary() -> None:
    assert defend_passes(DEFEND_PASS_THRESHOLD) is True
    assert defend_passes(DEFEND_PASS_THRESHOLD - 0.01) is False


def test_both_stages_must_clear_their_own_bar() -> None:
    assert attempt_passed(1.0, 1.0) is True
    # Perfect viva does not excuse an implementation that skipped half the
    # structure.
    assert attempt_passed(0.5, 1.0) is False
    # Complete code does not excuse being unable to explain it.
    assert attempt_passed(1.0, 0.4) is False
