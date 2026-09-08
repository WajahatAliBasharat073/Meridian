"""add reference_solution to questions

Revision ID: 0012_question_reference_solution
Revises: 0011_question_progress_timing
Create Date: 2026-09-08

Module B (ML Coding) was ingested from AIMLInterviews' summary *table*
only — title, difficulty, tags, interview focus. The 38 linked .py files
under src/MLC/problems/ that the table points to were never actually
read, so the bank never carried what a coding-interview record is
supposed to have: the real problem statement (each file's module
docstring, richer than the table's terse focus column) and an actual
reference implementation.

This column holds that implementation — MIT-licensed source, read and
stored for personal study, never redistributed (external/ is gitignored).
Nullable: only coding questions backed by a real source file get one; a
concept or system-design question has nothing to put here.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0012_question_reference_solution"
down_revision: str | None = "0011_question_progress_timing"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("reference_solution", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("questions", "reference_solution")
