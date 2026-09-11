"""End-to-end check of the vocab repository against the real database:
dedup on manual add, dedup+update on re-import, status persistence, and
per-user isolation of vocabulary lists.

Same pattern as test_cross_user_isolation.py / test_finance_integration.py:
one ephemeral user, real Postgres, full cleanup in a `finally`.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal, engine
from app.models.core import User
from app.models.life import VocabWord
from app.repositories import vocab as vocab_repo


@pytest.fixture
async def user() -> AsyncGenerator[tuple[AsyncSession, uuid.UUID], None]:
    session = SessionLocal()
    user_id = uuid.uuid4()
    session.add(User(id=user_id, email=f"vocab-test-{user_id}@test.local", settings={}))
    await session.commit()
    try:
        yield session, user_id
    finally:
        await session.execute(delete(VocabWord).where(VocabWord.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()
        await session.close()
        await engine.dispose()


async def test_find_by_word_is_case_insensitive(user: tuple[AsyncSession, uuid.UUID]) -> None:
    session, user_id = user
    await vocab_repo.create_word(session, user_id, "Ephemeral", "short-lived", None, None, None, None)

    found = await vocab_repo.find_by_word(session, user_id, "EPHEMERAL")
    assert found is not None
    assert found.word == "Ephemeral"


async def test_import_upsert_creates_once_then_updates_on_reimport(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user

    _, created_first = await vocab_repo.upsert_from_import(
        session,
        user_id,
        word="Sonder",
        definition="v1 definition",
        example_sentence=None,
        pronunciation=None,
        part_of_speech="noun",
        category=None,
        notion_page_id="notion-xyz",
    )
    assert created_first is True

    row, created_second = await vocab_repo.upsert_from_import(
        session,
        user_id,
        word="Sonder",
        definition="v2 definition, refined",
        example_sentence="A moment of sonder hit her on the train.",
        pronunciation=None,
        part_of_speech="noun",
        category="Emotions",
        notion_page_id="notion-xyz",
    )
    assert created_second is False
    assert row.definition == "v2 definition, refined"
    assert row.category == "Emotions"

    all_words = await vocab_repo.list_words(session, user_id)
    assert len([w for w in all_words if w.word == "Sonder"]) == 1


async def test_import_dedups_by_word_when_no_notion_id_given(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    await vocab_repo.upsert_from_import(
        session, user_id, word="Petrichor", definition="v1", example_sentence=None,
        pronunciation=None, part_of_speech=None, category=None, notion_page_id=None,
    )
    _, created_again = await vocab_repo.upsert_from_import(
        session, user_id, word="petrichor", definition="v2", example_sentence=None,
        pronunciation=None, part_of_speech=None, category=None, notion_page_id=None,
    )
    assert created_again is False
    words = await vocab_repo.list_words(session, user_id)
    assert len(words) == 1


async def test_learning_status_persists_and_filters(user: tuple[AsyncSession, uuid.UUID]) -> None:
    session, user_id = user
    a = await vocab_repo.create_word(session, user_id, "Word A", "def a", None, None, None, None)
    await vocab_repo.create_word(session, user_id, "Word B", "def b", None, None, None, None)

    await vocab_repo.set_learning_status(session, user_id, a.id, "need_to_revisit")

    flagged = await vocab_repo.list_words(session, user_id, learning_status="need_to_revisit")
    assert [w.word for w in flagged] == ["Word A"]

    everything = await vocab_repo.list_words(session, user_id)
    assert len(everything) == 2


async def test_upsert_oxford_word_creates_separate_rows_per_part_of_speech(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    _, created_adverb = await vocab_repo.upsert_oxford_word(
        session, user_id, word="about", part_of_speech="adverb", cefr_level="A1", definition=None
    )
    _, created_prep = await vocab_repo.upsert_oxford_word(
        session, user_id, word="about", part_of_speech="preposition", cefr_level="A1", definition=None
    )
    assert created_adverb is True
    assert created_prep is True

    rows = await vocab_repo.list_words(session, user_id)
    assert {w.part_of_speech for w in rows if w.word == "about"} == {"adverb", "preposition"}


async def test_upsert_oxford_word_updates_level_and_backfills_empty_definition_only(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    row, created = await vocab_repo.upsert_oxford_word(
        session, user_id, word="strip", part_of_speech="noun", cefr_level="B2", definition=None
    )
    assert created is True
    assert row.definition is None

    row, created_again = await vocab_repo.upsert_oxford_word(
        session, user_id, word="strip", part_of_speech="noun", cefr_level="C1", definition="long narrow piece"
    )
    assert created_again is False
    assert row.cefr_level == "C1"
    assert row.definition == "long narrow piece"

    row, _ = await vocab_repo.upsert_oxford_word(
        session, user_id, word="strip", part_of_speech="noun", cefr_level="C1", definition="a different hint"
    )
    assert row.definition == "long narrow piece"  # never overwrites a definition that's already there


async def test_update_word_edits_fields_and_can_clear_them(user: tuple[AsyncSession, uuid.UUID]) -> None:
    session, user_id = user
    row = await vocab_repo.create_word(
        session, user_id, "Meticulous", "very careful", None, None, "adjective", None
    )

    updated = await vocab_repo.update_word(
        session, user_id, row.id, {"synonyms": "careful, precise", "cefr_level": "C1"}
    )
    assert updated is not None
    assert updated.synonyms == "careful, precise"
    assert updated.cefr_level == "C1"

    cleared = await vocab_repo.update_word(session, user_id, row.id, {"synonyms": None})
    assert cleared is not None
    assert cleared.synonyms is None

    missing = await vocab_repo.update_word(session, user_id, 10_000_000, {"synonyms": "x"})
    assert missing is None


async def test_get_summary_counts_status_and_level_breakdowns(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    known = await vocab_repo.create_word(session, user_id, "Known", "d", None, None, None, None, cefr_level="B2")
    learning = await vocab_repo.create_word(
        session, user_id, "Learning", "d", None, None, None, None, cefr_level="C1"
    )
    await vocab_repo.create_word(session, user_id, "Untouched", "d", None, None, None, None, cefr_level="B2")

    await vocab_repo.set_learning_status(session, user_id, known.id, "known")
    await vocab_repo.set_learning_status(session, user_id, learning.id, "learning")

    summary = await vocab_repo.get_summary(session, user_id)
    assert summary["total_words"] == 3
    assert summary["attempted_count"] == 2
    assert summary["not_attempted_count"] == 1
    assert summary["known_count"] == 1
    assert summary["learning_count"] == 1
    assert summary["difficult_count"] == 0
    assert summary["need_to_revisit_count"] == 0
    assert summary["by_level"] == [("B2", 2), ("C1", 1)]


async def test_vocab_words_are_isolated_per_user() -> None:
    session_a = SessionLocal()
    session_b = SessionLocal()
    user_a, user_b = uuid.uuid4(), uuid.uuid4()
    session_a.add_all(
        [
            User(id=user_a, email=f"vocab-a-{user_a}@test.local", settings={}),
            User(id=user_b, email=f"vocab-b-{user_b}@test.local", settings={}),
        ]
    )
    await session_a.commit()
    try:
        await vocab_repo.create_word(session_a, user_a, "OnlyA", "def", None, None, None, None)
        await vocab_repo.create_word(session_b, user_b, "OnlyB", "def", None, None, None, None)

        words_a = await vocab_repo.list_words(session_a, user_a)
        words_b = await vocab_repo.list_words(session_b, user_b)
        assert [w.word for w in words_a] == ["OnlyA"]
        assert [w.word for w in words_b] == ["OnlyB"]
    finally:
        await session_a.execute(delete(VocabWord).where(VocabWord.user_id.in_([user_a, user_b])))
        await session_a.execute(delete(User).where(User.id.in_([user_a, user_b])))
        await session_a.commit()
        await session_a.close()
        await session_b.close()
        await engine.dispose()
