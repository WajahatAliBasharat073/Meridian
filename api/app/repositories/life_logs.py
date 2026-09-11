"""Adapts `thesis_log` / `reading_books` / `reading_sessions` ORM rows —
simple CRUD, no engine involved (there's no ladder or ranking logic here,
just a log — reading progress is a plain division, done in the router)."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.life import NutritionLog, ReadingBook, ReadingSession, RecoveryLog, ThesisLog


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


async def list_reading_books(
    session: AsyncSession,
    user_id: uuid.UUID,
    status_filter: str | None = None,
    category: str | None = None,
    tag: str | None = None,
    search: str | None = None,
    needs_revisit: bool = False,
) -> list[ReadingBook]:
    """Reading first, then most recently added — a book you're actively
    on belongs above your backlog and your finished shelf. Filters are
    applied server-side rather than fetched-then-filtered client-side,
    since a growing library is exactly the case this needs to scale for."""
    query = select(ReadingBook).where(ReadingBook.user_id == user_id)
    if status_filter:
        query = query.where(ReadingBook.status == status_filter)
    if category:
        query = query.where(ReadingBook.category == category)
    if tag:
        query = query.where(ReadingBook.tags.contains([tag]))
    if search:
        pattern = f"%{search}%"
        query = query.where(
            (ReadingBook.title.ilike(pattern)) | (ReadingBook.author.ilike(pattern))
        )
    if needs_revisit:
        query = query.where(ReadingBook.revisit_date.is_not(None))

    result = await session.execute(query.order_by(ReadingBook.id.desc()))
    books = list(result.scalars().all())

    status_order = {"reading": 0, "to_read": 1, "paused": 2, "completed": 3, "dropped": 4}
    books.sort(key=lambda b: status_order.get(b.status, 9))
    return books


async def delete_reading_book(session: AsyncSession, user_id: uuid.UUID, book_id: int) -> bool:
    book = await get_reading_book(session, user_id, book_id)
    if book is None:
        return False
    await session.execute(delete(ReadingSession).where(ReadingSession.book_id == book_id))
    await session.delete(book)
    await session.commit()
    return True


async def list_all_reading_sessions(session: AsyncSession, user_id: uuid.UUID) -> list[ReadingSession]:
    """Every session across every book, most recent first -- the raw
    material for reading-history and streak calculations."""
    result = await session.execute(
        select(ReadingSession)
        .where(ReadingSession.user_id == user_id)
        .order_by(ReadingSession.date.desc(), ReadingSession.id.desc())
    )
    return list(result.scalars().all())


async def get_reading_book(session: AsyncSession, user_id: uuid.UUID, book_id: int) -> ReadingBook | None:
    book = await session.get(ReadingBook, book_id)
    return book if book is not None and book.user_id == user_id else None


async def find_book_by_title_author(
    session: AsyncSession, user_id: uuid.UUID, title: str, author: str | None
) -> ReadingBook | None:
    """Case-insensitive (title, author) match -- the dedup key an import
    uses, since a personal library doesn't need a stronger identity than
    that (unlike vocab_words, there's no stable external id to key on)."""
    query = select(ReadingBook).where(
        ReadingBook.user_id == user_id, func.lower(ReadingBook.title) == title.strip().lower()
    )
    if author:
        query = query.where(func.lower(ReadingBook.author) == author.strip().lower())
    else:
        query = query.where(ReadingBook.author.is_(None))
    return (await session.execute(query)).scalar_one_or_none()


async def create_reading_book(
    session: AsyncSession,
    user_id: uuid.UUID,
    title: str,
    author: str | None,
    cover_url: str | None,
    total_pages: int | None,
    fmt: str,
    category: str | None,
    status: str,
    started_date: date | None,
    priority: str | None = None,
    tags: list[str] | None = None,
    why_reading: str | None = None,
) -> ReadingBook:
    book = ReadingBook(
        user_id=user_id,
        title=title,
        author=author,
        cover_url=cover_url,
        total_pages=total_pages,
        format=fmt,
        category=category,
        status=status,
        started_date=started_date or (date.today() if status == "reading" else None),
        priority=priority,
        tags=tags or [],
        why_reading=why_reading,
        created_at=datetime.now(),
    )
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book


async def add_quote(
    session: AsyncSession, user_id: uuid.UUID, book_id: int, text: str, page: int | None
) -> ReadingBook | None:
    """Quotes are additive -- appended one at a time, not sent as a whole
    replacement list the client would have to keep in sync itself."""
    book = await get_reading_book(session, user_id, book_id)
    if book is None:
        return None
    book.quotes = [*book.quotes, {"text": text, "page": page}]
    await session.commit()
    await session.refresh(book)
    return book


async def delete_quote(
    session: AsyncSession, user_id: uuid.UUID, book_id: int, quote_index: int
) -> ReadingBook | None:
    book = await get_reading_book(session, user_id, book_id)
    if book is None:
        return None
    if 0 <= quote_index < len(book.quotes):
        book.quotes = [q for i, q in enumerate(book.quotes) if i != quote_index]
        await session.commit()
        await session.refresh(book)
    return book


async def update_reading_book(
    session: AsyncSession,
    user_id: uuid.UUID,
    book_id: int,
    fields: dict[str, object],
) -> ReadingBook | None:
    book = await get_reading_book(session, user_id, book_id)
    if book is None:
        return None
    # `fields` only contains keys the caller actually sent (the router
    # builds it with `exclude_unset=True`), so an explicit None here means
    # "clear this" -- unlike an omitted key, which means "don't touch it".
    # Setting it unconditionally is what makes clearing revisit_date (or
    # any other nullable field) via update possible at all.
    for key, value in fields.items():
        setattr(book, key, value)
    # Finishing sets the date if the caller didn't supply one explicitly —
    # a status flip to "completed" is itself the record of when that
    # happened, so it shouldn't require a second field to be filled in.
    if fields.get("status") == "completed" and book.finished_date is None:
        book.finished_date = date.today()
    await session.commit()
    await session.refresh(book)
    return book


async def get_reading_progress(
    session: AsyncSession, user_id: uuid.UUID, book_ids: list[int]
) -> dict[int, tuple[int | None, int, int, date | None, str | None]]:
    """book_id -> (current_page, session_count, total_minutes, last_date, last_note).

    `current_page` comes from the most recent session that actually
    recorded a page — a session logged purely as a note doesn't overwrite
    the last known position with None.
    """
    if not book_ids:
        return {}

    rows = (
        await session.execute(
            select(ReadingSession)
            .where(ReadingSession.user_id == user_id, ReadingSession.book_id.in_(book_ids))
            .order_by(ReadingSession.date, ReadingSession.id)
        )
    ).scalars().all()

    out: dict[int, tuple[int | None, int, int, date | None, str | None]] = {}
    for r in rows:
        current_page, count, minutes, _, _ = out.get(r.book_id, (None, 0, 0, None, None))
        out[r.book_id] = (
            r.page_reached if r.page_reached is not None else current_page,
            count + 1,
            minutes + (r.minutes or 0),
            r.date,
            r.note,
        )
    return out


async def list_reading_sessions(
    session: AsyncSession, user_id: uuid.UUID, book_id: int
) -> list[ReadingSession]:
    result = await session.execute(
        select(ReadingSession)
        .where(ReadingSession.user_id == user_id, ReadingSession.book_id == book_id)
        .order_by(ReadingSession.date.desc(), ReadingSession.id.desc())
    )
    return list(result.scalars().all())


async def create_reading_session(
    session: AsyncSession,
    user_id: uuid.UUID,
    book_id: int,
    on_date: date,
    page_reached: int | None,
    minutes: int | None,
    note: str | None,
) -> ReadingSession:
    entry = ReadingSession(
        user_id=user_id,
        book_id=book_id,
        date=on_date,
        page_reached=page_reached,
        minutes=minutes,
        note=note,
        created_at=datetime.now(),
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


async def get_recovery_log(
    session: AsyncSession, user_id: uuid.UUID, on_date: date
) -> RecoveryLog | None:
    result = await session.execute(
        select(RecoveryLog).where(RecoveryLog.user_id == user_id, RecoveryLog.date == on_date)
    )
    return result.scalar_one_or_none()


async def get_nutrition_log(
    session: AsyncSession, user_id: uuid.UUID, on_date: date
) -> NutritionLog | None:
    result = await session.execute(
        select(NutritionLog).where(NutritionLog.user_id == user_id, NutritionLog.date == on_date)
    )
    return result.scalar_one_or_none()


async def upsert_recovery_log(
    session: AsyncSession, user_id: uuid.UUID, on_date: date, fields: dict[str, object]
) -> RecoveryLog:
    """One row per day, patched field by field.

    Only keys actually present are written, so entering sleep in the morning
    does not blank out the stress rating entered last night.
    """
    row = await get_recovery_log(session, user_id, on_date)
    if row is None:
        row = RecoveryLog(user_id=user_id, date=on_date)
        session.add(row)
    for key, value in fields.items():
        setattr(row, key, value)
    await session.commit()
    await session.refresh(row)
    return row


async def upsert_nutrition_log(
    session: AsyncSession, user_id: uuid.UUID, on_date: date, fields: dict[str, object]
) -> NutritionLog:
    row = await get_nutrition_log(session, user_id, on_date)
    if row is None:
        row = NutritionLog(user_id=user_id, date=on_date)
        session.add(row)
    for key, value in fields.items():
        setattr(row, key, value)
    await session.commit()
    await session.refresh(row)
    return row


async def add_water(
    session: AsyncSession, user_id: uuid.UUID, on_date: date, ml: int
) -> NutritionLog:
    """Increment today's water, creating the row if this is the first glass.

    Additive rather than a set: the hydration reminder fires several times a
    day and each "Done" is another glass, not a new total.
    """
    row = await get_nutrition_log(session, user_id, on_date)
    if row is None:
        row = NutritionLog(user_id=user_id, date=on_date, water_ml=0)
        session.add(row)
    row.water_ml = (row.water_ml or 0) + ml
    await session.commit()
    await session.refresh(row)
    return row


async def list_recovery_logs(
    session: AsyncSession, user_id: uuid.UUID, limit: int = 30
) -> list[RecoveryLog]:
    result = await session.execute(
        select(RecoveryLog)
        .where(RecoveryLog.user_id == user_id)
        .order_by(RecoveryLog.date.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
