"""topic-wise DSA curriculum: guides, company tags, non-LeetCode classics

Revision ID: 0014_dsa_topics_and_guides
Revises: 0013_reading_books_and_sessions
Create Date: 2026-09-08

Three gaps this closes, all of them blocking the 34-day topic-wise sheet
from being represented honestly:

1. **`lc_number` and `url` were NOT NULL.** Roughly forty problems on the
   sheet are classic algorithms with no LeetCode entry at all — Dijkstra,
   Kruskal, Prim, Floyd-Warshall, Bellman-Ford, Kosaraju, KMP,
   Rabin-Karp, Morris traversal, Aggressive Cows, Rat in a Maze, MCM,
   Rod Cutting, Heap Sort. They have no number and no canonical URL, and
   the alternative to making these nullable is inventing one, which
   `Problem`'s own docstring forbids.

2. **No company tags.** The sheet carries them per problem, and the only
   company data the table had was three frequency integers (Meta,
   Amazon, Google). `companies` mirrors the column of the same name and
   type already on `questions`. `company_extra_count` records the
   sheet's own truncation ("Quikr, Snapdeal, Synopsys +9") as the number
   it is, rather than dropping the +9 or fabricating nine names.

3. **No topic axis and nowhere to put "learn the DS first".** `pattern`
   is the NeetCode taxonomy (arrays_hashing, dp_1d, …), which is a
   solving-technique axis, not the data-structure axis a study plan is
   organised by. `topic` adds that axis; `topic_guides` holds the
   understand-it-before-you-solve-it material for each one, because
   going straight at the problems without knowing the structure is the
   specific failure mode this is meant to prevent.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0014_dsa_topics_and_guides"
down_revision: str | None = "0013_reading_books_and_sessions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_JSON_LIST = postgresql.JSONB(astext_type=sa.Text())


def upgrade() -> None:
    # 1. A classic algorithm has no LeetCode number and no canonical URL.
    op.alter_column("problems", "lc_number", existing_type=sa.Integer(), nullable=True)
    op.alter_column("problems", "url", existing_type=sa.String(), nullable=True)

    op.add_column(
        "problems",
        sa.Column("source", sa.String(), nullable=False, server_default="leetcode"),
    )
    op.create_check_constraint(
        "ck_problems_source", "problems", "source IN ('leetcode', 'classic')"
    )

    # 2. Company tags, and the sheet's own "+N" truncation kept as a count.
    op.add_column(
        "problems", sa.Column("companies", _JSON_LIST, nullable=False, server_default="[]")
    )
    op.add_column(
        "problems",
        sa.Column("company_extra_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_check_constraint(
        "ck_problems_company_extra", "problems", "company_extra_count >= 0"
    )

    # 3. The data-structure axis, plus where the sheet places each problem.
    op.add_column("problems", sa.Column("topic", sa.String(), nullable=True))
    op.create_index("ix_problems_topic", "problems", ["topic"])
    op.add_column("problems", sa.Column("sheet_day", sa.Integer(), nullable=True))
    op.create_index("ix_problems_sheet_day", "problems", ["sheet_day"])

    op.create_table(
        "topic_guides",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("topic", sa.String(), nullable=False, unique=True),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("one_liner", sa.Text(), nullable=False),
        sa.Column("learn_first", sa.Text(), nullable=False),
        sa.Column("types", _JSON_LIST, nullable=False, server_default="[]"),
        sa.Column("operations", _JSON_LIST, nullable=False, server_default="[]"),
        sa.Column("must_know", _JSON_LIST, nullable=False, server_default="[]"),
        sa.Column("pitfalls", _JSON_LIST, nullable=False, server_default="[]"),
        # True for the OOP entry: revision, not first-time learning.
        sa.Column("needs_revision", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_topic_guides_seq", "topic_guides", ["seq"])

    # Reference content, not user data — readable by any authenticated
    # user, writable only by the ingest script's service role. Same shape
    # as `problems`/`questions`, which are reference tables too.
    op.execute("ALTER TABLE topic_guides ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY topic_guides_select_all ON topic_guides FOR SELECT "
        "TO authenticated USING (true)"
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS topic_guides_select_all ON topic_guides")
    op.drop_index("ix_topic_guides_seq", table_name="topic_guides")
    op.drop_table("topic_guides")

    op.drop_index("ix_problems_sheet_day", table_name="problems")
    op.drop_column("problems", "sheet_day")
    op.drop_index("ix_problems_topic", table_name="problems")
    op.drop_column("problems", "topic")

    op.drop_constraint("ck_problems_company_extra", "problems", type_="check")
    op.drop_column("problems", "company_extra_count")
    op.drop_column("problems", "companies")

    op.drop_constraint("ck_problems_source", "problems", type_="check")
    op.drop_column("problems", "source")

    # Rows added with no lc_number/url would violate the restored NOT NULL
    # constraints, so they go first — they only exist because this
    # migration allowed them.
    op.execute("DELETE FROM problems WHERE lc_number IS NULL OR url IS NULL")
    op.alter_column("problems", "url", existing_type=sa.String(), nullable=False)
    op.alter_column("problems", "lc_number", existing_type=sa.Integer(), nullable=False)
