"""focus session events (pause/resume audit trail)

Revision ID: 0007_focus_session_events
Revises: 0006_focus_sessions
Create Date: 2026-09-07

Append-only, one row per start/pause/resume/extend/finish. A single
`paused_at` column on focus_sessions would be overwritten by the second
pause of a session and lose the history that makes focus breakdown
visible, so the events live in their own table.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_focus_session_events"
down_revision: str | None = "0006_focus_sessions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "focus_session_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("focus_sessions.id"), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("elapsed_seconds_at_event", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("note", sa.String(), nullable=True),
        sa.CheckConstraint(
            "event_type IN ('started','paused','resumed','extended','shortened','completed','abandoned')",
            name="ck_focus_session_events_type",
        ),
    )
    op.create_index("ix_focus_session_events_user_id", "focus_session_events", ["user_id"])
    op.create_index("ix_focus_session_events_session_id", "focus_session_events", ["session_id"])
    op.create_index("ix_focus_session_events_occurred_at", "focus_session_events", ["occurred_at"])

    op.execute("ALTER TABLE focus_session_events ENABLE ROW LEVEL SECURITY")
    for suffix, clause in [
        ("select_own", "FOR SELECT TO authenticated USING (user_id = auth.uid())"),
        ("insert_own", "FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid())"),
        (
            "update_own",
            "FOR UPDATE TO authenticated USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid())",
        ),
        ("delete_own", "FOR DELETE TO authenticated USING (user_id = auth.uid())"),
    ]:
        op.execute(f"CREATE POLICY focus_session_events_{suffix} ON focus_session_events {clause}")


def downgrade() -> None:
    for suffix in ("select_own", "insert_own", "update_own", "delete_own"):
        op.execute(f"DROP POLICY IF EXISTS focus_session_events_{suffix} ON focus_session_events")
    op.execute("ALTER TABLE focus_session_events DISABLE ROW LEVEL SECURITY")
    op.drop_table("focus_session_events")
