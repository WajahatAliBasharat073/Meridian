"""Resolves `start_spec` / `end_spec` against a date's prayer times.

Specs are either absolute ('17:05') or prayer-relative ('maghrib', 'asr+15m',
'fajr-10min'). Resolution happens at read/recompute time so the stored spec
survives a change to prayer parameters or convention (design doc 5.1, 6.1) —
`start_resolved` / `end_resolved` are a materialised cache, not the source
of truth.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from app.engines.prayer import PrayerTimesResult

PRAYER_NAMES = ("fajr", "sunrise", "zuhr", "asr", "maghrib", "isha")

_ABSOLUTE_RE = re.compile(r"^(?P<h>\d{1,2}):(?P<m>\d{2})$")
_RELATIVE_RE = re.compile(
    r"^(?P<prayer>" + "|".join(PRAYER_NAMES) + r")"
    r"(?:(?P<sign>[+-])(?P<amount>\d+)\s*(?:m|min|mins|minutes)?)?$",
    re.IGNORECASE,
)


class InvalidTimeSpecError(ValueError):
    pass


def _prayer_time(prayer_times: PrayerTimesResult, name: str) -> time:
    return getattr(prayer_times, name.lower())  # type: ignore[no-any-return]


def resolve_spec(spec: str, prayer_times: PrayerTimesResult, on_date: date) -> time:
    spec = spec.strip()

    abs_match = _ABSOLUTE_RE.match(spec)
    if abs_match:
        return time(hour=int(abs_match["h"]), minute=int(abs_match["m"]))

    rel_match = _RELATIVE_RE.match(spec)
    if rel_match:
        base = _prayer_time(prayer_times, rel_match["prayer"])
        offset_minutes = 0
        if rel_match["amount"]:
            offset_minutes = int(rel_match["amount"])
            if rel_match["sign"] == "-":
                offset_minutes = -offset_minutes
        base_dt = datetime.combine(on_date, base) + timedelta(minutes=offset_minutes)
        return base_dt.time()

    raise InvalidTimeSpecError(f"Unrecognised time spec: {spec!r}")


@dataclass(frozen=True)
class ResolvedBlock:
    seq: int
    start: time
    end: time
    overlaps_previous: bool
    gap_before_minutes: int | None


def resolve_day(
    specs: list[tuple[int, str, str]],  # (seq, start_spec, end_spec), already date-ordered by seq
    prayer_times: PrayerTimesResult,
    on_date: date,
) -> list[ResolvedBlock]:
    """Resolves every block for a date and flags overlaps/gaps so the
    scheduling engine can surface them rather than silently rendering a
    broken timeline."""
    resolved: list[ResolvedBlock] = []
    prev_end: time | None = None
    for seq, start_spec, end_spec in specs:
        start = resolve_spec(start_spec, prayer_times, on_date)
        end = resolve_spec(end_spec, prayer_times, on_date)
        overlaps = prev_end is not None and start < prev_end
        gap = None
        if prev_end is not None and start > prev_end:
            gap = (
                datetime.combine(on_date, start) - datetime.combine(on_date, prev_end)
            ).seconds // 60
        resolved.append(
            ResolvedBlock(seq=seq, start=start, end=end, overlaps_previous=overlaps, gap_before_minutes=gap)
        )
        prev_end = end
    return resolved
