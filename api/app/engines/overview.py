"""Pure function: the cross-domain highlights for a single "Personal OS"
overview -- the aggregator ARCHITECTURE_AUDIT.md found missing (today's
command center is schedule-shaped, the dashboard is DSA-mastery-shaped,
and neither reaches into goals or finance).

Deliberately thin: every number here is already computed by an existing,
tested engine (readiness_pct, month_summary, build_insights, ...) --
this just decides which of them are worth surfacing together as a single
sentence each, and only when there's something real to say (same
refuse-rather-than-pad discipline as everywhere else in this layer).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OverviewInputs:
    readiness_pct: float | None
    reviews_overdue: int
    active_goal_count: int
    finance_savings_this_month: float | None
    research_minutes_this_week: int


def build_overview_highlights(inputs: OverviewInputs) -> list[str]:
    highlights: list[str] = []

    if inputs.reviews_overdue > 0:
        highlights.append(
            f"{inputs.reviews_overdue} review{'s' if inputs.reviews_overdue != 1 else ''} overdue."
        )

    if inputs.readiness_pct is not None:
        highlights.append(f"DSA readiness at {inputs.readiness_pct:.0f}%.")

    if inputs.finance_savings_this_month is not None:
        if inputs.finance_savings_this_month < 0:
            highlights.append(
                f"Spent ${abs(inputs.finance_savings_this_month):,.0f} more than earned this month."
            )
        else:
            highlights.append(f"Saved ${inputs.finance_savings_this_month:,.0f} so far this month.")

    if inputs.research_minutes_this_week == 0:
        highlights.append("No research logged this week yet.")

    if inputs.active_goal_count > 0:
        highlights.append(
            f"{inputs.active_goal_count} active goal{'s' if inputs.active_goal_count != 1 else ''}."
        )

    return highlights
