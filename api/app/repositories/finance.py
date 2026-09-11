"""Finance repository: accounts, categories, transactions, recurring
obligations, budgets, goals, net-worth snapshots.

Balance maintenance rule, applied everywhere a transaction is written or
removed: `FinanceAccount.current_balance` is updated here, in the same
transaction as the write, and is never something a caller sets directly
— it must always equal `opening_balance + sum(this account's actual
transactions)`. Only `status='actual'` rows move a balance; `'planned'`
rows are projections and never touch it.
"""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.finance import (
    BudgetFixture,
    GoalFixture,
    NetWorthPoint,
    RecurringFixture,
    TransactionFixture,
)
from app.models.finance import (
    LIABILITY_ACCOUNT_TYPES,
    FinanceAccount,
    FinanceBudget,
    FinanceCategory,
    FinanceGoal,
    FinanceNetWorthSnapshot,
    FinanceRecurring,
    FinanceTransaction,
)

# ---------------------------------------------------------------- accounts


async def list_accounts(session: AsyncSession, user_id: uuid.UUID) -> list[FinanceAccount]:
    result = await session.execute(
        select(FinanceAccount)
        .where(FinanceAccount.user_id == user_id)
        .order_by(FinanceAccount.created_at)
    )
    return list(result.scalars().all())


async def create_account(
    session: AsyncSession,
    user_id: uuid.UUID,
    name: str,
    account_type: str,
    currency: str,
    opening_balance: float,
) -> FinanceAccount:
    account = FinanceAccount(
        user_id=user_id,
        name=name,
        account_type=account_type,
        currency=currency,
        opening_balance=opening_balance,
        current_balance=opening_balance,
        is_liability=account_type in LIABILITY_ACCOUNT_TYPES,
    )
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return account


async def update_account(
    session: AsyncSession,
    user_id: uuid.UUID,
    account_id: int,
    name: str | None,
    is_active: bool | None,
) -> FinanceAccount | None:
    account = await session.get(FinanceAccount, account_id)
    if account is None or account.user_id != user_id:
        return None
    if name is not None:
        account.name = name
    if is_active is not None:
        account.is_active = is_active
    await session.commit()
    await session.refresh(account)
    return account


async def delete_account(session: AsyncSession, user_id: uuid.UUID, account_id: int) -> bool:
    account = await session.get(FinanceAccount, account_id)
    if account is None or account.user_id != user_id:
        return False
    await session.delete(account)
    await session.commit()
    return True


# -------------------------------------------------------------- categories


async def list_categories(session: AsyncSession, user_id: uuid.UUID) -> list[FinanceCategory]:
    result = await session.execute(
        select(FinanceCategory)
        .where((FinanceCategory.user_id.is_(None)) | (FinanceCategory.user_id == user_id))
        .order_by(FinanceCategory.kind, FinanceCategory.parent_id.is_(None).desc(), FinanceCategory.name)
    )
    return list(result.scalars().all())


async def create_category(
    session: AsyncSession, user_id: uuid.UUID, name: str, kind: str, parent_id: int | None
) -> FinanceCategory:
    category = FinanceCategory(user_id=user_id, name=name, kind=kind, parent_id=parent_id, is_system=False)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


# ----------------------------------------------------------- transactions


async def _apply_balance_delta(
    session: AsyncSession, account_id: int, type_: str, amount: float, sign: int
) -> None:
    """sign=+1 to apply a transaction's effect, -1 to reverse it."""
    account = await session.get(FinanceAccount, account_id)
    if account is None:
        return
    delta = amount if type_ == "income" else -amount
    account.current_balance = float(account.current_balance) + sign * delta


