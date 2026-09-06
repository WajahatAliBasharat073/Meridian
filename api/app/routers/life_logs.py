from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.repositories import life_logs as life_logs_repo
from app.schemas import (
    ReadingLogCreate,
    ReadingLogOut,
    ReadingLogUpdate,
    ThesisLogCreate,
    ThesisLogOut,
)

router = APIRouter(tags=["life-logs"])


def _thesis_out(log) -> ThesisLogOut:  # type: ignore[no-untyped-def]
    return ThesisLogOut(
        id=log.id,
        date=log.date,
        milestone=log.milestone,
        work_summary=log.work_summary,
        minutes=log.minutes,
        output_type=log.output_type,
        deadline=log.deadline,
        status=log.status,
    )


def _reading_out(log) -> ReadingLogOut:  # type: ignore[no-untyped-def]
    return ReadingLogOut(
        id=log.id,
        date=log.date,
        title=log.title,
        author=log.author,
        kind=log.kind,
        progress_note=log.progress_note,
        status=log.status,
    )


@router.get("/api/thesis-log", response_model=list[ThesisLogOut])
async def list_thesis_log(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[ThesisLogOut]:
    logs = await life_logs_repo.list_thesis_logs(session, user_id)
    return [_thesis_out(log) for log in logs]


@router.post("/api/thesis-log", response_model=ThesisLogOut, status_code=status.HTTP_201_CREATED)
async def create_thesis_log(
    payload: ThesisLogCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ThesisLogOut:
    log = await life_logs_repo.create_thesis_log(
        session,
        user_id,
        payload.date,
        payload.work_summary,
        payload.milestone,
        payload.minutes,
        payload.output_type,
        payload.deadline,
        payload.status,
    )
    return _thesis_out(log)


@router.get("/api/reading-log", response_model=list[ReadingLogOut])
async def list_reading_log(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[ReadingLogOut]:
    logs = await life_logs_repo.list_reading_logs(session, user_id)
    return [_reading_out(log) for log in logs]


@router.post("/api/reading-log", response_model=ReadingLogOut, status_code=status.HTTP_201_CREATED)
async def create_reading_log(
    payload: ReadingLogCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ReadingLogOut:
    log = await life_logs_repo.create_reading_log(
        session, user_id, payload.date, payload.title, payload.author, payload.kind,
        payload.progress_note, payload.status,
    )
    return _reading_out(log)


@router.patch("/api/reading-log/{log_id}", response_model=ReadingLogOut)
async def update_reading_log(
    log_id: int,
    payload: ReadingLogUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ReadingLogOut:
    log = await life_logs_repo.update_reading_log(session, user_id, log_id, payload.status, payload.progress_note)
    if log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reading log not found")
    return _reading_out(log)
