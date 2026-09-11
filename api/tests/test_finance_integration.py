"""End-to-end check of the finance repository against the real database:
create an account, categorize a transaction against a system-seeded
category, confirm the account balance actually moved, confirm a goal's
progress is computed from a real linked contribution (never a typed-in
number), and confirm the dashboard aggregation runs without error.

Same pattern as test_cross_user_isolation.py: one ephemeral user, real
Postgres, full cleanup in a `finally` regardless of pass/fail.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from datetime import date

import pytest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal, engine
from app.engines.finance import goal_progress, month_summary
from app.models.core import User
from app.models.finance import (
    FinanceAccount,
    FinanceBudget,
    FinanceCategory,
    FinanceGoal,
    FinanceNetWorthSnapshot,
    FinanceRecurring,
    FinanceTransaction,
)
from app.repositories import finance as finance_repo


@pytest.fixture
async def user() -> AsyncGenerator[tuple[AsyncSession, uuid.UUID], None]:
    session = SessionLocal()
    user_id = uuid.uuid4()
    session.add(User(id=user_id, email=f"finance-test-{user_id}@test.local", settings={}))
    await session.commit()
    try:
        yield session, user_id
    finally:
        for model in (
            FinanceTransaction,
            FinanceRecurring,
            FinanceBudget,
            FinanceGoal,
            FinanceNetWorthSnapshot,
            FinanceAccount,
        ):
            await session.execute(delete(model).where(model.user_id == user_id))
        await session.execute(
            delete(FinanceCategory).where(FinanceCategory.user_id == user_id)
        )
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()
        await session.close()
        await engine.dispose()


async def _system_category(session: AsyncSession, kind: str) -> int:
    row = (
        await session.execute(
            select(FinanceCategory.id).where(FinanceCategory.is_system.is_(True), FinanceCategory.kind == kind)
        )
    ).first()
    assert row is not None, "system categories must already be seeded (migration 0023_finance)"
    return row[0]


async def test_creating_an_actual_transaction_moves_the_account_balance(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    account = await finance_repo.create_account(session, user_id, "Everyday", "bank", "AUD", 1000.0)
    salary_category = await _system_category(session, "income")
    rent_category = await _system_category(session, "expense")

    await finance_repo.create_transaction(
        session, user_id, account.id, salary_category, "income", 5000.0, "AUD", date.today(), "actual", None, None
    )
    await finance_repo.create_transaction(
        session, user_id, account.id, rent_category, "expense", 2000.0, "AUD", date.today(), "actual", None, None
    )

    refreshed = await session.get(FinanceAccount, account.id)
    assert refreshed is not None
    assert float(refreshed.current_balance) == 1000.0 + 5000.0 - 2000.0


async def test_planned_transactions_never_move_the_balance(user: tuple[AsyncSession, uuid.UUID]) -> None:
    session, user_id = user
    account = await finance_repo.create_account(session, user_id, "Everyday", "bank", "AUD", 500.0)
    rent_category = await _system_category(session, "expense")

    await finance_repo.create_transaction(
        session, user_id, account.id, rent_category, "expense", 2000.0, "AUD", date.today(), "planned", None, None
    )

    refreshed = await session.get(FinanceAccount, account.id)
    assert refreshed is not None
    assert float(refreshed.current_balance) == 500.0


async def test_deleting_a_transaction_reverses_its_balance_effect(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    account = await finance_repo.create_account(session, user_id, "Everyday", "bank", "AUD", 0.0)
    salary_category = await _system_category(session, "income")

    txn = await finance_repo.create_transaction(
        session, user_id, account.id, salary_category, "income", 1000.0, "AUD", date.today(), "actual", None, None
    )
    await finance_repo.delete_transaction(session, user_id, txn.id)

    refreshed = await session.get(FinanceAccount, account.id)
    assert refreshed is not None
    assert float(refreshed.current_balance) == 0.0


async def test_goal_progress_is_computed_from_real_linked_contributions(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    account = await finance_repo.create_account(session, user_id, "Savings", "savings", "AUD", 0.0)
    income_category = await _system_category(session, "income")

    goal = await finance_repo.create_goal(
        session, user_id, "Emergency fund", 6000.0, "AUD", date(2026, 12, 1), "emergency_fund", None
    )
    await finance_repo.create_transaction(
        session,
        user_id,
        account.id,
        income_category,
        "income",
        1500.0,
        "AUD",
        date.today(),
        "actual",
        None,
        None,
        goal_id=goal.id,
    )
    # An unrelated transaction, not tagged to the goal -- must not count.
    await finance_repo.create_transaction(
        session, user_id, account.id, income_category, "income", 999.0, "AUD", date.today(), "actual", None, None
    )

    fixtures = await finance_repo.get_goal_fixtures(session, user_id)
    fixture = next(f for f in fixtures if f.id == goal.id)
    assert fixture.current_amount == 1500.0

    status = goal_progress([fixture], date(2026, 9, 1))[0]
    assert status.remaining == 4500.0


async def test_net_worth_snapshot_sums_assets_and_liabilities_correctly(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    await finance_repo.create_account(session, user_id, "Bank", "bank", "AUD", 5000.0)
    await finance_repo.create_account(session, user_id, "Credit card", "credit", "AUD", 800.0)

    snapshot = await finance_repo.compute_and_store_snapshot(session, user_id, date.today())

    assert float(snapshot.total_assets) == 5000.0
    assert float(snapshot.total_liabilities) == 800.0
    assert float(snapshot.net_worth) == 4200.0


async def test_dashboard_fixtures_assemble_without_error_for_a_populated_account(
    user: tuple[AsyncSession, uuid.UUID],
) -> None:
    session, user_id = user
    account = await finance_repo.create_account(session, user_id, "Everyday", "bank", "AUD", 0.0)
    salary_category = await _system_category(session, "income")
    rent_category = await _system_category(session, "expense")

    await finance_repo.create_transaction(
        session, user_id, account.id, salary_category, "income", 5000.0, "AUD", date.today(), "actual", None, None
    )
    await finance_repo.create_transaction(
        session, user_id, account.id, rent_category, "expense", 1500.0, "AUD", date.today(), "actual", None, None
    )

    transactions = await finance_repo.get_transaction_fixtures(session, user_id)
    summary = month_summary(transactions, date.today())

    assert summary.income == 5000.0
    assert summary.expenses == 1500.0
    assert summary.savings == 3500.0
