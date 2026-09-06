"""Pure function: turns one day's real schedule into a short recap plus a
handful of suggestions. Every suggestion is a plain, deterministic
restatement of a real number crossing a real threshold — never a
generated or invented claim (build prompt: never fabricate).

Covers the whole schedule (prayer, job, thesis, recovery, interview prep —
whatever categories that day actually had), not interview prep alone."""

from __future__ import annotations

from datetime import date

from app.domain import CategoryBreakdown, DailyRecap, TimeBlockFixture

DONE_STATUSES = {"DONE", "PARTIAL"}


def compute_daily_recap(
    blocks: list[TimeBlockFixture],
    problems_attempted: int,
    recap_date: date,
) -> DailyRecap:
    total = len(blocks)
    done = sum(1 for b in blocks if b.status == "DONE")
    partial = sum(1 for b in blocks if b.status == "PARTIAL")
    not_done = sum(1 for b in blocks if b.status == "NOT DONE")
    rescheduled = sum(1 for b in blocks if b.status == "RESCHEDULED")
    completion_pct = round(100 * (done + partial) / total, 1) if total else None

    by_category: dict[str, list[int]] = {}
    for b in blocks:
        counts = by_category.setdefault(b.category, [0, 0])
        counts[1] += 1
        if b.status in DONE_STATUSES:
            counts[0] += 1
    category_breakdown = [
        CategoryBreakdown(category=cat, done=vals[0], total=vals[1])
        for cat, vals in sorted(by_category.items(), key=lambda kv: kv[0])
    ]

    deep_work = [b for b in blocks if b.tier == "T1"]
    deep_work_planned = sum(b.planned_minutes for b in deep_work)
    deep_work_actual = sum(b.actual_minutes or 0 for b in deep_work if b.status in DONE_STATUSES)

    headline = _headline(total, completion_pct)
    suggestions = _suggestions(
        total=total,
        completion_pct=completion_pct,
        rescheduled=rescheduled,
        category_breakdown=category_breakdown,
        deep_work_planned=deep_work_planned,
        deep_work_actual=deep_work_actual,
        problems_attempted=problems_attempted,
    )

    return DailyRecap(
        recap_date=recap_date,
        total_blocks=total,
        done_count=done,
        partial_count=partial,
        not_done_count=not_done,
        rescheduled_count=rescheduled,
        completion_pct=completion_pct,
        category_breakdown=category_breakdown,
        problems_attempted=problems_attempted,
        deep_work_planned_minutes=deep_work_planned,
        deep_work_actual_minutes=deep_work_actual,
        headline=headline,
        suggestions=suggestions,
    )


def _headline(total: int, completion_pct: float | None) -> str:
    if total == 0:
        return "Nothing was scheduled that day."
    if completion_pct is None:
        return "No blocks scheduled."
    if completion_pct >= 85:
        return f"Strong day — {completion_pct}% of the schedule held."
    if completion_pct >= 50:
        return f"Middling day — {completion_pct}% of the schedule held."
    return f"Rough day — only {completion_pct}% of the schedule held."


def _suggestions(
    *,
    total: int,
    completion_pct: float | None,
    rescheduled: int,
    category_breakdown: list[CategoryBreakdown],
    deep_work_planned: int,
    deep_work_actual: int,
    problems_attempted: int,
) -> list[str]:
    if total == 0:
        return []

    out: list[str] = []

    if completion_pct is not None and completion_pct < 50:
        out.append(
            "Under half the day's blocks held — the schedule may be sized "
            "above your real bandwidth that day. Trimming lower-tier blocks "
            "first usually protects the ones that matter more."
        )

    if rescheduled >= 3:
        out.append(
            f"{rescheduled} blocks were rescheduled — worth checking whether "
            "a specific time of day keeps slipping."
        )

    weakest = min(
        (c for c in category_breakdown if c.total >= 2),
        key=lambda c: c.done / c.total,
        default=None,
    )
    if weakest is not None and weakest.done / weakest.total < 0.5:
        out.append(
            f"{weakest.category} held up worst that day ({weakest.done}/{weakest.total} "
            "done) — the likeliest place to protect time first tomorrow."
        )

    if deep_work_planned > 0 and deep_work_actual < deep_work_planned * 0.6:
        out.append(
            f"Deep-work blocks ran well under plan ({deep_work_actual} of "
            f"{deep_work_planned} minutes) — that's usually the first thing "
            "worth protecting on a lighter day."
        )

    if problems_attempted == 0 and any(c.category == "InterviewPrep" for c in category_breakdown):
        out.append("No problems attempted that day, even though prep was on the schedule.")

    return out
