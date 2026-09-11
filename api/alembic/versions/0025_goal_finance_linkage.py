"""narrow goal <-> finance_goal linkage

Revision ID: 0025_goal_finance_linkage
Revises: 0024_vocab_words_enrichment
Create Date: 2026-09-11

The narrow linkage PRODUCT_AUDIT.md recommended over a full habit/task
system: an optional `finance_goal_id` on `goals`, not new columns on
`goals` itself. `Goal.progress_pct` is manual-only by design (see
models/goals.py's module docstring); a money goal's progress must be
computed from real transactions (FinanceGoal, via
engines/finance.py::goal_progress), which is a different guarantee than
"manual-only" -- so the two stay separate tables, linked, rather than
merged into one with inconsistent rules about where its number comes
from.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0025_goal_finance_linkage"
down_revision: str | None = "0024_vocab_words_enrichment"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "goals", sa.Column("finance_goal_id", sa.Integer(), sa.ForeignKey("finance_goals.id"), nullable=True)
    )
    op.create_index("ix_goals_finance_goal_id", "goals", ["finance_goal_id"])


def downgrade() -> None:
    op.drop_index("ix_goals_finance_goal_id", table_name="goals")
    op.drop_column("goals", "finance_goal_id")
