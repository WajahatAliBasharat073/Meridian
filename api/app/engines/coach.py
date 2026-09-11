"""Pure functions: assemble the system prompt that grounds the Ask
Meridian assistant in real data, and produce a deterministic local
answer when no LLM call is available.

Extracted from `routers/coach.py`, which mixed DB fetches, prompt
string-building, and Groq-call error handling in one function — the only
part of the business-logic layer that wasn't unit-testable the way every
other engine here is (ARCHITECTURE_AUDIT.md §4).

Fixed while extracting: the local fallback's catch-all reply and its
"thesis" branch both unconditionally asserted fabricated specifics —
"Monday, September 7, 2026", "21 scheduled blocks", "124 minutes for
Deep Research (04:41-06:45)" — regardless of what day it actually was or
what was actually scheduled. That's a literal violation of the very rule
the system prompt orders the LLM to follow (§ INSTRUCTIONS 3 below: "Do
NOT invent... If something needed is absent, say it is not recorded").
Both now describe only what's actually in `ctx`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time

from app.engines.prayer import PrayerTimesResult


@dataclass(frozen=True)
class CoachScheduleBlock:
    """A `time_blocks` row, reduced to what the coach prompt needs to
    describe today's schedule in prose."""

    start_resolved: time | None
    start_spec: str
    end_resolved: time | None
    end_spec: str
    activity: str
    tier: str
    category: str
    status: str
    planned_minutes: int


@dataclass(frozen=True)
class CoachContext:
    user_name: str
    now: datetime
    timezone_label: str
    blocks: tuple[CoachScheduleBlock, ...]
    prayer_times: PrayerTimesResult
    recommendation_titles: tuple[str, ...]
    operating_rules: tuple[str, ...]
    # Phase 6 additions -- same rule as everything above: absent means
    # "not recorded", never inferred or estimated.
    active_goal_titles: tuple[str, ...] = ()
    #: None when no recovery entry exists for today at all (distinct from
    #: a low score, which is still a real number).
    recovery_score: float | None = None
    finance_income_this_month: float | None = None
    finance_expenses_this_month: float | None = None
    finance_savings_this_month: float | None = None


def _time_label(resolved: time | None, spec: str) -> str:
    return resolved.strftime("%H:%M") if resolved else spec


def build_system_prompt(ctx: CoachContext) -> str:
    schedule_summary = (
        "\n".join(
            f"- {_time_label(b.start_resolved, b.start_spec)} to "
            f"{_time_label(b.end_resolved, b.end_spec)}: "
            f"{b.activity} ({b.tier}, {b.category}) [{b.status}]"
            for b in ctx.blocks
        )
        or "- (no blocks scheduled for today)"
    )

    prayer_block = (
        f"Fajr {ctx.prayer_times.fajr.strftime('%H:%M')}, "
        f"Zuhr {ctx.prayer_times.zuhr.strftime('%H:%M')}, "
        f"Asr {ctx.prayer_times.asr.strftime('%H:%M')}, "
        f"Maghrib {ctx.prayer_times.maghrib.strftime('%H:%M')}, "
        f"Isha {ctx.prayer_times.isha.strftime('%H:%M')}"
    )

    # The prep window comes from the schedule as it actually is today, not
    # a hardcoded time range that goes stale the moment the day changes.
    prep_blocks = [b for b in ctx.blocks if b.category == "InterviewPrep"]
    prep_block = (
        "\n".join(
            f"- {_time_label(b.start_resolved, b.start_spec)}-{_time_label(b.end_resolved, b.end_spec)}: "
            f"{b.activity} ({b.planned_minutes}m)"
            for b in prep_blocks
        )
        if prep_blocks
        else "- (no interview-prep block on today's schedule)"
    )

    rec_block = (
        "\n".join(f"- {t}" for t in ctx.recommendation_titles)
        if ctx.recommendation_titles
        else "- (the recommender has nothing queued; ask what he wants to work on rather than naming a problem)"
    )

    rules_block = (
        "\n".join(f"- {r}" for r in ctx.operating_rules)
        if ctx.operating_rules
        else "- (none recorded yet — do not invent policies on his behalf)"
    )

    goals_block = (
        "\n".join(f"- {t}" for t in ctx.active_goal_titles)
        if ctx.active_goal_titles
        else "- (no active goals recorded)"
    )

    recovery_block = (
        f"- Recovery score today: {ctx.recovery_score:.0f}/100"
        if ctx.recovery_score is not None
        else "- (no recovery entry logged today)"
    )

    if ctx.finance_savings_this_month is not None:
        finance_block = (
            f"- Income this month: ${ctx.finance_income_this_month:,.0f}\n"
            f"- Expenses this month: ${ctx.finance_expenses_this_month:,.0f}\n"
            f"- Savings this month: ${ctx.finance_savings_this_month:,.0f}"
        )
    else:
        finance_block = "- (no financial data recorded)"

    now_time_str = ctx.now.strftime("%I:%M %p")

    return f"""You are Meridian, a personal life, time and learning coach for {ctx.user_name}.
Current date: {ctx.now.strftime('%A, %d %B %Y')}
Current local time: {now_time_str} ({ctx.timezone_label})

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

HIS ACTIVE GOALS:
{goals_block}

RECOVERY / VITALS:
{recovery_block}

FINANCES THIS MONTH:
{finance_block}

INSTRUCTIONS:
1. Be crisp, concrete and actionable. No filler, no motivational padding.
2. If he asks what to do right now, compare {now_time_str} against the schedule
   above and answer with the specific block.
3. Everything above is real data from his own records. Do NOT invent schedule
   blocks, prayer times, problem names, deadlines, policies, goals, recovery
   scores or financial figures that are not listed. If something needed is
   absent, say it is not recorded and ask.
4. When his operating rules bear on the answer, apply them and say which one
   you are applying.
5. For DSA questions, give the pattern, the complexity, and code in Python.
6. Use Markdown: bold for emphasis, lists, code blocks where useful.
"""


