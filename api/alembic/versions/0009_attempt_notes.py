"""free-form notes on a problem attempt

Revision ID: 0009_attempt_notes
Revises: 0008_attempt_solve_method
Create Date: 2026-09-07

`key_insight` already exists but has a specific job: it is the one-line
recall prompt the recommender surfaces when the problem comes back for
review, so it has to stay short. This is the other thing you want to write
when you finish a problem — the working, the edge case that bit you, the
approach you rejected. Text, not String, because it is meant to be long.

Nullable: every existing attempt predates it.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0009_attempt_notes"
down_revision: str | None = "0008_attempt_solve_method"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("problem_attempts", sa.Column("notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("problem_attempts", "notes")
