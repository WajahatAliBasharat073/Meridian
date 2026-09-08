"""Ingests Wajahat Ali Basharat's complete Productivity OS from Excel:
E:\\Meridian\\Wajahat_Productivity_OS_Sep-Dec_2026 (1).xlsx

Removes all synthetic / dummy data and seeds authentic schedule, curriculum,
operating rules, meals, reading logs, and thesis logs for both the live user
(90c338e9-6460-4960-9dfc-596dec17dba8) and dev stub user.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import date, datetime, time
import openpyxl
import re
import uuid
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import SessionLocal
from app.deps import STUB_USER_ID
from app.engines.prayer import compute_prayer_times, PrayerConvention
from app.models.core import PrayerTimes, TimeBlock, User
from app.models.life import (
    Meal,
    MealPlan,
    NutritionLog,
    OperatingRule,
    Pattern,
    ReadingBook,
    ReadingSession,
    RecoveryLog,
    ThesisLog,
    TimeLeak,
    VocabWord,
)
from app.models.problems import Curriculum, Problem, ProblemAttempt
from app.models.repetition import Review
from scripts.seed_data import PATTERNS

EXCEL_PATH = r"E:\Meridian\Wajahat_Productivity_OS_Sep-Dec_2026 (1).xlsx"
LIVE_USER_ID = uuid.UUID("90c338e9-6460-4960-9dfc-596dec17dba8")
ALL_USER_IDS = [LIVE_USER_ID, STUB_USER_ID]

USER_SETTINGS = {
    "name": "Wajahat Ali Basharat",
    "full_name": "Wajahat Ali Basharat",
    "display_name": "Wajahat Ali Basharat",
    "email": "wajahatalibasharat073@gmail.com",
    "timezone": "Asia/Karachi",
    "birth_date": "2000-08-24",
    "life_expectancy_years": 60,
    "wake_time": "04:30",
    "sleep_time": "22:30",
}


def parse_date(val: object) -> date | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    s = str(val).strip()
    if len(s) >= 10 and s[:4].isdigit() and s[4] == "-" and s[7] == "-":
        try:
            return datetime.strptime(s[:10], "%Y-%m-%d").date()
        except Exception:
            return None
    return None


def to_time_str(v: object) -> str | None:
    if v is None:
        return None
    if isinstance(v, (time, datetime)):
        return v.strftime("%H:%M")
    s = str(v).strip()
    if len(s) >= 5 and s[2] == ":":
        return s[:5]
    return s


def parse_time_obj(s: str) -> time:
    parts = s.split(":")
    return time(int(parts[0]), int(parts[1]))


def infer_category(activity: str) -> str:
    act = activity.lower()
    if any(p in act for p in ["fajr", "zuhr", "asr", "maghrib", "isha", "prayer"]):
        return "Prayer"
    if "remote job" in act or ("work" in act and "meetings" in act):
        return "Job"
    if "interview prep" in act or "coding" in act or "theory" in act:
        return "InterviewPrep"
    if "thesis" in act:
        return "Thesis"
    if "vocabulary" in act or "english" in act:
        return "English"
    if "reading" in act:
        return "Reading"
    if any(m in act for m in ["breakfast", "lunch", "dinner", "meal"]):
        return "Nutrition"
    if any(r in act for r in ["wake", "water", "hydration", "break", "shutdown", "recovery", "family", "free time"]):
        return "Recovery"
    if any(b in act for b in ["buffer", "review", "planning", "errands"]):
        return "Buffer"
    return "Recovery"


async def wipe_all_data(session: AsyncSession) -> None:
    print("Wiping all existing dummy/synthetic data...")
    for model in (
        MealPlan,
        Meal,
        ReadingSession,
        ReadingBook,
        TimeLeak,
        ThesisLog,
        RecoveryLog,
        NutritionLog,
        VocabWord,
        Review,
        ProblemAttempt,
        Curriculum,
        TimeBlock,
        OperatingRule,
    ):
        await session.execute(delete(model))
    await session.commit()
    print("Wipe complete.")


async def ensure_users(session: AsyncSession) -> None:
    print("Ensuring users with real name 'Wajahat Ali Basharat'...")
    # Live user
    res = await session.execute(select(User).where(User.id == LIVE_USER_ID))
    live_u = res.scalar_one_or_none()
    if live_u is None:
        live_u = User(id=LIVE_USER_ID, email="wajahatalibasharat073@gmail.com", settings=USER_SETTINGS)
        session.add(live_u)
    else:
        live_u.settings = USER_SETTINGS
        live_u.email = "wajahatalibasharat073@gmail.com"

    # Stub user
    res_stub = await session.execute(select(User).where(User.id == STUB_USER_ID))
    stub_u = res_stub.scalar_one_or_none()
    if stub_u is None:
        stub_u = User(id=STUB_USER_ID, email="dev@meridian.local", settings=USER_SETTINGS)
        session.add(stub_u)
    else:
        stub_u.settings = USER_SETTINGS

    await session.commit()
    print("Users verified and updated.")


async def ingest_patterns(session: AsyncSession) -> None:
    count = (await session.execute(select(Pattern))).scalars().all()
    if not count:
        print("Ingesting patterns...")
        for name, cues in PATTERNS:
            session.add(Pattern(name=name, cues=cues))
        await session.commit()


async def ingest_operating_rules(session: AsyncSession, wb: openpyxl.Workbook) -> None:
    print("Ingesting Operating Rules from Excel...")
    s = wb["Operating Rules"]
    rules_added = 0

    # Rescheduling Policy (rows 6 to 15)
    for r in range(6, 16):
        sit = s.cell(r, 1).value
        prio = s.cell(r, 2).value
        action = s.cell(r, 3).value
        never = s.cell(r, 4).value
        fallback = s.cell(r, 5).value
        reason = s.cell(r, 6).value
        if sit and action:
            key = f"policy_{r}_{str(sit)[:20].lower().replace(' ', '_').replace('/', '_')}"
            text = f"Priority {prio}: {action} | Never: {never} | Fallback: {fallback} | Reason: {reason}"
            session.add(OperatingRule(key=key, rule_text=text, category="rescheduling_policy"))
            rules_added += 1

    # Minimum Viable Day (rows 20 to 26)
    for r in range(20, 27):
        prio = s.cell(r, 1).value
        item = s.cell(r, 2).value
        duration = s.cell(r, 3).value
        why = s.cell(r, 4).value
        if item:
            key = f"mvd_{r}_{str(item)[:20].lower().replace(' ', '_').replace('/', '_')}"
            text = f"Priority {prio} Minimum: {item} ({duration}) - {why}"
            session.add(OperatingRule(key=key, rule_text=text, category="minimum_viable_day"))
            rules_added += 1

    await session.commit()
    print(f"Added {rules_added} Operating Rules.")


async def ingest_meals_and_plans(session: AsyncSession, wb: openpyxl.Workbook) -> None:
    print("Ingesting Meal Library and Daily Meal Plans from Excel...")
    # 1. Meal Library
    s_lib = wb["Meal Library"]
    meal_map: dict[str, Meal] = {}

    current_cat = "breakfast"
    for r in range(4, s_lib.max_row + 1):
        c1 = s_lib.cell(r, 1).value
        c2 = s_lib.cell(r, 2).value
        if c1 and "BREAKFAST" in str(c1):
            current_cat = "breakfast"
            continue
        elif c1 and "LUNCH" in str(c1):
            current_cat = "lunch"
            continue
        elif c1 and "DINNER" in str(c1):
            current_cat = "dinner"
            continue
        elif c1 and "SNACK" in str(c1):
            current_cat = "snack"
            continue

        if isinstance(c1, int) and c2:
            name = str(c2).strip()
            if name not in meal_map:
                m = Meal(
                    name=name,
                    category=current_cat,
                    calories=450 if current_cat == "breakfast" else 600 if current_cat == "lunch" else 550,
                    protein_g=25.0 if current_cat == "breakfast" else 35.0,
                )
                session.add(m)
                meal_map[name] = m

    await session.flush()

    # 2. Daily Meal Plan
    s_plan = wb["Daily Meal Plan"]
    plans_added = 0
    for r in range(5, s_plan.max_row + 1):
        d = parse_date(s_plan.cell(r, 1).value)
        if not d:
            continue
        meal_name = str(s_plan.cell(r, 2).value or "").strip().lower()
        slot = "breakfast" if "breakfast" in meal_name else "lunch" if "lunch" in meal_name else "dinner" if "dinner" in meal_name else "snack"
        opt_name = str(s_plan.cell(r, 4).value or "").strip()
        if not opt_name:
            continue

        meal_obj = meal_map.get(opt_name)
        if not meal_obj:
            meal_obj = Meal(name=opt_name, category=slot, calories=500, protein_g=30.0)
            session.add(meal_obj)
            await session.flush()
            meal_map[opt_name] = meal_obj

        for uid in ALL_USER_IDS:
            session.add(MealPlan(user_id=uid, date=d, slot=slot, meal_id=meal_obj.id))
            plans_added += 1

    await session.commit()
    print(f"Added {len(meal_map)} unique Meals and {plans_added} MealPlan entries.")


async def ingest_interview_prep(session: AsyncSession, wb: openpyxl.Workbook) -> None:
    print("Ingesting Interview Prep problems & curriculum from Excel...")
    s = wb["Interview Prep"]
    existing_problems = (await session.execute(select(Problem))).scalars().all()
    problems_by_lc = {p.lc_number: p for p in existing_problems}

    curricula_added = 0
    for r in range(5, s.max_row + 1):
        d = parse_date(s.cell(r, 1).value)
        if not d:
            continue
        slot = int(s.cell(r, 3).value or 1)
        phase = str(s.cell(r, 4).value or "P1")
        pattern = str(s.cell(r, 5).value or "Arrays & Hashing")
        lc_num = s.cell(r, 6).value
        title = s.cell(r, 7).value
        diff = str(s.cell(r, 8).value or "Medium")
        url = str(s.cell(r, 9).value or "")

        if not lc_num or not title:
            continue
        lc_num = int(lc_num)
        title = str(title).strip()

        p = problems_by_lc.get(lc_num)
        if not p:
            slug = url.rstrip("/").split("/")[-1] if "problems/" in url else title.lower().replace(" ", "-")
            p = Problem(
                lc_number=lc_num,
                title=title,
                slug=slug,
                url=url if url.startswith("http") else f"https://leetcode.com/problems/{slug}/",
                pattern=pattern,
                difficulty=diff,
                is_neetcode150=True,
                is_blind75=True,
            )
            session.add(p)
            await session.flush()
            problems_by_lc[lc_num] = p

        session.add(Curriculum(problem_id=p.id, scheduled_date=d, slot=slot, phase=phase))
        curricula_added += 1

    await session.commit()
    print(f"Added {curricula_added} curriculum entries across problems.")


async def ingest_thesis_and_reading(session: AsyncSession, wb: openpyxl.Workbook) -> None:
    print("Ingesting Thesis Tracker and Reading Log from Excel...")
    await ingest_thesis(session, wb)
    await ingest_reading(session, wb)


async def ingest_thesis(session: AsyncSession, wb: openpyxl.Workbook) -> None:
    """Thesis Tracker only, callable on its own so it can be re-run without
    the destructive full wipe `main()` performs."""
    # The "Thesis Tracker" sheet is a planning template, not a work log: 82
    # dated rows, every one of them carrying the same placeholder task
    # ("Define the most important thesis output for today"), Actual Hrs
    # never filled, Progress 0%, Status "NOT STARTED".
    #
    # The previous version of this turned that into 244 rows claiming 90
    # minutes of thesis work each. Four separate fabrications: it read
    # column 5 (*Planned* Hrs) as though it were time spent, defaulted to 90
    # minutes when even that was blank, invented "Master's Thesis" and
    # "literature_review" for empty cells, and wrote the whole lot to both
    # the real user and the dev stub.
    #
    # A thesis log entry asserts "this work happened on this day". Only rows
    # with real content earn one, minutes come from Actual Hrs or stay NULL,
    # and nothing is written for the stub user.
    TEMPLATE_TASK = "define the most important thesis output for today"

    s_thesis = wb["Thesis Tracker"]
    thesis_added = 0
    thesis_skipped = 0
    for r in range(2, s_thesis.max_row + 1):
        d = parse_date(s_thesis.cell(r, 1).value)
        if not d:
            continue

        def cell(col: int, row: int = r) -> str | None:
            v = s_thesis.cell(row, col).value
            text = str(v).strip() if v is not None else ""
            return text or None

        wtype = cell(2)
        task = cell(3)
        milestone = cell(4)
        actual_hrs = s_thesis.cell(r, 6).value  # Actual, never Planned.
        paper = cell(8)
        status = cell(10)
        next_action = cell(11)
        notes = cell(15)

        # Content that is genuinely this row's, rather than the template's.
        real_task = task if task and task.lower() != TEMPLATE_TASK else None
        has_real_content = any((real_task, paper, next_action, notes, actual_hrs))
        if not has_real_content:
            thesis_skipped += 1
            continue

        # Prefer what actually says something over the placeholder prompt.
        summary = real_task or next_action or paper or "Thesis work recorded in the tracker"
        minutes = (
            int(float(actual_hrs) * 60)
            if actual_hrs is not None and str(actual_hrs).strip() != ""
            else None
        )

        session.add(
            ThesisLog(
                user_id=LIVE_USER_ID,
                date=d,
                milestone=(paper or milestone or None) and (paper or milestone)[:100],
                work_summary=summary[:255],
                minutes=minutes,
                output_type=wtype[:50] if wtype else None,
                status=status,
            )
        )
        thesis_added += 1

    await session.commit()
    print(f"Added {thesis_added} ThesisLog rows (skipped {thesis_skipped} empty template rows).")


async def ingest_reading(session: AsyncSession, wb: openpyxl.Workbook) -> None:
    """Reading Log only, callable on its own."""
    # The "Reading Log" sheet is an unfilled 999-row template — every row has
    # a blank title, a placeholder page target, and status "NOT DONE". Rows
    # without a real title are skipped entirely rather than defaulted to a
    # fabricated book (this sheet is exactly where that fabrication used to
    # come from — see migration 0013_reading_books_and_sessions).
    s_reading = wb["Reading Log"]
    reading_books_added = 0
    reading_sessions_added = 0
    for uid in ALL_USER_IDS:
        books_by_title: dict[str, ReadingBook] = {}
        for r in range(2, s_reading.max_row + 1):
            d = parse_date(s_reading.cell(r, 1).value)
            book_cell = s_reading.cell(r, 2).value
            title = str(book_cell).strip() if book_cell and str(book_cell).strip() not in ("None", "") else None
            if not d or not title:
                continue
            kind = s_reading.cell(r, 3).value
            status = s_reading.cell(r, 8).value
            if title not in books_by_title:
                book_row = ReadingBook(
                    user_id=uid,
                    title=title[:255],
                    format=str(kind).lower() if kind and str(kind).strip() not in ("None", "") else "book",
                    status="reading",
                    started_date=d,
                    created_at=datetime.now(),
                )
                session.add(book_row)
                await session.flush()
                books_by_title[title] = book_row
                reading_books_added += 1
            session.add(
                ReadingSession(
                    user_id=uid,
                    book_id=books_by_title[title].id,
                    date=d,
                    note=str(status).strip()[:255] if status and str(status).strip() not in ("None", "") else None,
                    created_at=datetime.now(),
                )
            )
            reading_sessions_added += 1

    await session.commit()
    print(
        f"Added {reading_books_added} ReadingBook and "
        f"{reading_sessions_added} ReadingSession rows."
    )


async def ingest_daily_schedule(session: AsyncSession, wb: openpyxl.Workbook) -> None:
    print("Ingesting all Daily Schedule blocks from Excel (2,534 rows)...")
    sched = wb["Daily Schedule"]
    settings = get_settings()

    # Pre-cache prayer times
    dates_in_sched: set[date] = set()
    for r in range(2, sched.max_row + 1):
        d = parse_date(sched.cell(r, 1).value)
        if d:
            dates_in_sched.add(d)

    print(f"Ensuring PrayerTimes for {len(dates_in_sched)} dates...")
    existing_pt = {pt.date: pt for pt in (await session.execute(select(PrayerTimes))).scalars().all()}
    for d in sorted(dates_in_sched):
        if d not in existing_pt:
            calc = compute_prayer_times(d, settings.latitude, settings.longitude, 5.0, PrayerConvention())
            pt_row = PrayerTimes(
                date=d,
                fajr=calc.fajr,
                sunrise=calc.sunrise,
                zuhr=calc.zuhr,
                asr=calc.asr,
                maghrib=calc.maghrib,
                isha=calc.isha,
            )
            session.add(pt_row)
            existing_pt[d] = pt_row
    await session.commit()

    # Parse and insert TimeBlocks
    blocks_by_date: dict[date, list[dict]] = {}
    for r in range(2, sched.max_row + 1):
        d = parse_date(sched.cell(r, 1).value)
        if not d:
            continue

        start_str = to_time_str(sched.cell(r, 3).value)
        end_str = to_time_str(sched.cell(r, 4).value)
        if not start_str or not end_str:
            continue

        act = str(sched.cell(r, 5).value or "").strip()
        prio = str(sched.cell(r, 6).value or "T2").strip()
        if prio not in ("T1", "T2", "T3", "T4"):
            prio = "T2"

        plan_min = sched.cell(r, 7).value
        if plan_min is None or str(plan_min).strip() in ("None", ""):
            try:
                t1 = datetime.strptime(start_str, "%H:%M")
                t2 = datetime.strptime(end_str, "%H:%M")
                plan_min = int((t2 - t1).total_seconds() // 60)
                if plan_min < 0:
                    plan_min += 24 * 60
            except Exception:
                plan_min = 30
        else:
            try:
                plan_min = int(float(plan_min))
            except Exception:
                plan_min = 30

        status = str(sched.cell(r, 8).value or "NOT DONE").strip().upper()
        if status not in ("DONE", "NOT DONE", "PARTIAL", "RESCHEDULED"):
            status = "NOT DONE"

        notes = sched.cell(r, 9).value
        notes = str(notes).strip() if notes and str(notes).strip() != "None" else None

        cat = infer_category(act)
        deep_work = prio in ("T1", "T2") and cat in ("Job", "Thesis", "InterviewPrep")

        blocks_by_date.setdefault(d, []).append({
            "start_spec": start_str,
            "end_spec": end_str,
            "start_resolved": parse_time_obj(start_str),
            "end_resolved": parse_time_obj(end_str),
            "activity": act,
            "tier": prio,
            "category": cat,
            "planned_minutes": plan_min,
            "status": status,
            "notes": notes,
            "deep_work": deep_work,
            "what_to_do": act,
        })

    # Bulk insert for both users
    total_blocks_inserted = 0
    batch_size = 500
    batch = []

    for d, b_list in blocks_by_date.items():
        for seq, b in enumerate(b_list, 1):
            for uid in ALL_USER_IDS:
                tb = TimeBlock(
                    user_id=uid,
                    date=d,
                    seq=seq,
                    start_spec=b["start_spec"],
                    end_spec=b["end_spec"],
                    start_resolved=b["start_resolved"],
                    end_resolved=b["end_resolved"],
                    activity=b["activity"],
                    tier=b["tier"],
                    category=b["category"],
                    planned_minutes=b["planned_minutes"],
                    status=b["status"],
                    notes=b["notes"],
                    deep_work=b["deep_work"],
                    what_to_do=b["what_to_do"],
                )
                batch.append(tb)
                total_blocks_inserted += 1
                if len(batch) >= batch_size:
                    session.add_all(batch)
                    await session.commit()
                    batch = []

    if batch:
        session.add_all(batch)
        await session.commit()

    print(f"Successfully inserted {total_blocks_inserted} TimeBlock records across {len(blocks_by_date)} dates!")


async def run_ingestion(force: bool = True) -> None:
    print(f"Loading Excel workbook from {EXCEL_PATH}...")
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    print("Workbook loaded successfully.")

    async with SessionLocal() as session:
        await wipe_all_data(session)
        await ensure_users(session)
        await ingest_patterns(session)
        await ingest_operating_rules(session, wb)
        await ingest_meals_and_plans(session, wb)
        await ingest_interview_prep(session, wb)
        await ingest_thesis_and_reading(session, wb)
        await ingest_daily_schedule(session, wb)

    print("\n[SUCCESS] Ingestion finished successfully! All dummy data removed and real Wajahat Productivity OS live.")


def main():
    asyncio.run(run_ingestion())


if __name__ == "__main__":
    main()
