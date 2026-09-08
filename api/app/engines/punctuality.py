"""Pure function: how punctually did real focus sessions start, compared
with when they were scheduled?

Same discipline as daily_recap/weekly_review — every figure is computed
from recorded sessions, and no claim is made until there are enough of
them. A single late start is not a pattern; the caller gets
`enough_data=False` and a count, not a confident-sounding percentage
built on two rows."""

from __future__ import annotations

from dataclasses import dataclass

# Below this, don't characterise punctuality at all — "you're 50% on time"
# off two sessions is noise dressed up as insight.
MIN_SESSIONS_FOR_INSIGHT = 5

ON_TIME_GRACE_MINUTES = 5


@dataclass(frozen=True)
class SessionDelay:
    """One recorded session, reduced to what this engine needs."""

    category: str
    hour_of_day: int
    start_delay_minutes: int


@dataclass(frozen=True)
class CategoryPunctuality:
    category: str
    sessions: int
    avg_delay_minutes: float
    on_time_pct: float


@dataclass(frozen=True)
class PunctualityReport:
    enough_data: bool
    session_count: int
    min_sessions_needed: int
    on_time_pct: float | None
    avg_delay_minutes: float | None
    median_delay_minutes: float | None
    started_early_or_on_time: int
    started_late: int
    worst_category: CategoryPunctuality | None
    best_category: CategoryPunctuality | None
    by_category: list[CategoryPunctuality]
    observations: list[str]


def compute_punctuality(sessions: list[SessionDelay]) -> PunctualityReport:
    count = len(sessions)

    if count < MIN_SESSIONS_FOR_INSIGHT:
        return PunctualityReport(
            enough_data=False,
            session_count=count,
            min_sessions_needed=MIN_SESSIONS_FOR_INSIGHT,
            on_time_pct=None,
            avg_delay_minutes=None,
            median_delay_minutes=None,
            started_early_or_on_time=sum(
                1 for s in sessions if s.start_delay_minutes <= ON_TIME_GRACE_MINUTES
            ),
            started_late=sum(1 for s in sessions if s.start_delay_minutes > ON_TIME_GRACE_MINUTES),
            worst_category=None,
            best_category=None,
            by_category=[],
            observations=[],
        )

    delays = sorted(s.start_delay_minutes for s in sessions)
    on_time = sum(1 for d in delays if d <= ON_TIME_GRACE_MINUTES)
    late = count - on_time

    avg = round(sum(delays) / count, 1)
    mid = count // 2
    median = float(delays[mid]) if count % 2 else round((delays[mid - 1] + delays[mid]) / 2, 1)

    by_cat_raw: dict[str, list[int]] = {}
    for s in sessions:
        by_cat_raw.setdefault(s.category, []).append(s.start_delay_minutes)

    by_category = [
        CategoryPunctuality(
            category=cat,
            sessions=len(ds),
            avg_delay_minutes=round(sum(ds) / len(ds), 1),
            on_time_pct=round(100 * sum(1 for d in ds if d <= ON_TIME_GRACE_MINUTES) / len(ds), 1),
        )
        for cat, ds in sorted(by_cat_raw.items())
    ]

    # Only rank categories that have enough sessions of their own to mean
    # anything — otherwise one late start makes a category "the worst".
    rankable = [c for c in by_category if c.sessions >= 3]
    worst = max(rankable, key=lambda c: c.avg_delay_minutes) if rankable else None
    best = min(rankable, key=lambda c: c.avg_delay_minutes) if rankable else None

    return PunctualityReport(
        enough_data=True,
        session_count=count,
        min_sessions_needed=MIN_SESSIONS_FOR_INSIGHT,
        on_time_pct=round(100 * on_time / count, 1),
        avg_delay_minutes=avg,
        median_delay_minutes=median,
        started_early_or_on_time=on_time,
        started_late=late,
        worst_category=worst,
        best_category=best,
        by_category=by_category,
        observations=_observe(count, on_time, late, avg, median, worst, best),
    )


def _observe(
    count: int,
    on_time: int,
    late: int,
    avg: float,
    median: float,
    worst: CategoryPunctuality | None,
    best: CategoryPunctuality | None,
) -> list[str]:
    out: list[str] = []

    pct = round(100 * on_time / count, 1)
    out.append(f"Started on time (within {ON_TIME_GRACE_MINUTES} min) on {on_time} of {count} sessions ({pct}%).")

    # Median over mean when they diverge: a couple of very late starts drag
    # the average somewhere no individual day actually was.
    if abs(avg - median) >= 10:
        out.append(
            f"Typical delay is {median} min, but the average is {avg} min — a few unusually late starts are pulling it up."
        )
    else:
        out.append(f"Average start delay is {avg} min.")

    if worst is not None and worst.avg_delay_minutes > ON_TIME_GRACE_MINUTES:
        out.append(
            f"{worst.category} starts latest — {worst.avg_delay_minutes} min average across {worst.sessions} sessions."
        )
    if best is not None and best is not worst:
        out.append(
            f"{best.category} is the most punctual — {best.avg_delay_minutes} min average across {best.sessions} sessions."
        )

    return out
