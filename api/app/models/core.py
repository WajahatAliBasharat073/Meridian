import uuid
from datetime import date as date_
from datetime import datetime, time
from typing import Any

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """Single user today, modelled properly so RLS and auth are not a
    retrofit later (design doc 2, G2/G7)."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True)
    # Plain JSON on other dialects, JSONB on Postgres — lets tests use
    # sqlite without losing JSONB in the real (Postgres-only) migration.
    settings: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"), default=dict
    )


class PrayerTimes(Base):
    """Computed once per date from solar position, cached (build prompt 2.5,
    design doc 6.1). Never fetched from an external API."""

    __tablename__ = "prayer_times"

    date: Mapped[date_] = mapped_column(Date, primary_key=True)
    fajr: Mapped[time] = mapped_column(Time)
    sunrise: Mapped[time] = mapped_column(Time)
    zuhr: Mapped[time] = mapped_column(Time)
    asr: Mapped[time] = mapped_column(Time)
    maghrib: Mapped[time] = mapped_column(Time)
    isha: Mapped[time] = mapped_column(Time)


class TimeBlock(Base):
    """The execution layer, and the ONLY store of task completion (build
    prompt 2.2). Every rollup, score and streak derives from `status` here —
    never a denormalised counter."""

    __tablename__ = "time_blocks"
    __table_args__ = (
        UniqueConstraint("user_id", "date", "seq", name="uq_time_blocks_user_date_seq"),
        CheckConstraint("tier IN ('T1','T2','T3','T4')", name="ck_time_blocks_tier"),
        CheckConstraint(
            "status IN ('DONE','NOT DONE','PARTIAL','RESCHEDULED')", name="ck_time_blocks_status"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    date: Mapped[date_] = mapped_column(Date, index=True)
    seq: Mapped[int] = mapped_column(Integer)

    # Absolute ('17:05') or prayer-relative ('maghrib+15m' / 'asr').
    start_spec: Mapped[str] = mapped_column(String)
    end_spec: Mapped[str] = mapped_column(String)
    # Materialised by the scheduling engine at write/recompute time so every
    # other query stays simple (design doc 5.1).
    start_resolved: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_resolved: Mapped[time | None] = mapped_column(Time, nullable=True)

    activity: Mapped[str] = mapped_column(String)
    tier: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)
    planned_minutes: Mapped[int] = mapped_column(Integer)

    status: Mapped[str] = mapped_column(String, default="NOT DONE")
    actual_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    energy_before: Mapped[int | None] = mapped_column(Integer, nullable=True)
    focus: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deep_work: Mapped[bool | None] = mapped_column(nullable=True)

    location: Mapped[str | None] = mapped_column(String, nullable=True)
    what_to_do: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
