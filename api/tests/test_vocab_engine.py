from datetime import date

from app.engines.vocab import VocabWordFixture, build_daily_review


def _words() -> list[VocabWordFixture]:
    return [
        VocabWordFixture(id=1, word="ubiquitous", learning_status="known"),
        VocabWordFixture(id=2, word="ephemeral", learning_status="difficult"),
        VocabWordFixture(id=3, word="cogent", learning_status=None),
        VocabWordFixture(id=4, word="obfuscate", learning_status="need_to_revisit"),
        VocabWordFixture(id=5, word="salient", learning_status="learning"),
    ]


def test_need_to_revisit_and_difficult_are_prioritized_over_known() -> None:
    plan = build_daily_review(_words(), date(2026, 9, 11), count=5)
    ids_in_order = [w.id for w in plan]

    assert ids_in_order.index(4) < ids_in_order.index(1)  # need_to_revisit before known
    assert ids_in_order.index(2) < ids_in_order.index(1)  # difficult before known
    assert ids_in_order.index(4) < ids_in_order.index(5)  # need_to_revisit before learning


def test_count_limits_the_batch() -> None:
    plan = build_daily_review(_words(), date(2026, 9, 11), count=2)
    assert len(plan) == 2
    # The two highest-priority statuses must be the ones returned.
    assert {w.learning_status for w in plan} == {"need_to_revisit", "difficult"}


def test_same_day_is_deterministic_across_calls() -> None:
    today = date(2026, 9, 11)
    first = [w.id for w in build_daily_review(_words(), today, count=5)]
    second = [w.id for w in build_daily_review(_words(), today, count=5)]
    assert first == second


def test_different_days_can_reorder_within_a_priority_tier() -> None:
    # Two never-reviewed words tie on priority; across enough days the
    # jitter must break the tie differently at least once, or a learner
    # who reviews nothing would see the exact same two words forever.
    words = [
        VocabWordFixture(id=10, word="a", learning_status=None),
        VocabWordFixture(id=11, word="b", learning_status=None),
    ]
    orders = {
        tuple(w.id for w in build_daily_review(words, date.fromordinal(d), count=2))
        for d in range(1, 30)
    }
    assert len(orders) > 1
