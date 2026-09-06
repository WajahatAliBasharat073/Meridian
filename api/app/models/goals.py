"""Goals, time budgets and daily reflection — none of these compute a
number that could be mistaken for more precision than it has. Goal
progress is the user's own self-reported check-in, never an
auto-computed guess at "how done" something fuzzy is; the read-only
activity rollup (minutes actually logged against the goal's category)
sits alongside it, not blended into it."""

import uuid
from datetime import date as date_

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Goal(Base, TimestampMixin):
    __tablename__ = "goals"
    __table_args__ = (
        CheckConstraint("status IN ('active','completed','abandoned')", name="ck_goals_status"),
        CheckConstraint("progress_pct >= 0 AND progress_pct <= 100", name="ck_goals_progress_pct"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    # Loosely ties the goal to one time_blocks.category for the activity
    # rollup — free text, same as TimeBlock.category, so it never needs
    # its own enum migration when a new category appears.
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    target_date: Mapped[date_ | None] = mapped_column(nullable=True)
    progress_pct: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="active")


class TimeBudget(Base):
    """A weekly time allocation the user sets for one category — compared
    against actual logged minutes, never against a target the system
    invented."""

    __tablename__ = "time_budgets"
    __table_args__ = (UniqueConstraint("user_id", "category", name="uq_time_budgets_user_category"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    category: Mapped[str] = mapped_column(String)
    minutes_per_week: Mapped[int] = mapped_column(Integer)


class DailyReflection(Base):
    """One optional end-of-day check-in per date — never mandatory
    (build prompt: reflection must not be forced)."""

    __tablename__ = "daily_reflections"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_daily_reflections_user_date"),
        CheckConstraint(
            "mood IN ('difficult','normal','good','excellent')", name="ck_daily_reflections_mood"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    date: Mapped[date_] = mapped_column()
    mood: Mapped[str] = mapped_column(String)
    what_got_in_the_way: Mapped[str | None] = mapped_column(String, nullable=True)
    what_went_well: Mapped[str | None] = mapped_column(String, nullable=True)
