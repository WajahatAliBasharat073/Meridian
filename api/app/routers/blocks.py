from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_session
from app.deps import get_current_user_id
from app.engines.scheduling import InvalidTimeSpecError
from app.models.core import TimeBlock
from app.repositories.schedule import create_block, get_or_compute_prayer_times, update_block_status
from app.schemas import BlockCreate, BlockStatusUpdate, TimeBlockOut

router = APIRouter(prefix="/api/blocks", tags=["blocks"])


def _to_out(block: TimeBlock) -> TimeBlockOut:
    return TimeBlockOut(
        id=block.id,
        seq=block.seq,
        start=block.start_resolved,
        end=block.end_resolved,
        activity=block.activity,
        tier=block.tier,
        category=block.category,
        planned_minutes=block.planned_minutes,
        status=block.status,
        actual_minutes=block.actual_minutes,
        what_to_do=block.what_to_do,
        notes=block.notes,
        is_current=False,
    )


@router.post("", response_model=TimeBlockOut, status_code=status.HTTP_201_CREATED)
async def add_block(
    payload: BlockCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TimeBlockOut:
    """Lets a user build their own schedule block by block — the only way
    to get real (non-seeded) time blocks into the app until the xlsx
    importer exists."""
    prayer_times = await get_or_compute_prayer_times(session, payload.date, settings)
    try:
        block = await create_block(
            session,
            user_id,
            payload.date,
            payload.start_spec,
            payload.end_spec,
            payload.activity,
            payload.tier,
            payload.category,
            payload.planned_minutes,
            payload.what_to_do,
            payload.notes,
            prayer_times,
        )
    except InvalidTimeSpecError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return _to_out(block)


@router.post("/{block_id}/status", response_model=TimeBlockOut)
async def set_block_status(
    block_id: int,
    payload: BlockStatusUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> TimeBlockOut:
    """One tap, optimistic on the client, undoable — the client re-POSTs
    the prior status to undo (build prompt 7 interaction rules)."""
    block = await update_block_status(session, user_id, block_id, payload.status, payload.actual_minutes)
    if block is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")
    return _to_out(block)
