"""enable row level security

Revision ID: 0002_enable_rls
Revises: 0001_initial_schema
Create Date: 2026-09-06

RLS on every table keyed to user_id (design doc §5 / §11). Targets the
Supabase `authenticated` role and `auth.uid()`, so this assumes a Supabase
Postgres instance (the `auth` schema) — it will not apply cleanly to a
vanilla local Postgres.

Our own FastAPI backend connects with the base `postgres` role (which
bypasses RLS by default) and does its own user_id scoping in the
repository layer — these policies are defence in depth for any other
client that queries Postgres directly with a Supabase-issued JWT (e.g. a
future frontend using the Supabase client library), not the primary
authorization mechanism for the API itself.
"""
from collections.abc import Sequence

from alembic import op

revision: str = "0002_enable_rls"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# (table, column checked against auth.uid())
USER_SCOPED_TABLES: list[tuple[str, str]] = [
    ("users", "id"),
    ("time_blocks", "user_id"),
    ("mistakes", "user_id"),
    ("problem_attempts", "user_id"),
    ("reviews", "user_id"),
    ("mocks", "user_id"),
    ("thesis_log", "user_id"),
    ("vocab_words", "user_id"),
    ("recovery_log", "user_id"),
    ("nutrition_log", "user_id"),
    ("meal_plan", "user_id"),
    ("reading_log", "user_id"),
    ("time_leaks", "user_id"),
    ("settings", "user_id"),
    ("observations", "user_id"),
]

# Shared reference data — no user_id column, so RLS here is read-only
# gating for `authenticated`, not per-row ownership. Writes happen via
# the ETL/seed scripts, which connect with the base postgres role.
REFERENCE_TABLES: list[str] = [
    "problems",
    "curriculum",
    "patterns",
    "operating_rules",
    "meals",
    "prayer_times",
]


def upgrade() -> None:
    for table, col in USER_SCOPED_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY {table}_select_own ON {table} "
            f"FOR SELECT TO authenticated USING ({col} = auth.uid())"
        )
        op.execute(
            f"CREATE POLICY {table}_insert_own ON {table} "
            f"FOR INSERT TO authenticated WITH CHECK ({col} = auth.uid())"
        )
        op.execute(
            f"CREATE POLICY {table}_update_own ON {table} "
            f"FOR UPDATE TO authenticated USING ({col} = auth.uid()) "
            f"WITH CHECK ({col} = auth.uid())"
        )
        op.execute(
            f"CREATE POLICY {table}_delete_own ON {table} "
            f"FOR DELETE TO authenticated USING ({col} = auth.uid())"
        )

    for table in REFERENCE_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY {table}_read_all ON {table} FOR SELECT TO authenticated USING (true)"
        )

    # current_mastery derives from problem_attempts. Without this, the view
    # runs with its owner's privileges and silently bypasses the RLS just
    # added above (Postgres's default view behaviour, not a Supabase quirk).
    op.execute("ALTER VIEW current_mastery SET (security_invoker = true)")


def downgrade() -> None:
    op.execute("ALTER VIEW current_mastery RESET (security_invoker)")

    for table in REFERENCE_TABLES:
        op.execute(f"DROP POLICY IF EXISTS {table}_read_all ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    for table, _ in USER_SCOPED_TABLES:
        for suffix in ("select_own", "insert_own", "update_own", "delete_own"):
            op.execute(f"DROP POLICY IF EXISTS {table}_{suffix} ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
