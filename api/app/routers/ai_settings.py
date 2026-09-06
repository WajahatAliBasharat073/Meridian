from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user_id
from app.groq_models import DEFAULT_MODEL_ID, GROQ_MODELS, is_known_model
from app.models.core import User
from app.schemas import AISettingsOut, AISettingsUpdate, GroqModelOut

router = APIRouter(prefix="/api/settings/ai", tags=["ai-settings"])


def _to_out(ai_settings: dict[str, Any]) -> AISettingsOut:
    enabled_ids = ai_settings.get("enabled_model_ids")
    if enabled_ids is None:
        enabled_ids = [m.id for m in GROQ_MODELS]  # all enabled by default
    active_model = ai_settings.get("active_model", DEFAULT_MODEL_ID)
    if active_model not in enabled_ids:
        active_model = enabled_ids[0] if enabled_ids else DEFAULT_MODEL_ID

    return AISettingsOut(
        api_key_set=bool(ai_settings.get("groq_api_key")),
        active_model=active_model,
        models=[
            GroqModelOut(id=m.id, label=m.label, description=m.description, enabled=m.id in enabled_ids)
            for m in GROQ_MODELS
        ],
    )


@router.get("", response_model=AISettingsOut)
async def get_ai_settings(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> AISettingsOut:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _to_out(user.settings.get("ai", {}))


@router.put("", response_model=AISettingsOut)
async def update_ai_settings(
    payload: AISettingsUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> AISettingsOut:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    ai_settings = dict(user.settings.get("ai", {}))

    if payload.enabled_model_ids is not None:
        unknown = [m for m in payload.enabled_model_ids if not is_known_model(m)]
        if unknown:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unknown model id(s): {unknown}"
            )
        if not payload.enabled_model_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="At least one model must stay enabled"
            )
        ai_settings["enabled_model_ids"] = payload.enabled_model_ids

    if payload.active_model is not None:
        if not is_known_model(payload.active_model):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unknown model id")
        enabled_now = ai_settings.get("enabled_model_ids", [m.id for m in GROQ_MODELS])
        if payload.active_model not in enabled_now:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Can't set an active model that's disabled",
            )
        ai_settings["active_model"] = payload.active_model

    if payload.api_key is not None:
        # Empty string clears it; a real value replaces it. Never echoed
        # back — only api_key_set (a boolean) is ever returned.
        if payload.api_key == "":
            ai_settings.pop("groq_api_key", None)
        else:
            ai_settings["groq_api_key"] = payload.api_key

    user.settings = {**user.settings, "ai": ai_settings}
    await session.commit()
    return _to_out(ai_settings)
