import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Observation(Base):
    """Output of the pattern engine (design doc 5.5, 6.4). The engine only
    proposes — `status` moves new -> accepted/dismissed/stale by user
    action or the 21-day staleness job, never by the engine itself."""

    __tablename__ = "observations"
    __table_args__ = (
        CheckConstraint(
            "confidence IN ('low','medium','high')", name="ck_observations_confidence"
        ),
        CheckConstraint(
            "status IN ('new','accepted','dismissed','stale')", name="ck_observations_status"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    detected_at: Mapped[datetime] = mapped_column(index=True)
    kind: Mapped[str] = mapped_column(String, index=True)
    subject: Mapped[str] = mapped_column(String)
    claim: Mapped[str] = mapped_column(String)
    sample_size: Mapped[int] = mapped_column(Integer)
    confidence: Mapped[str] = mapped_column(String)
    effect_size: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    suggested_action: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="new")