async def list_transactions(
    session: AsyncSession,
    user_id: uuid.UUID,
    account_id: int | None = None,
    category_id: int | None = None,
    type_: str | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[FinanceTransaction]:
    query = select(FinanceTransaction).where(FinanceTransaction.user_id == user_id)
    if account_id is not None:
        query = query.where(FinanceTransaction.account_id == account_id)
    if category_id is not None:
        query = query.where(FinanceTransaction.category_id == category_id)
    if type_ is not None:
        query = query.where(FinanceTransaction.type == type_)
    if status is not None:
        query = query.where(FinanceTransaction.status == status)
    if date_from is not None:
        query = query.where(FinanceTransaction.occurred_on >= date_from)
    if date_to is not None:
        query = query.where(FinanceTransaction.occurred_on <= date_to)
    query = query.order_by(FinanceTransaction.occurred_on.desc(), FinanceTransaction.id.desc())
    return list((await session.execute(query)).scalars().all())


async def create_transaction(
    session: AsyncSession,
    user_id: uuid.UUID,
    account_id: int,
    category_id: int,
    type_: str,
    amount: float,
    currency: str,
    occurred_on: date,
    status: str,
    description: str | None,
    notes: str | None,
    goal_id: int | None = None,
) -> FinanceTransaction:
    txn = FinanceTransaction(
        user_id=user_id,
        account_id=account_id,
        category_id=category_id,
        type=type_,
        amount=amount,
        currency=currency,
        occurred_on=occurred_on,
        status=status,
        description=description,
        notes=notes,
        goal_id=goal_id,
    )
    session.add(txn)
    if status == "actual":
        await _apply_balance_delta(session, account_id, type_, amount, sign=1)
    await session.commit()
    await session.refresh(txn)
    return txn


async def delete_transaction(session: AsyncSession, user_id: uuid.UUID, transaction_id: int) -> bool:
    txn = await session.get(FinanceTransaction, transaction_id)
    if txn is None or txn.user_id != user_id:
        return False
    if txn.status == "actual":
        await _apply_balance_delta(session, txn.account_id, txn.type, float(txn.amount), sign=-1)
    await session.delete(txn)
    await session.commit()
    return True


async def get_transaction_fixtures(
    session: AsyncSession, user_id: uuid.UUID, since: date | None = None
) -> list[TransactionFixture]:
    query = (
        select(FinanceTransaction, FinanceCategory.name)
        .join(FinanceCategory, FinanceTransaction.category_id == FinanceCategory.id)
        .where(FinanceTransaction.user_id == user_id)
    )
    if since is not None:
        query = query.where(FinanceTransaction.occurred_on >= since)
    rows = (await session.execute(query)).all()
    return [
        TransactionFixture(
            category_id=txn.category_id,
            category_name=category_name,
            type=txn.type,
            amount=float(txn.amount),
            status=txn.status,
            occurred_on=txn.occurred_on,
        )
        for txn, category_name in rows
    ]


# ------------------------------------------------------------- recurring


async def list_recurring(
    session: AsyncSession, user_id: uuid.UUID, active_only: bool = True
) -> list[FinanceRecurring]:
    query = select(FinanceRecurring).where(FinanceRecurring.user_id == user_id)
    if active_only:
        query = query.where(FinanceRecurring.active.is_(True))
    query = query.order_by(FinanceRecurring.next_due_date)
    return list((await session.execute(query)).scalars().all())


async def create_recurring(
    session: AsyncSession,
    user_id: uuid.UUID,
    description: str,
    account_id: int,
    category_id: int,
    type_: str,
    amount: float,
    currency: str,
    interval: str,
    anchor_day: int,
    next_due_date: date,
) -> FinanceRecurring:
    recurring = FinanceRecurring(
        user_id=user_id,
        description=description,
        account_id=account_id,
        category_id=category_id,
        type=type_,
        amount=amount,
        currency=currency,
        interval=interval,
        anchor_day=anchor_day,
        next_due_date=next_due_date,
    )
    session.add(recurring)
    await session.commit()
    await session.refresh(recurring)
    return recurring


async def delete_recurring(session: AsyncSession, user_id: uuid.UUID, recurring_id: int) -> bool:
    recurring = await session.get(FinanceRecurring, recurring_id)
    if recurring is None or recurring.user_id != user_id:
        return False
    await session.delete(recurring)
    await session.commit()
    return True


async def get_recurring_fixtures(session: AsyncSession, user_id: uuid.UUID) -> list[RecurringFixture]:
    query = (
        select(FinanceRecurring, FinanceCategory.name)
        .join(FinanceCategory, FinanceRecurring.category_id == FinanceCategory.id)
        .where(FinanceRecurring.user_id == user_id, FinanceRecurring.active.is_(True))
    )
    rows = (await session.execute(query)).all()
    return [
        RecurringFixture(
            id=r.id,
            description=r.description,
            amount=float(r.amount),
            type=r.type,
            next_due_date=r.next_due_date,
            category_name=category_name,
        )
        for r, category_name in rows
    ]


# --------------------------------------------------------------- budgets


async def list_budgets(session: AsyncSession, user_id: uuid.UUID) -> list[FinanceBudget]:
    result = await session.execute(select(FinanceBudget).where(FinanceBudget.user_id == user_id))
    return list(result.scalars().all())


async def upsert_budget(
    session: AsyncSession, user_id: uuid.UUID, category_id: int, monthly_amount: float
) -> FinanceBudget:
    existing = (
        await session.execute(
            select(FinanceBudget).where(
                FinanceBudget.user_id == user_id, FinanceBudget.category_id == category_id
            )
        )
    ).scalar_one_or_none()
    if existing:
        existing.monthly_amount = monthly_amount
        await session.commit()
        await session.refresh(existing)
        return existing
    budget = FinanceBudget(user_id=user_id, category_id=category_id, monthly_amount=monthly_amount)
    session.add(budget)
    await session.commit()
    await session.refresh(budget)
    return budget


async def delete_budget(session: AsyncSession, user_id: uuid.UUID, budget_id: int) -> bool:
    budget = await session.get(FinanceBudget, budget_id)
    if budget is None or budget.user_id != user_id:
        return False
    await session.delete(budget)
    await session.commit()
    return True


async def get_budget_fixtures(session: AsyncSession, user_id: uuid.UUID, month: date) -> list[BudgetFixture]:
    budgets = await list_budgets(session, user_id)
    if not budgets:
        return []
    month_start = month.replace(day=1)
    next_month = date(month.year + (month.month == 12), month.month % 12 + 1, 1)

    fixtures = []
    for b in budgets:
        category = await session.get(FinanceCategory, b.category_id)
        actual = (
            await session.execute(
                select(FinanceTransaction.amount).where(
                    FinanceTransaction.user_id == user_id,
                    FinanceTransaction.category_id == b.category_id,
                    FinanceTransaction.type == "expense",
                    FinanceTransaction.status == "actual",
                    FinanceTransaction.occurred_on >= month_start,
                    FinanceTransaction.occurred_on < next_month,
                )
            )
        ).scalars().all()
        fixtures.append(
            BudgetFixture(
                id=b.id,
                category_id=b.category_id,
                category_name=category.name if category else "Unknown",
                monthly_amount=float(b.monthly_amount),
                actual_this_month=float(sum(actual)),
            )
        )
    return fixtures


# ----------------------------------------------------------------- goals


async def list_goals(session: AsyncSession, user_id: uuid.UUID) -> list[FinanceGoal]:
    result = await session.execute(
        select(FinanceGoal).where(FinanceGoal.user_id == user_id).order_by(FinanceGoal.created_at.desc())
    )
    return list(result.scalars().all())


async def create_goal(
    session: AsyncSession,
    user_id: uuid.UUID,
    title: str,
    target_amount: float,
    currency: str,
    target_date: date | None,
    category: str,
    notes: str | None,
) -> FinanceGoal:
    goal = FinanceGoal(
        user_id=user_id,
        title=title,
        target_amount=target_amount,
        currency=currency,
        target_date=target_date,
        category=category,
        notes=notes,
    )
    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    return goal


async def update_goal(
    session: AsyncSession, user_id: uuid.UUID, goal_id: int, status: str | None
) -> FinanceGoal | None:
    goal = await session.get(FinanceGoal, goal_id)
    if goal is None or goal.user_id != user_id:
        return None
    if status is not None:
        goal.status = status
    await session.commit()
    await session.refresh(goal)
    return goal


async def delete_goal(session: AsyncSession, user_id: uuid.UUID, goal_id: int) -> bool:
    goal = await session.get(FinanceGoal, goal_id)
    if goal is None or goal.user_id != user_id:
        return False
    await session.delete(goal)
    await session.commit()
    return True


async def get_goal_fixtures(session: AsyncSession, user_id: uuid.UUID) -> list[GoalFixture]:
    """`current_amount` is always computed here from real contributions
    (SUM of transactions tagged with this goal), never a stored column —
    see models/finance.py's module docstring."""
    goals = await list_goals(session, user_id)
    fixtures = []
    for g in goals:
        contributed = (
            await session.execute(
                select(FinanceTransaction.amount).where(
                    FinanceTransaction.goal_id == g.id,
                    FinanceTransaction.status == "actual",
                )
            )
        ).scalars().all()
        fixtures.append(
            GoalFixture(
                id=g.id,
                title=g.title,
                target_amount=float(g.target_amount),
                current_amount=float(sum(contributed)),
                target_date=g.target_date,
                category=g.category,
            )
        )
    return fixtures


# ---------------------------------------------------------- net worth


async def compute_and_store_snapshot(
    session: AsyncSession, user_id: uuid.UUID, on_date: date
) -> FinanceNetWorthSnapshot:
    accounts = await list_accounts(session, user_id)
    total_assets = sum(float(a.current_balance) for a in accounts if not a.is_liability)
    total_liabilities = sum(float(a.current_balance) for a in accounts if a.is_liability)
    net_worth = total_assets - total_liabilities

    existing = (
        await session.execute(
            select(FinanceNetWorthSnapshot).where(
                FinanceNetWorthSnapshot.user_id == user_id,
                FinanceNetWorthSnapshot.snapshot_date == on_date,
            )
        )
    ).scalar_one_or_none()
    if existing:
        existing.total_assets = total_assets
        existing.total_liabilities = total_liabilities
        existing.net_worth = net_worth
        await session.commit()
        await session.refresh(existing)
        return existing

    snapshot = FinanceNetWorthSnapshot(
        user_id=user_id,
        snapshot_date=on_date,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        net_worth=net_worth,
    )
    session.add(snapshot)
    await session.commit()
    await session.refresh(snapshot)
    return snapshot


async def get_net_worth_points(session: AsyncSession, user_id: uuid.UUID) -> list[NetWorthPoint]:
    result = await session.execute(
        select(FinanceNetWorthSnapshot)
        .where(FinanceNetWorthSnapshot.user_id == user_id)
        .order_by(FinanceNetWorthSnapshot.snapshot_date)
    )
    return [
        NetWorthPoint(
            snapshot_date=s.snapshot_date,
            total_assets=float(s.total_assets),
            total_liabilities=float(s.total_liabilities),
            net_worth=float(s.net_worth),
        )
        for s in result.scalars().all()
    ]
