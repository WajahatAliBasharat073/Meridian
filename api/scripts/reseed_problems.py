"""Replaces the seeded `problems` table with the real 270-problem set
(scripts/seed_data.py), without touching anything else in the database.

Scoped narrowly on purpose: unlike scripts/seed.py, this never wipes
`users` or any real per-user data (time blocks, recovery/nutrition logs,
etc.). It only deletes rows that exist *because of* the old problem set —
Problem, Curriculum, and any Review/ProblemAttempt rows that reference a
problem — then reinserts the real set. Refuses to run if a real user (any
user_id other than the dev stub) already has recorded attempts, since that
would mean deleting real history rather than synthetic seed data.

Usage:
    python -m scripts.reseed_problems [--force]
"""

from __future__ import annotations

import argparse
import asyncio

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal
from app.deps import STUB_USER_ID
from app.models.problems import Curriculum, Problem, ProblemAttempt
from app.models.repetition import Review
from scripts.seed_data import PROBLEMS


async def _guard_against_real_attempts(session: AsyncSession, force: bool) -> None:
    real_attempt = (
        await session.execute(
            select(ProblemAttempt.id).where(ProblemAttempt.user_id != STUB_USER_ID).limit(1)
        )
    ).first()
    if real_attempt and not force:
        raise SystemExit(
            "Refusing to reseed: a real user already has recorded problem "
            "attempts. Reseeding would delete that history. Pass --force "
            "only if you are certain this is safe."
        )


async def reseed(force: bool) -> None:
    async with SessionLocal() as session:
        await _guard_against_real_attempts(session, force)

        await session.execute(delete(Review).where(Review.subject_type == "problem"))
        await session.execute(delete(ProblemAttempt))
        await session.execute(delete(Curriculum))
        await session.execute(delete(Problem))

        for lc_number, title, slug, pattern, difficulty, is_nc150, is_b75 in PROBLEMS:
            session.add(
                Problem(
                    lc_number=lc_number,
                    title=title,
                    slug=slug,
                    url=f"https://leetcode.com/problems/{slug}/",
                    pattern=pattern,
                    difficulty=difficulty,
                    is_neetcode150=is_nc150,
                    is_blind75=is_b75,
                )
            )

        await session.commit()

    print(f"Reseeded {len(PROBLEMS)} problems. Curriculum scheduling left empty "
          f"pending the real xlsx importer.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="proceed even if a real user has attempts")
    args = parser.parse_args()
    asyncio.run(reseed(args.force))


if __name__ == "__main__":
    main()
