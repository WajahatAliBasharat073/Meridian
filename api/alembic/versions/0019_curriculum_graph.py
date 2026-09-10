"""give the question bank a knowledge model: topics, prerequisites, levels

Revision ID: 0019_curriculum_graph
Revises: 0018_vitals_upsert_and_exercise
Create Date: 2026-09-10

The daily picker could serve a brand-new learner a Google case study on day
one because there was nothing in the schema for it to respect. `questions`
had category, module, submodule and difficulty -- all descriptive, none of
them ordering. No phase, no prerequisites, no notion of "foundational".
The fix is not a better sort; it is a knowledge model to sort against.

See CURRICULUM_AUDIT.md for the measured failure and the design. Two axes:

  curriculum_topics  the knowledge graph: phase, prerequisites. What to
                     learn next, and what must come first.
  questions.*        each question's single knowledge location, plus the
                     format and cognitive level describing how it tests.

Everything here is additive. `question_progress` carries real mastery data
and is untouched, so a learner's history survives the migration intact --
and is in fact what the placement step later reads to avoid dumping an
experienced learner back at "what is supervised learning?".

`classification_confidence` is deliberately stored. About 30% of the bank
is classified by keyword rather than by an exact submodule label, and
pretending those are as certain as the rest would be the same kind of
invented precision this codebase has been cleaned of twice already.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0019_curriculum_graph"
down_revision: str | None = "0018_vitals_upsert_and_exercise"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_JSON = postgresql.JSONB(astext_type=sa.Text())


def upgrade() -> None:
    op.create_table(
        "curriculum_topics",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("slug", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("phase", sa.Integer(), nullable=False, index=True),
        sa.Column("phase_name", sa.String(), nullable=False),
        # Topic slugs, AND semantics: every one must be mastered to unlock.
        sa.Column("prereqs", _JSON, nullable=False, server_default="[]"),
        # Ungated topics are always eligible. Behavioural questions and
        # project deep dives test transferable skill, and refusing to let
        # someone rehearse their own project story until they have mastered
        # PCA would be absurd.
        sa.Column("gated", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint("phase >= 0 AND phase <= 5", name="ck_topics_phase"),
    )

    # Invariant 1: every question is exactly one of knowledge | format.
    # A format question still carries a topic -- that is what gates it --
    # but it never drives the learner's position.
    op.add_column("questions", sa.Column("axis", sa.String(), nullable=True))
    op.add_column("questions", sa.Column("topic", sa.String(), nullable=True))
    op.add_column("questions", sa.Column("phase", sa.Integer(), nullable=True))
    op.add_column("questions", sa.Column("cognitive_level", sa.Integer(), nullable=True))
    op.add_column("questions", sa.Column("primary_format", sa.String(), nullable=True))
    # A preview is visible early on purpose ("what is an LLM?") but must
    # never advance the frontier, unlock a dependent topic, or count toward
    # prerequisite mastery.
    op.add_column(
        "questions",
        sa.Column("preview", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "questions", sa.Column("classification_confidence", sa.String(), nullable=True)
    )
    op.create_index("ix_questions_topic", "questions", ["topic"])
    op.create_index("ix_questions_phase", "questions", ["phase"])
    # L0 recognition, L1 recall, L2 understanding, L3 application,
    # L4 analysis, L5 design/synthesis.
    op.create_check_constraint(
        "ck_questions_cognitive_level",
        "questions",
        "cognitive_level IS NULL OR (cognitive_level >= 0 AND cognitive_level <= 5)",
    )
    op.create_check_constraint(
        "ck_questions_axis",
        "questions",
        "axis IS NULL OR axis IN ('knowledge', 'format')",
    )
    op.create_check_constraint(
        "ck_questions_confidence",
        "questions",
        "classification_confidence IS NULL OR "
        "classification_confidence IN ('exact', 'keyword', 'module_default')",
    )

    # Where the learner is. One row per user: the current topic, and the
    # phase it sits in. Everything else about eligibility is derived from
    # the graph plus question_progress, so this stays deliberately small.
    op.create_table(
        "learner_frontier",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column("current_topic", sa.String(), nullable=True),
        # UNASSESSED -> ASSESSING -> PLACED. The distinction that matters:
        # "no recorded progress" must not be read as "beginner". An
        # experienced engineer with an empty history is UNASSESSED, not P0.
        sa.Column(
            "placement_status", sa.String(), nullable=False, server_default="UNASSESSED"
        ),
        sa.Column("placement_phase", sa.Integer(), nullable=True),
        # 0..1. Placement may only skip material it has real evidence for.
        sa.Column("placement_confidence", sa.Float(), nullable=True),
        sa.Column("placed_at", sa.DateTime(), nullable=True),
        # How the starting position was arrived at, so a frontier that looks
        # surprising can be explained rather than guessed at.
        sa.Column("placement_method", sa.String(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("user_id", name="uq_learner_frontier_user"),
        sa.CheckConstraint(
            "placement_status IN ('UNASSESSED', 'ASSESSING', 'PLACED')",
            name="ck_frontier_placement_status",
        ),
        sa.CheckConstraint(
            "placement_phase IS NULL OR (placement_phase >= 0 AND placement_phase <= 5)",
            name="ck_frontier_placement_phase",
        ),
        sa.CheckConstraint(
            "placement_confidence IS NULL OR "
            "(placement_confidence >= 0 AND placement_confidence <= 1)",
            name="ck_frontier_placement_confidence",
        ),
    )

    op.execute("ALTER TABLE learner_frontier ENABLE ROW LEVEL SECURITY")
    for action in ("select", "insert", "update", "delete"):
        clause = "WITH CHECK" if action in ("insert", "update") else "USING"
        op.execute(
            f"CREATE POLICY learner_frontier_{action}_own "
            f"ON learner_frontier FOR {action.upper()} TO authenticated "
            f"{clause} (user_id = auth.uid())"
        )


def downgrade() -> None:
    for action in ("select", "insert", "update", "delete"):
        op.execute(f"DROP POLICY IF EXISTS learner_frontier_{action}_own ON learner_frontier")
    op.drop_table("learner_frontier")

    op.drop_constraint("ck_questions_axis", "questions", type_="check")
    op.drop_constraint("ck_questions_confidence", "questions", type_="check")
    op.drop_constraint("ck_questions_cognitive_level", "questions", type_="check")
    op.drop_index("ix_questions_phase", table_name="questions")
    op.drop_index("ix_questions_topic", table_name="questions")
    for col in (
        "classification_confidence",
        "preview",
        "primary_format",
        "axis",
        "cognitive_level",
        "phase",
        "topic",
    ):
        op.drop_column("questions", col)

    op.drop_table("curriculum_topics")
