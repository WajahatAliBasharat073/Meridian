import uuid
from datetime import date as date_
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Problem(Base):
    """The seeded curriculum — authoritative. Never invent a number, slug,
    url or company frequency (build prompt 2.3)."""

    __tablename__ = "problems"
    __table_args__ = (
        CheckConstraint("source IN ('leetcode', 'classic')", name="ck_problems_source"),
        CheckConstraint("company_extra_count >= 0", name="ck_problems_company_extra"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Nullable: a classic algorithm (Dijkstra, KMP, Rat in a Maze) has no
    # LeetCode entry, and inventing a number for it is exactly what the
    # docstring above forbids. Postgres allows repeated NULLs under UNIQUE.
    lc_number: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    title: Mapped[str] = mapped_column(String)
    slug: Mapped[str] = mapped_column(String, unique=True)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    # Solving-technique axis (NeetCode taxonomy: arrays_hashing, dp_1d, …).
    pattern: Mapped[str] = mapped_column(String, index=True)
    # Data-structure axis, which is how a study plan is actually ordered.
    topic: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    difficulty: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String, default="leetcode")
    is_neetcode150: Mapped[bool] = mapped_column(Boolean, default=False)
    is_blind75: Mapped[bool] = mapped_column(Boolean, default=False)

    # Named companies from the source sheet, and its own "+N" truncation
    # kept as a count — nine unnamed companies is a fact; nine invented
    # names would not be.
    companies: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    company_extra_count: Mapped[int] = mapped_column(Integer, default=0)

    # Netflix and OpenAI: no frequency data exists anywhere. NULL, never a
    # guessed value (design doc 5.2 / build prompt 2.3).
    freq_meta: Mapped[int | None] = mapped_column(Integer, nullable=True)
    freq_amazon: Mapped[int | None] = mapped_column(Integer, nullable=True)
    freq_google: Mapped[int | None] = mapped_column(Integer, nullable=True)


class TopicVerificationAttempt(Base):
    """One attempt at proving a topic's structure is understood, so its
    problems unlock — build (implement the required operations) then defend
    (closed-book questions, some about the submitted code).

    One row per attempt rather than a mutable "verified" flag, matching
    `ProblemAttempt`: a failure, a re-verification and an override are all
    history worth keeping. See app/engines/topic_gate.py for the policy that
    reads these, and migration 0015 for why it is shaped this way.
    """

    __tablename__ = "topic_verification_attempts"
    __table_args__ = (
        CheckConstraint(
            "stage IN ('build', 'defend', 'passed', 'failed', 'abandoned', 'override')",
            name="ck_tva_stage",
        ),
        CheckConstraint(
            "build_score IS NULL OR (build_score >= 0 AND build_score <= 1)",
            name="ck_tva_build_score",
        ),
        CheckConstraint(
            "defend_score IS NULL OR (defend_score >= 0 AND defend_score <= 1)",
            name="ck_tva_defend_score",
        ),
        CheckConstraint("focus_losses >= 0", name="ck_tva_focus_losses"),
        CheckConstraint("focus_lost_seconds >= 0", name="ck_tva_focus_seconds"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    topic: Mapped[str] = mapped_column(String, index=True)
    started_at: Mapped[datetime] = mapped_column()
    stage: Mapped[str] = mapped_column(String, default="build")

    code_submission: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes_submission: Mapped[str | None] = mapped_column(Text, nullable=True)
    coverage: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    build_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    questions: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    answers: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    grades: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    defend_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    passed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # A browser cannot prevent tab switching, so this records rather than
    # promises: every focus loss during the closed-book stage, and for how
    # long, shown back on the result.
    focus_losses: Mapped[int] = mapped_column(Integer, default=0)
    focus_lost_seconds: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    override: Mapped[bool] = mapped_column(Boolean, default=False)
    override_reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class TopicLearningEntry(Base):
    """What you actually studied for a topic — sources, notes, code you keep,
    and requirements you add yourself.

    Feeds question generation so the closed-book stage lands on your real
    mental model instead of asking generically. A `source` row is a bookmark
    plus your own summary: nothing fetches the link (no transcript access
    exists), and the summary is what the questioner reads. See migration
    0017 and the guardrail in app/grading.py — these entries steer the
    questions but never bound them."""

    __tablename__ = "topic_learning_entries"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('source', 'note', 'snippet', 'requirement')", name="ck_tle_kind"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    topic: Mapped[str] = mapped_column(String, index=True)
    kind: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column()


class TopicGuide(Base):
    """"Learn the structure before you solve its problems" — one row per
    DSA topic, rendered above that topic's problem list.

    Exists because going straight at the problem list without knowing the
    structure is the failure mode this is meant to prevent: the problems
    get pattern-matched and forgotten instead of understood. `oop` is in
    here as a revision topic rather than a new one."""

    __tablename__ = "topic_guides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic: Mapped[str] = mapped_column(String, unique=True)
    display_name: Mapped[str] = mapped_column(String)
    seq: Mapped[int] = mapped_column(Integer, index=True)
    one_liner: Mapped[str] = mapped_column(Text)
    learn_first: Mapped[str] = mapped_column(Text)
    types: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    operations: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    must_know: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    pitfalls: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    # Reading (above) versus doing (here). The gate's checklist is its own
    # short, hand-picked list of demonstrable items — deriving it from
    # `types`/`operations` demanded things like "implement a static array".
    gate_requirements: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    needs_revision: Mapped[bool] = mapped_column(Boolean, default=False)


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
        CheckConstraint(
            "solve_method IS NULL OR solve_method IN ("
            "'independent','recalled_pattern','after_hint','after_editorial',"
            "'after_video','brute_force_only','not_solved')",
            name="ck_problem_attempts_solve_method",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), index=True)
    attempted_at: Mapped[datetime] = mapped_column(index=True)
    minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mastery_level: Mapped[str] = mapped_column(String)
    hint_used: Mapped[bool] = mapped_column(Boolean, default=False)

    # A second, independent axis from mastery_level. Mastery answers "how
    # well do I know this now"; solve_method answers "how much help did I
    # need this time". Tracking both is what makes "I need the editorial on
    # most DP problems" visible — one level alone can't show that.
    # Nullable: seeded/historical attempts predate this and are left
    # unknown rather than back-filled with a guess.
    solve_method: Mapped[str | None] = mapped_column(String, nullable=True)
    # Did the approach come from you, before consulting anything?
    understood_approach_independently: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    # Did the final solution reach the optimal complexity?
    reached_optimal: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Two different kinds of writing, deliberately kept apart:
    # key_insight is the one-line recall prompt the recommender shows when
    # this problem comes back for review, so it has to stay short; notes is
    # the long-form workings you want when you revisit the problem itself.
    key_insight: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    mistake_id: Mapped[int | None] = mapped_column(ForeignKey("mistakes.id"), nullable=True)


CURRENT_MASTERY_VIEW_SQL = """
CREATE VIEW current_mastery AS
SELECT DISTINCT ON (user_id, problem_id) user_id, problem_id, mastery_level, attempted_at
FROM problem_attempts
ORDER BY user_id, problem_id, attempted_at DESC;
"""

CURRENT_MASTERY_VIEW_DROP_SQL = "DROP VIEW IF EXISTS current_mastery;"
