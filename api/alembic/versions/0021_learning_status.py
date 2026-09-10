"""per-question learning status and a needs-review flag, both user-specific

Revision ID: 0021_learning_status
Revises: 0020_adjudicated_confidence
Create Date: 2026-09-10

Two additive columns on `question_progress`, which is already the
per-user, per-question row (unique on user_id + question_id) -- this is
not a second, parallel mastery system. `mastery` (0-7) stays the
quantitative ladder the curriculum engine and spaced review already read;
`learning_status` is a qualitative self-tag layered on top, for personal
filtering ("show me what I struggled with"), and never fed into the
curriculum's mastery-fraction calculation.

`needs_review` is a separate boolean rather than a status value, because
the workflow described is "solved with help -> auto-flagged for revisit,
AND independently toggleable" -- a flag that can be true or false under
any status is a cleaner fit than folding it into the status enum, where
"solved_with_help_and_flagged" and "solved_with_help_not_flagged" would
otherwise have to be two different values.

`not_attempted` is deliberately not a stored value: it is the absence of a
question_progress row, which already exists and already means exactly
that everywhere else in the app.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0021_learning_status"
down_revision: str | None = "0020_adjudicated_confidence"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_STATUSES = (
    "already_know", "easy", "understood", "solved_with_help", "struggled", "no_idea",
)


def upgrade() -> None:
    op.add_column("question_progress", sa.Column("learning_status", sa.String(), nullable=True))
    op.add_column(
        "question_progress",
        sa.Column("needs_review", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index(
        "ix_question_progress_learning_status", "question_progress", ["learning_status"]
    )
    op.create_index("ix_question_progress_needs_review", "question_progress", ["needs_review"])
    op.create_check_constraint(
        "ck_question_progress_learning_status",
        "question_progress",
        "learning_status IS NULL OR learning_status IN ("
        + ", ".join(f"'{s}'" for s in _STATUSES)
        + ")",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_question_progress_learning_status", "question_progress", type_="check"
    )
    op.drop_index("ix_question_progress_needs_review", table_name="question_progress")
    op.drop_index("ix_question_progress_learning_status", table_name="question_progress")
    op.drop_column("question_progress", "needs_review")
    op.drop_column("question_progress", "learning_status")
