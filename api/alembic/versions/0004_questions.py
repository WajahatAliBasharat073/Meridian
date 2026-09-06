"""interview question bank

Revision ID: 0004_questions
Revises: 0003_ml_concepts
Create Date: 2026-09-06

Adds `questions` (reference data) and `question_coverage` (a per-user
toggle — row exists iff covered — deliberately simpler than
concept_attempts' mastery ladder; the user asked for "mark it covered",
not a spaced-repetition claim of mastery).
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_questions"
down_revision: str | None = "0003_ml_concepts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
    )
    op.create_index("ix_questions_category", "questions", ["category"])

    op.create_table(
        "question_coverage",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("covered_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("user_id", "question_id", name="uq_question_coverage_user_question"),
    )
    op.create_index("ix_question_coverage_user_id", "question_coverage", ["user_id"])
    op.create_index("ix_question_coverage_question_id", "question_coverage", ["question_id"])

    op.execute("ALTER TABLE questions ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY questions_read_all ON questions FOR SELECT TO authenticated USING (true)")

    op.execute("ALTER TABLE question_coverage ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY question_coverage_select_own ON question_coverage "
        "FOR SELECT TO authenticated USING (user_id = auth.uid())"
    )
    op.execute(
        "CREATE POLICY question_coverage_insert_own ON question_coverage "
        "FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid())"
    )
    op.execute(
        "CREATE POLICY question_coverage_update_own ON question_coverage "
        "FOR UPDATE TO authenticated USING (user_id = auth.uid()) "
        "WITH CHECK (user_id = auth.uid())"
    )
    op.execute(
        "CREATE POLICY question_coverage_delete_own ON question_coverage "
        "FOR DELETE TO authenticated USING (user_id = auth.uid())"
    )


def downgrade() -> None:
    for suffix in ("select_own", "insert_own", "update_own", "delete_own"):
        op.execute(f"DROP POLICY IF EXISTS question_coverage_{suffix} ON question_coverage")
    op.execute("ALTER TABLE question_coverage DISABLE ROW LEVEL SECURITY")

    op.execute("DROP POLICY IF EXISTS questions_read_all ON questions")
    op.execute("ALTER TABLE questions DISABLE ROW LEVEL SECURITY")

    op.drop_table("question_coverage")
    op.drop_table("questions")
