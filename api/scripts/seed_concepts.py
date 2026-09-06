"""Loads the ML/GenAI/system-design roadmap (scripts/concepts_data.py)
into `concepts`. Safe to re-run: refuses if any real attempts already
exist (would mean deleting real history, not just reference data),
otherwise wipes and reinserts — same shape as scripts/reseed_problems.py.

Usage:
    python -m scripts.seed_concepts [--force]
"""

from __future__ import annotations

import argparse
import asyncio

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal
from app.models.concepts import Concept, ConceptAttempt
from scripts.concepts_data import CONCEPTS


async def _guard_against_real_attempts(session: AsyncSession, force: bool) -> None:
    existing = (await session.execute(select(ConceptAttempt.id).limit(1))).first()
    if existing and not force:
        raise SystemExit(
            "Refusing to reseed: concept_attempts already has rows. "
            "Reseeding would delete real history. Pass --force only if "
            "you are certain this is safe."
        )


async def seed(force: bool) -> None:
    async with SessionLocal() as session:
        await _guard_against_real_attempts(session, force)

        await session.execute(delete(ConceptAttempt))
        await session.execute(delete(Concept))

        for category, title, summary, resources, phase, order_index in CONCEPTS:
            session.add(
                Concept(
                    category=category,
                    title=title,
                    summary=summary,
                    resources=[{"label": label, "url": url} for label, url in resources],
                    phase=phase,
                    order_index=order_index,
                )
            )

        await session.commit()

    print(f"Seeded {len(CONCEPTS)} concepts across "
          f"{len(set(c[0] for c in CONCEPTS))} categories.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="proceed even if real attempts exist")
    args = parser.parse_args()
    asyncio.run(seed(args.force))


if __name__ == "__main__":
    main()
