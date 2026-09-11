from __future__ import annotations

import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.engines.finance import budget_utilization
from app.logging import get_logger
from app.repositories import finance as finance_repo
from app.schemas import FinanceBudgetOut, FinanceBudgetUpsert

log = get_logger(__name__)

router = APIRouter(prefix="/api/finance/budgets", tags=["finance"])


@router.get("", response_model=list[FinanceBudgetOut])
async def list_budgets(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[FinanceBudgetOut]:
    fixtures = await finance_repo.get_budget_fixtures(session, user_id, date.today())
    statuses = budget_utilization(fixtures)
    return [
        FinanceBudgetOut(
            id=s.id,
            category_id=f.category_id,
            category_name=s.category_name,
            planned=s.planned,
            actual=s.actual,
            remaining=s.remaining,
            utilization_pct=s.utilization_pct,
            over_budget=s.over_budget,
        )
        for f, s in zip(fixtures, statuses, strict=True)
    ]


@router.put("", response_model=FinanceBudgetOut)
async def upsert_budget(
    payload: FinanceBudgetUpsert,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> FinanceBudgetOut:
    await finance_repo.upsert_budget(session, user_id, payload.category_id, payload.monthly_amount)
    fixtures = await finance_repo.get_budget_fixtures(session, user_id, date.today())
    fixture = next((f for f in fixtures if f.category_id == payload.category_id), None)
    if fixture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    s = budget_utilization([fixture])[0]
    return FinanceBudgetOut(
        id=s.id,
        category_id=fixture.category_id,
        category_name=s.category_name,
        planned=s.planned,
        actual=s.actual,
        remaining=s.remaining,
        utilization_pct=s.utilization_pct,
        over_budget=s.over_budget,
    )


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> None:
    deleted = await finance_repo.delete_budget(session, user_id, budget_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
