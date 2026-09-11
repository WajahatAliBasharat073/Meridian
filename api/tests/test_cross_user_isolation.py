"""Cross-user isolation.

Every one of the other test files here is a pure engine unit test — none
of them touch the database, and none assert that user A cannot see user
B's data. RLS is bypassed by the API's own connection role
(0002_enable_rls.py's own docstring says so explicitly), so the
repository layer's `user_id` filtering is the *only* real enforcement
this app has — and, until this file, it was completely unverified by
anything but reading the code (SECURITY_AUDIT.md).

This is a representative sample across three repository modules
(goals.py, life_logs.py, questions.py) spanning four tables, not
literally every list/get endpoint in the app — the pattern (every query
filters by `user_id`) was confirmed identical across every router during
the audit, so a sample spanning multiple files gives real confidence
without an unbounded test-writing task.

Runs against the real configured database, the same as every engine that
already hits Postgres in this project — there is no separate test
database wired up yet. Creates two ephemeral users with random UUIDs and
deletes every row it creates, including the two user rows, whether the
test passes or fails.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from datetime import date

import pytest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal, engine
from app.models.core import User
from app.models.goals import Goal, TimeBudget
from app.models.life import ThesisLog
from app.models.questions import Question, QuestionProgress
from app.repositories import goals as goals_repo
from app.repositories import life_logs as life_logs_repo
from app.repositories import questions as questions_repo


@pytest.fixture
async def two_users() -> AsyncGenerator[tuple[AsyncSession, uuid.UUID, uuid.UUID], None]:
    session = SessionLocal()
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()
    session.add_all(
        [
            User(id=user_a, email=f"isolation-test-a-{user_a}@test.local", settings={}),
            User(id=user_b, email=f"isolation-test-b-{user_b}@test.local", settings={}),
        ]
    )
    await session.commit()
    try:
        yield session, user_a, user_b
    finally:
        # Child rows first -- users.id has no ON DELETE CASCADE, by design
        # (this schema is hard-delete-only and deliberate about it
        # everywhere, per DATA_MODEL_AUDIT.md).
        for model in (Goal, TimeBudget, ThesisLog, QuestionProgress):
            await session.execute(delete(model).where(model.user_id.in_([user_a, user_b])))
        await session.execute(delete(User).where(User.id.in_([user_a, user_b])))
        await session.commit()
        await session.close()
        # pytest-asyncio gives each test its own event loop by default;
        # app.db's engine/pool is a module-level singleton, so a pooled
        # connection opened under this test's loop must not survive into
        # the next test's (different) loop -- dispose it here, in the
        # loop it was actually used in, rather than let SQLAlchemy try to
        # close it later against a closed loop.
        await engine.dispose()


async def test_goals_are_isolated_per_user(
    two_users: tuple[AsyncSession, uuid.UUID, uuid.UUID],
) -> None:
    session, user_a, user_b = two_users
    await goals_repo.create_goal(session, user_a, "User A's private goal", None, None, None)
    await goals_repo.create_goal(session, user_b, "User B's private goal", None, None, None)

    a_titles = {g.title for g in await goals_repo.list_goals(session, user_a)}
    b_titles = {g.title for g in await goals_repo.list_goals(session, user_b)}

    assert "User A's private goal" in a_titles
    assert "User B's private goal" not in a_titles
    assert "User B's private goal" in b_titles
    assert "User A's private goal" not in b_titles


async def test_time_budgets_are_isolated_per_user(
    two_users: tuple[AsyncSession, uuid.UUID, uuid.UUID],
) -> None:
    session, user_a, user_b = two_users
    await goals_repo.upsert_time_budget(session, user_a, "Deep Work", 600)
    await goals_repo.upsert_time_budget(session, user_b, "Deep Work", 120)

    a_minutes = {b.minutes_per_week for b in await goals_repo.list_time_budgets(session, user_a)}
    b_minutes = {b.minutes_per_week for b in await goals_repo.list_time_budgets(session, user_b)}

    assert a_minutes == {600}
    assert b_minutes == {120}


async def test_thesis_logs_are_isolated_per_user(
    two_users: tuple[AsyncSession, uuid.UUID, uuid.UUID],
) -> None:
    session, user_a, user_b = two_users
    await life_logs_repo.create_thesis_log(
        session, user_a, date.today(), "User A's research summary", None, 30, None, None, None
    )
    await life_logs_repo.create_thesis_log(
        session, user_b, date.today(), "User B's research summary", None, 45, None, None, None
    )

    a_summaries = {log.work_summary for log in await life_logs_repo.list_thesis_logs(session, user_a)}
    b_summaries = {log.work_summary for log in await life_logs_repo.list_thesis_logs(session, user_b)}

    assert "User B's research summary" not in a_summaries
    assert "User A's research summary" not in b_summaries


async def test_question_progress_is_isolated_per_user(
    two_users: tuple[AsyncSession, uuid.UUID, uuid.UUID],
) -> None:
    session, user_a, user_b = two_users
    question_id = (await session.execute(select(Question.id).limit(1))).scalar_one()

    await questions_repo.set_learning_status(session, user_a, question_id, "struggled", None)

    rows_for_a = await questions_repo.list_questions(session, user_a)
    rows_for_b = await questions_repo.list_questions(session, user_b)

    progress_a = next(p for q, _mastery, p in rows_for_a if q.id == question_id)
    progress_b = next(p for q, _mastery, p in rows_for_b if q.id == question_id)

    assert progress_a is not None
    assert progress_a.learning_status == "struggled"
    assert progress_b is None
