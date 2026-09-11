"""enrich vocab_words for a real vocabulary feature

Revision ID: 0024_vocab_words_enrichment
Revises: 0023_finance
Create Date: 2026-09-11

`vocab_words` existed with zero router/repository/frontend built on it --
dead schema from an earlier pass. This adds what a real vocabulary
learning flow needs: a four-value learning status (known/learning/
difficult/need_to_revisit -- one flat status, not a mastery-ladder split,
since there's nothing quantitative to keep separate from it here),
optional pronunciation/part_of_speech/category fields a Notion export may
carry, and an import-tracking pair (`source`, `notion_page_id`) so a
CSV re-import (scripts/import_vocab_csv.py -- no live Notion API access
exists for this project) never creates a duplicate row for the same
Notion entry.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0024_vocab_words_enrichment"
down_revision: str | None = "0023_finance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("vocab_words", sa.Column("pronunciation", sa.String(), nullable=True))
    op.add_column("vocab_words", sa.Column("part_of_speech", sa.String(), nullable=True))
    op.add_column("vocab_words", sa.Column("category", sa.String(), nullable=True))
    op.add_column("vocab_words", sa.Column("learning_status", sa.String(), nullable=True))
    op.add_column(
        "vocab_words", sa.Column("source", sa.String(), nullable=False, server_default="manual")
    )
    op.add_column("vocab_words", sa.Column("notion_page_id", sa.String(), nullable=True))
    op.add_column("vocab_words", sa.Column("last_synced_at", sa.DateTime(), nullable=True))

    op.create_index("ix_vocab_words_word", "vocab_words", ["word"])
    op.create_index("ix_vocab_words_category", "vocab_words", ["category"])
    op.create_index("ix_vocab_words_learning_status", "vocab_words", ["learning_status"])
    op.create_unique_constraint("uq_vocab_words_notion_page_id", "vocab_words", ["notion_page_id"])

    op.create_check_constraint(
        "ck_vocab_words_learning_status",
        "vocab_words",
        "learning_status IS NULL OR learning_status IN ('known','learning','difficult','need_to_revisit')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_vocab_words_learning_status", "vocab_words", type_="check")
    op.drop_constraint("uq_vocab_words_notion_page_id", "vocab_words", type_="unique")
    op.drop_index("ix_vocab_words_learning_status", table_name="vocab_words")
    op.drop_index("ix_vocab_words_category", table_name="vocab_words")
    op.drop_index("ix_vocab_words_word", table_name="vocab_words")

    for col in (
        "last_synced_at",
        "notion_page_id",
        "source",
        "learning_status",
        "category",
        "part_of_speech",
        "pronunciation",
    ):
        op.drop_column("vocab_words", col)
