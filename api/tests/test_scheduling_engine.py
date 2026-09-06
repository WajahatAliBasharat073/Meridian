from datetime import date, time

import pytest

from app.engines.prayer import compute_prayer_times
from app.engines.scheduling import InvalidTimeSpecError, resolve_day, resolve_spec

ON_DATE = date(2026, 9, 6)
PRAYER_TIMES = compute_prayer_times(ON_DATE, 33.6844, 73.0479, 5.0)


def test_resolves_absolute_spec() -> None:
    assert resolve_spec("17:05", PRAYER_TIMES, ON_DATE) == time(17, 5)


def test_resolves_bare_prayer_name() -> None:
    assert resolve_spec("asr", PRAYER_TIMES, ON_DATE) == PRAYER_TIMES.asr


def test_resolves_prayer_plus_offset() -> None:
    expected_minute = (PRAYER_TIMES.maghrib.minute + 15) % 60
    resolved = resolve_spec("maghrib+15m", PRAYER_TIMES, ON_DATE)
    assert resolved.minute == expected_minute


def test_resolves_prayer_minus_offset() -> None:
    resolved = resolve_spec("fajr-10min", PRAYER_TIMES, ON_DATE)
    fajr_dt_minutes = PRAYER_TIMES.fajr.hour * 60 + PRAYER_TIMES.fajr.minute
    resolved_minutes = resolved.hour * 60 + resolved.minute
    assert resolved_minutes == (fajr_dt_minutes - 10) % (24 * 60)


def test_rejects_unrecognised_spec() -> None:
    with pytest.raises(InvalidTimeSpecError):
        resolve_spec("teatime", PRAYER_TIMES, ON_DATE)


def test_resolve_day_flags_overlap() -> None:
    specs = [(1, "09:00", "10:00"), (2, "09:30", "11:00")]
    resolved = resolve_day(specs, PRAYER_TIMES, ON_DATE)
    assert resolved[1].overlaps_previous is True


def test_resolve_day_flags_gap() -> None:
    specs = [(1, "09:00", "10:00"), (2, "10:30", "11:00")]
    resolved = resolve_day(specs, PRAYER_TIMES, ON_DATE)
    assert resolved[1].gap_before_minutes == 30
    assert resolved[1].overlaps_previous is False


def test_resolve_day_back_to_back_has_no_gap_or_overlap() -> None:
    specs = [(1, "09:00", "10:00"), (2, "10:00", "11:00")]
    resolved = resolve_day(specs, PRAYER_TIMES, ON_DATE)
    assert resolved[1].gap_before_minutes is None
    assert resolved[1].overlaps_previous is False
