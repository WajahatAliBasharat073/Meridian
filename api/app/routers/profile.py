from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.models.core import User
from app.schemas import ProfileOut, ProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
async def get_profile(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ProfileOut:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return ProfileOut(
        birth_date=user.settings.get("birth_date"),
        life_expectancy_years=user.settings.get("life_expectancy_years"),
    )


@router.put("", response_model=ProfileOut)
async def update_profile(
    payload: ProfileUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> ProfileOut:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.settings = {
        **user.settings,
        "birth_date": payload.birth_date.isoformat(),
        "life_expectancy_years": payload.life_expectancy_years,
    }
    await session.commit()
    return ProfileOut(birth_date=payload.birth_date, life_expectancy_years=payload.life_expectancy_years)
