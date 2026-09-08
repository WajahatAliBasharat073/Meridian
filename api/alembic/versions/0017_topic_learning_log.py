"""per-topic learning log: sources, what was learned, code, extra requirements

Revision ID: 0017_topic_learning_log
Revises: 0016_gate_requirements
Create Date: 2026-09-08

The defend stage was generating questions from two things only: the topic
guide, and the submitted code. Neither says what the person actually
*studied*, so the questions were generic where they could have been aimed.

This table is that missing context, in four kinds:

* `source` — a video or article, kept as a **bookmark plus your own summary**.
  Nothing here fetches or reads the link: no transcript access exists, and
  claiming the questioner "watched" it would be a lie. The summary is what
  feeds question generation, which is also the honest arrangement — writing
  it yourself is a real signal that a link never is.
* `note` — what you learned, in your words.
* `snippet` — code you keep as you go, so verification draws on an
  accumulated scratchpad rather than one textarea filled in under pressure.
* `requirement` — something you decide the topic also demands. Additive
  only: it joins the curated gate checklist, and the curated items cannot
  be deleted, or the gate becomes self-set.

The guardrail that matters lives in app/grading.py, not here: these entries
*steer* the questions but never *bound* them, and at least one question must
target a checklist item the notes never mentioned. Otherwise the exam scope
would be chosen by the person sitting it.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0017_topic_learning_log"
down_revision: str | None = "0016_gate_requirements"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "topic_learning_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column("topic", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        # Only ever a bookmark — see the module docstring.
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "kind IN ('source', 'note', 'snippet', 'requirement')",
            name="ck_tle_kind",
        ),
    )
    op.create_index("ix_tle_user_topic", "topic_learning_entries", ["user_id", "topic"])

    op.execute("ALTER TABLE topic_learning_entries ENABLE ROW LEVEL SECURITY")
    for action in ("select", "insert", "update", "delete"):
        clause = "WITH CHECK" if action in ("insert", "update") else "USING"
        op.execute(
            f"CREATE POLICY topic_learning_entries_{action}_own "
            f"ON topic_learning_entries FOR {action.upper()} TO authenticated "
            f"{clause} (user_id = auth.uid())"
        )


def downgrade() -> None:
    for action in ("select", "insert", "update", "delete"):
        op.execute(
            f"DROP POLICY IF EXISTS topic_learning_entries_{action}_own "
            "ON topic_learning_entries"
        )
    op.drop_index("ix_tle_user_topic", table_name="topic_learning_entries")
    op.drop_table("topic_learning_entries")
