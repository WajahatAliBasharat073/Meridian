"""Next-problem recommender (build prompt 5.2, design doc 6.3).

Deterministic and explainable — never an LLM. Given the same fixture state
(reviews, problems, attempt history, date) this always returns the same
ranked list, which is exactly what makes it unit-testable and what makes
"why did it suggest this" answerable in the UI.

Ranking, most urgent first:
  1 FAILED REVIEW   regressed last time, due today or overdue
  2 OVERDUE REVIEW   due_date < today, oldest first
  3 DUE REVIEW       due_date == today
  4 SCHEDULED        today's curriculum slot, never attempted before
  5 PATTERN GAP      weakest pattern by (L5+ count / scheduled count)
  6 INTERLEAVE       an earlier, already-covered pattern

Constraint: never more than 2 consecutive results from the same pattern
once `foundation_phase` is False — pattern recognition is the skill being
trained, and blocked practice inflates it artificially (build prompt 5.2).
"""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from app.domain import AttemptFixture, ProblemFixture, Recommendation, ReviewState

MAX_CONSECUTIVE_SAME_PATTERN = 2


@dataclass(frozen=True)
class _Candidate:
    problem: ProblemFixture
    reason: str
    queue: str
    is_review: bool
    prior_key_insight: str | None
    priority: int  # 1..6, lower = more urgent


def _latest_attempt_by_problem(attempts: list[AttemptFixture]) -> dict[int, AttemptFixture]:
    latest: dict[int, AttemptFixture] = {}
    for a in sorted(attempts, key=lambda x: x.attempted_at):
        latest[a.problem_id] = a
    return latest


def _current_level(problem_id: int, latest: dict[int, AttemptFixture]) -> str | None:
    a = latest.get(problem_id)
    return a.mastery_level if a else None


def recommend(
    reviews: list[ReviewState],
    problems: list[ProblemFixture],
    attempts: list[AttemptFixture],
    today: date,
    max_results: int = 1,
    foundation_phase: bool = False,
    random_seed: int | None = None,
) -> list[Recommendation]:
    problems_by_id = {p.problem_id: p for p in problems}
    latest = _latest_attempt_by_problem(attempts)
    attempted_ids = set(latest.keys())
    problem_reviews = {r.subject_id: r for r in reviews if r.subject_type == "problem"}

    candidates: list[_Candidate] = []
    used_problem_ids: set[int] = set()

    # 1. FAILED REVIEW
    failed = [
        r for r in problem_reviews.values() if r.last_result == "regressed" and r.due_date <= today
    ]
    for r in sorted(failed, key=lambda r: r.due_date):
        p = problems_by_id.get(r.subject_id)
        if p is None or r.subject_id in used_problem_ids:
            continue
        candidates.append(
            _Candidate(
                problem=p,
                reason=(
                    f"Failed review — dropped to {r.current_level} last time, "
                    f"due {'today' if r.due_date == today else r.due_date.isoformat()}."
                ),
                queue="FAILED_REVIEW",
                is_review=True,
                prior_key_insight=_insight_for(p.problem_id, latest),
                priority=1,
            )
        )
        used_problem_ids.add(r.subject_id)

    # 2. OVERDUE REVIEW — oldest (most overdue_days) first
    overdue = [
        r
        for r in problem_reviews.values()
        if r.due_date < today and r.subject_id not in used_problem_ids
    ]
    for r in sorted(overdue, key=lambda r: -r.overdue_days):
        p = problems_by_id.get(r.subject_id)
        if p is None:
            continue
        candidates.append(
            _Candidate(
                problem=p,
                reason=(
                    f"Overdue {r.overdue_days} day{'s' if r.overdue_days != 1 else ''} — "
                    f"you rated this {r.current_level} on {r.due_date.isoformat()}."
                ),
                queue="OVERDUE_REVIEW",
                is_review=True,
                prior_key_insight=_insight_for(p.problem_id, latest),
                priority=2,
            )
        )
        used_problem_ids.add(r.subject_id)

    # 3. DUE REVIEW — due exactly today
    due_today = [
        r
        for r in problem_reviews.values()
        if r.due_date == today and r.subject_id not in used_problem_ids
    ]
    for r in sorted(due_today, key=lambda r: r.subject_id):
        p = problems_by_id.get(r.subject_id)
        if p is None:
            continue
        candidates.append(
            _Candidate(
                problem=p,
                reason=f"Due today — you rated this {r.current_level} on {r.due_date.isoformat()}.",
                queue="DUE_REVIEW",
                is_review=True,
                prior_key_insight=_insight_for(p.problem_id, latest),
                priority=3,
            )
        )
        used_problem_ids.add(r.subject_id)

    # 4. SCHEDULED — today's curriculum slot, never attempted before
    scheduled = [
        p
        for p in problems
        if p.scheduled_date == today
        and p.problem_id not in attempted_ids
        and p.problem_id not in used_problem_ids
    ]
    for p in sorted(scheduled, key=lambda p: p.scheduled_slot or 0):
        candidates.append(
            _Candidate(
                problem=p,
                reason=f"Today's scheduled problem — slot {p.scheduled_slot}.",
                queue="SCHEDULED",
                is_review=False,
                prior_key_insight=None,
                priority=4,
            )
        )
        used_problem_ids.add(p.problem_id)

    # 5. PATTERN GAP — weakest pattern by L5+ ratio, from problems not yet used
    pattern_gap = _pattern_gap_candidates(problems, latest, used_problem_ids)
    for p, ratio, l5_count, scheduled_count in pattern_gap:
        candidates.append(
            _Candidate(
                problem=p,
                reason=(
                    f"Weakest pattern: {p.pattern} is only {l5_count}/{scheduled_count} at L5+ "
                    f"({ratio:.0%})."
                ),
                queue="PATTERN_GAP",
                is_review=False,
                prior_key_insight=None,
                priority=5,
            )
        )
        used_problem_ids.add(p.problem_id)

    # 6. INTERLEAVE — a random earlier (already-covered) pattern
    rng = random.Random(random_seed if random_seed is not None else today.toordinal())
    covered_patterns = sorted({p.pattern for pid in attempted_ids if (p := problems_by_id.get(pid))})
    interleave_pool = [
        p
        for p in problems
        if p.pattern in covered_patterns
        and p.problem_id not in used_problem_ids
        and p.problem_id not in attempted_ids
    ]
    interleave_pool.sort(key=lambda p: p.problem_id)
    rng.shuffle(interleave_pool)
    for p in interleave_pool:
        candidates.append(
            _Candidate(
                problem=p,
                reason=f"Interleaved from an earlier pattern ({p.pattern}) to prevent blocked practice.",
                queue="INTERLEAVE",
                is_review=False,
                prior_key_insight=None,
                priority=6,
            )
        )
        used_problem_ids.add(p.problem_id)

    selected = _apply_pattern_spacing(candidates, max_results, foundation_phase)
    return [
        Recommendation(
            problem_id=c.problem.problem_id,
            title=c.problem.title,
            pattern=c.problem.pattern,
            difficulty=c.problem.difficulty,
            reason=c.reason,
            queue=c.queue,
            is_review=c.is_review,
            prior_key_insight=c.prior_key_insight,
        )
        for c in selected
    ]


