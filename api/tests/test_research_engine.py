from datetime import date

from app.engines.research import (
    MilestoneSummary,
    OpportunitySummary,
    TopicSummary,
    build_at_a_glance,
)

_TODAY = date(2026, 9, 15)


def test_no_topic_at_all_says_so_plainly() -> None:
    glance = build_at_a_glance([], 0, [], [], _TODAY)
    assert glance.active_topic is None
    assert "No active research topic recorded" in glance.highlights[0]


def test_active_topic_with_a_blocker_surfaces_it() -> None:
    topic = TopicSummary(id=1, title="LLM calibration", current_blocker="Waiting on advisor feedback")
    glance = build_at_a_glance([topic], 0, [], [], _TODAY)
    assert glance.active_topic == topic
    assert "Blocked on: Waiting on advisor feedback" in glance.highlights


def test_no_blocker_produces_no_blocker_highlight() -> None:
    topic = TopicSummary(id=1, title="LLM calibration", current_blocker=None)
    glance = build_at_a_glance([topic], 0, [], [], _TODAY)
    assert not any("Blocked on" in h for h in glance.highlights)


def test_papers_to_read_count_is_pluralized_correctly() -> None:
    glance = build_at_a_glance([], 1, [], [], _TODAY)
    assert "1 paper waiting to be read." in glance.highlights
    glance = build_at_a_glance([], 5, [], [], _TODAY)
    assert "5 papers waiting to be read." in glance.highlights


def test_next_milestone_states_days_until_due() -> None:
    milestone = MilestoneSummary(id=1, title="Finish chapter 2", target_date=date(2026, 9, 20))
    glance = build_at_a_glance([], 0, [milestone], [], _TODAY)
    assert glance.next_milestone == milestone
    assert 'Next milestone: "Finish chapter 2" due in 5 days.' in glance.highlights


def test_milestone_due_today_says_today_not_in_0_days() -> None:
    milestone = MilestoneSummary(id=1, title="Submit draft", target_date=_TODAY)
    glance = build_at_a_glance([], 0, [milestone], [], _TODAY)
    assert any("due today" in h for h in glance.highlights)
    assert not any("in 0 days" in h for h in glance.highlights)


def test_next_opportunity_deadline_is_surfaced() -> None:
    opp = OpportunitySummary(id=1, venue_name="NeurIPS 2027", submission_deadline=date(2026, 10, 1))
    glance = build_at_a_glance([], 0, [], [opp], _TODAY)
    assert glance.next_opportunity == opp
    assert any("NeurIPS 2027" in h and "submission due" in h for h in glance.highlights)


def test_only_the_nearest_milestone_and_opportunity_are_surfaced() -> None:
    near = MilestoneSummary(id=1, title="Near", target_date=date(2026, 9, 16))
    far = MilestoneSummary(id=2, title="Far", target_date=date(2026, 12, 1))
    glance = build_at_a_glance([], 0, [near, far], [], _TODAY)
    assert glance.next_milestone == near
    assert not any("Far" in h for h in glance.highlights)
