"""Manual-first personal finance: accounts, categories, transactions,
recurring obligations, budgets, savings goals, net-worth history.

Same discipline as the rest of this schema (DATA_MODEL_AUDIT.md): a
reference/definition table (`FinanceCategory`, with system-seeded rows
alongside a user's own) plus per-user activity tables, `user_id` + RLS
everywhere, hard-delete-only, `TimestampMixin`.

One rule specific to this module, carried over from the app's existing
"never fabricate a number" ethos (Goal.progress_pct is manual and the
codebase is otherwise strict about deriving numbers from real rows):
`FinanceGoal.current_amount` is NOT a column here. It is always
SUM(FinanceTransaction.amount) for that goal's linked contributions,
computed in the repository layer — a savings goal's progress must never
be a typed-in number that can drift from what was actually saved.

Deliberately named `finance_budgets`, not `budgets` — `time_budgets`
already owns that name for a different concept (weekly minutes per
category, not money).
"""

from __future__ import annotations

import uuid
from datetime import date as date_

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin

ACCOUNT_TYPES = ("cash", "bank", "savings", "investment", "receivable", "credit", "loan", "other")
LIABILITY_ACCOUNT_TYPES = ("credit", "loan")
TRANSACTION_TYPES = ("income", "expense")
TRANSACTION_STATUSES = ("actual", "planned")
RECURRING_INTERVALS = ("weekly", "monthly", "yearly")
GOAL_CATEGORIES = ("emergency_fund", "short_term", "long_term", "custom")
GOAL_STATUSES = ("active", "completed", "abandoned")


class FinanceAccount(Base, TimestampMixin):
    __tablename__ = "finance_accounts"
    __table_args__ = (
        CheckConstraint(f"account_type IN {ACCOUNT_TYPES!r}", name="ck_finance_accounts_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String)
    account_type: Mapped[str] = mapped_column(String)
    currency: Mapped[str] = mapped_column(String, default="AUD")
    opening_balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    # Maintained by the repository layer on every transaction write, never
    # user-edited directly — the one balance figure that must always
    # equal opening_balance + sum(its transactions), not a number someone
    # can type over reality.
    current_balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    is_liability: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class FinanceCategory(Base, TimestampMixin):
    """Reference data (system-seeded rows, `user_id IS NULL`) plus a
    user's own custom categories layered on top — same reference/
    per-user split as `problems`/`problem_attempts`, applied to a single
    table via a nullable owner column instead of two tables, since a
    category has no per-user activity of its own to log."""

    __tablename__ = "finance_categories"
    __table_args__ = (
        CheckConstraint(f"kind IN {TRANSACTION_TYPES!r}", name="ck_finance_categories_kind"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True, index=True)
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("finance_categories.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String)
    kind: Mapped[str] = mapped_column(String)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)


class FinanceGoal(Base, TimestampMixin):
    __tablename__ = "finance_goals"
    __table_args__ = (
        CheckConstraint(f"category IN {GOAL_CATEGORIES!r}", name="ck_finance_goals_category"),
        CheckConstraint(f"status IN {GOAL_STATUSES!r}", name="ck_finance_goals_status"),
        CheckConstraint("target_amount > 0", name="ck_finance_goals_target_amount"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String)
    target_amount: Mapped[float] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String, default="AUD")
    target_date: Mapped[date_ | None] = mapped_column(nullable=True)
    category: Mapped[str] = mapped_column(String, default="custom")
    status: Mapped[str] = mapped_column(String, default="active")
    notes: Mapped[str | None] = mapped_column(String, nullable=True)


class FinanceRecurring(Base, TimestampMixin):
    __tablename__ = "finance_recurring"
    __table_args__ = (
        CheckConstraint(f"type IN {TRANSACTION_TYPES!r}", name="ck_finance_recurring_type"),
        CheckConstraint(f"interval IN {RECURRING_INTERVALS!r}", name="ck_finance_recurring_interval"),
        CheckConstraint("amount > 0", name="ck_finance_recurring_amount"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    description: Mapped[str] = mapped_column(String)
    account_id: Mapped[int] = mapped_column(ForeignKey("finance_accounts.id"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("finance_categories.id"), index=True)
    type: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String, default="AUD")
    interval: Mapped[str] = mapped_column(String)
    # Day-of-month (1-31) for monthly/yearly, day-of-week (0=Monday) for
    # weekly — interpreted by the repository layer when it rolls
    # `next_due_date` forward, never re-derived from `next_due_date`
    # alone so the user's intended anchor survives a skipped occurrence.
    anchor_day: Mapped[int] = mapped_column(Integer)
    next_due_date: Mapped[date_] = mapped_column()
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class FinanceTransaction(Base, TimestampMixin):
    __tablename__ = "finance_transactions"
    __table_args__ = (
        CheckConstraint(f"type IN {TRANSACTION_TYPES!r}", name="ck_finance_transactions_type"),
        CheckConstraint(f"status IN {TRANSACTION_STATUSES!r}", name="ck_finance_transactions_status"),
        CheckConstraint("amount > 0", name="ck_finance_transactions_amount"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("finance_accounts.id"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("finance_categories.id"), index=True)
    type: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String, default="AUD")
    occurred_on: Mapped[date_] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(String, default="actual")
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    recurring_id: Mapped[int | None] = mapped_column(
        ForeignKey("finance_recurring.id"), nullable=True, index=True
    )
    # A contribution toward a savings goal — FinanceGoal.current_amount is
    # SUM(amount) over transactions linking here, never a stored column.
    goal_id: Mapped[int | None] = mapped_column(ForeignKey("finance_goals.id"), nullable=True, index=True)


class FinanceBudget(Base, TimestampMixin):
    __tablename__ = "finance_budgets"
    __table_args__ = (
        UniqueConstraint("user_id", "category_id", name="uq_finance_budgets_user_category"),
        CheckConstraint("monthly_amount > 0", name="ck_finance_budgets_amount"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("finance_categories.id"), index=True)
    monthly_amount: Mapped[float] = mapped_column(Numeric(12, 2))


class FinanceNetWorthSnapshot(Base, TimestampMixin):
    __tablename__ = "finance_net_worth_snapshots"
    __table_args__ = (
        UniqueConstraint("user_id", "snapshot_date", name="uq_finance_net_worth_user_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    snapshot_date: Mapped[date_] = mapped_column(index=True)
    total_assets: Mapped[float] = mapped_column(Numeric(12, 2))
    total_liabilities: Mapped[float] = mapped_column(Numeric(12, 2))
    net_worth: Mapped[float] = mapped_column(Numeric(12, 2))
