"""full interview curriculum: modules, question records, mastery ladder

Revision ID: 0010_interview_curriculum
Revises: 0009_attempt_notes
Create Date: 2026-09-07

The question bank started as (category, title, source, order_index) with a
binary "covered" toggle. That shape cannot express what an interview
curriculum actually needs: which module a question belongs to, how hard it
is, which seniority bar it targets, what the interviewer is testing, what
the follow-ups are, and — critically — *how confident we are that a company
actually asks it*.

Three structural additions:

1. `interview_modules` — the master map (A..AF). Modules are reference
   data with their own priority, so "prepare P0 modules first" is a query
   rather than a judgement call each time.

2. `questions` gains the full record: module, difficulty, seniority,
   priority, frequency, companies, evidence tier, what's being tested,
   answer dimensions, follow-ups, mistakes, signals, prerequisites.

   `evidence` is the load-bearing column. Values:
     reported     — a named source associates this question with a company
     common       — appears across multiple independent prep sources
     fundamental  — core knowledge; no company claim made or needed
     derived      — generated from a topic outline, not a reported question
   Nothing may claim a company without `evidence = 'reported'` AND a
   `source_url`. This is enforced by a check constraint, not convention,
   because "asked at Meta" is exactly the claim that gets fabricated.

3. `question_progress` replaces the binary toggle with the 0-7 mastery
   ladder (0 never seen -> 7 can teach it). Seeing a question is not
   knowing it, and the old schema could not tell those apart.

The old `question_coverage` table is dropped: it holds a strict subset of
what `question_progress` holds, and carrying both would let two different
answers to "have I covered this?" drift apart.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0010_interview_curriculum"
down_revision: str | None = "0009_attempt_notes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_JSON_LIST = postgresql.JSONB(astext_type=sa.Text())


def upgrade() -> None:
    op.create_table(
        "interview_modules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(), nullable=False, unique=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("priority", sa.String(), nullable=False),
        sa.Column("submodules", _JSON_LIST, nullable=False, server_default="[]"),
        sa.Column("target_seniority", _JSON_LIST, nullable=False, server_default="[]"),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.CheckConstraint("priority IN ('P0','P1','P2','P3')", name="ck_modules_priority"),
    )
    op.create_index("ix_interview_modules_code", "interview_modules", ["code"])

    for col, type_ in [
        ("module_code", sa.String()),
        ("submodule", sa.String()),
        ("concept", sa.String()),
        ("question_type", sa.String()),
        ("difficulty", sa.String()),
        ("seniority", sa.String()),
        ("priority", sa.String()),
        ("frequency", sa.String()),
        ("evidence", sa.String()),
        ("source_url", sa.String()),
        ("tests_for", sa.Text()),
        ("strong_signal", sa.Text()),
        ("weak_signal", sa.Text()),
    ]:
        op.add_column("questions", sa.Column(col, type_, nullable=True))

    for col in ["companies", "answer_dimensions", "follow_ups", "common_mistakes", "prerequisites", "related"]:
        op.add_column("questions", sa.Column(col, _JSON_LIST, nullable=False, server_default="[]"))

    op.create_check_constraint(
        "ck_questions_evidence",
        "questions",
        "evidence IS NULL OR evidence IN ('reported','common','fundamental','derived')",
    )
    op.create_check_constraint(
        "ck_questions_priority",
        "questions",
        "priority IS NULL OR priority IN ('P0','P1','P2','P3')",
    )
    op.create_check_constraint(
        "ck_questions_difficulty",
        "questions",
        "difficulty IS NULL OR difficulty IN ('beginner','intermediate','advanced','expert')",
    )
    op.create_check_constraint(
        "ck_questions_seniority",
        "questions",
        "seniority IS NULL OR seniority IN ('junior','mid','senior','staff','principal')",
    )
    op.create_check_constraint(
        "ck_questions_frequency",
        "questions",
        "frequency IS NULL OR frequency IN ('very_high','high','medium','low','unknown')",
    )
    # The anti-fabrication rule, in the database rather than in a comment:
    # a company attribution requires a reported-evidence tier and a URL that
    # can be checked.
    op.create_check_constraint(
        "ck_questions_company_claim_needs_evidence",
        "questions",
        "companies = '[]'::jsonb OR (evidence = 'reported' AND source_url IS NOT NULL)",
    )
    op.create_index("ix_questions_module_code", "questions", ["module_code"])
    op.create_index("ix_questions_priority", "questions", ["priority"])

    op.create_table(
        "question_progress",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("mastery", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("user_id", "question_id", name="uq_question_progress_user_question"),
        sa.CheckConstraint("mastery BETWEEN 0 AND 7", name="ck_question_progress_mastery"),
    )
    op.create_index("ix_question_progress_user_id", "question_progress", ["user_id"])
    op.create_index("ix_question_progress_question_id", "question_progress", ["question_id"])

    op.execute("ALTER TABLE question_progress ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY question_progress_owner ON question_progress "
        "USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid())"
    )

    op.drop_table("question_coverage")


def downgrade() -> None:
    op.create_table(
        "question_coverage",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("covered_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("user_id", "question_id", name="uq_question_coverage_user_question"),
    )
    op.drop_table("question_progress")

    op.drop_index("ix_questions_priority", table_name="questions")
    op.drop_index("ix_questions_module_code", table_name="questions")
    for name in [
        "ck_questions_company_claim_needs_evidence",
        "ck_questions_frequency",
        "ck_questions_seniority",
        "ck_questions_difficulty",
        "ck_questions_priority",
        "ck_questions_evidence",
    ]:
        op.drop_constraint(name, "questions", type_="check")
    for col in [
        "related", "prerequisites", "common_mistakes", "follow_ups", "answer_dimensions", "companies",
        "weak_signal", "strong_signal", "tests_for", "source_url", "evidence", "frequency",
        "seniority", "priority", "difficulty", "question_type", "concept", "submodule", "module_code",
    ]:
        op.drop_column("questions", col)

    op.drop_index("ix_interview_modules_code", table_name="interview_modules")
    op.drop_table("interview_modules")
