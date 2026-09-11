"""Research command center: the reference layer `thesis_log` never had.

`thesis_log` (app/models/life.py) stays exactly as it was -- a daily
activity log, the same role problem_attempts/reading_sessions play
elsewhere. These six tables are what it was missing: what actually
*exists* to work on. See migration 0027 for why six tables, not the
larger list of nouns the feature request named -- several of those
collapse into `ResearchNote.kind` or plain columns rather than becoming
their own tables.
"""

from __future__ import annotations

import uuid
from datetime import date as date_
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin

RESEARCH_TOPIC_STATUSES = ("active", "paused", "completed", "abandoned")
RESEARCH_PAPER_STATUSES = ("to_read", "reading", "read")
RESEARCH_NOTE_KINDS = ("idea", "question", "hypothesis", "methodology", "note")
RESEARCH_EXPERIMENT_STATUSES = ("planned", "running", "completed", "abandoned")
RESEARCH_MILESTONE_STATUSES = ("pending", "in_progress", "completed", "missed")
RESEARCH_OPPORTUNITY_VENUE_TYPES = ("conference", "journal", "workshop")
RESEARCH_OPPORTUNITY_STATUSES = (
    "interested",
    "shortlisted",
    "preparing",
    "submitted",
    "accepted",
    "rejected",
    "not_relevant",
)


class ResearchTopic(Base, TimestampMixin):
    """The anchor entity: what am I researching, and -- the one field
    that makes this a motivation tool rather than a database -- what's
    currently blocking it, in plain words."""

    __tablename__ = "research_topics"
    __table_args__ = (
        CheckConstraint(f"status IN {RESEARCH_TOPIC_STATUSES!r}", name="ck_research_topics_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active")
    current_blocker: Mapped[str | None] = mapped_column(Text, nullable=True)


class ResearchPaper(Base, TimestampMixin):
    __tablename__ = "research_papers"
    __table_args__ = (
        CheckConstraint(f"status IN {RESEARCH_PAPER_STATUSES!r}", name="ck_research_papers_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    topic_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("research_topics.id"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String)
    authors: Mapped[str | None] = mapped_column(String, nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    venue: Mapped[str | None] = mapped_column(String, nullable=True)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="to_read")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    relevance_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class ResearchNote(Base, TimestampMixin):
    """Ideas, questions, hypotheses, methodology notes, and plain notes --
    distinguished by `kind` rather than five separate tables that would
    each hold the same (topic, paper, content, timestamp) shape."""

    __tablename__ = "research_notes"
    __table_args__ = (
        CheckConstraint(f"kind IN {RESEARCH_NOTE_KINDS!r}", name="ck_research_notes_kind"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    topic_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("research_topics.id"), nullable=True, index=True
    )
    paper_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("research_papers.id"), nullable=True, index=True
    )
    kind: Mapped[str] = mapped_column(String, default="note")
    content: Mapped[str] = mapped_column(Text)


class ResearchExperiment(Base, TimestampMixin):
    """Dataset and result are columns here, not their own tables -- a
    personal research log doesn't need dataset versioning or a
    structured result schema, just a place to write down what happened."""

    __tablename__ = "research_experiments"
    __table_args__ = (
        CheckConstraint(
            f"status IN {RESEARCH_EXPERIMENT_STATUSES!r}", name="ck_research_experiments_status"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    topic_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("research_topics.id"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    dataset: Mapped[str | None] = mapped_column(String, nullable=True)
    methodology_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="planned")
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_date: Mapped[date_ | None] = mapped_column(nullable=True)
    completed_date: Mapped[date_ | None] = mapped_column(nullable=True)


class ResearchMilestone(Base, TimestampMixin):
    """Anything with a deadline: a thesis chapter, a paper submission, an
    experiment due date. One entity rather than three, since they all
    need exactly the same (title, target_date, status) shape."""

    __tablename__ = "research_milestones"
    __table_args__ = (
        CheckConstraint(
            f"status IN {RESEARCH_MILESTONE_STATUSES!r}", name="ck_research_milestones_status"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    topic_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("research_topics.id"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_date: Mapped[date_ | None] = mapped_column(nullable=True, index=True)
    status: Mapped[str] = mapped_column(String, default="pending")


class ResearchOpportunity(Base, TimestampMixin):
    """A conference/journal being tracked as a submission target --
    interested -> shortlisted -> preparing -> submitted ->
    accepted/rejected/not_relevant."""

    __tablename__ = "research_opportunities"
    __table_args__ = (
        CheckConstraint(
            f"venue_type IN {RESEARCH_OPPORTUNITY_VENUE_TYPES!r}", name="ck_research_opp_venue_type"
        ),
        CheckConstraint(
            "relevance IS NULL OR relevance IN ('high','medium','low')", name="ck_research_opp_relevance"
        ),
        CheckConstraint(
            "priority IS NULL OR priority IN ('high','medium','low')", name="ck_research_opp_priority"
        ),
        CheckConstraint(
            f"status IN {RESEARCH_OPPORTUNITY_STATUSES!r}", name="ck_research_opp_status"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    venue_name: Mapped[str] = mapped_column(String)
    venue_type: Mapped[str] = mapped_column(String)
    research_area: Mapped[str | None] = mapped_column(String, nullable=True)
    submission_deadline: Mapped[date_ | None] = mapped_column(nullable=True, index=True)
    notification_date: Mapped[date_ | None] = mapped_column(nullable=True)
    event_date: Mapped[date_ | None] = mapped_column(nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    links: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    submission_type: Mapped[str | None] = mapped_column(String, nullable=True)
    relevance: Mapped[str | None] = mapped_column(String, nullable=True)
    priority: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="interested")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
