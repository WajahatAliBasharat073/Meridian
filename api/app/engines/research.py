"""Pure function: "Research at a Glance" -- what am I researching, why,
what's next, what's blocking it. The request's own words: "less tracking
for the sake of tracking, more guidance toward meaningful progress."

Same discipline as engines/overview.py -- every line here reads an
already-fetched real row; nothing is computed that isn't grounded in an
actual topic/milestone/opportunity, and a section with nothing behind it
is omitted rather than padded.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class TopicSummary:
    id: int
    title: str
    current_blocker: str | None


@dataclass(frozen=True)
class MilestoneSummary:
    id: int
    title: str
    target_date: date


@dataclass(frozen=True)
class OpportunitySummary:
    id: int
    venue_name: str
    submission_deadline: date


@dataclass(frozen=True)
class ResearchAtAGlance:
    active_topic: TopicSummary | None
    papers_to_read_count: int
    next_milestone: MilestoneSummary | None
    next_opportunity: OpportunitySummary | None
    highlights: list[str]


def _days_until(target: date, today: date) -> int:
    return (target - today).days


def build_at_a_glance(
    active_topics: list[TopicSummary],
    papers_to_read_count: int,
    upcoming_milestones: list[MilestoneSummary],
    upcoming_opportunities: list[OpportunitySummary],
    today: date,
) -> ResearchAtAGlance:
    active_topic = active_topics[0] if active_topics else None
    next_milestone = upcoming_milestones[0] if upcoming_milestones else None
    next_opportunity = upcoming_opportunities[0] if upcoming_opportunities else None

    highlights: list[str] = []

    if active_topic is None:
        highlights.append("No active research topic recorded -- add one to anchor everything else here.")
    elif active_topic.current_blocker:
        highlights.append(f"Blocked on: {active_topic.current_blocker}")

    if papers_to_read_count > 0:
        highlights.append(
            f"{papers_to_read_count} paper{'s' if papers_to_read_count != 1 else ''} waiting to be read."
        )

    if next_milestone is not None:
        days = _days_until(next_milestone.target_date, today)
        when = "today" if days == 0 else f"in {days} day{'s' if days != 1 else ''}"
        highlights.append(f"Next milestone: \"{next_milestone.title}\" due {when}.")

    if next_opportunity is not None:
        days = _days_until(next_opportunity.submission_deadline, today)
        when = "today" if days == 0 else f"in {days} day{'s' if days != 1 else ''}"
        highlights.append(f"{next_opportunity.venue_name} submission due {when}.")

    return ResearchAtAGlance(
        active_topic=active_topic,
        papers_to_read_count=papers_to_read_count,
        next_milestone=next_milestone,
        next_opportunity=next_opportunity,
        highlights=highlights,
    )
