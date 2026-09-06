from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_session
from app.deps import get_current_user_id
from app.repositories.problems import list_problems
from app.schemas import ProblemOut

router = APIRouter(prefix="/api/problems", tags=["problems"])


@router.get("", response_model=list[ProblemOut])
async def get_problems(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
    pattern: str | None = None,
    difficulty: str | None = None,
) -> list[ProblemOut]:
    today = datetime.now(ZoneInfo(settings.timezone)).date()
    rows = await list_problems(session, user_id, pattern=pattern, difficulty=difficulty)

    return [
        ProblemOut(
            problem_id=problem.id,
            lc_number=problem.lc_number,
            title=problem.title,
            slug=problem.slug,
            url=problem.url,
            pattern=problem.pattern,
            difficulty=problem.difficulty,
            is_neetcode150=problem.is_neetcode150,
            is_blind75=problem.is_blind75,
            current_mastery=mastery,
            is_scheduled_today=scheduled_date == today,
        )
        for problem, scheduled_date, mastery in rows
    ]
