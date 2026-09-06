"""Generates a realistic 4-week development dataset (quality bar: "Seed
script producing a realistic 4-week dataset for development").

Deterministic — seeded RNG, same output every run — so it's diffable and
so a bug reproduces. Reviews are derived by actually calling the
repetition engine's `on_attempt` rather than hand-writing due dates, which
keeps the seed data consistent with the real ladder logic instead of a
second, divergent copy of it.

Refuses to run against a database that already has users in it unless
--force is passed — this is dev-only seed data, and DATABASE_URL may be
pointed at a real project.

Usage:
    python -m scripts.seed [--force] [--days N]
"""

from __future__ import annotations

import argparse
import asyncio
import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import SessionLocal
from app.deps import STUB_USER_ID
from app.domain import ReviewState
from app.engines.prayer import PrayerTimesResult, compute_prayer_times
from app.engines.repetition import on_attempt
from app.engines.scheduling import resolve_spec
from app.models.core import PrayerTimes, TimeBlock, User
from app.models.life import (
    Meal,
    MealPlan,
    NutritionLog,
    OperatingRule,
    Pattern,
    ReadingLog,
    RecoveryLog,
    ThesisLog,
    TimeLeak,
    VocabWord,
)
from app.models.problems import Curriculum, Problem, ProblemAttempt
from app.models.repetition import Review
from scripts.seed_data import OPERATING_RULES, PATTERNS, PROBLEMS

SEED = 20260906  # today's date as an arbitrary, memorable, fixed seed
DEFAULT_DAYS = 28
PAST_DAYS = 21  # window starts this many days before "today"

MASTERY_LEVELS = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]

VOCAB: list[tuple[str, str]] = [
    ("ubiquitous", "present, appearing, or found everywhere"),
    ("ephemeral", "lasting for a very short time"),
    ("pragmatic", "dealing with things sensibly and realistically"),
    ("meticulous", "showing great attention to detail; very careful and precise"),
    ("ambiguous", "open to more than one interpretation; not having one obvious meaning"),
    ("cogent", "clear, logical, and convincing"),
    ("terse", "sparing in the use of words; abrupt"),
    ("prudent", "acting with or showing care and thought for the future"),
    ("candid", "truthful and straightforward; frank"),
    ("resilient", "able to withstand or recover quickly from difficult conditions"),
    ("succinct", "briefly and clearly expressed"),
    ("arbitrary", "based on random choice rather than reason or system"),
    ("coherent", "logical and consistent"),
    ("empirical", "based on observation or experience rather than theory"),
    ("tenuous", "very weak or slight"),
    ("verbose", "using more words than needed"),
    ("robust", "strong and healthy; able to withstand adverse conditions"),
    ("nuanced", "characterized by subtle shades of meaning"),
    ("plausible", "seeming reasonable or probable"),
    ("redundant", "no longer needed; superfluous"),
]

MEALS: list[tuple[str, str, int, float]] = [
    ("Oatmeal with banana and peanut butter", "breakfast", 420, 14.0),
    ("Greek yogurt with mixed nuts and honey", "breakfast", 380, 22.0),
    ("Scrambled eggs with whole-wheat toast", "breakfast", 400, 24.0),
    ("Grilled chicken with rice and vegetables", "lunch", 620, 45.0),
    ("Lentil soup with whole-wheat bread", "lunch", 480, 24.0),
    ("Chickpea salad with olive oil and feta", "lunch", 520, 20.0),
    ("Grilled fish with roasted vegetables", "dinner", 550, 40.0),
    ("Beef and vegetable stir-fry with brown rice", "dinner", 600, 38.0),
    ("Vegetable and paneer curry with roti", "dinner", 580, 26.0),
    ("Mixed nuts and an apple", "snack", 220, 6.0),
    ("Greek yogurt", "snack", 150, 15.0),
]

READING: list[tuple[str, str, str]] = [
    ("Cracking the Coding Interview", "Gayle Laakmann McDowell", "book"),
    ("Designing Data-Intensive Applications", "Martin Kleppmann", "book"),
    ("Deep Work", "Cal Newport", "book"),
    ("Attention Is All You Need", "Vaswani et al.", "paper"),
]

TIME_LEAK_TRIGGERS = [
    "phone notifications",
    "context-switching between job and prep",
    "oversleeping after Isha",
    "doomscrolling",
    "unplanned social call",
]

THESIS_OUTPUT_TYPES = ["literature_review", "writing", "experiments", "analysis"]


