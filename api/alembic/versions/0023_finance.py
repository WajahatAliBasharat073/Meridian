"""finance module: accounts, categories, transactions, budgets, goals

Revision ID: 0023_finance
Revises: 0022_curriculum_topics_rls
Create Date: 2026-09-10

Manual-first personal finance (FINANCE_MODULE_PROPOSAL.md). No money
vocabulary existed anywhere in this schema before this migration
(DATA_MODEL_AUDIT.md §1) -- these are new tables, not a retrofit of
`goals`/`time_budgets`, and deliberately named `finance_budgets` rather
than `budgets` since `time_budgets` already owns that word for a
different concept (weekly minutes, not money).

Table order matters here for FK dependencies: categories and accounts
first (no deps on each other), then goals (independent), then recurring
(needs accounts+categories), then transactions (needs accounts+
categories+recurring+goals), then budgets (needs categories), then net
worth snapshots (independent, just user_id).

`finance_categories` is a hybrid table: system-seeded rows have
`user_id IS NULL` and are readable by every authenticated user (like any
other reference table -- `problems`, `patterns`); a user's own custom
categories have `user_id` set and follow the normal per-owner RLS
pattern. Its RLS policies reflect both halves.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0023_finance"
down_revision: str | None = "0022_curriculum_topics_rls"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_MONEY = sa.Numeric(12, 2)

# (name, kind, [subcategories]) -- subcategories inherit kind from parent.
_DEFAULT_CATEGORIES: list[tuple[str, str, list[str]]] = [
    ("Salary", "income", []),
    ("Freelance", "income", []),
    ("Contract", "income", []),
    ("Research Income", "income", []),
    ("Bonus", "income", []),
    ("One-time", "income", []),
    ("Other Income", "income", []),
    ("Rent", "expense", []),
    ("Utilities", "expense", []),
    ("Food", "expense", []),
    ("Transportation", "expense", []),
    ("Subscriptions", "expense", []),
    ("Gym", "expense", []),
    ("Software", "expense", []),
    ("Entertainment", "expense", []),
    ("Shopping", "expense", []),
    ("Family/Personal", "expense", []),
    ("Misc", "expense", []),
    ("Education", "expense", ["Courses", "Books", "Conferences", "Certifications"]),
    ("Research", "expense", ["Papers", "Conferences", "Compute/GPU", "APIs", "Software", "Books"]),
]


def upgrade() -> None:
    op.create_table(
        "finance_categories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("finance_categories.id"), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("kind IN ('income', 'expense')", name="ck_finance_categories_kind"),
    )
    op.create_index("ix_finance_categories_user_id", "finance_categories", ["user_id"])
    op.create_index("ix_finance_categories_parent_id", "finance_categories", ["parent_id"])

    op.create_table(
        "finance_accounts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("account_type", sa.String(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False, server_default="AUD"),
        sa.Column("opening_balance", _MONEY, nullable=False, server_default="0"),
        sa.Column("current_balance", _MONEY, nullable=False, server_default="0"),
        sa.Column("is_liability", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "account_type IN ('cash','bank','savings','investment','receivable','credit','loan','other')",
            name="ck_finance_accounts_type",
        ),
    )
    op.create_index("ix_finance_accounts_user_id", "finance_accounts", ["user_id"])

    op.create_table(
        "finance_goals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("target_amount", _MONEY, nullable=False),
        sa.Column("currency", sa.String(), nullable=False, server_default="AUD"),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("category", sa.String(), nullable=False, server_default="custom"),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "category IN ('emergency_fund','short_term','long_term','custom')",
            name="ck_finance_goals_category",
        ),
        sa.CheckConstraint("status IN ('active','completed','abandoned')", name="ck_finance_goals_status"),
        sa.CheckConstraint("target_amount > 0", name="ck_finance_goals_target_amount"),
    )
    op.create_index("ix_finance_goals_user_id", "finance_goals", ["user_id"])

    op.create_table(
        "finance_recurring",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("finance_accounts.id"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("finance_categories.id"), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("amount", _MONEY, nullable=False),
        sa.Column("currency", sa.String(), nullable=False, server_default="AUD"),
        sa.Column("interval", sa.String(), nullable=False),
        sa.Column("anchor_day", sa.Integer(), nullable=False),
        sa.Column("next_due_date", sa.Date(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("type IN ('income', 'expense')", name="ck_finance_recurring_type"),
        sa.CheckConstraint(
            "interval IN ('weekly','monthly','yearly')", name="ck_finance_recurring_interval"
        ),
        sa.CheckConstraint("amount > 0", name="ck_finance_recurring_amount"),
    )
    op.create_index("ix_finance_recurring_user_id", "finance_recurring", ["user_id"])
    op.create_index("ix_finance_recurring_account_id", "finance_recurring", ["account_id"])
    op.create_index("ix_finance_recurring_category_id", "finance_recurring", ["category_id"])

    op.create_table(
        "finance_transactions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("finance_accounts.id"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("finance_categories.id"), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("amount", _MONEY, nullable=False),
        sa.Column("currency", sa.String(), nullable=False, server_default="AUD"),
        sa.Column("occurred_on", sa.Date(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="actual"),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("recurring_id", sa.Integer(), sa.ForeignKey("finance_recurring.id"), nullable=True),
        sa.Column("goal_id", sa.Integer(), sa.ForeignKey("finance_goals.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("type IN ('income', 'expense')", name="ck_finance_transactions_type"),
        sa.CheckConstraint("status IN ('actual', 'planned')", name="ck_finance_transactions_status"),
        sa.CheckConstraint("amount > 0", name="ck_finance_transactions_amount"),
    )
    op.create_index("ix_finance_transactions_user_id", "finance_transactions", ["user_id"])
    op.create_index("ix_finance_transactions_account_id", "finance_transactions", ["account_id"])
    op.create_index("ix_finance_transactions_category_id", "finance_transactions", ["category_id"])
    op.create_index("ix_finance_transactions_occurred_on", "finance_transactions", ["occurred_on"])
    op.create_index("ix_finance_transactions_recurring_id", "finance_transactions", ["recurring_id"])
    op.create_index("ix_finance_transactions_goal_id", "finance_transactions", ["goal_id"])

    op.create_table(
        "finance_budgets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("finance_categories.id"), nullable=False),
        sa.Column("monthly_amount", _MONEY, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "category_id", name="uq_finance_budgets_user_category"),
        sa.CheckConstraint("monthly_amount > 0", name="ck_finance_budgets_amount"),
    )
    op.create_index("ix_finance_budgets_user_id", "finance_budgets", ["user_id"])
    op.create_index("ix_finance_budgets_category_id", "finance_budgets", ["category_id"])

    op.create_table(
        "finance_net_worth_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("total_assets", _MONEY, nullable=False),
        sa.Column("total_liabilities", _MONEY, nullable=False),
        sa.Column("net_worth", _MONEY, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "snapshot_date", name="uq_finance_net_worth_user_date"),
    )
    op.create_index("ix_finance_net_worth_user_id", "finance_net_worth_snapshots", ["user_id"])
    op.create_index("ix_finance_net_worth_date", "finance_net_worth_snapshots", ["snapshot_date"])

    # -- Seed system default categories --------------------------------
    for name, kind, children in _DEFAULT_CATEGORIES:
        op.execute(
            sa.text(
                "INSERT INTO finance_categories (name, kind, is_system) VALUES (:name, :kind, true)"
            ).bindparams(name=name, kind=kind)
        )
        for child in children:
            op.execute(
                sa.text(
                    "INSERT INTO finance_categories (name, kind, is_system, parent_id) "
                    "SELECT :child, :kind, true, id FROM finance_categories "
                    "WHERE name = :name AND is_system = true"
                ).bindparams(child=child, kind=kind, name=name)
            )

    # -- RLS -------------------------------------------------------------
    _USER_SCOPED = (
        "finance_accounts",
        "finance_goals",
        "finance_recurring",
        "finance_transactions",
        "finance_budgets",
        "finance_net_worth_snapshots",
    )
    for table in _USER_SCOPED:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY {table}_select_own ON {table} "
            f"FOR SELECT TO authenticated USING (user_id = auth.uid())"
        )
        op.execute(
            f"CREATE POLICY {table}_insert_own ON {table} "
            f"FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid())"
        )
        op.execute(
            f"CREATE POLICY {table}_update_own ON {table} "
            f"FOR UPDATE TO authenticated USING (user_id = auth.uid()) "
            f"WITH CHECK (user_id = auth.uid())"
        )
        op.execute(
            f"CREATE POLICY {table}_delete_own ON {table} "
            f"FOR DELETE TO authenticated USING (user_id = auth.uid())"
        )

    # finance_categories: system rows (user_id IS NULL) are readable by
    # everyone like any other reference table; a user's own custom
    # categories follow the normal per-owner pattern for all four verbs.
    # System rows can never be inserted/updated/deleted by a regular user
    # (there is no policy granting that), only read.
    op.execute("ALTER TABLE finance_categories ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY finance_categories_select ON finance_categories "
        "FOR SELECT TO authenticated USING (user_id IS NULL OR user_id = auth.uid())"
    )
    op.execute(
        "CREATE POLICY finance_categories_insert_own ON finance_categories "
        "FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid())"
    )
    op.execute(
        "CREATE POLICY finance_categories_update_own ON finance_categories "
        "FOR UPDATE TO authenticated USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid())"
    )
    op.execute(
        "CREATE POLICY finance_categories_delete_own ON finance_categories "
        "FOR DELETE TO authenticated USING (user_id = auth.uid())"
    )


def downgrade() -> None:
    for action in ("select", "insert", "update", "delete"):
        op.execute(f"DROP POLICY IF EXISTS finance_categories_{action}_own ON finance_categories")
    op.execute("DROP POLICY IF EXISTS finance_categories_select ON finance_categories")

    for table in (
        "finance_net_worth_snapshots",
        "finance_budgets",
        "finance_transactions",
        "finance_recurring",
        "finance_goals",
        "finance_accounts",
    ):
        for suffix in ("select_own", "insert_own", "update_own", "delete_own"):
            op.execute(f"DROP POLICY IF EXISTS {table}_{suffix} ON {table}")

    op.drop_table("finance_net_worth_snapshots")
    op.drop_table("finance_budgets")
    op.drop_table("finance_transactions")
    op.drop_table("finance_recurring")
    op.drop_table("finance_goals")
    op.drop_table("finance_accounts")
    op.drop_table("finance_categories")
