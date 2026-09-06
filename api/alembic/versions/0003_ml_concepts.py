"""ml/genai/system-design concept curriculum

Revision ID: 0003_ml_concepts
Revises: 0002_enable_rls
Create Date: 2026-09-06

Adds `concepts` (reference data, same shape as `problems`) and
`concept_attempts` (same shape as `problem_attempts`) so the existing
spaced-repetition engine's `ml_concept` subject type — already allowed by
`reviews.subject_type`'s check constraint since 0001 — has a real table
behind it instead of being unused.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003_ml_concepts"
down_revision: str | None = "0002_enable_rls"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "concepts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("summary", sa.String(), nullable=False),
        sa.Column("resources", postgresql.JSONB(), nullable=False),
        sa.Column("phase", sa.String(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
    )
    op.create_index("ix_concepts_category", "concepts", ["category"])

    op.create_table(
        "concept_attempts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("concept_id", sa.Integer(), sa.ForeignKey("concepts.id"), nullable=False),
        sa.Column("attempted_at", sa.DateTime(), nullable=False),
        sa.Column("mastery_level", sa.String(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.CheckConstraint("mastery_level ~ '^L[0-6]$'", name="ck_concept_attempts_mastery"),
    )
    op.create_index("ix_concept_attempts_user_id", "concept_attempts", ["user_id"])
    op.create_index("ix_concept_attempts_concept_id", "concept_attempts", ["concept_id"])

    # Same RLS shape as 0002: reference data is read-only for `authenticated`,
    # attempts are owner-scoped.
    op.execute("ALTER TABLE concepts ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY concepts_read_all ON concepts FOR SELECT TO authenticated USING (true)")

    op.execute("ALTER TABLE concept_attempts ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY concept_attempts_select_own ON concept_attempts "
        "FOR SELECT TO authenticated USING (user_id = auth.uid())"
    )
    op.execute(
        "CREATE POLICY concept_attempts_insert_own ON concept_attempts "
        "FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid())"
    )
    op.execute(
        "CREATE POLICY concept_attempts_update_own ON concept_attempts "
        "FOR UPDATE TO authenticated USING (user_id = auth.uid()) "
        "WITH CHECK (user_id = auth.uid())"
    )
    op.execute(
        "CREATE POLICY concept_attempts_delete_own ON concept_attempts "
        "FOR DELETE TO authenticated USING (user_id = auth.uid())"
    )


def downgrade() -> None:
    for suffix in ("select_own", "insert_own", "update_own", "delete_own"):
        op.execute(f"DROP POLICY IF EXISTS concept_attempts_{suffix} ON concept_attempts")
    op.execute("ALTER TABLE concept_attempts DISABLE ROW LEVEL SECURITY")

    op.execute("DROP POLICY IF EXISTS concepts_read_all ON concepts")
    op.execute("ALTER TABLE concepts DISABLE ROW LEVEL SECURITY")

    op.drop_table("concept_attempts")
    op.drop_table("concepts")
