"""vocab_words: word family, structured collocations, common mistake

Revision ID: 0030_vocab_family_collocations
Revises: 0029_vocab_notes
Create Date: 2026-09-15

Three fields from the vocabulary-mentor field review:

`word_family` (JSONB object, e.g. {"noun": "achievement", "verb": "achieve",
"adjective": "achievable"}) -- the single biggest vocabulary multiplier:
teaching one word's forms teaches 3-4 words for the price of one. Distinct
from `part_of_speech`, which is this row's own single form.

`collocations` (JSONB array of short phrases, e.g. ["achieve a goal",
"achieve success"]) -- natural word partnerships, structured so the UI can
render a bullet list or quiz on individual entries. This is deliberately a
*new* field rather than a repurposing of `word_patterns`: that column is
free text bundling Oxford's "Word Patterns and Collocations" export column
(grammar rules and collocations mixed together) and existing data/imports
depend on that shape. `collocations` is for cleaner, structured phrases
added going forward (manually, or a future importer), and the two are
free to coexist on the same row.

`common_mistake` (text) -- the specific, predictable error learners make
with this word (e.g. "achieve to" instead of "manage to"), not a generic
grammar note. Nullable and sparse by design: most words won't have one
worth recording.

All three are nullable, like every other enrichment field on this table --
imported rows commonly lack them, and a required value would force a
fabricated placeholder into thousands of existing rows.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0030_vocab_family_collocations"
down_revision: str | None = "0029_vocab_notes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "vocab_words",
        sa.Column("word_family", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "vocab_words",
        sa.Column("collocations", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column("vocab_words", sa.Column("common_mistake", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("vocab_words", "common_mistake")
    op.drop_column("vocab_words", "collocations")
    op.drop_column("vocab_words", "word_family")