@dataclass(frozen=True)
class BlockTemplate:
    seq: int
    start_spec: str
    end_spec: str
    activity: str
    tier: str
    category: str
    planned_minutes: int
    what_to_do: str


DAY_TEMPLATE: list[BlockTemplate] = [
    BlockTemplate(1, "fajr", "fajr+15m", "Fajr prayer", "T1", "Prayer", 15, "Pray Fajr"),
    BlockTemplate(2, "fajr+15m", "06:00", "Qur'an + quiet planning", "T2", "Recovery", 30, "Read, plan the day"),
    BlockTemplate(3, "06:00", "07:30", "DSA — new problem (deep work)", "T1", "InterviewPrep", 90, "Today's scheduled problem"),
    BlockTemplate(4, "07:30", "08:00", "Breakfast", "T3", "Nutrition", 30, "Eat, no screens"),
    BlockTemplate(5, "08:00", "08:15", "Vocabulary — 5 words", "T2", "English", 15, "Spaced-repetition vocab queue"),
    BlockTemplate(6, "08:15", "09:00", "Buffer", "T4", "Buffer", 45, "Commute / admin / slack"),
    BlockTemplate(7, "09:00", "12:00", "Job — deep work block", "T1", "Job", 180, "Primary work tasks"),
    BlockTemplate(8, "zuhr", "zuhr+15m", "Zuhr prayer", "T1", "Prayer", 15, "Pray Zuhr"),
    BlockTemplate(9, "zuhr+15m", "13:00", "Lunch", "T3", "Nutrition", 30, "Eat, no screens"),
    BlockTemplate(10, "13:00", "17:00", "Job — afternoon block", "T1", "Job", 240, "Primary work tasks"),
    BlockTemplate(11, "asr", "asr+15m", "Asr prayer", "T1", "Prayer", 15, "Pray Asr"),
    BlockTemplate(12, "asr+15m", "18:00", "Thesis", "T2", "Thesis", 45, "Work-log entry"),
    BlockTemplate(13, "maghrib", "maghrib+15m", "Maghrib prayer", "T1", "Prayer", 15, "Pray Maghrib"),
    BlockTemplate(14, "maghrib+15m", "19:00", "Dinner", "T3", "Nutrition", 30, "Eat, no screens"),
    BlockTemplate(15, "19:00", "19:45", "DSA — review queue", "T1", "InterviewPrep", 45, "Clear due/overdue reviews"),
    BlockTemplate(16, "19:45", "20:15", "Theory rotation", "T2", "InterviewPrep", 30, "ML/CS fundamentals topic"),
    BlockTemplate(17, "isha", "isha+15m", "Isha prayer", "T1", "Prayer", 15, "Pray Isha"),
    BlockTemplate(18, "isha+15m", "21:00", "Mock / system design", "T2", "InterviewPrep", 45, "Twice-weekly mock slot"),
    BlockTemplate(19, "21:00", "21:30", "Reading", "T3", "Reading", 30, "Book or paper log"),
    BlockTemplate(20, "21:30", "22:00", "Reviews — flashcards", "T2", "InterviewPrep", 30, "Vocab/ML-concept reviews"),
    BlockTemplate(21, "22:00", "22:30", "Wind-down", "T3", "Recovery", 30, "Recovery log, lights out prep"),
]


def _weighted_status(rng: random.Random, is_past: bool) -> str:
    if not is_past:
        return "NOT DONE"
    return rng.choices(
        ["DONE", "PARTIAL", "NOT DONE", "RESCHEDULED"],
        weights=[72, 14, 9, 5],
        k=1,
    )[0]


def _weighted_initial_level(rng: random.Random) -> str:
    return rng.choices(MASTERY_LEVELS, weights=[5, 15, 30, 25, 15, 7, 3], k=1)[0]


async def _guard_against_populated_db(session: AsyncSession, force: bool) -> None:
    existing = (await session.execute(select(User.id).limit(1))).first()
    if existing and not force:
        raise SystemExit(
            "Refusing to seed: `users` already has a row (this looks like a "
            "real database, not a fresh dev one). Pass --force to wipe and reseed anyway."
        )


async def _wipe(session: AsyncSession) -> None:
    for model in (
        MealPlan,
        Meal,
        ReadingLog,
        TimeLeak,
        ThesisLog,
        RecoveryLog,
        NutritionLog,
        VocabWord,
        Review,
        ProblemAttempt,
        Curriculum,
        Problem,
        TimeBlock,
        PrayerTimes,
        Pattern,
        OperatingRule,
        User,
    ):
        await session.execute(delete(model))
    await session.commit()


