from app.engines.overview import OverviewInputs, build_overview_highlights


def _inputs(**overrides: object) -> OverviewInputs:
    defaults: dict[str, object] = dict(
        readiness_pct=None,
        reviews_overdue=0,
        active_goal_count=0,
        finance_savings_this_month=None,
        research_minutes_this_week=0,
    )
    defaults.update(overrides)
    return OverviewInputs(**defaults)  # type: ignore[arg-type]


def test_empty_state_still_flags_no_research_logged_this_week() -> None:
    # research_minutes_this_week=0 is meaningful even with nothing else set
    # -- it's a real observation ("nothing logged"), not a placeholder.
    highlights = build_overview_highlights(_inputs())
    assert highlights == ["No research logged this week yet."]


def test_overdue_reviews_are_singular_or_plural_correctly() -> None:
    assert "1 review overdue." in build_overview_highlights(_inputs(reviews_overdue=1))
    assert "3 reviews overdue." in build_overview_highlights(_inputs(reviews_overdue=3))


def test_readiness_only_shown_when_known() -> None:
    assert build_overview_highlights(_inputs(readiness_pct=None)) == [
        "No research logged this week yet."
    ]
    highlights = build_overview_highlights(_inputs(readiness_pct=42.0))
    assert "DSA readiness at 42%." in highlights


def test_savings_direction_is_stated_correctly() -> None:
    positive = build_overview_highlights(_inputs(finance_savings_this_month=500.0))
    assert "Saved $500 so far this month." in positive

    negative = build_overview_highlights(_inputs(finance_savings_this_month=-200.0))
    assert "Spent $200 more than earned this month." in negative


def test_active_goal_count_pluralization() -> None:
    assert "1 active goal." in build_overview_highlights(_inputs(active_goal_count=1))
    assert "2 active goals." in build_overview_highlights(_inputs(active_goal_count=2))


def test_research_logged_this_week_produces_no_warning() -> None:
    highlights = build_overview_highlights(_inputs(research_minutes_this_week=30))
    assert "No research logged this week yet." not in highlights
