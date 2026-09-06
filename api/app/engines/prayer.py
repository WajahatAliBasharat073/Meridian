"""Prayer times computed from solar position — never fetched from an API
(build prompt 2.5). Ports the standard declination + equation-of-time
formulas used by praytimes.org, evaluated once per date at solar noon.

Accuracy is stated, not hidden: neglecting the (normally iterative)
per-time refinement of declination costs at most a few tenths of a minute,
comfortably inside the ±5-15 minute tolerance this system discloses in the
UI (build prompt 2.5, design doc 6.1). Do not silently swap in an external
API — if accuracy ever needs to improve, iterate this function, don't
replace it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, time

KARACHI_FAJR_ANGLE = 18.0
KARACHI_ISHA_ANGLE = 18.0
HANAFI_ASR_FACTOR = 2.0
SUN_ANGLE_SUNRISE_SUNSET = 0.833  # atmospheric refraction + solar radius


@dataclass(frozen=True)
class PrayerConvention:
    fajr_angle: float = KARACHI_FAJR_ANGLE
    isha_angle: float = KARACHI_ISHA_ANGLE
    asr_factor: float = HANAFI_ASR_FACTOR


@dataclass(frozen=True)
class PrayerTimesResult:
    fajr: time
    sunrise: time
    zuhr: time
    asr: time
    maghrib: time
    isha: time
    accuracy_minutes: tuple[int, int] = (5, 15)


def _sind(deg: float) -> float:
    return math.sin(math.radians(deg))


def _cosd(deg: float) -> float:
    return math.cos(math.radians(deg))


def _tand(deg: float) -> float:
    return math.tan(math.radians(deg))


def _arcsind(x: float) -> float:
    return math.degrees(math.asin(max(-1.0, min(1.0, x))))


def _arccosd(x: float) -> float:
    return math.degrees(math.acos(max(-1.0, min(1.0, x))))


def _arccotd(x: float) -> float:
    return math.degrees(math.atan2(1.0, x))


def _arctan2d(y: float, x: float) -> float:
    return math.degrees(math.atan2(y, x))


def _fix_angle(a: float) -> float:
    a = a % 360.0
    return a + 360.0 if a < 0 else a


def _fix_hour(a: float) -> float:
    a = a % 24.0
    return a + 24.0 if a < 0 else a


def julian_date(d: date) -> float:
    y, m, day = d.year, d.month, d.day
    if m <= 2:
        y -= 1
        m += 12
    a = math.floor(y / 100)
    b = 2 - a + math.floor(a / 4)
    return (
        math.floor(365.25 * (y + 4716))
        + math.floor(30.6001 * (m + 1))
        + day
        + b
        - 1524.5
    )


def sun_position(jd: float) -> tuple[float, float]:
    """Returns (declination_deg, equation_of_time_hours)."""
    d = jd - 2451545.0
    g = _fix_angle(357.529 + 0.98560028 * d)
    q = _fix_angle(280.459 + 0.98564736 * d)
    ecliptic_lon = _fix_angle(q + 1.915 * _sind(g) + 0.020 * _sind(2 * g))
    obliquity = 23.439 - 0.00000036 * d
    declination = _arcsind(_sind(obliquity) * _sind(ecliptic_lon))
    right_ascension = _fix_hour(
        _arctan2d(_cosd(obliquity) * _sind(ecliptic_lon), _cosd(ecliptic_lon)) / 15.0
    )
    equation_of_time = q / 15.0 - right_ascension
    return declination, equation_of_time


def _sun_angle_hour(angle_deg: float, lat: float, decl: float) -> float:
    """Hours between solar noon and the moment the sun is `angle_deg`
    below (positive) or above the horizon."""
    numerator = -_sind(angle_deg) - _sind(decl) * _sind(lat)
    denominator = _cosd(decl) * _cosd(lat)
    return (1.0 / 15.0) * _arccosd(numerator / denominator)


def _asr_angle(factor: float, lat: float, decl: float) -> float:
    return -_arccotd(factor + _tand(abs(lat - decl)))


def _hours_to_time(hours: float) -> time:
    hours = _fix_hour(hours)
    total_minutes = round(hours * 60)
    hh, mm = divmod(total_minutes % (24 * 60), 60)
    return time(hour=hh, minute=mm)


def compute_prayer_times(
    d: date,
    latitude: float,
    longitude: float,
    timezone_offset_hours: float,
    convention: PrayerConvention | None = None,
) -> PrayerTimesResult:
    convention = convention or PrayerConvention()
    jd = julian_date(d)
    decl, eqt = sun_position(jd)

    noon = _fix_hour(12 - eqt)
    tz_correction = timezone_offset_hours - longitude / 15.0

    fajr_h = noon - _sun_angle_hour(convention.fajr_angle, latitude, decl)
    sunrise_h = noon - _sun_angle_hour(SUN_ANGLE_SUNRISE_SUNSET, latitude, decl)
    maghrib_h = noon + _sun_angle_hour(SUN_ANGLE_SUNRISE_SUNSET, latitude, decl)
    isha_h = noon + _sun_angle_hour(convention.isha_angle, latitude, decl)
    asr_angle = _asr_angle(convention.asr_factor, latitude, decl)
    asr_h = noon + _sun_angle_hour(asr_angle, latitude, decl)

    return PrayerTimesResult(
        fajr=_hours_to_time(fajr_h + tz_correction),
        sunrise=_hours_to_time(sunrise_h + tz_correction),
        zuhr=_hours_to_time(noon + tz_correction),
        asr=_hours_to_time(asr_h + tz_correction),
        maghrib=_hours_to_time(maghrib_h + tz_correction),
        isha=_hours_to_time(isha_h + tz_correction),
    )
