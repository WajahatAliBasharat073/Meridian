"""reading_books: priority, tags, quotes, why_reading, revisit_date

Revision ID: 0026_reading_books_enrichment
Revises: 0025_goal_finance_linkage
Create Date: 2026-09-11

Five additions, chosen against "don't add a field just because it's
possible" -- each maps to a real requested workflow, not a speculative one:

  priority      triage the to-read backlog ("High priority" view)
  tags          free-text, multi-value topic tagging beyond the single
                fixed `category` genre enum -- lets "by topic" be finer
                grained than the 9-value category list without a migration
                every time a new genre nuance shows up
  quotes        highlights/quotes are a different kind of note than a
                reading-session note (which is "what I did today") --
                kept as its own JSONB list of {text, page} objects
  why_reading   the stated reason for picking this book up -- distinct
                from `notes`, which accumulates over the read
  revisit_date  powers a "need to revisit" view without overloading
                `status`, which already means something else (reading
                progress state, not "worth a second look")

Explicitly not added: difficulty, language, source/location, a separate
"usefulness" rating -- `rating` + `notes` already give real expressive
room for a single-user, single-language personal reading log, and adding
columns nothing will read yet is exactly the kind of unnecessary tracking
the request itself asked to avoid.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0026_reading_books_enrichment"
down_revision: str | None = "0025_goal_finance_linkage"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_JSON = postgresql.JSONB(astext_type=sa.Text())


def upgrade() -> None:
    op.add_column("reading_books", sa.Column("priority", sa.String(), nullable=True))
    op.add_column(
        "reading_books", sa.Column("tags", _JSON, nullable=False, server_default="[]")
    )
    op.add_column(
        "reading_books", sa.Column("quotes", _JSON, nullable=False, server_default="[]")
    )
    op.add_column("reading_books", sa.Column("why_reading", sa.Text(), nullable=True))
    op.add_column("reading_books", sa.Column("revisit_date", sa.Date(), nullable=True))

    op.create_check_constraint(
        "ck_reading_books_priority",
        "reading_books",
        "priority IS NULL OR priority IN ('high','medium','low')",
    )
    op.create_index("ix_reading_books_priority", "reading_books", ["priority"])
    op.create_index("ix_reading_books_revisit_date", "reading_books", ["revisit_date"])


def downgrade() -> None:
    op.drop_index("ix_reading_books_revisit_date", table_name="reading_books")
    op.drop_index("ix_reading_books_priority", table_name="reading_books")
    op.drop_constraint("ck_reading_books_priority", "reading_books", type_="check")
    for col in ("revisit_date", "why_reading", "quotes", "tags", "priority"):
        op.drop_column("reading_books", col)
