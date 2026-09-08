"""replace the flat reading_log with reading_books + reading_sessions

Revision ID: 0013_reading_books_and_sessions
Revises: 0012_question_reference_solution
Create Date: 2026-09-08

`reading_log` was one row per (user, day) with the book's title and author
copied onto every row — so tracking a single book for a week meant seven
duplicate rows, and there was nowhere to put a cover image, a page count,
or a genre. It also turned out to be entirely synthetic: the source
workbook's "Reading Log" sheet has a blank title on all 999 template rows,
and the ingester silently defaulted every blank to "Designing
Data-Intensive Applications" by Martin Kleppmann — i.e. every one of the
244 existing rows names a book the user never entered.

Replaced with the same reference-entity + attempt-log split used
elsewhere (problems/problem_attempts, questions/question_progress):

  reading_books     one row per book/paper you're tracking - cover,
                    author, genre, format, total pages, status, rating
  reading_sessions  one row per day you logged progress on it - the page
                    you reached, a note, minutes spent

Percent complete is `latest_session.page_reached / book.total_pages`,
computed at read time rather than stored, so it can never drift from the
sessions that actually justify it.

No data is migrated forward - `reading_log` is dropped outright, per the
above.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0013_reading_books_and_sessions"
down_revision: str | None = "0012_question_reference_solution"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_RLS_TABLES = ["reading_books", "reading_sessions"]


def upgrade() -> None:
    op.drop_table("reading_log")

    op.create_table(
        "reading_books",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("cover_url", sa.String(), nullable=True),
        sa.Column("total_pages", sa.Integer(), nullable=True),
        sa.Column("format", sa.String(), nullable=False, server_default="book"),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="reading"),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("started_date", sa.Date(), nullable=True),
        sa.Column("finished_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "format IN ('book','paper','article','docs')", name="ck_reading_books_format"
        ),
        sa.CheckConstraint(
            "status IN ('to_read','reading','completed','paused','dropped')",
            name="ck_reading_books_status",
        ),
        sa.CheckConstraint(
            "rating IS NULL OR rating BETWEEN 1 AND 5", name="ck_reading_books_rating"
        ),
        sa.CheckConstraint(
            "total_pages IS NULL OR total_pages > 0", name="ck_reading_books_total_pages"
        ),
    )

    op.create_table(
        "reading_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("reading_books.id"), nullable=False, index=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("page_reached", sa.Integer(), nullable=True),
        sa.Column("minutes", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "page_reached IS NULL OR page_reached >= 0", name="ck_reading_sessions_page"
        ),
        sa.CheckConstraint(
            "minutes IS NULL OR minutes > 0", name="ck_reading_sessions_minutes"
        ),
    )

    for table in _RLS_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY {table}_select_own ON {table} "
            f"FOR SELECT TO authenticated USING (user_id = auth.uid())"
        )
        op.execute(
            f"CREATE POLICY {table}_insert_own ON {table} "
            f"FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid())"
        )
        op.execute(
            f"CREATE POLICY {table}_update_own ON {table} "
            f"FOR UPDATE TO authenticated USING (user_id = auth.uid()) "
            f"WITH CHECK (user_id = auth.uid())"
        )
        op.execute(
            f"CREATE POLICY {table}_delete_own ON {table} "
            f"FOR DELETE TO authenticated USING (user_id = auth.uid())"
        )


def downgrade() -> None:
    op.drop_table("reading_sessions")
    op.drop_table("reading_books")

    op.create_table(
        "reading_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("kind", sa.String(), nullable=False, server_default="book"),
        sa.Column("progress_note", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
    )
