"""allow 'adjudicated' as a classification confidence

Revision ID: 0020_adjudicated_confidence
Revises: 0019_curriculum_graph
Create Date: 2026-09-10

A fourth confidence tier above 'exact': a classification decided by
reading the question, recorded in scripts/curriculum_overrides.py with a
written reason. It outranks the submodule label because those entries are
precisely the cases where the source metadata contradicts its own content.
"""
from collections.abc import Sequence

from alembic import op

revision: str = "0020_adjudicated_confidence"
down_revision: str | None = "0019_curriculum_graph"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("ck_questions_confidence", "questions", type_="check")
    op.create_check_constraint(
        "ck_questions_confidence",
        "questions",
        "classification_confidence IS NULL OR classification_confidence IN "
        "('exact', 'keyword', 'module_default', 'adjudicated')",
    )


def downgrade() -> None:
    op.execute(
        "UPDATE questions SET classification_confidence = 'exact' "
        "WHERE classification_confidence = 'adjudicated'"
    )
    op.drop_constraint("ck_questions_confidence", "questions", type_="check")
    op.create_check_constraint(
        "ck_questions_confidence",
        "questions",
        "classification_confidence IS NULL OR classification_confidence IN "
        "('exact', 'keyword', 'module_default')",
    )
