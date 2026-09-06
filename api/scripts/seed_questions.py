"""Loads the ML/GenAI/Agentic/Production interview question bank
(scripts/questions_data.py) into `questions`. Safe to re-run: refuses if
any coverage rows already exist (would mean deleting real progress),
otherwise wipes and reinserts.

Usage:
    python -m scripts.seed_questions [--force]
"""

from __future__ import annotations

import argparse
import asyncio

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal
from app.models.questions import Question, QuestionCoverage
from scripts.questions_data import QUESTIONS


async def _guard_against_real_coverage(session: AsyncSession, force: bool) -> None:
    existing = (await session.execute(select(QuestionCoverage.id).limit(1))).first()
    if existing and not force:
        raise SystemExit(
            "Refusing to reseed: question_coverage already has rows. "
            "Reseeding would delete real progress. Pass --force only if "
            "you are certain this is safe."
        )


async def seed(force: bool) -> None:
    async with SessionLocal() as session:
        await _guard_against_real_coverage(session, force)

        await session.execute(delete(QuestionCoverage))
        await session.execute(delete(Question))

        for category, title, source, order_index in QUESTIONS:
            session.add(Question(category=category, title=title, source=source, order_index=order_index))

        await session.commit()

    print(f"Seeded {len(QUESTIONS)} questions across "
          f"{len(set(q[0] for q in QUESTIONS))} categories.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="proceed even if real coverage exists")
    args = parser.parse_args()
    asyncio.run(seed(args.force))


if __name__ == "__main__":
    main()
