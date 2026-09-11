"""vocab_words repository. Dedup is applied here, at the write boundary,
for both write paths (manual add and CSV import) -- case-insensitive on
`word`, per-user, so the same word typed twice or re-imported twice
never produces two rows.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.vocab import VocabWordFixture
from app.models.life import VocabWord


async def list_words(
    session: AsyncSession, user_id: uuid.UUID, learning_status: str | None = None
) -> list[VocabWord]:
    query = select(VocabWord).where(VocabWord.user_id == user_id)
    if learning_status is not None:
        query = query.where(VocabWord.learning_status == learning_status)
    query = query.order_by(VocabWord.word)
    return list((await session.execute(query)).scalars().all())


async def get_word_fixtures(session: AsyncSession, user_id: uuid.UUID) -> list[VocabWordFixture]:
    rows = (
        await session.execute(
            select(VocabWord.id, VocabWord.learning_status, VocabWord.word).where(
                VocabWord.user_id == user_id
            )
        )
    ).all()
    return [VocabWordFixture(id=r.id, word=r.word, learning_status=r.learning_status) for r in rows]


async def find_by_word(session: AsyncSession, user_id: uuid.UUID, word: str) -> VocabWord | None:
    """Case-insensitive lookup -- the dedup check every write path uses."""
    return (
        await session.execute(
            select(VocabWord).where(
                VocabWord.user_id == user_id, func.lower(VocabWord.word) == word.strip().lower()
            )
        )
    ).scalar_one_or_none()


async def create_word(
    session: AsyncSession,
    user_id: uuid.UUID,
    word: str,
    definition: str | None,
    example_sentence: str | None,
    pronunciation: str | None,
    part_of_speech: str | None,
    category: str | None,
    cefr_level: str | None = None,
    synonyms: str | None = None,
    antonyms: str | None = None,
    word_patterns: str | None = None,
    paraphrase: str | None = None,
    dictionary_link: str | None = None,
    notes: str | None = None,
) -> VocabWord:
    row = VocabWord(
        user_id=user_id,
        word=word.strip(),
        definition=definition,
        example_sentence=example_sentence,
        pronunciation=pronunciation,
        part_of_speech=part_of_speech,
        category=category,
        cefr_level=cefr_level,
        synonyms=synonyms,
        antonyms=antonyms,
        word_patterns=word_patterns,
        paraphrase=paraphrase,
        dictionary_link=dictionary_link,
        notes=notes,
        date_introduced=date.today(),
        source="manual",
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def update_word(
    session: AsyncSession, user_id: uuid.UUID, word_id: int, fields: dict[str, object]
) -> VocabWord | None:
    row = await session.get(VocabWord, word_id)
    if row is None or row.user_id != user_id:
        return None
    for key, value in fields.items():
        setattr(row, key, value)
    await session.commit()
    await session.refresh(row)
    return row


async def set_learning_status(
    session: AsyncSession, user_id: uuid.UUID, word_id: int, learning_status: str | None
) -> VocabWord | None:
    row = await session.get(VocabWord, word_id)
    if row is None or row.user_id != user_id:
        return None
    row.learning_status = learning_status
    await session.commit()
    await session.refresh(row)
    return row


async def delete_word(session: AsyncSession, user_id: uuid.UUID, word_id: int) -> bool:
    row = await session.get(VocabWord, word_id)
    if row is None or row.user_id != user_id:
        return False
    await session.delete(row)
    await session.commit()
    return True


async def upsert_from_import(
    session: AsyncSession,
    user_id: uuid.UUID,
    *,
    word: str,
    definition: str,
    example_sentence: str | None,
    pronunciation: str | None,
    part_of_speech: str | None,
    category: str | None,
    notion_page_id: str | None,
) -> tuple[VocabWord, bool]:
    """Insert, or update in place if this Notion page (or, lacking one,
    this exact word) was already imported. Returns (row, created)."""
    existing: VocabWord | None = None
    if notion_page_id:
        existing = (
            await session.execute(
                select(VocabWord).where(
                    VocabWord.user_id == user_id, VocabWord.notion_page_id == notion_page_id
                )
            )
        ).scalar_one_or_none()
    if existing is None:
        existing = await find_by_word(session, user_id, word)

    if existing is not None:
        existing.definition = definition
        existing.example_sentence = example_sentence
        existing.pronunciation = pronunciation
        existing.part_of_speech = part_of_speech
        existing.category = category
        existing.notion_page_id = notion_page_id or existing.notion_page_id
        existing.last_synced_at = datetime.now(UTC).replace(tzinfo=None)
        await session.commit()
        await session.refresh(existing)
        return existing, False

    row = VocabWord(
        user_id=user_id,
        word=word.strip(),
        definition=definition,
        example_sentence=example_sentence,
        pronunciation=pronunciation,
        part_of_speech=part_of_speech,
        category=category,
        date_introduced=date.today(),
        source="notion_import",
        notion_page_id=notion_page_id,
        last_synced_at=datetime.now(UTC).replace(tzinfo=None),
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row, True


async def find_by_word_and_pos(
    session: AsyncSession, user_id: uuid.UUID, word: str, part_of_speech: str | None
) -> VocabWord | None:
    """The dedup key scripts/import_oxford_5000.py uses -- a word list
    (unlike a Notion export) has no stable external id, and a single word
    legitimately gets more than one row when it has more than one part of
    speech (e.g. "about" as adverb and "about" as preposition are two
    real, different rows, matching how the user's own Notion tracker
    already represents this)."""
    query = select(VocabWord).where(
        VocabWord.user_id == user_id, func.lower(VocabWord.word) == word.strip().lower()
    )
    if part_of_speech:
        query = query.where(VocabWord.part_of_speech == part_of_speech)
    else:
        query = query.where(VocabWord.part_of_speech.is_(None))
    return (await session.execute(query)).scalars().first()


async def upsert_oxford_word(
    session: AsyncSession,
    user_id: uuid.UUID,
    *,
    word: str,
    part_of_speech: str | None,
    cefr_level: str | None,
    definition: str | None,
) -> tuple[VocabWord, bool]:
    """Insert, or update cefr_level/definition in place if this exact
    (word, part_of_speech) row already exists for this user -- so
    re-running the Oxford importer is always safe."""
    existing = await find_by_word_and_pos(session, user_id, word, part_of_speech)
    if existing is not None:
        existing.cefr_level = cefr_level
        if definition and not existing.definition:
            existing.definition = definition
        await session.commit()
        await session.refresh(existing)
        return existing, False

    row = VocabWord(
        user_id=user_id,
        word=word.strip(),
        definition=definition,
        part_of_speech=part_of_speech,
        cefr_level=cefr_level,
        date_introduced=date.today(),
        source="oxford_5000_import",
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row, True


async def get_summary(session: AsyncSession, user_id: uuid.UUID) -> dict[str, object]:
    """Same shape as the ML/DSA bank summaries: total, attempted (any
    learning_status set) vs. not attempted, a per-status breakdown, and a
    CEFR-level breakdown."""
    rows = (
        await session.execute(
            select(VocabWord.learning_status, VocabWord.cefr_level).where(VocabWord.user_id == user_id)
        )
    ).all()

    total = len(rows)
    attempted = sum(1 for status, _ in rows if status is not None)
    by_status: dict[str, int] = {}
    by_level: dict[str, int] = {}
    for status, level in rows:
        if status:
            by_status[status] = by_status.get(status, 0) + 1
        if level:
            by_level[level] = by_level.get(level, 0) + 1

    return {
        "total_words": total,
        "attempted_count": attempted,
        "not_attempted_count": total - attempted,
        "known_count": by_status.get("known", 0),
        "learning_count": by_status.get("learning", 0),
        "difficult_count": by_status.get("difficult", 0),
        "need_to_revisit_count": by_status.get("need_to_revisit", 0),
        "by_level": sorted(by_level.items()),
    }
