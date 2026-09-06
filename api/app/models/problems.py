import uuid
from datetime import date as date_
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Problem(Base):
    """The seeded LeetCode curriculum — authoritative. Never invent a
    number, slug, url or company frequency (build prompt 2.3)."""

    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lc_number: Mapped[int] = mapped_column(Integer, unique=True)
    title: Mapped[str] = mapped_column(String)
    slug: Mapped[str] = mapped_column(String, unique=True)
    url: Mapped[str] = mapped_column(String)
    pattern: Mapped[str] = mapped_column(String, index=True)
    difficulty: Mapped[str] = mapped_column(String)
    is_neetcode150: Mapped[bool] = mapped_column(Boolean, default=False)
    is_blind75: Mapped[bool] = mapped_column(Boolean, default=False)

    # Netflix and OpenAI: no frequency data exists anywhere. NULL, never a
    # guessed value (design doc 5.2 / build prompt 2.3).
    freq_meta: Mapped[int | None] = mapped_column(Integer, nullable=True)
    freq_amazon: Mapped[int | None] = mapped_column(Integer, nullable=True)
    freq_google: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Curriculum(Base):
    """Pre-assigned schedule of problems, source of the SCHEDULED rank in
    the recommender (design doc 6.3)."""

    __tablename__ = "curriculum"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), index=True)
    scheduled_date: Mapped[date_] = mapped_column(Date, index=True)
    slot: Mapped[int] = mapped_column(Integer)
    phase: Mapped[str] = mapped_column(String)


class ProblemAttempt(Base):
    """One row per attempt, not per problem. Mastery is a property of the
    latest attempt — never a mutable column on `problems` — so history is
    preserved and the review engine is auditable (build prompt 4.2, design
    doc 5.2)."""

    __tablename__ = "problem_attempts"
    __table_args__ = (
        CheckConstraint("mastery_level ~ '^L[0-6]$'", name="ck_problem_attempts_mastery"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), index=True)
    attempted_at: Mapped[datetime] = mapped_column(index=True)
    minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mastery_level: Mapped[str] = mapped_column(String)
    hint_used: Mapped[bool] = mapped_column(Boolean, default=False)
    key_insight: Mapped[str | None] = mapped_column(String, nullable=True)
    mistake_id: Mapped[int | None] = mapped_column(ForeignKey("mistakes.id"), nullable=True)


CURRENT_MASTERY_VIEW_SQL = """
CREATE VIEW current_mastery AS
SELECT DISTINCT ON (user_id, problem_id) user_id, problem_id, mastery_level, attempted_at
FROM problem_attempts
ORDER BY user_id, problem_id, attempted_at DESC;
"""

CURRENT_MASTERY_VIEW_DROP_SQL = "DROP VIEW IF EXISTS current_mastery;"
