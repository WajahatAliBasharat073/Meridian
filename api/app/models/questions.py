"""ML/GenAI/Agentic/Production interview question bank — simple binary
'covered' tracking, deliberately separate from `concepts`' L0-L6 mastery
ladder (a different kind of claim: "I've been asked/practiced this",
not "I've mastered this topic")."""

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Question(Base):
    """One interview question — reference data, same shape as `problems`
    and `concepts`."""

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)
    order_index: Mapped[int] = mapped_column(Integer)


class QuestionCoverage(Base):
    """Row exists iff this user has marked the question covered — a
    toggle, not a history log (unlike problem_attempts/concept_attempts,
    there is no ladder here to preserve history for)."""

    __tablename__ = "question_coverage"
    __table_args__ = (UniqueConstraint("user_id", "question_id", name="uq_question_coverage_user_question"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    covered_at: Mapped[datetime] = mapped_column()
