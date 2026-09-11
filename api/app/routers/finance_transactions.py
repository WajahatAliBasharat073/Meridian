from __future__ import annotations

import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.logging import get_logger
from app.models.finance import FinanceTransaction
from app.repositories import finance as finance_repo
from app.schemas import FinanceTransactionCreate, FinanceTransactionOut

log = get_logger(__name__)

router = APIRouter(prefix="/api/finance/transactions", tags=["finance"])


def _out(t: FinanceTransaction) -> FinanceTransactionOut:
    return FinanceTransactionOut(
        id=t.id,
        account_id=t.account_id,
        category_id=t.category_id,
        type=t.type,
        amount=float(t.amount),
        currency=t.currency,
        occurred_on=t.occurred_on,
        status=t.status,
        description=t.description,
        notes=t.notes,
        goal_id=t.goal_id,
    )


@router.get("", response_model=list[FinanceTransactionOut])
async def list_transactions(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    account_id: int | None = None,
    category_id: int | None = None,
    type: str | None = None,  # noqa: A002
    status_: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[FinanceTransactionOut]:
    transactions = await finance_repo.list_transactions(
        session,
        user_id,
        account_id=account_id,
        category_id=category_id,
        type_=type,
        status=status_,
        date_from=date_from,
        date_to=date_to,
    )
    return [_out(t) for t in transactions]


@router.post("", response_model=FinanceTransactionOut, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: FinanceTransactionCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> FinanceTransactionOut:
    txn = await finance_repo.create_transaction(
        session,
        user_id,
        account_id=payload.account_id,
        category_id=payload.category_id,
        type_=payload.type,
        amount=payload.amount,
        currency=payload.currency,
        occurred_on=payload.occurred_on,
        status=payload.status,
        description=payload.description,
        notes=payload.notes,
        goal_id=payload.goal_id,
    )
    log.info(
        "finance_transaction_created",
        user_id=str(user_id),
        transaction_id=txn.id,
        type=txn.type,
        status=txn.status,
    )
    return _out(txn)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> None:
    deleted = await finance_repo.delete_transaction(session, user_id, transaction_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    log.info("finance_transaction_deleted", user_id=str(user_id), transaction_id=transaction_id)