def _insight_for(problem_id: int, latest: dict[int, AttemptFixture]) -> str | None:
    a = latest.get(problem_id)
    return a.key_insight if a else None


def _pattern_gap_candidates(
    problems: list[ProblemFixture],
    latest: dict[int, AttemptFixture],
    used_problem_ids: set[int],
) -> list[tuple[ProblemFixture, float, int, int]]:
    by_pattern: dict[str, list[ProblemFixture]] = defaultdict(list)
    for p in problems:
        by_pattern[p.pattern].append(p)

    stats: list[tuple[str, float, int, int]] = []
    for pattern, plist in by_pattern.items():
        scheduled_count = sum(1 for p in plist if p.scheduled_date is not None)
        if scheduled_count == 0:
            continue
        l5_count = sum(
            1
            for p in plist
            if (a := latest.get(p.problem_id)) is not None and a.mastery_level in ("L5", "L6")
        )
        ratio = l5_count / scheduled_count
        stats.append((pattern, ratio, l5_count, scheduled_count))

    stats.sort(key=lambda s: s[1])

    out: list[tuple[ProblemFixture, float, int, int]] = []
    for pattern, ratio, l5_count, scheduled_count in stats:
        pool = []
        for p in by_pattern[pattern]:
            if p.problem_id in used_problem_ids:
                continue
            a = latest.get(p.problem_id)
            if a is not None and a.mastery_level in ("L5", "L6"):
                continue
            pool.append(p)
        pool.sort(key=lambda p: p.problem_id)
        if pool:
            out.append((pool[0], ratio, l5_count, scheduled_count))
    return out


def _apply_pattern_spacing(
    candidates: list[_Candidate],
    max_results: int,
    foundation_phase: bool,
) -> list[_Candidate]:
    """Fills the output in priority order, at each step taking the
    highest-priority remaining candidate that would not create a 3rd
    consecutive same-pattern result. "Never serve more than 2 consecutive
    from the same pattern" (build prompt 5.2) is absolute — if every
    remaining candidate would violate it, the list comes back shorter than
    `max_results` rather than breaking the rule.
    """
    if foundation_phase:
        return candidates[:max_results]

    remaining = list(candidates)
    selected: list[_Candidate] = []

    while remaining and len(selected) < max_results:
        last_two = [s.problem.pattern for s in selected[-MAX_CONSECUTIVE_SAME_PATTERN:]]
        blocked_pattern = (
            last_two[0]
            if len(last_two) == MAX_CONSECUTIVE_SAME_PATTERN and len(set(last_two)) == 1
            else None
        )

        chosen_index = next(
            (i for i, c in enumerate(remaining) if c.problem.pattern != blocked_pattern),
            None,
        )
        if chosen_index is None:
            break
        selected.append(remaining.pop(chosen_index))

    return selected
