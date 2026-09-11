"""A Goal linked to a FinanceGoal must show computed financial progress
(never a typed-in number) alongside its own manual progress_pct --
neither replaces the other, since they measure different things.
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
from app.models.finance import FinanceAccount, FinanceGoal, FinanceTransaction
from app.models.goals import Goal
from app.repositories import finance as finance_repo
from app.repositories import goals as goals_repo


@pytest.fixture
async def user() -> AsyncGenerator[tuple[AsyncSession, uuid.UUID], None]:
    session = SessionLocal()
    user_id = uuid.uuid4()
    session.add(User(id=user_id, email=f"goal-link-test-{user_id}@test.local", settings={}))
    await session.commit()
    try:
        yield session, user_id
    finally:
        await session.execute(delete(Goal).where(Goal.user_id == user_id))
        await session.execute(delete(FinanceTransaction).where(FinanceTransaction.user_id == user_id))
        await session.execute(delete(FinanceGoal).where(FinanceGoal.user_id == user_id))
        await session.execute(delete(FinanceAccount).where(FinanceAccount.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()
        await session.close()
        await engine.dispose()


async def test_goal_can_link_to_a_finance_goal_and_computed_progress_follows(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user

    account = await finance_repo.create_account(session, user_id, "Savings", "savings", "AUD", 0.0)
    finance_goal = await finance_repo.create_goal(
        session, user_id, "Emergency fund", 6000.0, "AUD", date(2026, 12, 1), "emergency_fund", None
    )
    goal = await goals_repo.create_goal(
        session, user_id, "Build emergency fund", None, None, None, finance_goal_id=finance_goal.id
    )
    assert goal.finance_goal_id == finance_goal.id

    # Contribute $1500 toward it -- the goal's linked progress must reflect
    # this real transaction, not a number anyone typed in.
    categories = await finance_repo.list_categories(session, user_id)
    income_cat = next(c for c in categories if c.kind == "income")
    await finance_repo.create_transaction(
        session, user_id, account.id, income_cat.id, "income", 1500.0, "AUD",
        date.today(), "actual", None, None, goal_id=finance_goal.id,
    )

    fixtures = await finance_repo.get_goal_fixtures(session, user_id)
    fixture = next(f for f in fixtures if f.id == finance_goal.id)
    assert fixture.current_amount == 1500.0


async def test_finance_goal_id_zero_clears_an_existing_link(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    finance_goal = await finance_repo.create_goal(
        session, user_id, "Laptop", 1200.0, "AUD", None, "custom", None
    )
    goal = await goals_repo.create_goal(
        session, user_id, "Save for a laptop", None, None, None, finance_goal_id=finance_goal.id
    )
    assert goal.finance_goal_id == finance_goal.id

    updated = await goals_repo.update_goal(
        session, user_id, goal.id, progress_pct=None, status=None, finance_goal_id=0
    )
    assert updated is not None
    assert updated.finance_goal_id is None


async def test_a_goal_with_no_link_is_unaffected(user: tuple[AsyncSession, uuid.UUID]) -> None:
    session, user_id = user
    goal = await goals_repo.create_goal(session, user_id, "Read 12 books", None, "Reading", None)
    assert goal.finance_goal_id is None
