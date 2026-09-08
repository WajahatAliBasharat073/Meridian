from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.repositories import life_logs as life_logs_repo
from app.schemas import (
    ReadingBookCreate,
    ReadingBookOut,
    ReadingBookUpdate,
    ReadingSessionCreate,
    ReadingSessionOut,
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


def _book_out(  # type: ignore[no-untyped-def]
    book,
    progress: tuple[int | None, int, int, object, str | None] | None,
) -> ReadingBookOut:
    current_page, session_count, total_minutes, last_date, last_note = progress or (
        None,
        0,
        0,
        None,
        None,
    )
    progress_pct = (
        round(100 * min(current_page, book.total_pages) / book.total_pages, 1)
        if current_page is not None and book.total_pages
        else None
    )
    return ReadingBookOut(
        id=book.id,
        title=book.title,
        author=book.author,
        cover_url=book.cover_url,
        total_pages=book.total_pages,
        format=book.format,
        category=book.category,
        status=book.status,
        rating=book.rating,
        started_date=book.started_date,
        finished_date=book.finished_date,
        notes=book.notes,
        current_page=current_page,
        progress_pct=progress_pct,
        session_count=session_count,
        total_minutes_logged=total_minutes,
        last_session_date=last_date,
        last_session_note=last_note,
    )


def _session_out(entry) -> ReadingSessionOut:  # type: ignore[no-untyped-def]
    return ReadingSessionOut(
        id=entry.id,
        book_id=entry.book_id,
        date=entry.date,
        page_reached=entry.page_reached,
        minutes=entry.minutes,
        note=entry.note,
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


@router.get("/api/reading/books", response_model=list[ReadingBookOut])
async def list_reading_books(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[ReadingBookOut]:
    books = await life_logs_repo.list_reading_books(session, user_id)
    progress = await life_logs_repo.get_reading_progress(session, user_id, [b.id for b in books])
    return [_book_out(b, progress.get(b.id)) for b in books]


@router.post("/api/reading/books", response_model=ReadingBookOut, status_code=status.HTTP_201_CREATED)
async def create_reading_book(
    payload: ReadingBookCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ReadingBookOut:
    book = await life_logs_repo.create_reading_book(
        session, user_id, payload.title, payload.author, payload.cover_url, payload.total_pages,
        payload.format, payload.category, payload.status, payload.started_date,
    )
    return _book_out(book, None)


@router.patch("/api/reading/books/{book_id}", response_model=ReadingBookOut)
async def update_reading_book(
    book_id: int,
    payload: ReadingBookUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ReadingBookOut:
    book = await life_logs_repo.update_reading_book(
        session, user_id, book_id, payload.model_dump(exclude_unset=True)
    )
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    progress = await life_logs_repo.get_reading_progress(session, user_id, [book.id])
    return _book_out(book, progress.get(book.id))


@router.get("/api/reading/books/{book_id}/sessions", response_model=list[ReadingSessionOut])
async def list_reading_sessions(
    book_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[ReadingSessionOut]:
    book = await life_logs_repo.get_reading_book(session, user_id, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    entries = await life_logs_repo.list_reading_sessions(session, user_id, book_id)
    return [_session_out(e) for e in entries]


@router.post(
    "/api/reading/books/{book_id}/sessions",
    response_model=ReadingBookOut,
    status_code=status.HTTP_201_CREATED,
)
async def log_reading_session(
    book_id: int,
    payload: ReadingSessionCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ReadingBookOut:
    """Logs today's page and returns the *book*, not the session row — the
    UI shows a progress bar per book, so recomputing it here saves the
    frontend a second round trip on every log."""
    book = await life_logs_repo.get_reading_book(session, user_id, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    await life_logs_repo.create_reading_session(
        session, user_id, book_id, payload.date, payload.page_reached, payload.minutes, payload.note
    )
    # A page logged at or past the last page is a strong, unambiguous
    # signal the book is finished — worth reflecting immediately rather
    # than leaving status stuck on "reading" until the user remembers to
    # flip it by hand.
    if (
        book.total_pages
        and payload.page_reached is not None
        and payload.page_reached >= book.total_pages
        and book.status == "reading"
    ):
        book = await life_logs_repo.update_reading_book(session, user_id, book_id, {"status": "completed"})
    progress = await life_logs_repo.get_reading_progress(session, user_id, [book_id])
    return _book_out(book, progress.get(book_id))
