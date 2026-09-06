"""Adapts `thesis_log` / `reading_log` ORM rows — simple CRUD, no engine
involved (there's no ladder or ranking logic here, just a log)."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.life import ReadingLog, ThesisLog


async def list_thesis_logs(session: AsyncSession, user_id: uuid.UUID, limit: int = 100) -> list[ThesisLog]:
    result = await session.execute(
        select(ThesisLog).where(ThesisLog.user_id == user_id).order_by(ThesisLog.date.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def create_thesis_log(
    session: AsyncSession,
    user_id: uuid.UUID,
    on_date: date,
    work_summary: str,
    milestone: str | None,
    minutes: int | None,
    output_type: str | None,
    deadline: date | None,
    status: str | None,
) -> ThesisLog:
    log = ThesisLog(
        user_id=user_id,
        date=on_date,
        work_summary=work_summary,
        milestone=milestone,
        minutes=minutes,
        output_type=output_type,
        deadline=deadline,
        status=status,
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log


async def list_reading_logs(session: AsyncSession, user_id: uuid.UUID, limit: int = 200) -> list[ReadingLog]:
    result = await session.execute(
        select(ReadingLog).where(ReadingLog.user_id == user_id).order_by(ReadingLog.date.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def create_reading_log(
    session: AsyncSession,
    user_id: uuid.UUID,
    on_date: date,
    title: str,
    author: str | None,
    kind: str,
    progress_note: str | None,
    status: str | None,
) -> ReadingLog:
    log = ReadingLog(
        user_id=user_id,
        date=on_date,
        title=title,
        author=author,
        kind=kind,
        progress_note=progress_note,
        status=status,
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log


async def update_reading_log(
    session: AsyncSession,
    user_id: uuid.UUID,
    log_id: int,
    status: str | None,
    progress_note: str | None,
) -> ReadingLog | None:
    log = await session.get(ReadingLog, log_id)
    if log is None or log.user_id != user_id:
        return None
    if status is not None:
        log.status = status
    if progress_note is not None:
        log.progress_note = progress_note
    await session.commit()
    await session.refresh(log)
    return log
