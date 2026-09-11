from datetime import datetime, time
from zoneinfo import ZoneInfo

from app.engines.coach import (
    CoachContext,
    CoachScheduleBlock,
    build_system_prompt,
    local_fallback_response,
)
from app.engines.prayer import PrayerTimesResult

_PRAYER = PrayerTimesResult(
    fajr=time(5, 0),
    sunrise=time(6, 20),
    zuhr=time(12, 30),
    asr=time(16, 0),
    maghrib=time(19, 0),
    isha=time(20, 30),
)
_NOW = datetime(2026, 9, 10, 14, 0, tzinfo=ZoneInfo("UTC"))


def _ctx(**overrides: object) -> CoachContext:
    defaults: dict[str, object] = dict(
        user_name="Wajahat",
        now=_NOW,
        timezone_label="UTC",
        blocks=(),
        prayer_times=_PRAYER,
        recommendation_titles=(),
        operating_rules=(),
    )
    defaults.update(overrides)
    return CoachContext(**defaults)  # type: ignore[arg-type]


def _block(activity: str, status: str = "NOT DONE", category: str = "Job") -> CoachScheduleBlock:
    return CoachScheduleBlock(
        start_resolved=time(14, 0),
        start_spec="14:00",
        end_resolved=time(15, 0),
        end_spec="15:00",
        activity=activity,
        tier="core",
        category=category,
        status=status,
        planned_minutes=60,
    )


def test_prompt_states_absence_rather_than_inventing_when_nothing_is_recorded() -> None:
    prompt = build_system_prompt(_ctx())

    assert "no blocks scheduled for today" in prompt
    assert "no interview-prep block on today's schedule" in prompt
    assert "the recommender has nothing queued" in prompt
    assert "do not invent policies on his behalf" in prompt


def test_prompt_reflects_real_data_when_present() -> None:
    ctx = _ctx(
        blocks=(_block("Deep Work"),),
        recommendation_titles=("Two Sum",),
        operating_rules=("No screens after Isha",),
    )
    prompt = build_system_prompt(ctx)

    assert "Deep Work" in prompt
    assert "Two Sum" in prompt
    assert "No screens after Isha" in prompt
    assert "Fajr 05:00" in prompt


def test_right_now_fallback_names_the_actual_next_block() -> None:
    ctx = _ctx(blocks=(_block("Focused Reading", status="NOT DONE"),))
    reply = local_fallback_response("what should I do right now?", ctx)

    assert "Focused Reading" in reply
    assert "14:00" in reply


def test_right_now_fallback_does_not_claim_a_block_when_all_are_done() -> None:
    ctx = _ctx(blocks=(_block("Focused Reading", status="DONE"),))
    reply = local_fallback_response("what should I do right now?", ctx)

    assert "Focused Reading" not in reply
    assert "completed all scheduled blocks" in reply


def test_thesis_fallback_reflects_a_real_research_block_not_a_hardcoded_one() -> None:
    ctx = _ctx(blocks=(_block("Thesis writing sprint", category="Research"),))
    reply = local_fallback_response("how should I structure my thesis work?", ctx)

    assert "Thesis writing sprint" in reply
    # The old version asserted a fixed "124 minutes (04:41-06:45)" here
    # regardless of what was actually scheduled -- must not reappear.
    assert "04:41" not in reply
    assert "124 minutes" not in reply


def test_thesis_fallback_admits_absence_when_no_research_block_exists() -> None:
    ctx = _ctx(blocks=(_block("Standup", category="Job"),))
    reply = local_fallback_response("thesis time?", ctx)

    assert "no thesis/research block" in reply


def test_default_fallback_uses_the_real_date_and_block_count_not_a_fabricated_day() -> None:
    ctx = _ctx(blocks=(_block("A"), _block("B")))
    reply = local_fallback_response("hello", ctx)

    assert "2 scheduled blocks" in reply
    assert ctx.now.strftime("%A, %d %B %Y") in reply
    # The old catch-all always said "Monday, September 7, 2026" and "21
    # scheduled blocks" no matter what day it actually was.
    assert "September 7, 2026" not in reply
    assert "21 scheduled" not in reply


def test_default_fallback_admits_an_empty_schedule() -> None:
    reply = local_fallback_response("hello", _ctx())
    assert "nothing on today's schedule yet" in reply


def test_prompt_admits_absence_of_goals_recovery_and_finance_when_unset() -> None:
    prompt = build_system_prompt(_ctx())
    assert "no active goals recorded" in prompt
    assert "no recovery entry logged today" in prompt
    assert "no financial data recorded" in prompt


def test_prompt_states_real_goals_recovery_and_finance_when_present() -> None:
    ctx = _ctx(
        active_goal_titles=("Ship the finance module", "Read 12 books"),
        recovery_score=72.0,
        finance_income_this_month=5000.0,
        finance_expenses_this_month=3200.0,
        finance_savings_this_month=1800.0,
    )
    prompt = build_system_prompt(ctx)

    assert "Ship the finance module" in prompt
    assert "Read 12 books" in prompt
    assert "72/100" in prompt
    assert "$5,000" in prompt
    assert "$3,200" in prompt
    assert "$1,800" in prompt


def test_prompt_never_shows_finance_figures_when_savings_is_none_even_if_others_set() -> None:
    # Router only ever supplies these three together (all from the same
    # month_summary call) or not at all -- this pins that the prompt
    # honours the same all-or-nothing gate rather than rendering a
    # partial, misleading figure.
    ctx = _ctx(finance_savings_this_month=None)
    prompt = build_system_prompt(ctx)
    assert "no financial data recorded" in prompt
