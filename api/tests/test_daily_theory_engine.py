from datetime import date, datetime, timedelta

from app.domain import QuestionFixture, QuestionProgressFixture
from app.engines.daily_theory import REVIEW_INTERVAL_DAYS, pick_daily_theory

TODAY = date(2026, 9, 8)


def _bank() -> list[QuestionFixture]:
    """32 questions across 6 modules, mirroring the shape of the real bank:
    a handful of case studies (module AA) plus a spread of other types."""
    out = []
    # Module AA — case studies only.
    for i in range(1, 6):
        out.append(QuestionFixture(i, "AA", "ml_case_study", "case_study", "P1", "medium"))
    # Module D — classical ML, P0, mixed frequency.
    for i in range(10, 16):
        out.append(QuestionFixture(i, "D", "classical_ml", "concept", "P0", "high"))
    # Module K — transformers, P0, very_high frequency (should rank early).
    for i in range(20, 24):
        out.append(QuestionFixture(i, "K", "transformers", "concept", "P0", "very_high"))
    # Module R — system design, P0.
    for i in range(30, 34):
        out.append(QuestionFixture(i, "R", "ml_system_design", "system_design", "P0", "high"))
    # Module AE — responsible AI, P2 (low priority, should rank late).
    for i in range(40, 44):
        out.append(QuestionFixture(i, "AE", "responsible_ai", "concept", "P2", "low"))
    return out


def test_returns_requested_count_with_exactly_one_case_study_when_bank_is_untouched() -> None:
    picks = pick_daily_theory(_bank(), progress=[], today=TODAY, count=3, case_study_count=1)
    assert len(picks) == 3
    assert sum(1 for p in picks if p.is_case_study) == 1
    assert sum(1 for p in picks if not p.is_case_study) == 2


def test_never_seen_questions_beat_p2_low_frequency_ones() -> None:
    # Everything is mastery 0 (never seen) except the AE (P2/low) rows,
    # which are already at mastery 7 and not due for 60 days.
    progress = [
        QuestionProgressFixture(i, mastery=7, updated_at=datetime.combine(TODAY, datetime.min.time()))
        for i in range(40, 44)
    ]
    picks = pick_daily_theory(_bank(), progress, today=TODAY, count=3, case_study_count=1)
    other_ids = {p.question_id for p in picks if not p.is_case_study}
    assert other_ids.isdisjoint(range(40, 44))


def test_module_diversity_no_repeats_when_pool_is_large_enough() -> None:
    picks = pick_daily_theory(_bank(), progress=[], today=TODAY, count=3, case_study_count=1)
    non_case_modules = [p.question_id for p in picks if not p.is_case_study]
    # Map back to modules via the bank fixture to check diversity.
    bank_by_id = {q.question_id: q for q in _bank()}
    modules = [bank_by_id[qid].module_code for qid in non_case_modules]
    assert len(modules) == len(set(modules)), f"expected distinct modules, got {modules}"


def test_deterministic_same_day_same_progress_same_result() -> None:
    bank = _bank()
    progress: list[QuestionProgressFixture] = []
    first = pick_daily_theory(bank, progress, today=TODAY, count=3, case_study_count=1)
    second = pick_daily_theory(bank, progress, today=TODAY, count=3, case_study_count=1)
    assert [p.question_id for p in first] == [p.question_id for p in second]


def test_rotates_across_different_days() -> None:
    bank = _bank()
    day1 = pick_daily_theory(bank, [], today=TODAY, count=3, case_study_count=1)
    day2 = pick_daily_theory(bank, [], today=TODAY + timedelta(days=1), count=3, case_study_count=1)
    # Not a guarantee of full disjointness, but the shuffle seed differs per
    # day so an identical 3-of-3 result across two different days would
    # indicate the seed isn't doing anything.
    assert [p.question_id for p in day1] != [p.question_id for p in day2]


def test_rated_question_resurfaces_only_after_its_review_interval() -> None:
    # A mastery-2 question rated exactly REVIEW_INTERVAL_DAYS[2] days ago
    # should be due; the same rating from yesterday should not be.
    interval = REVIEW_INTERVAL_DAYS[2]
    due_at = datetime.combine(TODAY - timedelta(days=interval), datetime.min.time())
    not_due_at = datetime.combine(TODAY - timedelta(days=1), datetime.min.time())

    bank = [
        QuestionFixture(100, "D", "classical_ml", "concept", "P0", "high"),
        QuestionFixture(101, "D", "classical_ml", "concept", "P0", "high"),
    ]
    due_progress = [QuestionProgressFixture(100, mastery=2, updated_at=due_at)]
    not_due_progress = [QuestionProgressFixture(101, mastery=2, updated_at=not_due_at)]

    due_picks = pick_daily_theory(bank[:1], due_progress, today=TODAY, count=1, case_study_count=0)
    not_due_picks = pick_daily_theory(
        bank[1:], not_due_progress, today=TODAY, count=1, case_study_count=0
    )

    assert due_picks[0].question_id == 100
    assert "reinforcement" in due_picks[0].reason.lower()
    # Not-yet-due still returns something (never leaves a slot empty) but
    # says so honestly rather than claiming it's due.
    assert not_due_picks[0].question_id == 101
    assert "not yet due" in not_due_picks[0].reason.lower()


def test_no_case_studies_in_bank_degrades_gracefully() -> None:
    bank = [q for q in _bank() if q.module_code != "AA"]
    picks = pick_daily_theory(bank, [], today=TODAY, count=3, case_study_count=1)
    assert len(picks) == 3
    assert all(not p.is_case_study for p in picks)


def test_empty_bank_returns_nothing() -> None:
    assert pick_daily_theory([], [], today=TODAY, count=3) == []


def test_count_zero_returns_nothing() -> None:
    assert pick_daily_theory(_bank(), [], today=TODAY, count=0) == []


def test_case_study_pool_smaller_than_requested_takes_what_exists() -> None:
    bank = [q for q in _bank() if q.module_code != "AA"]
    bank.append(QuestionFixture(999, "AA", "ml_case_study", "case_study", "P1", "medium"))
    picks = pick_daily_theory(bank, [], today=TODAY, count=3, case_study_count=2)
    case_picks = [p for p in picks if p.is_case_study]
    assert len(case_picks) == 1
    assert case_picks[0].question_id == 999
