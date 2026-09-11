"""Life-track tables (design doc 5.4). Only table names and a one-line
nature are specified in the docs; columns below are a reasonable reading of
those descriptions (build prompt section 1's per-track summaries) and are
CRUD-only in this phase — no engine reads them yet. Flagged for the user to
confirm/adjust once the remaining-CRUD views (build prompt phase 6) are
built against them.
"""

import uuid
from datetime import date as date_
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    CheckConstraint,
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


VOCAB_LEARNING_STATUSES = ("known", "learning", "difficult", "need_to_revisit")


class VocabWord(Base):
    """English vocabulary, importable from a Notion export (no Notion API
    access exists for this project -- see scripts/import_vocab_csv.py) and
    manually addable. `notion_page_id` is the de-dup key for a re-import
    (a Notion page id is stable across exports); `word` is matched
    case-insensitively at the application layer for manual adds, since a
    single-user table this size doesn't need a DB-level expression index
    for it.

    `learning_status` is one of four values the user picks directly --
    unlike question_progress's mastery+status split, there is no separate
    quantitative ladder here to keep independent from it, so
    "need_to_revisit" is just a fourth status value, not a derived flag.
    """

    __tablename__ = "vocab_words"
    __table_args__ = (
        CheckConstraint(
            f"learning_status IS NULL OR learning_status IN {VOCAB_LEARNING_STATUSES!r}",
            name="ck_vocab_words_learning_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    word: Mapped[str] = mapped_column(String, index=True)
    # Nullable: a word list import supplies word + part_of_speech +
    # cefr_level and nothing else -- a required definition would force a
    # fabricated placeholder into every imported row.
    definition: Mapped[str | None] = mapped_column(String, nullable=True)
    example_sentence: Mapped[str | None] = mapped_column(String, nullable=True)
    pronunciation: Mapped[str | None] = mapped_column(String, nullable=True)
    part_of_speech: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    # CEFR level (A1-C2) -- distinct from `category`, which is a free-text
    # tag; this is the Oxford-list-sourced proficiency level shown as its
    # own column in the user's real Notion tracker.
    cefr_level: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    synonyms: Mapped[str | None] = mapped_column(Text, nullable=True)
    antonyms: Mapped[str | None] = mapped_column(Text, nullable=True)
    word_patterns: Mapped[str | None] = mapped_column(Text, nullable=True)
    paraphrase: Mapped[str | None] = mapped_column(Text, nullable=True)
    dictionary_link: Mapped[str | None] = mapped_column(String, nullable=True)
    # Freeform per-word notes the user writes themselves while reviewing --
    # distinct from `paraphrase` (a rephrasing of the definition) and
    # `word_patterns` (collocations); this is just a blank space for
    # whatever the user wants to remember about the word.
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_introduced: Mapped[date_] = mapped_column()
    learning_status: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    # "manual" | "notion_import" | "oxford_5000_import" -- which path
    # created this row.
    source: Mapped[str] = mapped_column(String, default="manual")
    # Stable Notion page id, only set for a Notion-imported row -- the
    # de-dup key a re-import matches against so re-running that importer
    # never creates a second row for the same Notion entry. An Oxford
    # 5000 import has no such id and dedups on (word, part_of_speech)
    # instead -- see scripts/import_oxford_5000.py.
    notion_page_id: Mapped[str | None] = mapped_column(String, nullable=True, unique=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(nullable=True)


class RecoveryLog(Base):
    """One row per day, edited through the day — see migration 0018 for why
    (user_id, date) is unique. Every measure is nullable because every
    measure is genuinely optional: sleep gets entered at 06:00 and stress
    may never get entered at all. `recovery_score` is derived by
    app/engines/recovery.py and is NULL when too little was logged to say
    anything honest."""

    __tablename__ = "recovery_log"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_recovery_log_user_date"),
        CheckConstraint(
            "exercise_minutes IS NULL OR exercise_minutes >= 0", name="ck_recovery_log_exercise"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    date: Mapped[date_] = mapped_column()
    sleep_hours: Mapped[float | None] = mapped_column(nullable=True)
    sleep_quality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    energy: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mood: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stress: Mapped[int | None] = mapped_column(Integer, nullable=True)
    exercise_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recovery_score: Mapped[float | None] = mapped_column(nullable=True)


class NutritionLog(Base):
    """One row per day, same shape as RecoveryLog — water accumulates
    through the day via the hydration reminder, so this is upserted rather
    than inserted."""

    __tablename__ = "nutrition_log"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_nutrition_log_user_date"),)

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


class ReadingBook(Base):
    """One book/paper/article being tracked — reference entity, same split
    as problems/problem_attempts: this row is what it *is*, `ReadingSession`
    rows are what actually happened on which days.

    Replaced a flat `reading_log` (one row per day, title copied onto every
    one) that had nowhere to put a cover, a page count, or a genre, and
    turned out to be entirely synthetic besides — see migration
    0013_reading_books_and_sessions.
    """

    __tablename__ = "reading_books"
    __table_args__ = (
        CheckConstraint("format IN ('book','paper','article','docs')", name="ck_reading_books_format"),
        CheckConstraint(
            "status IN ('to_read','reading','completed','paused','dropped')",
            name="ck_reading_books_status",
        ),
        CheckConstraint("rating IS NULL OR rating BETWEEN 1 AND 5", name="ck_reading_books_rating"),
        CheckConstraint("total_pages IS NULL OR total_pages > 0", name="ck_reading_books_total_pages"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String)
    author: Mapped[str | None] = mapped_column(String, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String, nullable=True)
    total_pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # book/paper/article/docs — what it is, not what it's about.
    format: Mapped[str] = mapped_column(String, default="book")
    # Genre, so a self-help title like "The 5 AM Club" or "The 7 Habits of
    # Highly Effective People" has somewhere to go alongside technical
    # reading — see READING_CATEGORIES in app/schemas.py for the full list.
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="reading")
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_date: Mapped[date_ | None] = mapped_column(nullable=True)
    finished_date: Mapped[date_ | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Triage for the to-read backlog -- distinct from `status` (a reading
    # progress state) and from `category` (a genre).
    priority: Mapped[str | None] = mapped_column(String, nullable=True)
    tags: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    # {text, page?} objects -- a highlight is a different kind of note
    # than a reading_session's "what I did today" note.
    quotes: Mapped[list[Any]] = mapped_column(JSONB, default=list)
    why_reading: Mapped[str | None] = mapped_column(Text, nullable=True)
    revisit_date: Mapped[date_ | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column()


class ReadingSession(Base):
    """One day's real progress on a book: the page you reached, not the
    pages you read that session — `page_reached` is a position, so percent
    complete (page_reached / book.total_pages) is always computable from
    whichever session is most recent, without summing anything."""

    __tablename__ = "reading_sessions"
    __table_args__ = (
        CheckConstraint("page_reached IS NULL OR page_reached >= 0", name="ck_reading_sessions_page"),
        CheckConstraint("minutes IS NULL OR minutes > 0", name="ck_reading_sessions_minutes"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("reading_books.id"), index=True)
    date: Mapped[date_] = mapped_column()
    page_reached: Mapped[int | None] = mapped_column(Integer, nullable=True)
    minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column()


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
    value: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB(), "postgresql"))
