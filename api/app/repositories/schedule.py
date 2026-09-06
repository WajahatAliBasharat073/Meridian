"""Adapts `time_blocks` / `prayer_times` ORM rows to and from the
scheduling engine. The engine itself never sees a Session (app/domain.py)."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.engines.prayer import PrayerConvention, PrayerTimesResult, compute_prayer_times
from app.engines.scheduling import resolve_spec
from app.models.core import PrayerTimes, TimeBlock


async def get_or_compute_prayer_times(
    session: AsyncSession, on_date: date, settings: Settings
) -> PrayerTimesResult:
    row = await session.get(PrayerTimes, on_date)
    if row is not None:
        return PrayerTimesResult(
            fajr=row.fajr,
            sunrise=row.sunrise,
            zuhr=row.zuhr,
            asr=row.asr,
            maghrib=row.maghrib,
            isha=row.isha,
        )

    timezone_offset = _tz_offset_hours(settings.timezone, on_date)
    result = compute_prayer_times(
        on_date, settings.latitude, settings.longitude, timezone_offset, PrayerConvention()
    )
    row = PrayerTimes(
        date=on_date,
        fajr=result.fajr,
        sunrise=result.sunrise,
        zuhr=result.zuhr,
        asr=result.asr,
        maghrib=result.maghrib,
        isha=result.isha,
    )
    session.add(row)
    await session.commit()
    return result


def _tz_offset_hours(tz_name: str, on_date: date) -> float:
    from zoneinfo import ZoneInfo

    dt = datetime(on_date.year, on_date.month, on_date.day, 12, tzinfo=ZoneInfo(tz_name))
    offset = dt.utcoffset()
    return (offset.total_seconds() / 3600.0) if offset else 0.0


async def get_blocks_for_date(
    session: AsyncSession, user_id: uuid.UUID, on_date: date, prayer_times: PrayerTimesResult
) -> list[TimeBlock]:
    result = await session.execute(
        select(TimeBlock)
        .where(TimeBlock.user_id == user_id, TimeBlock.date == on_date)
        .order_by(TimeBlock.seq)
    )
    blocks = list(result.scalars().all())
    dirty = False
    for b in blocks:
        start = resolve_spec(b.start_spec, prayer_times, on_date)
        end = resolve_spec(b.end_spec, prayer_times, on_date)
        if b.start_resolved != start or b.end_resolved != end:
            b.start_resolved = start
            b.end_resolved = end
            dirty = True
    if dirty:
        await session.commit()
    return blocks


async def update_block_status(
    session: AsyncSession,
    user_id: uuid.UUID,
    block_id: int,
    status: str,
    actual_minutes: int | None,
) -> TimeBlock | None:
    block = await session.get(TimeBlock, block_id)
    if block is None or block.user_id != user_id:
        return None
    block.status = status
    if actual_minutes is not None:
        block.actual_minutes = actual_minutes
    block.completed_at = datetime.now() if status == "DONE" else block.completed_at
    await session.commit()
    await session.refresh(block)
    return block
