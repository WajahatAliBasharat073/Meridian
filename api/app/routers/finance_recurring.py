from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.logging import get_logger
from app.models.finance import FinanceRecurring
from app.repositories import finance as finance_repo
from app.schemas import FinanceRecurringCreate, FinanceRecurringOut

log = get_logger(__name__)

router = APIRouter(prefix="/api/finance/recurring", tags=["finance"])


def _out(r: FinanceRecurring) -> FinanceRecurringOut:
    return FinanceRecurringOut(
        id=r.id,
        description=r.description,
        account_id=r.account_id,
        category_id=r.category_id,
        type=r.type,
        amount=float(r.amount),
        currency=r.currency,
        interval=r.interval,
        anchor_day=r.anchor_day,
        next_due_date=r.next_due_date,
        active=r.active,
    )


@router.get("", response_model=list[FinanceRecurringOut])
async def list_recurring(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[FinanceRecurringOut]:
    items = await finance_repo.list_recurring(session, user_id)
    return [_out(r) for r in items]


@router.post("", response_model=FinanceRecurringOut, status_code=status.HTTP_201_CREATED)
async def create_recurring(
    payload: FinanceRecurringCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> FinanceRecurringOut:
    r = await finance_repo.create_recurring(
        session,
        user_id,
        description=payload.description,
        account_id=payload.account_id,
        category_id=payload.category_id,
        type_=payload.type,
        amount=payload.amount,
        currency=payload.currency,
        interval=payload.interval,
        anchor_day=payload.anchor_day,
        next_due_date=payload.next_due_date,
    )
    log.info("finance_recurring_created", user_id=str(user_id), recurring_id=r.id)
    return _out(r)


@router.delete("/{recurring_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring(
    recurring_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> None:
    deleted = await finance_repo.delete_recurring(session, user_id, recurring_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring item not found")
    log.info("finance_recurring_deleted", user_id=str(user_id), recurring_id=recurring_id)
