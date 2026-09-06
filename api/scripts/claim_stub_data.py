"""One-time migration: reassign every row seeded under the dev stub user
to a real Supabase Auth account, once one exists (i.e. after signing up
through the web login page).

Safe ordering, all in one transaction:
  1. Insert a `users` row for the real UID (copies the stub row's data).
  2. Repoint every user-scoped table's rows from stub -> real UID.
  3. Only then delete the stub `users` row — by then nothing references it,
     so this never violates a foreign key mid-migration.

Usage:
    python -m scripts.claim_stub_data you@example.com
"""

from __future__ import annotations

import argparse
import asyncio
import json

from sqlalchemy import text

from app.db import SessionLocal
from app.deps import STUB_USER_ID

# Same table list as alembic/versions/0002_enable_rls.py's USER_SCOPED_TABLES,
# minus "users" itself (handled separately — its id is the value being moved).
USER_SCOPED_TABLES = [
    "time_blocks",
    "mistakes",
    "problem_attempts",
    "reviews",
    "mocks",
    "thesis_log",
    "vocab_words",
    "recovery_log",
    "nutrition_log",
    "meal_plan",
    "reading_log",
    "time_leaks",
    "settings",
    "observations",
]


async def claim(email: str) -> None:
    async with SessionLocal() as session:
        result = await session.execute(
            text("SELECT id FROM auth.users WHERE email = :email"), {"email": email}
        )
        row = result.first()
        if row is None:
            raise SystemExit(f"No Supabase Auth user found for {email!r}. Sign up first.")
        real_uid = row[0]

        if str(real_uid) == str(STUB_USER_ID):
            raise SystemExit("That account already is the stub user — nothing to do.")

        stub_row = (
            await session.execute(
                text("SELECT email, settings FROM users WHERE id = :stub_id"),
                {"stub_id": str(STUB_USER_ID)},
            )
        ).first()
        if stub_row is None:
            raise SystemExit("No stub user row found — has this already been claimed?")

        await session.execute(
            text(
                "INSERT INTO users (id, email, settings) VALUES (:real_uid, :email, CAST(:settings AS jsonb)) "
                "ON CONFLICT (id) DO NOTHING"
            ),
            {
                "real_uid": str(real_uid),
                "email": stub_row.email,
                "settings": json.dumps(stub_row.settings),
            },
        )

        for table in USER_SCOPED_TABLES:
            await session.execute(
                text(f"UPDATE {table} SET user_id = :real_uid WHERE user_id = :stub_id"),
                {"real_uid": str(real_uid), "stub_id": str(STUB_USER_ID)},
            )

        await session.execute(text("DELETE FROM users WHERE id = :stub_id"), {"stub_id": str(STUB_USER_ID)})

        await session.commit()

    print(f"Reassigned all stub-owned data to {email} ({real_uid}).")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("email", help="Email of the real Supabase Auth account to claim the data")
    args = parser.parse_args()
    asyncio.run(claim(args.email))


if __name__ == "__main__":
    main()
