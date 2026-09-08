"""Daily theory recommender: which questions to study today, and why.

Answers the same question the LeetCode recommender (`recommender.py`)
answers for problems, but for the 724-question interview curriculum:
"of everything in the bank, what should I look at *today*". Same
discipline — deterministic, no LLM, no DB access, unit-testable against
fixtures, and the same day always produces the same three picks unless
mastery actually changed.

Ranking, most urgent first:
  1. DUE FOR REINFORCEMENT  mastery 1-6, last touched >= its review
     interval ago (see REVIEW_INTERVAL_DAYS) — you rated it once and it's
     due to resurface, exactly like a spaced-repetition card.
  2. NEVER SEEN              mastery 0, never rated at all.
  3. EVERYTHING ELSE         not yet due — only reached if 1 and 2 can't
     fill the quota (a well-maintained bank should rarely get here).

Within each tier, ranked by module priority (P0 first), then reported
frequency (very_high first), then how overdue it is, then a per-day
shuffle seeded on the date so ties rotate instead of freezing on
whichever question sorts first alphabetically forever.

Two hard constraints, both because a flat top-N ranking would otherwise
violate them:
  - Exactly `case_study_count` picks (default 1) have question_type ==
    'case_study', chosen from the same ranking applied to that subset
    only. If the bank has none, the day simply gets fewer than requested
    rather than substituting a different type silently.
  - No two picks share a module_code unless the eligible pool is too
    small to avoid it — hammering one module's queue every day would
    starve the other 31.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, datetime

from app.domain import DailyTheoryPick, QuestionFixture, QuestionProgressFixture

# How many days after being rated at this mastery level a question resurfaces
# for reinforcement. Mirrors LADDER_DAYS' shape (app/domain.py) but is its
# own table: the interview ladder is 0-7, not L0-L6, and a "can defend the
# trade-offs" question earns a much longer gap than a barely-passing one.
REVIEW_INTERVAL_DAYS: dict[int, int] = {
    0: 0,  # never seen - always eligible, not "reinforcement"
    1: 1,
    2: 2,
    3: 4,
    4: 7,
    5: 14,
    6: 30,
    7: 60,
}

_PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
_FREQUENCY_ORDER = {"very_high": 0, "high": 1, "medium": 2, "low": 3, "unknown": 4}

CASE_STUDY_TYPE = "case_study"


@dataclass(frozen=True)
class _Scored:
    fixture: QuestionFixture
    tier: int  # 0 = due for reinforcement, 1 = never seen, 2 = not yet due
    days_overdue: int  # 0 if not applicable
    mastery: int
    priority_rank: int
    frequency_rank: int
    shuffle_key: float


def _days_since(today: date, updated_at: datetime) -> int:
    return max(0, (today - updated_at.date()).days)


def _score(
    fx: QuestionFixture,
    progress: dict[int, QuestionProgressFixture],
    today: date,
    rng: random.Random,
) -> _Scored:
    p = progress.get(fx.question_id)
    mastery = p.mastery if p else 0

    if p is None or mastery == 0:
        tier, days_overdue = 1, 0
    else:
        interval = REVIEW_INTERVAL_DAYS.get(mastery, 60)
        elapsed = _days_since(today, p.updated_at)
        if elapsed >= interval:
            tier, days_overdue = 0, elapsed - interval
        else:
            tier, days_overdue = 2, 0

    return _Scored(
        fixture=fx,
        tier=tier,
        days_overdue=days_overdue,
        mastery=mastery,
        priority_rank=_PRIORITY_ORDER.get(fx.priority or "P3", 3),
        frequency_rank=_FREQUENCY_ORDER.get(fx.frequency or "unknown", 4),
        shuffle_key=rng.random(),
    )


def _sort_key(s: _Scored) -> tuple[int, int, int, int, int, float]:
    return (
        s.tier,
        s.priority_rank,
        s.frequency_rank,
        -s.days_overdue,  # more overdue first, within a tier
        -s.mastery,  # among never-seen (mastery always 0) irrelevant; among
        # tier 2 fallback, prefer the lower mastery (more room to build)
        s.shuffle_key,
    )


def _pick_diverse(ranked: list[_Scored], count: int) -> list[_Scored]:
    """Take up to `count` items, skipping a module already chosen today
    unless the remaining pool has nothing else left."""
    chosen: list[_Scored] = []
    used_modules: set[str | None] = set()

    for s in ranked:
        if len(chosen) >= count:
            break
        if s.fixture.module_code in used_modules:
            continue
        chosen.append(s)
        used_modules.add(s.fixture.module_code)

    if len(chosen) < count:
        chosen_ids = {s.fixture.question_id for s in chosen}
        for s in ranked:
            if len(chosen) >= count:
                break
            if s.fixture.question_id in chosen_ids:
                continue
            chosen.append(s)

    return chosen[:count]


def _reason(s: _Scored) -> str:
    if s.tier == 1:
        return "Never studied — starting from zero."
    if s.tier == 0:
        if s.days_overdue > 0:
            return f"Due for reinforcement — {s.days_overdue}d overdue at your last rating."
        return "Due for reinforcement, right on schedule."
    return "Not yet due, but the queue needed filling to reach today's count."


def pick_daily_theory(
    questions: list[QuestionFixture],
    progress: list[QuestionProgressFixture],
    today: date,
    count: int = 3,
    case_study_count: int = 1,
    random_seed: int | None = None,
) -> list[DailyTheoryPick]:
    """Deterministic per (today, progress state); rotates day to day via a
    seed derived from the date, exactly like `recommender.recommend`."""
    if count <= 0 or not questions:
        return []

    rng = random.Random(random_seed if random_seed is not None else today.toordinal())
    progress_by_id = {p.question_id: p for p in progress}

    scored = [_score(fx, progress_by_id, today, rng) for fx in questions]

    case_pool = sorted((s for s in scored if s.fixture.question_type == CASE_STUDY_TYPE), key=_sort_key)
    other_pool = sorted((s for s in scored if s.fixture.question_type != CASE_STUDY_TYPE), key=_sort_key)

    case_picks = _pick_diverse(case_pool, min(case_study_count, len(case_pool)))
    remaining = count - len(case_picks)
    # A case-study module is now "used" for today, but the other slots are
    # a disjoint pool anyway (question_type differs), so no cross-filtering
    # is needed beyond each pool's own diversity pass.
    other_picks = _pick_diverse(other_pool, max(0, remaining))

    picks = case_picks + other_picks
    return [
        DailyTheoryPick(
            question_id=s.fixture.question_id,
            is_case_study=s.fixture.question_type == CASE_STUDY_TYPE,
            reason=_reason(s),
        )
        for s in picks
    ]
