from datetime import date, time

from app.engines.prayer import PrayerConvention, compute_prayer_times

ISLAMABAD_LAT = 33.6844
ISLAMABAD_LON = 73.0479
PKT_OFFSET = 5.0  # Asia/Karachi, no DST


def test_prayer_times_are_correctly_ordered() -> None:
    result = compute_prayer_times(date(2026, 9, 6), ISLAMABAD_LAT, ISLAMABAD_LON, PKT_OFFSET)
    order = [result.fajr, result.sunrise, result.zuhr, result.asr, result.maghrib, result.isha]
    assert order == sorted(order)


def test_prayer_times_fall_within_plausible_bounds_for_islamabad() -> None:
    # Sanity bounds, not ground truth — the disclosed tolerance is ±5-15
    # min (build prompt 2.5), and these are wide enough to catch a real
    # formula error while tolerating that.
    result = compute_prayer_times(date(2026, 9, 6), ISLAMABAD_LAT, ISLAMABAD_LON, PKT_OFFSET)
    assert time(4, 0) <= result.fajr <= time(5, 30)
    assert time(5, 30) <= result.sunrise <= time(7, 0)
    assert time(11, 45) <= result.zuhr <= time(12, 45)
    assert time(15, 0) <= result.asr <= time(17, 0)
    assert time(17, 30) <= result.maghrib <= time(19, 30)
    assert time(18, 30) <= result.isha <= time(21, 0)


def test_hanafi_asr_is_later_than_shafii_asr() -> None:
    hanafi = compute_prayer_times(
        date(2026, 9, 6), ISLAMABAD_LAT, ISLAMABAD_LON, PKT_OFFSET, PrayerConvention(asr_factor=2.0)
    )
    shafii = compute_prayer_times(
        date(2026, 9, 6), ISLAMABAD_LAT, ISLAMABAD_LON, PKT_OFFSET, PrayerConvention(asr_factor=1.0)
    )
    assert hanafi.asr > shafii.asr


def test_winter_and_summer_dates_both_resolve_sensibly() -> None:
    winter = compute_prayer_times(date(2026, 12, 21), ISLAMABAD_LAT, ISLAMABAD_LON, PKT_OFFSET)
    summer = compute_prayer_times(date(2026, 6, 21), ISLAMABAD_LAT, ISLAMABAD_LON, PKT_OFFSET)
    # Winter fajr is later and maghrib earlier than summer's, at this latitude.
    assert winter.fajr > summer.fajr
    assert winter.maghrib < summer.maghrib