def local_fallback_response(message: str, ctx: CoachContext) -> str:
    """Deterministic answer used when no Groq key is configured or every
    model call failed. Same anti-invention rule as the system prompt
    above applies here too — every branch describes `ctx`, never a
    fabricated day or schedule."""
    msg = message.lower()
    now_time = ctx.now.strftime("%I:%M %p")

    if "right now" in msg or "what should i do" in msg:
        next_block = next((b for b in ctx.blocks if b.status == "NOT DONE"), None)
        if next_block:
            return (
                f"**Current Time:** {now_time}\n\n"
                f"Your upcoming scheduled block is **{next_block.activity}** "
                f"({next_block.tier} · {next_block.planned_minutes}m) scheduled from "
                f"**{_time_label(next_block.start_resolved, next_block.start_spec)} to "
                f"{_time_label(next_block.end_resolved, next_block.end_spec)}**.\n\n"
                f"- **Focus Action:** Review notes or prepare materials.\n"
                f"- **Preparation:** Drink a glass of water and eliminate screen distractions.\n"
                f"When you begin, activate your session timer in the Today Command Center."
            )
        return (
            f"Hello {ctx.user_name}, you have completed all scheduled blocks for today "
            f"or are in an open rest window."
        )

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
            "**Key Insight:** Never compute all pairs with an $O(n^2)$ nested loop. "
            "Storing past elements in a hash map gives $O(1)$ complement lookups."
        )

    if "thesis" in msg:
        research_blocks = [
            b for b in ctx.blocks if "thesis" in b.activity.lower() or "research" in b.activity.lower()
        ]
        if research_blocks:
            lines = "\n".join(
                f"- **{_time_label(b.start_resolved, b.start_spec)}"
                f"-{_time_label(b.end_resolved, b.end_spec)}:** {b.activity} ({b.planned_minutes}m)"
                for b in research_blocks
            )
            return (
                f"### Thesis Strategy for {ctx.user_name}\n\n"
                f"Today's schedule has:\n{lines}\n\n"
                "**Recommended 3-Step Rhythm:**\n"
                "1. **Read with a Question in Mind:** identify one specific thing "
                "you're trying to confirm or refute before you start.\n"
                "2. **Log Concrete Deliverables:** record one clear summary entry "
                "in your research log before moving on.\n"
                "3. **Defend the Block:** treat this as protected time — no other "
                "work until it's done."
            )
        return (
            f"Hello {ctx.user_name}, there's no thesis/research block on today's schedule. "
            "If you want to work on it anyway, tell me how long and I'll help you plan the session."
        )

    block_count = len(ctx.blocks)
    schedule_note = (
        f"You have **{block_count} scheduled block{'s' if block_count != 1 else ''}** today."
        if block_count
        else "There's nothing on today's schedule yet."
    )
    return (
        f"Hello {ctx.user_name}. Today is {ctx.now.strftime('%A, %d %B %Y')}.\n\n"
        f"{schedule_note} Ask me what to do right now, or name a topic you want help with.\n\n"
        "How can I assist you right now?"
    )
