"""vocab_words: freeform notes field

Revision ID: 0029_vocab_notes
Revises: 0028_vocab_oxford_fields
Create Date: 2026-09-11

A per-word blank space the user writes themselves while reviewing --
distinct from `paraphrase` (a rephrasing of the definition) and
`word_patterns` (collocations), which are both Oxford-sourced-content
fields. Nullable, like every other user-fillable field on this table.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0029_vocab_notes"
down_revision: str | None = "0028_vocab_oxford_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("vocab_words", sa.Column("notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("vocab_words", "notes")
