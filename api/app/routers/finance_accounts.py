from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.logging import get_logger
from app.models.finance import FinanceAccount
from app.repositories import finance as finance_repo
from app.schemas import (
    FinanceAccountCreate,
    FinanceAccountOut,
    FinanceAccountUpdate,
    FinanceCategoryCreate,
    FinanceCategoryOut,
)

log = get_logger(__name__)

router = APIRouter(prefix="/api/finance/accounts", tags=["finance"])
categories_router = APIRouter(prefix="/api/finance/categories", tags=["finance"])


def _account_out(a: FinanceAccount) -> FinanceAccountOut:
    return FinanceAccountOut(
        id=a.id,
        name=a.name,
        account_type=a.account_type,
        currency=a.currency,
        opening_balance=float(a.opening_balance),
        current_balance=float(a.current_balance),
        is_liability=a.is_liability,
        is_active=a.is_active,
    )


@router.get("", response_model=list[FinanceAccountOut])
async def list_accounts(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[FinanceAccountOut]:
    accounts = await finance_repo.list_accounts(session, user_id)
    return [_account_out(a) for a in accounts]


@router.post("", response_model=FinanceAccountOut, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: FinanceAccountCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> FinanceAccountOut:
    account = await finance_repo.create_account(
        session, user_id, payload.name, payload.account_type, payload.currency, payload.opening_balance
    )
    log.info("finance_account_created", user_id=str(user_id), account_id=account.id, type=account.account_type)
    return _account_out(account)


@router.patch("/{account_id}", response_model=FinanceAccountOut)
async def update_account(
    account_id: int,
    payload: FinanceAccountUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> FinanceAccountOut:
    account = await finance_repo.update_account(session, user_id, account_id, payload.name, payload.is_active)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return _account_out(account)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> None:
    deleted = await finance_repo.delete_account(session, user_id, account_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    log.info("finance_account_deleted", user_id=str(user_id), account_id=account_id)


@categories_router.get("", response_model=list[FinanceCategoryOut])
async def list_categories(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[FinanceCategoryOut]:
    categories = await finance_repo.list_categories(session, user_id)
    return [
        FinanceCategoryOut(id=c.id, name=c.name, kind=c.kind, parent_id=c.parent_id, is_system=c.is_system)
        for c in categories
    ]


@categories_router.post("", response_model=FinanceCategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: FinanceCategoryCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> FinanceCategoryOut:
    category = await finance_repo.create_category(session, user_id, payload.name, payload.kind, payload.parent_id)
    return FinanceCategoryOut(
        id=category.id,
        name=category.name,
        kind=category.kind,
        parent_id=category.parent_id,
        is_system=category.is_system,
    )
