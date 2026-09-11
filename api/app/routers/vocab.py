from __future__ import annotations

import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.engines.vocab import build_daily_review
from app.logging import get_logger
from app.models.life import VocabWord
from app.repositories import vocab as vocab_repo
from app.schemas import (
    VocabStatusUpdate,
    VocabSummaryOut,
    VocabWordCreate,
    VocabWordOut,
    VocabWordUpdate,
)

log = get_logger(__name__)

router = APIRouter(prefix="/api/vocab", tags=["vocab"])


def _out(w: VocabWord) -> VocabWordOut:
    return VocabWordOut(
        id=w.id,
        word=w.word,
        definition=w.definition,
        example_sentence=w.example_sentence,
        pronunciation=w.pronunciation,
        part_of_speech=w.part_of_speech,
        category=w.category,
        cefr_level=w.cefr_level,
        synonyms=w.synonyms,
        antonyms=w.antonyms,
        word_patterns=w.word_patterns,
        paraphrase=w.paraphrase,
        dictionary_link=w.dictionary_link,
        notes=w.notes,
        date_introduced=w.date_introduced,
        learning_status=w.learning_status,
        source=w.source,
    )


@router.get("", response_model=list[VocabWordOut])
async def list_words(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    learning_status: str | None = None,
) -> list[VocabWordOut]:
    words = await vocab_repo.list_words(session, user_id, learning_status)
    return [_out(w) for w in words]


@router.get("/daily", response_model=list[VocabWordOut])
async def get_daily_review(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    count: int = 10,
) -> list[VocabWordOut]:
    fixtures = await vocab_repo.get_word_fixtures(session, user_id)
    plan = build_daily_review(fixtures, date.today(), count=count)
    words = await vocab_repo.list_words(session, user_id)
    by_id = {w.id: w for w in words}
    return [_out(by_id[f.id]) for f in plan if f.id in by_id]


@router.post("", response_model=VocabWordOut, status_code=status.HTTP_201_CREATED)
async def create_word(
    payload: VocabWordCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> VocabWordOut:
    existing = await vocab_repo.find_by_word(session, user_id, payload.word)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"'{payload.word}' is already in your vocabulary list",
        )
    row = await vocab_repo.create_word(
        session,
        user_id,
        word=payload.word,
        definition=payload.definition,
        example_sentence=payload.example_sentence,
        pronunciation=payload.pronunciation,
        part_of_speech=payload.part_of_speech,
        category=payload.category,
        cefr_level=payload.cefr_level,
        synonyms=payload.synonyms,
        antonyms=payload.antonyms,
        word_patterns=payload.word_patterns,
        paraphrase=payload.paraphrase,
        dictionary_link=payload.dictionary_link,
        notes=payload.notes,
    )
    log.info("vocab_word_created", user_id=str(user_id), word_id=row.id)
    return _out(row)


@router.get("/summary", response_model=VocabSummaryOut)
async def get_summary(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> VocabSummaryOut:
    summary = await vocab_repo.get_summary(session, user_id)
    return VocabSummaryOut(**summary)


@router.patch("/{word_id}", response_model=VocabWordOut)
async def edit_word(
    word_id: int,
    payload: VocabWordUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> VocabWordOut:
    fields = payload.model_dump(exclude_unset=True)
    row = await vocab_repo.update_word(session, user_id, word_id, fields)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found")
    return _out(row)


@router.patch("/{word_id}/status", response_model=VocabWordOut)
async def set_status(
    word_id: int,
    payload: VocabStatusUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> VocabWordOut:
    row = await vocab_repo.set_learning_status(session, user_id, word_id, payload.learning_status)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found")
    return _out(row)


@router.delete("/{word_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word(
    word_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> None:
    deleted = await vocab_repo.delete_word(session, user_id, word_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found")
    log.info("vocab_word_deleted", user_id=str(user_id), word_id=word_id)
