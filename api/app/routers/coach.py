"""Ask Meridian AI Executive Coach Router.
Provides real-time conversational intelligence powered by Groq and grounded
in Wajahat Ali Basharat's authentic schedule, thesis goals, MAANG curriculum,
operating rules, and recovery metrics.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from groq import Groq
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_session
from app.deps import get_current_user_id
from app.engines.coach import (
    CoachContext,
    CoachScheduleBlock,
    build_system_prompt,
    local_fallback_response,
)
from app.engines.finance import month_summary
from app.logging import get_logger
from app.models.core import User
from app.models.life import OperatingRule
from app.repositories import finance as finance_repo
from app.repositories import goals as goals_repo
from app.repositories import life_logs as life_logs_repo
from app.repositories import schedule as schedule_repo
from app.services import get_recommendations

log = get_logger(__name__)

router = APIRouter(prefix="/api/coach", tags=["coach"])


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    model: str | None = None


class ChatResponse(BaseModel):
    reply: str
    suggestions: list[str]
    model_used: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_coach(
    payload: ChatRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ChatResponse:
    now_dt = datetime.now(ZoneInfo(settings.timezone))
    today = now_dt.date()

    # 1. Fetch User Settings & Profile
    user = await session.get(User, user_id)
    # str(), because `settings` is untyped JSON and this value is later passed
    # somewhere that requires a real string.
    raw_name = (user.settings.get("full_name") or user.settings.get("name")) if user else None
    user_name = str(raw_name) if raw_name else "there"

    # 2. Fetch Today's Blocks
    prayer_times = await schedule_repo.get_or_compute_prayer_times(session, today, settings)
    blocks = await schedule_repo.get_blocks_for_date(session, user_id, today, prayer_times)

    # 3. Fetch Active Recommendations / Problems
    recs = await get_recommendations(session, user_id, today, max_results=3)
    # No invented fallback: the old version named Two Sum, Valid Anagram and
    # Contains Duplicate whenever the recommender had nothing, so the coach
    # confidently assigned problems that were never scheduled.
    rec_titles = [r.title for r in recs]

    # 4. Fetch Operating Rules — these are the user's own written policies,
    # and until now they were fetched and then thrown away while the prompt
    # asserted a hardcoded set instead.
    rules_res = await session.execute(select(OperatingRule).limit(20))
    rules = tuple(r.rule_text for r in rules_res.scalars().all())

    # 5. Active goals, today's recovery score, this month's finances --
    # same real-data-only rule as everything already fetched above.
    active_goals = await goals_repo.list_goals(session, user_id, status="active")
    recovery_log = await life_logs_repo.get_recovery_log(session, user_id, today)
    this_month = today.replace(day=1)
    transactions = await finance_repo.get_transaction_fixtures(session, user_id, since=this_month)
    finance_summary = month_summary(transactions, this_month) if transactions else None

    ctx = CoachContext(
        user_name=user_name,
        now=now_dt,
        timezone_label=settings.timezone,
        blocks=tuple(
            CoachScheduleBlock(
                start_resolved=b.start_resolved,
                start_spec=b.start_spec,
                end_resolved=b.end_resolved,
                end_spec=b.end_spec,
                activity=b.activity,
                tier=b.tier,
                category=b.category,
                status=b.status,
                planned_minutes=b.planned_minutes,
            )
            for b in blocks
        ),
        prayer_times=prayer_times,
        recommendation_titles=tuple(rec_titles),
        operating_rules=rules,
        active_goal_titles=tuple(g.title for g in active_goals),
        recovery_score=recovery_log.recovery_score if recovery_log else None,
        finance_income_this_month=finance_summary.income if finance_summary else None,
        finance_expenses_this_month=finance_summary.expenses if finance_summary else None,
        finance_savings_this_month=finance_summary.savings if finance_summary else None,
    )
    system_prompt = build_system_prompt(ctx)

    model_to_use = payload.model or settings.groq_model or "openai/gpt-oss-120b"
    groq_key = settings.groq_api_key

    reply_text = ""
    if groq_key:
        try:
            client = Groq(api_key=groq_key)
            # The SDK wants its own per-role param types; this is a plain
            # list of role/content dicts, which it accepts at runtime.
            messages: list[Any] = [{"role": "system", "content": system_prompt}]
            for h in payload.history[-6:]:
                messages.append({"role": h.role, "content": h.content})
            messages.append({"role": "user", "content": payload.message})

            resp = client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                max_tokens=1000,
                temperature=0.6,
            )
            reply_text = resp.choices[0].message.content or ""
        except Exception as exc:
            log.warning("coach_primary_model_failed", model=model_to_use, error=str(exc))
            # If primary model has an issue, try smaller fast fallback
            try:
                client = Groq(api_key=groq_key)
                resp = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": payload.message}],
                    max_tokens=800,
                    temperature=0.6,
                )
                reply_text = resp.choices[0].message.content or ""
                model_to_use = "openai/gpt-oss-20b"
            except Exception as exc:
                log.error("coach_fallback_model_failed", error=str(exc))
                reply_text = ""

    # Fallback to local heuristic intelligence if API key is missing or failed
    if not reply_text:
        reply_text = local_fallback_response(payload.message, ctx)

    # Dynamic suggestions based on context
    suggestions = [
        "What should I do right now?",
        "Break down Two Sum optimal approach",
        "How should I structure my thesis sprint?",
        "Show my Minimum Viable Day fallback",
    ]

    return ChatResponse(reply=reply_text, suggestions=suggestions, model_used=model_to_use)
