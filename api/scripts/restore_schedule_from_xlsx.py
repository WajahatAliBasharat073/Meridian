"""Restore `time_blocks` for future dates from the source workbook.

The workbook is the source of truth for the schedule; the database is a
materialised copy of it. This script rewrites that copy for every date
from today forward, so a bad transformation can always be undone without
touching the rest of the ingest (curriculum, meals, reading logs).

Two things it will not do:

* It never touches a date before today, and never a block that already
  has work recorded against it. Those are history.
* It never touches anything but `time_blocks`.

Usage:
    python -m scripts.restore_schedule_from_xlsx            # dry run
    python -m scripts.restore_schedule_from_xlsx --apply
"""

from __future__ import annotations

import asyncio
import sys
from collections import defaultdict
from datetime import date as date_
from datetime import datetime, time
from zoneinfo import ZoneInfo

import openpyxl
from sqlalchemy import delete, select

from app.config import get_settings
from app.db import SessionLocal
from app.models.core import TimeBlock, User
from app.models.sessions import FocusSession
from scripts.ingest_wajahat_os import (
    EXCEL_PATH,
    infer_category,
    parse_date,
    parse_time_obj,
    to_time_str,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def read_workbook_days(since: date_) -> dict[date_, list[dict[str, object]]]:
    wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True, data_only=True)
    sched = wb["Daily Schedule"]
    days: dict[date_, list[dict[str, object]]] = defaultdict(list)

    for row in sched.iter_rows(min_row=2, values_only=True):
        d = parse_date(row[0])
        if not d or d < since:
            continue
        start_str = to_time_str(row[2])
        end_str = to_time_str(row[3])
        if not start_str or not end_str:
            continue

        activity = str(row[4] or "").strip()
        tier = str(row[5] or "T2").strip()
        if tier not in ("T1", "T2", "T3", "T4"):
            tier = "T2"

        planned = row[6]
        if planned is None or str(planned).strip() in ("", "None"):
            a, b = parse_time_obj(start_str), parse_time_obj(end_str)
            planned = int(
                (
                    datetime.combine(date_(2000, 1, 1), b)
                    - datetime.combine(date_(2000, 1, 1), a)
                ).total_seconds()
                // 60
            )
            if planned < 0:
                planned += 24 * 60
        else:
            try:
                planned = int(float(planned))
            except (TypeError, ValueError):
                planned = 30

        notes = row[8]
        notes = str(notes).strip() if notes and str(notes).strip() != "None" else None
        category = infer_category(activity)

        days[d].append(
            {
                "start_spec": start_str,
                "end_spec": end_str,
                "start_resolved": parse_time_obj(start_str),
                "end_resolved": parse_time_obj(end_str),
                "activity": activity,
                "tier": tier,
                "category": category,
                "planned_minutes": planned,
                "notes": notes,
                "what_to_do": activity,
                "deep_work": tier in ("T1", "T2")
                and category in ("Job", "Thesis", "InterviewPrep"),
            }
        )

    for blocks in days.values():
        blocks.sort(key=lambda spec: str(spec["start_resolved"]))
    return days


async def main(apply: bool) -> None:
    settings = get_settings()
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    days = read_workbook_days(today)

    if not days:
        print("Workbook has no rows dated today or later.")
        return

    print(f"Workbook holds {len(days)} date(s) from {today}, "
          f"{sum(len(v) for v in days.values())} blocks.")
    sample = sorted(days)[0]
    print(f"\n{sample} ({len(days[sample])} blocks) as the workbook has it:")
    for spec in days[sample]:
        print(
            f"  {spec['start_spec']}-{spec['end_spec']}  {spec['planned_minutes']!s:>3}m  "
            f"{spec['tier']}  {str(spec['category']):<13} {str(spec['activity'])[:48]}"
        )

    if not apply:
        print("\nDry run. Re-run with --apply to restore.")
        return

    async with SessionLocal() as session:
        user_ids = [u.id for u in (await session.execute(select(User))).scalars().all()]
        # A block referenced by a focus session cannot be deleted (FK), and
        # should not be: the session is a record of real work against it.
        referenced = set(
            (await session.execute(select(FocusSession.block_id))).scalars().all()
        )
        deleted = inserted = protected = 0

        for d in sorted(days):
            for uid in user_ids:
                existing = list(
                    (
                        await session.execute(
                            select(TimeBlock).where(TimeBlock.user_id == uid, TimeBlock.date == d)
                        )
                    )
                    .scalars()
                    .all()
                )
                keep = [
                    b
                    for b in existing
                    if b.status != "NOT DONE" or b.actual_minutes or b.id in referenced
                ]
                protected += len(keep)
                drop = [b for b in existing if b not in keep]
                if drop:
                    await session.execute(
                        delete(TimeBlock).where(TimeBlock.id.in_([b.id for b in drop]))
                    )
                    deleted += len(drop)

                kept_starts = {b.start_resolved for b in keep}
                for i, spec in enumerate(days[d], 1):
                    # Don't reinstate a block whose slot is already held by
                    # preserved history.
                    if spec["start_resolved"] in kept_starts:
                        continue
                    session.add(
                        TimeBlock(
                            user_id=uid,
                            date=d,
                            seq=-(2000 + i),
                            status="NOT DONE",
                            **spec,
                        )
                    )
                    inserted += 1
                await session.flush()

                everything = list(
                    (
                        await session.execute(
                            select(TimeBlock).where(TimeBlock.user_id == uid, TimeBlock.date == d)
                        )
                    )
                    .scalars()
                    .all()
                )
                everything.sort(key=lambda row: (row.start_resolved or time(0, 0), row.id))
                for i, row in enumerate(everything, 1):
                    row.seq = -i
                await session.flush()
                for i, row in enumerate(everything, 1):
                    row.seq = i
                await session.flush()

        await session.commit()
        print(f"\nRestored {len(days)} date(s): deleted {deleted}, inserted {inserted}.")
        print(f"Preserved {protected} block(s) with recorded work.")


if __name__ == "__main__":
    asyncio.run(main(apply="--apply" in sys.argv))
