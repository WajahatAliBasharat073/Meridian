"""goals, time budgets, daily reflection

Revision ID: 0005_goals_budgets_reflection
Revises: 0004_questions
Create Date: 2026-09-06
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_goals_budgets_reflection"
down_revision: str | None = "0004_questions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

USER_SCOPED_TABLES = ["goals", "time_budgets", "daily_reflections"]


def upgrade() -> None:
    op.create_table(
        "goals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("progress_pct", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status IN ('active','completed','abandoned')", name="ck_goals_status"),
        sa.CheckConstraint("progress_pct >= 0 AND progress_pct <= 100", name="ck_goals_progress_pct"),
    )
    op.create_index("ix_goals_user_id", "goals", ["user_id"])

    op.create_table(
        "time_budgets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("minutes_per_week", sa.Integer(), nullable=False),
        sa.UniqueConstraint("user_id", "category", name="uq_time_budgets_user_category"),
    )
    op.create_index("ix_time_budgets_user_id", "time_budgets", ["user_id"])

    op.create_table(
        "daily_reflections",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("mood", sa.String(), nullable=False),
        sa.Column("what_got_in_the_way", sa.String(), nullable=True),
        sa.Column("what_went_well", sa.String(), nullable=True),
        sa.UniqueConstraint("user_id", "date", name="uq_daily_reflections_user_date"),
        sa.CheckConstraint(
            "mood IN ('difficult','normal','good','excellent')", name="ck_daily_reflections_mood"
        ),
    )
    op.create_index("ix_daily_reflections_user_id", "daily_reflections", ["user_id"])

    for table in USER_SCOPED_TABLES:
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


def downgrade() -> None:
    for table in USER_SCOPED_TABLES:
        for suffix in ("select_own", "insert_own", "update_own", "delete_own"):
            op.execute(f"DROP POLICY IF EXISTS {table}_{suffix} ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    op.drop_table("daily_reflections")
    op.drop_table("time_budgets")
    op.drop_table("goals")
