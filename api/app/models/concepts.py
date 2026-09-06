"""ML/GenAI/system-design theory curriculum — the same shape as `problems`
(reference table + per-user attempts), reusing the spaced-repetition
engine that already treats `ml_concept` as one of its subject types
(design doc: `reviews.subject_type IN (..., 'ml_concept', ...)`)."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, CheckConstraint, ForeignKey, Integer, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Concept(Base):
    """One theory topic. `resources` is a real, curated reading/watch
    list — never a placeholder and never an invented URL (build prompt:
    never fabricate); an entry with no confidently-known URL just omits
    one rather than guessing."""

    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String)
    summary: Mapped[str] = mapped_column(String)
    resources: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql")
    )
    phase: Mapped[str] = mapped_column(String)
    order_index: Mapped[int] = mapped_column(Integer)


class ConceptAttempt(Base):
    """One row per self-rating, mirroring `problem_attempts` — mastery is
    a property of the latest attempt, never a mutable column on
    `concepts`, so the same repetition engine and ladder apply unchanged."""

    __tablename__ = "concept_attempts"
    __table_args__ = (
        CheckConstraint("mastery_level ~ '^L[0-6]$'", name="ck_concept_attempts_mastery"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"), index=True)
    attempted_at: Mapped[datetime] = mapped_column(index=True)
    mastery_level: Mapped[str] = mapped_column(String)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
