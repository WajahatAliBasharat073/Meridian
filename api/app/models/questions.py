"""The AI/ML interview curriculum: modules, question records, progress.

Three tables, and the split matters. `interview_modules` is the master map
(A..AF) — reference data with its own priority so "what do I prepare
first" is a query. `questions` is the canonical bank: one row per
question, deduplicated across sources. `question_progress` is the user's
0-7 mastery ladder over it.

Kept separate from `concepts` (L0-L6) on purpose: a concept is a topic you
master, a question is a prompt you can answer under follow-up pressure.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class InterviewModule(Base):
    """One module of the master map. Reference data, not user state."""

    __tablename__ = "interview_modules"
    __table_args__ = (
        CheckConstraint("priority IN ('P0','P1','P2','P3')", name="ck_modules_priority"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String)
    submodules: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    target_seniority: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    order_index: Mapped[int] = mapped_column(Integer)


class Question(Base):
    """One canonical interview question.

    `evidence` is the column that keeps this bank honest:

      reported     a named source ties this question to a company
      common       appears across several independent prep sources
      fundamental  core knowledge; no company claim made or needed
      derived      generated from a topic outline, not a reported question

    A non-empty `companies` list requires evidence='reported' and a
    `source_url` — enforced by a database check constraint, because
    "asked at Meta" is precisely the claim that gets invented.
    """

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)
    order_index: Mapped[int] = mapped_column(Integer)

    # --- curriculum position (migration 0019) -------------------------
    # `axis` is the knowledge/format split; `topic` is the single knowledge
    # location; `phase` is P0..P5 curriculum position.
    #
    # Note carefully: `priority` below is *interview* priority (how often
    # this shows up in a loop). It is NOT curriculum position and must
    # never be used as one -- conflating them is what made a brand-new
    # learner's day one "Design an LLM chatbot at scale", because GenAI
    # System Design is a P0-priority module.
    axis: Mapped[str | None] = mapped_column(String, nullable=True)
    topic: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    phase: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    cognitive_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    primary_format: Mapped[str | None] = mapped_column(String, nullable=True)
    preview: Mapped[bool] = mapped_column(Boolean, default=False)
    classification_confidence: Mapped[str | None] = mapped_column(String, nullable=True)

    module_code: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    submodule: Mapped[str | None] = mapped_column(String, nullable=True)
    concept: Mapped[str | None] = mapped_column(String, nullable=True)
    question_type: Mapped[str | None] = mapped_column(String, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String, nullable=True)
    seniority: Mapped[str | None] = mapped_column(String, nullable=True)
    priority: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    frequency: Mapped[str | None] = mapped_column(String, nullable=True)
    evidence: Mapped[str | None] = mapped_column(String, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)

    tests_for: Mapped[str | None] = mapped_column(Text, nullable=True)
    # The real problem statement + reference implementation, for coding
    # questions backed by an actual source file (Module B). Populated only
    # when one exists — a concept or system-design question has nothing to
    # put here.
    reference_solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    strong_signal: Mapped[str | None] = mapped_column(Text, nullable=True)
    weak_signal: Mapped[str | None] = mapped_column(Text, nullable=True)

    companies: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    answer_dimensions: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    follow_ups: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    common_mistakes: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    prerequisites: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    related: Mapped[list[Any]] = mapped_column(JSONB, default=list)


class QuestionProgress(Base):
    """Where this user sits on the 0-7 mastery ladder for one question.

    0 never seen | 1 recognize | 2 can explain | 3 can solve
    4 can reason about trade-offs | 5 can answer follow-ups
    6 can design a production system with it | 7 can teach it

    This replaced a binary "covered" flag. Having seen a question and
    being able to hold it under follow-up pressure are different states,
    and a checkbox could not tell them apart — which made the readiness
    percentage meaningless.

    `rating_count`/`total_minutes` are cumulative across every rating of
    this question, not just the latest one — overwriting a single
    `minutes` field on each re-rating would silently discard the history
    of a question studied more than once, and that history is exactly
    what the pace-projection engine (app/engines/theory_pace.py) needs.
    """

    __tablename__ = "question_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uq_question_progress_user_question"),
        CheckConstraint("mastery BETWEEN 0 AND 7", name="ck_question_progress_mastery"),
        CheckConstraint("total_minutes >= 0", name="ck_question_progress_total_minutes_nonneg"),
        CheckConstraint("rating_count >= 0", name="ck_question_progress_rating_count_nonneg"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    mastery: Mapped[int] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column()
    rating_count: Mapped[int] = mapped_column(Integer, default=0)
    total_minutes: Mapped[int] = mapped_column(Integer, default=0)


class CurriculumTopic(Base):
    """One node of the knowledge graph: what it is, which phase, and what
    must be mastered before it opens.

    Authored by hand in scripts/curriculum_graph.py and seeded from there,
    because "what genuinely depends on what" is a judgement, not something
    to be derived from the question text. See CURRICULUM_AUDIT.md.
    """

    __tablename__ = "curriculum_topics"
    __table_args__ = (CheckConstraint("phase >= 0 AND phase <= 5", name="ck_topics_phase"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    phase: Mapped[int] = mapped_column(Integer, index=True)
    phase_name: Mapped[str] = mapped_column(String)
    prereqs: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    gated: Mapped[bool] = mapped_column(Boolean, default=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)


class LearnerFrontier(Base):
    """Where one learner currently is.

    Deliberately small: the *set* of eligible topics is derived from the
    graph plus question_progress on every request, so there is no second
    copy of mastery to drift out of sync with the first.

    `placement_status` exists because "no recorded progress" and "beginner"
    are different things, and treating them as the same would send an
    experienced engineer back to "what is supervised learning?".
    """

    __tablename__ = "learner_frontier"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_learner_frontier_user"),
        CheckConstraint(
            "placement_status IN ('UNASSESSED', 'ASSESSING', 'PLACED')",
            name="ck_frontier_placement_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    current_topic: Mapped[str | None] = mapped_column(String, nullable=True)
    placement_status: Mapped[str] = mapped_column(String, default="UNASSESSED")
    placement_phase: Mapped[int | None] = mapped_column(Integer, nullable=True)
    placement_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    placed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    placement_method: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column()
