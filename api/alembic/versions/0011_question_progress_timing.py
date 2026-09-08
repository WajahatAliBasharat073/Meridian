"""track real time spent rating theory questions

Revision ID: 0011_question_progress_timing
Revises: 0010_interview_curriculum
Create Date: 2026-09-08

Adds two columns to `question_progress` so the daily-theory pace analysis
(api/app/engines/theory_pace.py) has real numbers to work from instead of
guessing at how long a question takes:

  rating_count   how many times this question has been rated at all
  total_minutes  the sum of minutes logged across those ratings

Cumulative rather than "last logged minutes", because `question_progress`
is one row per question — overwriting a single `minutes` field on every
re-rating would silently discard the history of a question studied more
than once. Both default to 0/NULL-safe so every existing row is valid
without backfilling a guess.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0011_question_progress_timing"
down_revision: str | None = "0010_interview_curriculum"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "question_progress",
        sa.Column("rating_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "question_progress",
        sa.Column("total_minutes", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_check_constraint(
        "ck_question_progress_total_minutes_nonneg", "question_progress", "total_minutes >= 0"
    )
    op.create_check_constraint(
        "ck_question_progress_rating_count_nonneg", "question_progress", "rating_count >= 0"
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_question_progress_rating_count_nonneg", "question_progress", type_="check"
    )
    op.drop_constraint(
        "ck_question_progress_total_minutes_nonneg", "question_progress", type_="check"
    )
    op.drop_column("question_progress", "total_minutes")
    op.drop_column("question_progress", "rating_count")
