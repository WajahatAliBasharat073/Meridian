"""gate a topic's problems behind proving you understand the structure

Revision ID: 0015_topic_verification
Revises: 0014_dsa_topics_and_guides
Create Date: 2026-09-08

The problem this solves is self-deception, not cheating: jumping into the
array problems without knowing what an array actually costs, pattern-matching
a few solutions, and recording that as progress. So a topic's problems stay
locked until the structure has been demonstrated, and the demonstration is
two stages — build, then defend:

1. **Build** — implement the topic's required operations (for a linked list:
   singly, doubly, circular; insert at start/middle/end; delete at
   start/middle/end) and submit the code plus notes. Checked for *coverage
   against that topic's own checklist*, which is generated from the topic
   guide's `types` and `operations`.

2. **Defend** — immediately afterwards, a short closed-book set of questions,
   some of them about the code just submitted. This is what makes stage 1
   unfakeable: pasted code cannot be defended. No plagiarism check is
   attempted, because none of them work; being asked why your own `delete`
   needs `prev` does work.

One row per attempt (never a mutable "verified" flag on the topic), matching
`problem_attempts` — so a failed attempt, a re-verification and an override
are all preserved history rather than overwrites.

`focus_losses` / `focus_lost_seconds` are a flight recorder, not a lock: a
browser cannot prevent tab switching (no API exists, and a phone defeats it
regardless), so leaving the window is *recorded and shown* instead of being
falsely promised as impossible.

`override` is the escape hatch — unlocking without verifying, kept as a
permanent mark on that topic rather than a silent bypass. A gate with no
exit gets resented and abandoned; one whose exit costs an honest mark on
your own dashboard does not.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0015_topic_verification"
down_revision: str | None = "0014_dsa_topics_and_guides"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_JSON = postgresql.JSONB(astext_type=sa.Text())


def upgrade() -> None:
    op.create_table(
        "topic_verification_attempts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("topic", sa.String(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        # 'build' while the submission is being checked, 'defend' once the
        # questions are out, then a terminal state.
        sa.Column("stage", sa.String(), nullable=False, server_default="build"),
        sa.Column("code_submission", sa.Text(), nullable=True),
        sa.Column("notes_submission", sa.Text(), nullable=True),
        # What the checker found: which required items are covered, which are
        # missing, and any correctness concerns — shown back verbatim.
        sa.Column("coverage", _JSON, nullable=False, server_default="{}"),
        sa.Column("build_score", sa.Float(), nullable=True),
        # The generated questions, the answers given, and the per-question
        # verdicts. Kept so a pass can be re-read later and is auditable.
        sa.Column("questions", _JSON, nullable=False, server_default="[]"),
        sa.Column("answers", _JSON, nullable=False, server_default="[]"),
        sa.Column("grades", _JSON, nullable=False, server_default="[]"),
        sa.Column("defend_score", sa.Float(), nullable=True),
        sa.Column("passed", sa.Boolean(), nullable=True),
        sa.Column("passed_at", sa.DateTime(), nullable=True),
        # Flight recorder for the closed-book stage.
        sa.Column("focus_losses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("focus_lost_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        # The escape hatch, recorded rather than silent.
        sa.Column("override", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("override_reason", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "stage IN ('build', 'defend', 'passed', 'failed', 'abandoned', 'override')",
            name="ck_tva_stage",
        ),
        sa.CheckConstraint(
            "build_score IS NULL OR (build_score >= 0 AND build_score <= 1)",
            name="ck_tva_build_score",
        ),
        sa.CheckConstraint(
            "defend_score IS NULL OR (defend_score >= 0 AND defend_score <= 1)",
            name="ck_tva_defend_score",
        ),
        sa.CheckConstraint("focus_losses >= 0", name="ck_tva_focus_losses"),
        sa.CheckConstraint("focus_lost_seconds >= 0", name="ck_tva_focus_seconds"),
    )
    op.create_index("ix_tva_user_topic", "topic_verification_attempts", ["user_id", "topic"])
    op.create_index("ix_tva_passed_at", "topic_verification_attempts", ["passed_at"])

    op.execute("ALTER TABLE topic_verification_attempts ENABLE ROW LEVEL SECURITY")
    for action in ("select", "insert", "update", "delete"):
        clause = "WITH CHECK" if action in ("insert", "update") else "USING"
        op.execute(
            f"CREATE POLICY topic_verification_attempts_{action}_own "
            f"ON topic_verification_attempts FOR {action.upper()} TO authenticated "
            f"{clause} (user_id = auth.uid())"
        )


def downgrade() -> None:
    for action in ("select", "insert", "update", "delete"):
        op.execute(
            f"DROP POLICY IF EXISTS topic_verification_attempts_{action}_own "
            "ON topic_verification_attempts"
        )
    op.drop_index("ix_tva_passed_at", table_name="topic_verification_attempts")
    op.drop_index("ix_tva_user_topic", table_name="topic_verification_attempts")
    op.drop_table("topic_verification_attempts")
