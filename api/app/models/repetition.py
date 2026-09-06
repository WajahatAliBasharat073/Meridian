import uuid
from datetime import date as date_

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Review(Base, TimestampMixin):
    """The spaced-repetition queue. Polymorphic on purpose: problems,
    vocabulary, ML concepts and mistakes all need the same engine
    (design doc 5.3, build prompt 5.1)."""

    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint(
            "subject_type IN ('problem','vocab','ml_concept','mistake')",
            name="ck_reviews_subject_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    subject_type: Mapped[str] = mapped_column(String)
    subject_id: Mapped[int] = mapped_column(Integer)
    due_date: Mapped[date_] = mapped_column(Date, index=True)
    interval_days: Mapped[int] = mapped_column(Integer)
    overdue_days: Mapped[int] = mapped_column(Integer, default=0)
    last_result: Mapped[str | None] = mapped_column(String, nullable=True)


class Mistake(Base):
    """`root_cause` is the field that matters — repeat detection groups on
    its normalised form; three occurrences flags CRITICAL (design doc 5.3)."""

    __tablename__ = "mistakes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    occurred_on: Mapped[date_] = mapped_column(Date)
    track: Mapped[str] = mapped_column(String)
    topic: Mapped[str] = mapped_column(String)
    what_went_wrong: Mapped[str] = mapped_column(String)
    root_cause: Mapped[str] = mapped_column(String, index=True)
    correct_thinking: Mapped[str | None] = mapped_column(String, nullable=True)
    memory_hook: Mapped[str | None] = mapped_column(String, nullable=True)
    redo_date: Mapped[date_ | None] = mapped_column(Date, nullable=True)
    redo_result: Mapped[str | None] = mapped_column(String, nullable=True)


class Mock(Base):
    __tablename__ = "mocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    date: Mapped[date_] = mapped_column(Date)
    company_mode: Mapped[str] = mapped_column(String)
    round_type: Mapped[str] = mapped_column(String)
    prompt: Mapped[str] = mapped_column(String)
    score_coding: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_ml: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_sysdesign: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_comms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    top_weakness: Mapped[str | None] = mapped_column(String, nullable=True)
    next_action: Mapped[str | None] = mapped_column(String, nullable=True)
