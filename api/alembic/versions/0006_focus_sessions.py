"""focus sessions (actual start/end vs scheduled)

Revision ID: 0006_focus_sessions
Revises: 0005_goals_budgets_reflection
Create Date: 2026-09-07
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_focus_sessions"
down_revision: str | None = "0005_goals_budgets_reflection"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "focus_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("block_id", sa.Integer(), sa.ForeignKey("time_blocks.id"), nullable=False),
        sa.Column("scheduled_start", sa.Time(), nullable=True),
        sa.Column("planned_minutes", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("elapsed_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("start_delay_minutes", sa.Integer(), nullable=True),
        sa.Column("state", sa.String(), nullable=False, server_default="in_progress"),
        sa.Column("focus_rating", sa.Integer(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.CheckConstraint(
            "state IN ('in_progress','paused','completed','abandoned')",
            name="ck_focus_sessions_state",
        ),
    )
    op.create_index("ix_focus_sessions_user_id", "focus_sessions", ["user_id"])
    op.create_index("ix_focus_sessions_block_id", "focus_sessions", ["block_id"])
    op.create_index("ix_focus_sessions_started_at", "focus_sessions", ["started_at"])

    op.execute("ALTER TABLE focus_sessions ENABLE ROW LEVEL SECURITY")
    for suffix, clause in [
        ("select_own", "FOR SELECT TO authenticated USING (user_id = auth.uid())"),
        ("insert_own", "FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid())"),
        (
            "update_own",
            "FOR UPDATE TO authenticated USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid())",
        ),
        ("delete_own", "FOR DELETE TO authenticated USING (user_id = auth.uid())"),
    ]:
        op.execute(f"CREATE POLICY focus_sessions_{suffix} ON focus_sessions {clause}")


def downgrade() -> None:
    for suffix in ("select_own", "insert_own", "update_own", "delete_own"):
        op.execute(f"DROP POLICY IF EXISTS focus_sessions_{suffix} ON focus_sessions")
    op.execute("ALTER TABLE focus_sessions DISABLE ROW LEVEL SECURITY")
    op.drop_table("focus_sessions")
