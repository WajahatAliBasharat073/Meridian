"""track how a problem was solved, not just how well it's known

Revision ID: 0008_attempt_solve_method
Revises: 0007_focus_session_events
Create Date: 2026-09-07

`mastery_level` records confidence after the attempt. These columns record
what the attempt actually took: solved alone, needed a hint, needed the
editorial, needed a video. Two different questions, so two columns rather
than overloading the ladder.

All nullable — existing attempts predate this and are left as unknown
instead of being back-filled with an assumption.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008_attempt_solve_method"
down_revision: str | None = "0007_focus_session_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("problem_attempts", sa.Column("solve_method", sa.String(), nullable=True))
    op.add_column(
        "problem_attempts",
        sa.Column("understood_approach_independently", sa.Boolean(), nullable=True),
    )
    op.add_column("problem_attempts", sa.Column("reached_optimal", sa.Boolean(), nullable=True))

    op.create_check_constraint(
        "ck_problem_attempts_solve_method",
        "problem_attempts",
        "solve_method IS NULL OR solve_method IN ("
        "'independent','recalled_pattern','after_hint','after_editorial',"
        "'after_video','brute_force_only','not_solved')",
    )
    op.create_index("ix_problem_attempts_solve_method", "problem_attempts", ["solve_method"])


def downgrade() -> None:
    op.drop_index("ix_problem_attempts_solve_method", table_name="problem_attempts")
    op.drop_constraint("ck_problem_attempts_solve_method", "problem_attempts", type_="check")
    op.drop_column("problem_attempts", "reached_optimal")
    op.drop_column("problem_attempts", "understood_approach_independently")
    op.drop_column("problem_attempts", "solve_method")
