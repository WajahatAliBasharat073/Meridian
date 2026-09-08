"""Daily vitals: the real backing store for the Health page.

`recovery_log` and `nutrition_log` existed from the first migration and had
no API for the whole life of the project, so the Health page invented its
own numbers and kept them in browser localStorage — 7.2 hours of sleep and
1250 ml of water that nobody had entered, per-browser, never reaching
Postgres. These endpoints replace that.

Two deliberate properties:

* **Patch, don't replace.** Each PUT writes only the fields it was sent, so
  logging sleep at 06:00 does not blank the stress rating from last night.
* **The score can be absent.** `recovery_score` is computed by
  app/engines/recovery.py and is null when too little was logged to say
  anything honest, rather than defaulting to a comfortable number.
"""

from __future__ import annotations

import uuid
from datetime import date as date_
from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_session
from app.deps import get_current_user_id
from app.engines.recovery import (
    WATER_TARGET_ML,
    VitalsFixture,
    compute_recovery_score,
    hydration_pct,
)
from app.repositories import life_logs as life_repo
from app.schemas import (
    NutritionUpdateIn,
    RecoveryUpdateIn,
    VitalsOut,
    WaterAddIn,
)

router = APIRouter(prefix="/api/vitals", tags=["vitals"])


def _today(settings: Settings) -> date_:
    return datetime.now(ZoneInfo(settings.timezone)).date()


async def _build_out(
    session: AsyncSession, user_id: uuid.UUID, on_date: date_
) -> VitalsOut:
    recovery = await life_repo.get_recovery_log(session, user_id, on_date)
    nutrition = await life_repo.get_nutrition_log(session, user_id, on_date)

    fixture = VitalsFixture(
        sleep_hours=recovery.sleep_hours if recovery else None,
        sleep_quality=recovery.sleep_quality if recovery else None,
        energy=recovery.energy if recovery else None,
        stress=recovery.stress if recovery else None,
        water_ml=nutrition.water_ml if nutrition else None,
        exercise_minutes=recovery.exercise_minutes if recovery else None,
    )
    scored = compute_recovery_score(fixture)

    return VitalsOut(
        date=on_date,
        sleep_hours=fixture.sleep_hours,
        sleep_quality=fixture.sleep_quality,
        energy=fixture.energy,
        mood=recovery.mood if recovery else None,
        stress=fixture.stress,
        exercise_minutes=fixture.exercise_minutes,
        water_ml=fixture.water_ml,
        calories=nutrition.calories if nutrition else None,
        protein_g=nutrition.protein_g if nutrition else None,
        recovery_score=scored.score,
        score_components=scored.components,
        missing=scored.missing,
        water_target_ml=WATER_TARGET_ML,
        hydration_pct=hydration_pct(fixture.water_ml),
        has_any_entry=recovery is not None or nutrition is not None,
    )


async def _persist_score(
    session: AsyncSession, user_id: uuid.UUID, on_date: date_, out: VitalsOut
) -> None:
    """Store the derived score alongside the inputs.

    Kept in the row so history can be read back without recomputing against
    whatever the weights happen to be later — and written as NULL when the
    engine declined to score, never as 0.
    """
    await life_repo.upsert_recovery_log(
        session, user_id, on_date, {"recovery_score": out.recovery_score}
    )


@router.get("/today", response_model=VitalsOut)
async def get_today_vitals(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> VitalsOut:
    return await _build_out(session, user_id, _today(settings))


@router.put("/recovery", response_model=VitalsOut)
async def update_recovery(
    payload: RecoveryUpdateIn,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> VitalsOut:
    on_date = payload.date or _today(settings)
    fields = payload.model_dump(exclude_unset=True, exclude={"date"})
    if fields:
        await life_repo.upsert_recovery_log(session, user_id, on_date, fields)
    out = await _build_out(session, user_id, on_date)
    await _persist_score(session, user_id, on_date, out)
    return out


@router.put("/nutrition", response_model=VitalsOut)
async def update_nutrition(
    payload: NutritionUpdateIn,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> VitalsOut:
    on_date = payload.date or _today(settings)
    fields = payload.model_dump(exclude_unset=True, exclude={"date"})
    if fields:
        await life_repo.upsert_nutrition_log(session, user_id, on_date, fields)
    out = await _build_out(session, user_id, on_date)
    await _persist_score(session, user_id, on_date, out)
    return out


@router.post("/water", response_model=VitalsOut)
async def add_water(
    payload: WaterAddIn,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> VitalsOut:
    """Add a glass. Additive, because the hydration reminder fires several
    times a day and each "Done" is another glass rather than a new total."""
    on_date = _today(settings)
    await life_repo.add_water(session, user_id, on_date, payload.ml)
    out = await _build_out(session, user_id, on_date)
    await _persist_score(session, user_id, on_date, out)
    return out