async def seed(days: int, force: bool) -> None:
    settings = get_settings()
    rng = random.Random(SEED)
    today = date.today()
    start = today - timedelta(days=PAST_DAYS)
    window = [start + timedelta(days=i) for i in range(days)]

    async with SessionLocal() as session:
        await _guard_against_populated_db(session, force)
        await _wipe(session)

        user = User(id=STUB_USER_ID, email="dev@meridian.local", settings={})
        session.add(user)

        for name, cues in PATTERNS:
            session.add(Pattern(name=name, cues=cues))
        for key, rule_text, category in OPERATING_RULES:
            session.add(OperatingRule(key=key, rule_text=rule_text, category=category))

        problems_by_pattern: dict[str, list[Problem]] = {}
        for lc_number, title, slug, pattern, difficulty, is_nc150, is_b75 in PROBLEMS:
            p = Problem(
                lc_number=lc_number,
                title=title,
                slug=slug,
                url=f"https://leetcode.com/problems/{slug}/",
                pattern=pattern,
                difficulty=difficulty,
                is_neetcode150=is_nc150,
                is_blind75=is_b75,
            )
            session.add(p)
            problems_by_pattern.setdefault(pattern, []).append(p)
        await session.flush()  # assign problem.id before referencing it

        for m_name, m_category, m_cal, m_protein in MEALS:
            session.add(Meal(name=m_name, category=m_category, calories=m_cal, protein_g=m_protein))
        await session.flush()
        meals_by_category: dict[str, list[Meal]] = {}
        for meal in (await session.execute(select(Meal))).scalars().all():
            meals_by_category.setdefault(meal.category, []).append(meal)

        prayer_cache: dict[date, PrayerTimesResult] = {}

        def prayer_times_for(d: date) -> PrayerTimesResult:
            if d not in prayer_cache:
                prayer_cache[d] = compute_prayer_times(
                    d, settings.latitude, settings.longitude, 5.0
                )
            return prayer_cache[d]

        all_problems = list(problems_by_pattern.values())
        flat_problems = [p for group in all_problems for p in group]
        scheduled_days = [d for d in window if d.weekday() < 6]  # skip Sunday
        curriculum_days = [d for d in scheduled_days if d <= today][: len(flat_problems)]

        vocab_i = 0
        for d in window:
            pt = prayer_times_for(d)
            row = PrayerTimes(
                date=d, fajr=pt.fajr, sunrise=pt.sunrise, zuhr=pt.zuhr,
                asr=pt.asr, maghrib=pt.maghrib, isha=pt.isha,
            )
            session.add(row)

            is_past = d < today
            is_today = d == today
            for tpl in DAY_TEMPLATE:
                start_r = resolve_spec(tpl.start_spec, pt, d)
                end_r = resolve_spec(tpl.end_spec, pt, d)
                status = _weighted_status(rng, is_past or (is_today and tpl.seq <= 12))
                actual = None
                energy = focus = None
                if status == "DONE":
                    actual = max(5, tpl.planned_minutes + rng.randint(-10, 15))
                    energy, focus = rng.randint(2, 5), rng.randint(2, 5)
                elif status == "PARTIAL":
                    actual = max(5, int(tpl.planned_minutes * rng.uniform(0.35, 0.7)))
                    energy, focus = rng.randint(1, 4), rng.randint(1, 4)
                session.add(
                    TimeBlock(
                        user_id=STUB_USER_ID, date=d, seq=tpl.seq,
                        start_spec=tpl.start_spec, end_spec=tpl.end_spec,
                        start_resolved=start_r, end_resolved=end_r,
                        activity=tpl.activity, tier=tpl.tier, category=tpl.category,
                        planned_minutes=tpl.planned_minutes, status=status,
                        actual_minutes=actual, energy_before=energy, focus=focus,
                        deep_work=tpl.tier == "T1", what_to_do=tpl.what_to_do,
                    )
                )

            for _ in range(5):
                word, definition = VOCAB[vocab_i % len(VOCAB)]
                session.add(
                    VocabWord(
                        user_id=STUB_USER_ID, word=word, definition=definition, date_introduced=d
                    )
                )
                vocab_i += 1

            if is_past or is_today:
                sleep_hours = round(rng.uniform(4.5, 8.0), 1)
                session.add(
                    RecoveryLog(
                        user_id=STUB_USER_ID, date=d, sleep_hours=sleep_hours,
                        sleep_quality=rng.randint(1, 5), energy=rng.randint(1, 5),
                        mood=rng.randint(1, 5), stress=rng.randint(1, 5),
                        recovery_score=round(min(sleep_hours / 8.0, 1.0) * 100, 1),
                    )
                )
                water_ml = rng.randint(1500, 3000)
                session.add(
                    NutritionLog(
                        user_id=STUB_USER_ID, date=d, water_ml=water_ml,
                        calories=rng.randint(1800, 2600), protein_g=round(rng.uniform(80, 150), 1),
                        nutrition_score=round(min(water_ml / 2500.0, 1.0) * 100, 1),
                    )
                )
                for slot in ("breakfast", "lunch", "dinner"):
                    pool = meals_by_category.get(slot, [])
                    if pool:
                        meal = pool[(d.toordinal() + hash(slot)) % len(pool)]
                        session.add(MealPlan(user_id=STUB_USER_ID, date=d, slot=slot, meal_id=meal.id))

                if d.day % 3 == 0:
                    session.add(
                        ThesisLog(
                            user_id=STUB_USER_ID, date=d,
                            work_summary=f"{rng.choice(THESIS_OUTPUT_TYPES).replace('_', ' ').title()} session",
                            minutes=rng.randint(30, 90),
                            output_type=rng.choice(THESIS_OUTPUT_TYPES),
                        )
                    )
                if d.day % 4 == 0:
                    title, author, kind = READING[d.day % len(READING)]
                    session.add(
                        ReadingLog(
                            user_id=STUB_USER_ID, date=d, title=title, author=author,
                            kind=kind, status="in_progress",
                        )
                    )
                if d.day % 3 == 1:
                    session.add(
                        TimeLeak(
                            user_id=STUB_USER_ID, date=d, minutes=rng.randint(15, 60),
                            trigger=rng.choice(TIME_LEAK_TRIGGERS),
                            root_cause="no trigger-specific mitigation in place yet",
                        )
                    )

        for i, d in enumerate(curriculum_days):
            problem = flat_problems[i]
            phase = "foundation" if i < 7 else "core"
            session.add(Curriculum(problem_id=problem.id, scheduled_date=d, slot=1, phase=phase))

            level = _weighted_initial_level(rng)
            attempted_at = datetime.combine(d, time(6, 30))
            session.add(
                ProblemAttempt(
                    user_id=STUB_USER_ID, problem_id=problem.id, attempted_at=attempted_at,
                    minutes=rng.randint(15, 45), mastery_level=level, hint_used=level in ("L0", "L1", "L2"),
                )
            )
            outcome = on_attempt(None, "problem", problem.id, level, d, engaged=True)
            cycles = 0
            while outcome is not None and outcome.due_date <= today and cycles < 5:
                next_level = rng.choices(
                    [outcome.new_level, _demote_one(outcome.new_level)], weights=[80, 20], k=1
                )[0]
                review_state = ReviewState(
                    subject_type="problem", subject_id=problem.id, due_date=outcome.due_date,
                    interval_days=outcome.interval_days, current_level=outcome.new_level,
                    overdue_days=0, last_result=outcome.last_result, streak_at_level=outcome.streak_at_level,
                )
                session.add(
                    ProblemAttempt(
                        user_id=STUB_USER_ID, problem_id=problem.id,
                        attempted_at=datetime.combine(outcome.due_date, time(6, 30)),
                        minutes=rng.randint(10, 30), mastery_level=next_level,
                    )
                )
                new_outcome = on_attempt(
                    review_state, "problem", problem.id, next_level, outcome.due_date, engaged=True
                )
                outcome = new_outcome
                cycles += 1

            if outcome is not None:
                overdue_days = max(0, (today - outcome.due_date).days)
                session.add(
                    Review(
                        user_id=STUB_USER_ID, subject_type="problem", subject_id=problem.id,
                        due_date=outcome.due_date, interval_days=outcome.interval_days,
                        overdue_days=overdue_days, last_result=outcome.last_result,
                    )
                )

        await session.commit()

    print(f"Seeded {len(window)} days ({window[0]} .. {window[-1]}), "
          f"{len(PROBLEMS)} problems, {len(curriculum_days)} with attempts/reviews.")


def _demote_one(level: str) -> str:
    idx = max(MASTERY_LEVELS.index(level) - 1, 0)
    return MASTERY_LEVELS[idx]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="wipe and reseed even if users already has rows")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="window size in days (default 28)")
    args = parser.parse_args()
    asyncio.run(seed(args.days, args.force))


if __name__ == "__main__":
    main()
