"""Adapts `goals` / `time_budgets` / `daily_reflections` ORM rows."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.core import TimeBlock
from app.models.goals import DailyReflection, Goal, TimeBudget


async def list_goals(session: AsyncSession, user_id: uuid.UUID, status: str | None = None) -> list[Goal]:
    query = select(Goal).where(Goal.user_id == user_id)
    if status:
        query = query.where(Goal.status == status)
    query = query.order_by(Goal.created_at.desc())
    return list((await session.execute(query)).scalars().all())


async def create_goal(
    session: AsyncSession,
    user_id: uuid.UUID,
    title: str,
    description: str | None,
    category: str | None,
    target_date: date | None,
    finance_goal_id: int | None = None,
) -> Goal:
    goal = Goal(
        user_id=user_id,
        title=title,
        description=description,
        category=category,
        target_date=target_date,
        finance_goal_id=finance_goal_id,
    )
    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    return goal


async def update_goal(
    session: AsyncSession,
    user_id: uuid.UUID,
    goal_id: int,
    progress_pct: int | None,
    status: str | None,
    finance_goal_id: int | None = None,
) -> Goal | None:
    goal = await session.get(Goal, goal_id)
    if goal is None or goal.user_id != user_id:
        return None
    if progress_pct is not None:
        goal.progress_pct = progress_pct
    if status is not None:
        goal.status = status
    if finance_goal_id is not None:
        # 0 is never a real finance_goals.id (autoincrement starts at 1) --
        # used here as the explicit "clear the link" value, since None
        # already means "no change requested", matching progress_pct and
        # status above.
        goal.finance_goal_id = None if finance_goal_id == 0 else finance_goal_id
    await session.commit()
    await session.refresh(goal)
    return goal


async def minutes_logged_for_category(
    session: AsyncSession, user_id: uuid.UUID, category: str, since: date
) -> int:
    """Real, already-logged minutes for a category since a date — the
    read-only activity rollup shown beside a goal's self-reported
    progress, never blended into it."""
    result = await session.execute(
        select(TimeBlock.status, TimeBlock.planned_minutes, TimeBlock.actual_minutes).where(
            TimeBlock.user_id == user_id, TimeBlock.category == category, TimeBlock.date >= since
        )
    )
    total = 0
    for status, planned, actual in result.all():
        if status == "DONE":
            total += actual if actual is not None else planned
        elif status == "PARTIAL":
            total += actual if actual is not None else planned // 2
    return total


async def list_time_budgets(session: AsyncSession, user_id: uuid.UUID) -> list[TimeBudget]:
    result = await session.execute(
        select(TimeBudget).where(TimeBudget.user_id == user_id).order_by(TimeBudget.category)
    )
    return list(result.scalars().all())


async def upsert_time_budget(
    session: AsyncSession, user_id: uuid.UUID, category: str, minutes_per_week: int
) -> TimeBudget:
    existing = (
        await session.execute(
            select(TimeBudget).where(TimeBudget.user_id == user_id, TimeBudget.category == category)
        )
    ).scalar_one_or_none()
    if existing is None:
        existing = TimeBudget(user_id=user_id, category=category, minutes_per_week=minutes_per_week)
        session.add(existing)
    else:
        existing.minutes_per_week = minutes_per_week
    await session.commit()
    await session.refresh(existing)
    return existing


async def delete_time_budget(session: AsyncSession, user_id: uuid.UUID, budget_id: int) -> bool:
    budget = await session.get(TimeBudget, budget_id)
    if budget is None or budget.user_id != user_id:
        return False
    await session.delete(budget)
    await session.commit()
    return True


async def actual_minutes_by_category(
    session: AsyncSession, user_id: uuid.UUID, since: date
) -> dict[str, int]:
    result = await session.execute(
        select(TimeBlock.category, TimeBlock.status, TimeBlock.planned_minutes, TimeBlock.actual_minutes).where(
            TimeBlock.user_id == user_id, TimeBlock.date >= since
        )
    )
    totals: dict[str, int] = {}
    for category, status, planned, actual in result.all():
        if status == "DONE":
            totals[category] = totals.get(category, 0) + (actual if actual is not None else planned)
        elif status == "PARTIAL":
            totals[category] = totals.get(category, 0) + (actual if actual is not None else planned // 2)
    return totals


async def get_reflection(session: AsyncSession, user_id: uuid.UUID, on_date: date) -> DailyReflection | None:
    result = await session.execute(
        select(DailyReflection).where(DailyReflection.user_id == user_id, DailyReflection.date == on_date)
    )
    return result.scalar_one_or_none()


async def upsert_reflection(
    session: AsyncSession,
    user_id: uuid.UUID,
    on_date: date,
    mood: str,
    what_got_in_the_way: str | None,
    what_went_well: str | None,
) -> DailyReflection:
    existing = await get_reflection(session, user_id, on_date)
    if existing is None:
        existing = DailyReflection(user_id=user_id, date=on_date, mood=mood)
        session.add(existing)
    existing.mood = mood
    existing.what_got_in_the_way = what_got_in_the_way
    existing.what_went_well = what_went_well
    await session.commit()
    await session.refresh(existing)
    return existing


async def list_reflections_since(
    session: AsyncSession, user_id: uuid.UUID, since: date
) -> list[DailyReflection]:
    result = await session.execute(
        select(DailyReflection)
        .where(DailyReflection.user_id == user_id, DailyReflection.date >= since)
        .order_by(DailyReflection.date)
    )
    return list(result.scalars().all())


async def blocks_since(session: AsyncSession, user_id: uuid.UUID, since: date) -> list[TimeBlock]:
    result = await session.execute(
        select(TimeBlock)
        .where(TimeBlock.user_id == user_id, TimeBlock.date >= since)
        .order_by(TimeBlock.date, TimeBlock.seq)
    )
    return list(result.scalars().all())
