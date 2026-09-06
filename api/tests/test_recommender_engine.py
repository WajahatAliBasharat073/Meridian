from datetime import date, datetime, timedelta

from app.domain import AttemptFixture, ProblemFixture, ReviewState
from app.engines.recommender import recommend

TODAY = date(2026, 9, 6)


def _problems() -> list[ProblemFixture]:
    return [
        ProblemFixture(1, "P1", "sliding_window", "Medium"),
        ProblemFixture(2, "P2", "two_pointers", "Medium"),
        ProblemFixture(3, "P3", "sliding_window", "Easy", scheduled_date=TODAY, scheduled_slot=1),
        ProblemFixture(4, "P4", "dfs", "Hard", scheduled_date=TODAY, scheduled_slot=2),
        ProblemFixture(5, "P5", "two_pointers", "Medium"),
        ProblemFixture(6, "P6", "dfs", "Medium"),
        ProblemFixture(7, "P7", "two_pointers", "Medium"),
    ]


def _attempts() -> list[AttemptFixture]:
    base = datetime(2026, 9, 1, 10, 0)
    return [
        AttemptFixture(1, base, "L3", key_insight="watch the window shrink"),
        AttemptFixture(2, base + timedelta(days=1), "L2", key_insight=None),
        AttemptFixture(5, base + timedelta(days=2), "L4", key_insight=None),
    ]


def _reviews() -> list[ReviewState]:
    return [
        ReviewState("problem", 1, TODAY, 14, "L4", overdue_days=0, last_result="regressed"),
        ReviewState("problem", 2, TODAY - timedelta(days=2), 3, "L2", overdue_days=2, last_result="success"),
        ReviewState("problem", 5, TODAY, 14, "L4", overdue_days=0, last_result="success"),
    ]


def test_priority_order_failed_overdue_due_scheduled_gap_interleave() -> None:
    recs = recommend(_reviews(), _problems(), _attempts(), TODAY, max_results=7)
    queues = [r.queue for r in recs]
    ids = [r.problem_id for r in recs]

    assert ids[0] == 1 and queues[0] == "FAILED_REVIEW"
    assert ids[1] == 2 and queues[1] == "OVERDUE_REVIEW"
    assert ids[2] == 5 and queues[2] == "DUE_REVIEW"
    assert set(ids[3:5]) == {3, 4}
    assert queues[3] == "SCHEDULED" and queues[4] == "SCHEDULED"
    # scheduled slot order preserved
    assert ids[3] == 3  # slot 1
    assert ids[4] == 4  # slot 2
    assert queues[5] == "PATTERN_GAP"
    assert ids[5] == 6  # only unused, unattempted dfs problem
    assert queues[6] == "INTERLEAVE"
    assert ids[6] == 7  # only remaining two_pointers problem


def test_every_recommendation_has_a_nonempty_reason() -> None:
    recs = recommend(_reviews(), _problems(), _attempts(), TODAY, max_results=7)
    assert all(r.reason.strip() for r in recs)


def test_prior_key_insight_surfaces_for_reviews() -> None:
    recs = recommend(_reviews(), _problems(), _attempts(), TODAY, max_results=1)
    assert recs[0].prior_key_insight == "watch the window shrink"


def test_result_is_capped_at_max_results() -> None:
    recs = recommend(_reviews(), _problems(), _attempts(), TODAY, max_results=2)
    assert len(recs) == 2


def test_deterministic_across_repeated_calls() -> None:
    first = recommend(_reviews(), _problems(), _attempts(), TODAY, max_results=7)
    second = recommend(_reviews(), _problems(), _attempts(), TODAY, max_results=7)
    assert [r.problem_id for r in first] == [r.problem_id for r in second]


def test_pattern_gap_favours_weakest_ratio() -> None:
    # 'weak' pattern has 1 scheduled, 0 at L5+  -> ratio 0.0
    # 'strong' pattern has 1 scheduled, 1 at L5+ -> ratio 1.0
    problems = [
        ProblemFixture(10, "weak-a", "weak", "Medium", scheduled_date=TODAY, scheduled_slot=1),
        ProblemFixture(11, "weak-b", "weak", "Medium"),
        ProblemFixture(12, "strong-a", "strong", "Medium", scheduled_date=TODAY, scheduled_slot=2),
        ProblemFixture(13, "strong-b", "strong", "Medium"),
    ]
    attempts = [
        AttemptFixture(13, datetime(2026, 9, 1), "L6"),
    ]
    recs = recommend([], problems, attempts, TODAY, max_results=10)
    gap_recs = [r for r in recs if r.queue == "PATTERN_GAP"]
    assert gap_recs, "expected at least one pattern-gap recommendation"
    assert gap_recs[0].pattern == "weak"


def test_never_more_than_two_consecutive_same_pattern() -> None:
    problems = [ProblemFixture(i, f"P{i}", "graph", "Medium") for i in range(10, 14)]
    reviews = [ReviewState("problem", i, TODAY, 1, "L1", last_result="success") for i in range(10, 14)]
    recs = recommend(reviews, problems, [], TODAY, max_results=4)
    # All four candidates share one pattern with nothing else to interleave
    # with — the "never" rule wins over filling the requested count.
    assert len(recs) == 2


def test_foundation_phase_skips_the_spacing_constraint() -> None:
    problems = [ProblemFixture(i, f"P{i}", "graph", "Medium") for i in range(10, 14)]
    reviews = [ReviewState("problem", i, TODAY, 1, "L1", last_result="success") for i in range(10, 14)]
    recs = recommend(reviews, problems, [], TODAY, max_results=4, foundation_phase=True)
    assert len(recs) == 4
