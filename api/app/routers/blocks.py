from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.repositories.schedule import update_block_status
from app.schemas import BlockStatusUpdate, TimeBlockOut

router = APIRouter(prefix="/api/blocks", tags=["blocks"])


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
