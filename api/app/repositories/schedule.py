"""Adapts `time_blocks` / `prayer_times` ORM rows to and from the
scheduling engine. The engine itself never sees a Session (app/domain.py)."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.engines.block_lock import (
    BlockLockedError,
    TooEarlyToCompleteError,
    is_block_locked,
    is_too_early_to_complete,
)
from app.engines.prayer import PrayerConvention, PrayerTimesResult, compute_prayer_times
from app.engines.scheduling import resolve_spec
from app.models.core import PrayerTimes, TimeBlock
from app.models.sessions import FocusSession


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


async def create_block(
    session: AsyncSession,
    user_id: uuid.UUID,
    on_date: date,
    start_spec: str,
    end_spec: str,
    activity: str,
    tier: str,
    category: str,
    planned_minutes: int,
    what_to_do: str | None,
    notes: str | None,
    prayer_times: PrayerTimesResult,
) -> TimeBlock:
    """Resolves the spec up front (raises InvalidTimeSpecError on a bad
    one, same validation the read path already trusts) and assigns the
    next sequence slot for that day — no manual seq juggling for the
    caller."""
    start_resolved = resolve_spec(start_spec, prayer_times, on_date)
    end_resolved = resolve_spec(end_spec, prayer_times, on_date)

    next_seq = await session.scalar(
        select(func.coalesce(func.max(TimeBlock.seq), 0) + 1).where(
            TimeBlock.user_id == user_id, TimeBlock.date == on_date
        )
    )

    block = TimeBlock(
        user_id=user_id,
        date=on_date,
        seq=next_seq,
        start_spec=start_spec,
        end_spec=end_spec,
        start_resolved=start_resolved,
        end_resolved=end_resolved,
        activity=activity,
        tier=tier,
        category=category,
        planned_minutes=planned_minutes,
        status="NOT DONE",
        what_to_do=what_to_do,
        notes=notes,
    )
    session.add(block)
    await session.commit()
    await session.refresh(block)
    return block


async def update_block_status(
    session: AsyncSession,
    user_id: uuid.UUID,
    block_id: int,
    status: str,
    actual_minutes: int | None,
    now: datetime,
) -> TimeBlock | None:
    """`now` is required (not read from the clock in here) so this stays as
    testable as the rest of the layer, and so it's unambiguously the same
    "now" the caller used to decide anything else about the request.

    Raises BlockLockedError when marking a block DONE would claim real
    work happened on it after most of its window passed with no focus
    session ever started, and TooEarlyToCompleteError when marking it DONE
    while most of its window is still ahead — see app/engines/block_lock.py.
    """
    block = await session.get(TimeBlock, block_id)
    if block is None or block.user_id != user_id:
        return None

    if status == "DONE" and block.date == now.date():
        already_engaged = (
            await session.execute(
                select(FocusSession.id)
                .where(FocusSession.user_id == user_id, FocusSession.block_id == block_id)
                .limit(1)
            )
        ).first() is not None
        if is_block_locked(block.start_resolved, block.planned_minutes, now.time(), already_engaged):
            raise BlockLockedError(
                "Most of this block's window passed without starting focus on it"
            )
        if is_too_early_to_complete(block.end_resolved, now.time()):
            raise TooEarlyToCompleteError(
                "Too early to mark this done — wait until the last "
                "5 minutes of its window (or after it ends)"
            )

    block.status = status
    if actual_minutes is not None:
        block.actual_minutes = actual_minutes
    block.completed_at = datetime.now() if status == "DONE" else block.completed_at
    await session.commit()
    await session.refresh(block)
    return block
