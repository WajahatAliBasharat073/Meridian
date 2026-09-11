"""End-to-end check of the reading-books repository against the real
database: dedup on title+author, quote add/delete, book delete cascades
its sessions, and filters actually filter.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from datetime import date

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal, engine
from app.models.core import User
from app.models.life import ReadingBook, ReadingSession
from app.repositories import life_logs as life_logs_repo


@pytest.fixture
async def user() -> AsyncGenerator[tuple[AsyncSession, uuid.UUID], None]:
    session = SessionLocal()
    user_id = uuid.uuid4()
    session.add(User(id=user_id, email=f"reading-test-{user_id}@test.local", settings={}))
    await session.commit()
    try:
        yield session, user_id
    finally:
        await session.execute(delete(ReadingSession).where(ReadingSession.user_id == user_id))
        await session.execute(delete(ReadingBook).where(ReadingBook.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()
        await session.close()
        await engine.dispose()


async def test_find_by_title_author_is_case_insensitive(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    await life_logs_repo.create_reading_book(
        session, user_id, "Atomic Habits", "James Clear", None, None, "book", None, "reading", None
    )
    found = await life_logs_repo.find_book_by_title_author(session, user_id, "ATOMIC HABITS", "james clear")
    assert found is not None
    assert found.title == "Atomic Habits"


async def test_quotes_can_be_added_and_deleted(user: tuple[AsyncSession, uuid.UUID]) -> None:
    session, user_id = user
    book = await life_logs_repo.create_reading_book(
        session, user_id, "Deep Work", None, None, None, "book", None, "reading", None
    )
    updated = await life_logs_repo.add_quote(session, user_id, book.id, "Focus is the new IQ.", 42)
    assert updated is not None
    assert updated.quotes == [{"text": "Focus is the new IQ.", "page": 42}]

    updated = await life_logs_repo.add_quote(session, user_id, book.id, "Clarity breeds focus.", 10)
    assert len(updated.quotes) == 2

    after_delete = await life_logs_repo.delete_quote(session, user_id, book.id, 0)
    assert after_delete is not None
    assert after_delete.quotes == [{"text": "Clarity breeds focus.", "page": 10}]


async def test_deleting_a_book_removes_its_sessions_too(user: tuple[AsyncSession, uuid.UUID]) -> None:
    session, user_id = user
    book = await life_logs_repo.create_reading_book(
        session, user_id, "Sapiens", None, None, 400, "book", None, "reading", None
    )
    await life_logs_repo.create_reading_session(session, user_id, book.id, date.today(), 50, 30, None)

    deleted = await life_logs_repo.delete_reading_book(session, user_id, book.id)
    assert deleted is True

    remaining_sessions = await life_logs_repo.list_reading_sessions(session, user_id, book.id)
    assert remaining_sessions == []
    assert await life_logs_repo.get_reading_book(session, user_id, book.id) is None


async def test_status_and_revisit_filters_narrow_the_list(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    await life_logs_repo.create_reading_book(
        session, user_id, "Currently Reading Book", None, None, None, "book", None, "reading", None
    )
    to_revisit = await life_logs_repo.create_reading_book(
        session, user_id, "Revisit Book", None, None, None, "book", None, "completed", None
    )
    await life_logs_repo.update_reading_book(
        session, user_id, to_revisit.id, {"revisit_date": date(2026, 12, 1)}
    )

    reading_only = await life_logs_repo.list_reading_books(session, user_id, status_filter="reading")
    assert [b.title for b in reading_only] == ["Currently Reading Book"]

    revisit_only = await life_logs_repo.list_reading_books(session, user_id, needs_revisit=True)
    assert [b.title for b in revisit_only] == ["Revisit Book"]


async def test_tag_filter_matches_books_containing_that_tag(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    await life_logs_repo.create_reading_book(
        session, user_id, "Tagged Book", None, None, None, "book", None, "reading", None,
        tags=["ml", "career"],
    )
    await life_logs_repo.create_reading_book(
        session, user_id, "Untagged Book", None, None, None, "book", None, "reading", None,
    )

    matches = await life_logs_repo.list_reading_books(session, user_id, tag="ml")
    assert [b.title for b in matches] == ["Tagged Book"]
