"""Delete everything the user recorded *before* today, per "we are starting
from today".

Destructive and irreversible, so it is two-phase: run with no arguments to
see exactly what would go, and only `--apply` actually deletes. Curriculum,
problems, concepts and questions are the seeded catalogue, not recorded
history — they are never touched here.

Usage:
    python -m scripts.purge_before_today            # dry run, counts only
    python -m scripts.purge_before_today --apply
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy import text

from app.config import get_settings
from app.db import SessionLocal

# (label, table, the column that dates the row, whether that column is a
# timestamp rather than a date). Ordered children-first so foreign keys
# never block a delete. asyncpg is strict about the two types, hence the
# flag — a date bound against a timestamp column is a DataError, not a
# silent cast.
#
# focus_sessions is dated by started_at, not scheduled_start: the latter is
# a bare time-of-day copied off the block, so it can't place a row on a day.
TARGETS: list[tuple[str, str, str, bool]] = [
    ("focus session events", "focus_session_events", "occurred_at", True),
    ("focus sessions", "focus_sessions", "started_at", True),
    ("time blocks", "time_blocks", "date", False),
    ("daily reflections", "daily_reflections", "date", False),
    ("problem attempts", "problem_attempts", "attempted_at", True),
    ("concept attempts", "concept_attempts", "attempted_at", True),
    ("question attempts", "question_attempts", "attempted_at", True),
    ("reviews", "reviews", "due_date", False),
]


async def main(apply: bool) -> None:
    settings = get_settings()
    tz = ZoneInfo(settings.timezone)
    today = datetime.now(tz).date()
    # These timestamp columns are naive local time (the writers store
    # `datetime.now(...).replace(tzinfo=None)`), so the cutoff has to be a
    # naive local midnight too — an aware one is a type error to asyncpg,
    # and a UTC one would sit 5 hours off in Karachi.
    midnight = datetime.combine(today, time(0, 0))
    print(f"Today in {settings.timezone}: {today} (cutoff {midnight.isoformat()})\n")

    async with SessionLocal() as session:
        # Which of these tables exist at all — the schema has grown by
        # migration and a missing table shouldn't abort the purge.
        rows = await session.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
        )
        present = {r[0] for r in rows.fetchall()}

        plan: list[tuple[str, str, str, object, int]] = []
        for label, table, date_col, is_timestamp in TARGETS:
            if table not in present:
                print(f"  (skip) {label}: table {table} not present")
                continue
            cutoff: object = midnight if is_timestamp else today
            total = await session.scalar(text(f"SELECT count(*) FROM {table}"))
            stale = await session.scalar(
                text(f"SELECT count(*) FROM {table} WHERE {date_col} < :cutoff"),
                {"cutoff": cutoff},
            )
            print(f"  {label}: {stale} of {total} rows dated before today")
            if stale:
                plan.append((label, table, date_col, cutoff, int(stale)))

        if not plan:
            print("\nNothing dated before today. No changes needed.")
            return

        if not apply:
            print(f"\nDry run. Re-run with --apply to delete {sum(p[4] for p in plan)} rows.")
            return

        print()
        for label, table, date_col, cutoff, expected in plan:
            result = await session.execute(
                text(f"DELETE FROM {table} WHERE {date_col} < :cutoff"),
                {"cutoff": cutoff},
            )
            print(f"  deleted {result.rowcount} {label} (expected {expected})")

        await session.commit()

        print("\nRemaining, after commit:")
        for label, table, date_col, cutoff, _ in plan:
            left = await session.scalar(
                text(f"SELECT count(*) FROM {table} WHERE {date_col} < :cutoff"),
                {"cutoff": cutoff},
            )
            print(f"  {label}: {left} rows before today")


if __name__ == "__main__":
    asyncio.run(main(apply="--apply" in sys.argv))
