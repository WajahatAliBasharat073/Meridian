"""Life-track tables (design doc 5.4). Only table names and a one-line
nature are specified in the docs; columns below are a reasonable reading of
those descriptions (build prompt section 1's per-track summaries) and are
CRUD-only in this phase — no engine reads them yet. Flagged for the user to
confirm/adjust once the remaining-CRUD views (build prompt phase 6) are
built against them.
"""

import uuid
from datetime import date as date_
from typing import Any

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ThesisLog(Base):
    __tablename__ = "thesis_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    date: Mapped[date_] = mapped_column()
    milestone: Mapped[str | None] = mapped_column(String, nullable=True)
    work_summary: Mapped[str] = mapped_column(String)
    minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_type: Mapped[str | None] = mapped_column(String, nullable=True)
    deadline: Mapped[date_ | None] = mapped_column(nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)


class VocabWord(Base):
    __tablename__ = "vocab_words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    word: Mapped[str] = mapped_column(String)
    definition: Mapped[str] = mapped_column(String)
    example_sentence: Mapped[str | None] = mapped_column(String, nullable=True)
    date_introduced: Mapped[date_] = mapped_column()


class RecoveryLog(Base):
    __tablename__ = "recovery_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    date: Mapped[date_] = mapped_column(unique=False)
    sleep_hours: Mapped[float | None] = mapped_column(nullable=True)
    sleep_quality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    energy: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mood: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stress: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recovery_score: Mapped[float | None] = mapped_column(nullable=True)


class NutritionLog(Base):
    __tablename__ = "nutrition_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    date: Mapped[date_] = mapped_column()
    water_ml: Mapped[int | None] = mapped_column(Integer, nullable=True)
    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    protein_g: Mapped[float | None] = mapped_column(nullable=True)
    nutrition_score: Mapped[float | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)


class Meal(Base):
    """The rotating meal library."""

    __tablename__ = "meals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)
    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    protein_g: Mapped[float | None] = mapped_column(nullable=True)
    recipe_ref: Mapped[str | None] = mapped_column(String, nullable=True)


class MealPlan(Base):
    __tablename__ = "meal_plan"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    date: Mapped[date_] = mapped_column()
    slot: Mapped[str] = mapped_column(String)
    meal_id: Mapped[int] = mapped_column(ForeignKey("meals.id"))


class ReadingLog(Base):
    __tablename__ = "reading_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    date: Mapped[date_] = mapped_column()
    title: Mapped[str] = mapped_column(String)
    author: Mapped[str | None] = mapped_column(String, nullable=True)
    kind: Mapped[str] = mapped_column(String, default="book")
    progress_note: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)


class TimeLeak(Base):
    __tablename__ = "time_leaks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    date: Mapped[date_] = mapped_column()
    minutes: Mapped[int] = mapped_column(Integer)
    trigger: Mapped[str] = mapped_column(String, index=True)
    root_cause: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)


class Pattern(Base):
    """The 18 DSA patterns and their recognition cues — reference data,
    distinct from the behavioural pattern engine (design doc 6.4)."""

    __tablename__ = "patterns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    cues: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)


class OperatingRule(Base):
    """Reference: the Minimum Viable Day and other operating rules the
    bandwidth engine and UI defer to (build prompt section 9)."""

    __tablename__ = "operating_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String, unique=True)
    rule_text: Mapped[str] = mapped_column(String)
    category: Mapped[str | None] = mapped_column(String, nullable=True)


class Setting(Base):
    """Configurable operating parameters (e.g. `daily_review_cap`,
    design doc 6.2) — distinct from `users.settings`, which holds
    per-user UI/account preferences."""

    __tablename__ = "settings"
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_settings_user_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    key: Mapped[str] = mapped_column(String)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB)
