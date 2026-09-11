"""research command center: topics, papers, notes, experiments, milestones, opportunities

Revision ID: 0027_research_command_center
Revises: 0026_reading_books_enrichment
Create Date: 2026-09-11

`thesis_log` stays exactly as it is -- a daily activity log (what did I do
today), the same role `problem_attempts`/`reading_sessions` play
elsewhere. What's added here is the reference layer that was missing:
what actually *exists* to work on.

Six tables, not the fifteen-odd nouns the request listed (research ideas,
questions, hypotheses, methodology, notes, papers, experiments, datasets,
results, tasks, milestones, deadlines, writing, publications) -- per the
same request's own explicit instruction ("less tracking for the sake of
tracking"), several of those collapse into one table with a `kind`
column rather than becoming separate tables that would all hold the same
three fields:

  research_topics        the anchor: what am I researching, why, and
                          what's currently blocking it
  research_papers         literature -- one row per paper/reference
  research_notes          ideas / questions / hypotheses / methodology /
                          plain notes, distinguished by `kind`, each
                          optionally linked to a topic and/or a paper
  research_experiments    one row per experiment -- dataset and result
                          are columns here, not their own tables, since
                          a personal research log doesn't need dataset
                          versioning or structured result schemas
  research_milestones     anything with a deadline: a thesis chapter, a
                          paper submission, an experiment due date
  research_opportunities  conferences/journals being tracked as
                          submission targets, with the interested ->
                          shortlisted -> preparing -> submitted ->
                          accepted/rejected pipeline

All six link back to `research_topics` (nullable -- a paper or note
doesn't have to belong to a topic yet) rather than to each other in a
deeper graph a solo user has no real need to navigate.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0027_research_command_center"
down_revision: str | None = "0026_reading_books_enrichment"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_JSON = postgresql.JSONB(astext_type=sa.Text())

_USER_SCOPED_TABLES = (
    "research_topics",
    "research_papers",
    "research_notes",
    "research_experiments",
    "research_milestones",
    "research_opportunities",
)


def upgrade() -> None:
    op.create_table(
        "research_topics",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        # The single most useful field for "keep the process motivating":
        # what's actually stopping progress right now, in plain words.
        sa.Column("current_blocker", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status IN ('active','paused','completed','abandoned')", name="ck_research_topics_status"
        ),
    )
    op.create_index("ix_research_topics_user_id", "research_topics", ["user_id"])

    op.create_table(
        "research_papers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("topic_id", sa.Integer(), sa.ForeignKey("research_topics.id"), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("authors", sa.String(), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("venue", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="to_read"),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("relevance_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status IN ('to_read','reading','read')", name="ck_research_papers_status"
        ),
    )
    op.create_index("ix_research_papers_user_id", "research_papers", ["user_id"])
    op.create_index("ix_research_papers_topic_id", "research_papers", ["topic_id"])

    op.create_table(
        "research_notes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("topic_id", sa.Integer(), sa.ForeignKey("research_topics.id"), nullable=True),
        sa.Column("paper_id", sa.Integer(), sa.ForeignKey("research_papers.id"), nullable=True),
        sa.Column("kind", sa.String(), nullable=False, server_default="note"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "kind IN ('idea','question','hypothesis','methodology','note')",
            name="ck_research_notes_kind",
        ),
    )
    op.create_index("ix_research_notes_user_id", "research_notes", ["user_id"])
    op.create_index("ix_research_notes_topic_id", "research_notes", ["topic_id"])
    op.create_index("ix_research_notes_paper_id", "research_notes", ["paper_id"])

    op.create_table(
        "research_experiments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("topic_id", sa.Integer(), sa.ForeignKey("research_topics.id"), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("dataset", sa.String(), nullable=True),
        sa.Column("methodology_note", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="planned"),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("started_date", sa.Date(), nullable=True),
        sa.Column("completed_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status IN ('planned','running','completed','abandoned')",
            name="ck_research_experiments_status",
        ),
    )
    op.create_index("ix_research_experiments_user_id", "research_experiments", ["user_id"])
    op.create_index("ix_research_experiments_topic_id", "research_experiments", ["topic_id"])

    op.create_table(
        "research_milestones",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("topic_id", sa.Integer(), sa.ForeignKey("research_topics.id"), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending','in_progress','completed','missed')",
            name="ck_research_milestones_status",
        ),
    )
    op.create_index("ix_research_milestones_user_id", "research_milestones", ["user_id"])
    op.create_index("ix_research_milestones_topic_id", "research_milestones", ["topic_id"])
    op.create_index("ix_research_milestones_target_date", "research_milestones", ["target_date"])

    op.create_table(
        "research_opportunities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("venue_name", sa.String(), nullable=False),
        sa.Column("venue_type", sa.String(), nullable=False),
        sa.Column("research_area", sa.String(), nullable=True),
        sa.Column("submission_deadline", sa.Date(), nullable=True),
        sa.Column("notification_date", sa.Date(), nullable=True),
        sa.Column("event_date", sa.Date(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("links", _JSON, nullable=False, server_default="[]"),
        sa.Column("submission_type", sa.String(), nullable=True),
        sa.Column("relevance", sa.String(), nullable=True),
        sa.Column("priority", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="interested"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "venue_type IN ('conference','journal','workshop')", name="ck_research_opp_venue_type"
        ),
        sa.CheckConstraint(
            "relevance IS NULL OR relevance IN ('high','medium','low')", name="ck_research_opp_relevance"
        ),
        sa.CheckConstraint(
            "priority IS NULL OR priority IN ('high','medium','low')", name="ck_research_opp_priority"
        ),
        sa.CheckConstraint(
            "status IN ('interested','shortlisted','preparing','submitted','accepted','rejected','not_relevant')",
            name="ck_research_opp_status",
        ),
    )
    op.create_index("ix_research_opportunities_user_id", "research_opportunities", ["user_id"])
    op.create_index(
        "ix_research_opportunities_submission_deadline", "research_opportunities", ["submission_deadline"]
    )

    for table in _USER_SCOPED_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY {table}_select_own ON {table} "
            f"FOR SELECT TO authenticated USING (user_id = auth.uid())"
        )
        op.execute(
            f"CREATE POLICY {table}_insert_own ON {table} "
            f"FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid())"
        )
        op.execute(
            f"CREATE POLICY {table}_update_own ON {table} "
            f"FOR UPDATE TO authenticated USING (user_id = auth.uid()) "
            f"WITH CHECK (user_id = auth.uid())"
        )
        op.execute(
            f"CREATE POLICY {table}_delete_own ON {table} "
            f"FOR DELETE TO authenticated USING (user_id = auth.uid())"
        )


def downgrade() -> None:
    for table in _USER_SCOPED_TABLES:
        for suffix in ("select_own", "insert_own", "update_own", "delete_own"):
            op.execute(f"DROP POLICY IF EXISTS {table}_{suffix} ON {table}")

    op.drop_table("research_opportunities")
    op.drop_table("research_milestones")
    op.drop_table("research_experiments")
    op.drop_table("research_notes")
    op.drop_table("research_papers")
    op.drop_table("research_topics")
