"""make daily vitals a real, one-row-per-day record; drop the dead sheet_day

Revision ID: 0018_vitals_upsert_and_exercise
Revises: 0017_topic_learning_log
Create Date: 2026-09-08

`recovery_log` and `nutrition_log` have existed since the first migration
and have never had an API. Meanwhile the Health page invented its own
vitals — 7.2 hours of sleep, 1250 ml of water, energy 4, stress 2, 30
minutes of exercise — hardcoded as defaults and kept in browser
localStorage, so the recovery score was computed from numbers nobody
entered, was different in every browser, and never reached Postgres. Same
class of fabrication as the reading and thesis logs.

Three changes to make these tables usable as the real backing store:

1. **`exercise_minutes` on `recovery_log`.** The page already tracked it and
   there was nowhere to put it.

2. **UNIQUE (user_id, date) on both.** Daily vitals are one row per day that
   gets edited through the day — water goes up, sleep is entered in the
   morning, energy in the evening. Without the constraint, an upsert races
   into duplicate rows and "today's water" becomes ambiguous.

3. **Drop `problems.sheet_day`.** Added in 0014 to record which day of the
   34-day sheet placed each problem, then made redundant when the plan
   became topic-wise and days were explicitly dropped. Nothing reads it; the
   source spreadsheet still has the information if it is ever wanted again.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0018_vitals_upsert_and_exercise"
down_revision: str | None = "0017_topic_learning_log"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("recovery_log", sa.Column("exercise_minutes", sa.Integer(), nullable=True))
    op.create_check_constraint(
        "ck_recovery_log_exercise", "recovery_log", "exercise_minutes IS NULL OR exercise_minutes >= 0"
    )

    # Collapse any pre-existing duplicates before the constraint lands.
    # Keeps the highest id per (user, date) — the most recently written.
    op.execute(
        """
        DELETE FROM recovery_log a USING recovery_log b
        WHERE a.user_id = b.user_id AND a.date = b.date AND a.id < b.id
        """
    )
    op.execute(
        """
        DELETE FROM nutrition_log a USING nutrition_log b
        WHERE a.user_id = b.user_id AND a.date = b.date AND a.id < b.id
        """
    )
    op.create_unique_constraint("uq_recovery_log_user_date", "recovery_log", ["user_id", "date"])
    op.create_unique_constraint("uq_nutrition_log_user_date", "nutrition_log", ["user_id", "date"])

    op.drop_index("ix_problems_sheet_day", table_name="problems")
    op.drop_column("problems", "sheet_day")


def downgrade() -> None:
    op.add_column("problems", sa.Column("sheet_day", sa.Integer(), nullable=True))
    op.create_index("ix_problems_sheet_day", "problems", ["sheet_day"])

    op.drop_constraint("uq_nutrition_log_user_date", "nutrition_log", type_="unique")
    op.drop_constraint("uq_recovery_log_user_date", "recovery_log", type_="unique")
    op.drop_constraint("ck_recovery_log_exercise", "recovery_log", type_="check")
    op.drop_column("recovery_log", "exercise_minutes")
