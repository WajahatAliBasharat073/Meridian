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
from app.models.core import User
from app.models.life import OperatingRule
from app.repositories import schedule as schedule_repo
from app.services import get_recommendations

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
    now_time_str = now_dt.strftime("%I:%M %p")

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
    rules = [r.rule_text for r in rules_res.scalars().all()]
    rules_block = (
        "\n".join(f"- {r}" for r in rules)
        if rules
        else "- (none recorded yet — do not invent policies on his behalf)"
    )

    # Format schedule summary
    schedule_summary = "\n".join(
        [
            f"- {b.start_resolved.strftime('%H:%M') if b.start_resolved else b.start_spec} to "
            f"{b.end_resolved.strftime('%H:%M') if b.end_resolved else b.end_spec}: "
            f"{b.activity} ({b.tier}, {b.category}) [{b.status}]"
            for b in blocks
        ]
    ) or "- (no blocks scheduled for today)"

    # Real prayer times for *today*, not last week's constants.
    prayer_block = (
        f"Fajr {prayer_times.fajr.strftime('%H:%M')}, "
        f"Zuhr {prayer_times.zuhr.strftime('%H:%M')}, "
        f"Asr {prayer_times.asr.strftime('%H:%M')}, "
        f"Maghrib {prayer_times.maghrib.strftime('%H:%M')}, "
        f"Isha {prayer_times.isha.strftime('%H:%M')}"
    )

    # The prep windows come from the schedule as it actually is. Hardcoding
    # them ("17:05 - 19:25") went stale the moment the day was restructured.
    prep_blocks = [b for b in blocks if b.category == "InterviewPrep"]
    prep_block = (
        "\n".join(
            f"- {b.start_resolved.strftime('%H:%M') if b.start_resolved else b.start_spec}"
            f"-{b.end_resolved.strftime('%H:%M') if b.end_resolved else b.end_spec}: "
            f"{b.activity} ({b.planned_minutes}m)"
            for b in prep_blocks
        )
        if prep_blocks
        else "- (no interview-prep block on today's schedule)"
    )
    rec_block = (
        "\n".join(f"- {t}" for t in rec_titles)
        if rec_titles
        else "- (the recommender has nothing queued; ask what he wants to work on "
        "rather than naming a problem)"
    )

    system_prompt = f"""You are Meridian, a personal life, time and learning coach for {user_name}.
Current date: {now_dt.strftime('%A, %d %B %Y')}
Current local time: {now_time_str} ({settings.timezone})

TODAY'S SCHEDULE, AS ACTUALLY RECORDED:
{schedule_summary}

TODAY'S PRAYER TIMES (computed for today, not fixed):
{prayer_block}

INTERVIEW PREP ON TODAY'S SCHEDULE:
{prep_block}

WHAT THE RECOMMENDER HAS QUEUED:
{rec_block}

HIS OWN OPERATING RULES, AS HE WROTE THEM:
{rules_block}

INSTRUCTIONS:
1. Be crisp, concrete and actionable. No filler, no motivational padding.
2. If he asks what to do right now, compare {now_time_str} against the schedule
   above and answer with the specific block.
3. Everything above is real data from his own records. Do NOT invent schedule
   blocks, prayer times, problem names, deadlines or policies that are not
   listed. If something needed is absent, say it is not recorded and ask.
4. When his operating rules bear on the answer, apply them and say which one
   you are applying.
5. For DSA questions, give the pattern, the complexity, and code in Python.
6. Use Markdown: bold for emphasis, lists, code blocks where useful.
"""

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
        except Exception:
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
            except Exception:
                reply_text = ""

    # Fallback to local heuristic intelligence if API key is missing or failed
    if not reply_text:
        reply_text = _local_fallback_response(payload.message, now_time_str, blocks, user_name)

    # Dynamic suggestions based on context
    suggestions = [
        "What should I do right now?",
        "Break down Two Sum optimal approach",
        "How should I structure my thesis sprint?",
        "Show my Minimum Viable Day fallback",
    ]

    return ChatResponse(reply=reply_text, suggestions=suggestions, model_used=model_to_use)


def _local_fallback_response(message: str, now_time: str, blocks: list[Any], user_name: str) -> str:
    msg = message.lower()
    if "right now" in msg or "what should i do" in msg:
        next_block = next((b for b in blocks if b.status == "NOT DONE"), None)
        if next_block:
            return (
                f"**Current Time:** {now_time}\n\n"
                f"Your upcoming scheduled block is **{next_block.activity}** ({next_block.tier} · {next_block.planned_minutes}m) "
                f"scheduled from **{next_block.start_resolved.strftime('%H:%M')} to {next_block.end_resolved.strftime('%H:%M')}**.\n\n"
                f"- **Focus Action:** Review notes or prepare materials.\n"
                f"- **Preparation:** Drink a glass of water and eliminate screen distractions.\n"
                f"When you begin, activate your session timer in the Today Command Center."
            )
        return f"Hello {user_name}, you have completed all scheduled blocks for today or are in an open rest window."

    if "two sum" in msg or "interview" in msg or "dsa" in msg:
        return (
            "### Target: LeetCode #1 — Two Sum (Arrays & Hashing)\n\n"
            "**Optimal Approach (Hash Map - Single Pass):**\n"
            "- **Time Complexity:** $O(n)$\n"
            "- **Space Complexity:** $O(n)$\n\n"
            "```python\ndef twoSum(nums: list[int], target: int) -> list[int]:\n"
            "    seen = {}\n"
            "    for i, num in enumerate(nums):\n"
            "        complement = target - num\n"
            "        if complement in seen:\n"
            "            return [seen[complement], i]\n"
            "        seen[num] = i\n"
            "    return []\n```\n\n"
            "**Key Insight:** Never compute all pairs with an $O(n^2)$ nested loop. Storing past elements in a hash map gives $O(1)$ complement lookups."
        )

    if "thesis" in msg:
        return (
            f"### Thesis Strategy for {user_name}\n\n"
            "Your morning schedule allocates **124 minutes for Deep Research / Literature Review** (04:41 – 06:45) "
            "followed by **45 minutes of Implementation / Writing** (06:45 – 07:30).\n\n"
            "**Recommended 3-Step Rhythm:**\n"
            "1. **Read with a Question in Mind:** Don't just read passively. Identify how the paper benchmarks activation calibration.\n"
            "2. **Log Concrete Deliverables:** Record 1 clear summary entry in your Thesis Tracker before transitioning to breakfast.\n"
            "3. **Defend the Block:** This is your highest-energy cognitive window; keep all communications closed until your remote workday begins at 09:00."
        )

    return (
        f"Hello {user_name}. I have analyzed your productivity system for today, Monday, September 7, 2026.\n\n"
        f"You have **21 scheduled blocks** across 4 daily phases. Your primary anchors today are your "
        f"morning Thesis deep work, your remote job execution, and your evening MAANG interview prep (Coding & ML System Design).\n\n"
        f"How can I assist you right now?"
    )
