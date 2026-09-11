"""vocab_words: CEFR level + the remaining Notion-schema fields

Revision ID: 0028_vocab_oxford_fields
Revises: 0027_research_command_center
Create Date: 2026-09-11

The user's real Notion vocabulary tracker (screenshot, not fabricated)
has columns this app's vocab_words didn't yet have: a CEFR level
distinct from any generic category, synonyms, antonyms, word patterns/
collocations, a paraphrase, and a dictionary/video link. Added here to
match it, all nullable -- a real Oxford 5000 import fills in word +
part_of_speech + cefr_level from the source PDFs (they contain nothing
else), and the rest waits for the user to fill in, exactly like their
Notion ("a" is the only row with a real definition; everything else
says "Not started").

`definition` becomes nullable for the same reason -- a word imported
from a plain word list has no definition yet, and a required column
would force a fabricated placeholder into every row.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0028_vocab_oxford_fields"
down_revision: str | None = "0027_research_command_center"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("vocab_words", "definition", existing_type=sa.String(), nullable=True)

    op.add_column("vocab_words", sa.Column("cefr_level", sa.String(), nullable=True))
    op.add_column("vocab_words", sa.Column("synonyms", sa.Text(), nullable=True))
    op.add_column("vocab_words", sa.Column("antonyms", sa.Text(), nullable=True))
    op.add_column("vocab_words", sa.Column("word_patterns", sa.Text(), nullable=True))
    op.add_column("vocab_words", sa.Column("paraphrase", sa.Text(), nullable=True))
    op.add_column("vocab_words", sa.Column("dictionary_link", sa.String(), nullable=True))

    op.create_check_constraint(
        "ck_vocab_words_cefr_level",
        "vocab_words",
        "cefr_level IS NULL OR cefr_level IN ('A1','A2','B1','B2','C1','C2')",
    )
    op.create_index("ix_vocab_words_cefr_level", "vocab_words", ["cefr_level"])


def downgrade() -> None:
    op.drop_index("ix_vocab_words_cefr_level", table_name="vocab_words")
    op.drop_constraint("ck_vocab_words_cefr_level", "vocab_words", type_="check")
    for col in ("dictionary_link", "paraphrase", "word_patterns", "antonyms", "synonyms", "cefr_level"):
        op.drop_column("vocab_words", col)
    op.alter_column("vocab_words", "definition", existing_type=sa.String(), nullable=False)
