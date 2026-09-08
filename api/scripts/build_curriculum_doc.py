"""Generate CURRICULUM.md — the 19 specified outputs, rendered from the
database rather than written by hand.

Every number in the document is a query result. That matters: a curriculum
document that is typed out drifts from the bank it describes within a week,
and then quietly starts lying about what has been covered. Re-run this
after any ingestion.

Usage:
    python -m scripts.build_curriculum_doc
"""

from __future__ import annotations

import asyncio
from collections import Counter, defaultdict
from pathlib import Path

from sqlalchemy import select

from app.db import SessionLocal
from app.models.questions import InterviewModule, Question

OUT_PATH = Path(__file__).resolve().parents[2] / "CURRICULUM.md"

TARGET_COMPANIES = ["Meta", "Amazon", "Netflix", "Google", "OpenAI"]

EVIDENCE_ORDER = {"reported": 0, "common": 1, "fundamental": 2, "derived": 3}
FREQ_ORDER = {"very_high": 0, "high": 1, "medium": 2, "low": 3, "unknown": 4}


def _rank(q: Question) -> tuple:
    """Highest-ROI first: P0 before P1, actually-reported before inferred,
    frequently-reported before rarely."""
    return (
        {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(q.priority or "P3", 3),
        FREQ_ORDER.get(q.frequency or "unknown", 4),
        EVIDENCE_ORDER.get(q.evidence or "derived", 3),
        -len(q.companies or []),
        q.title.lower(),
    )


def _line(q: Question, show_module: bool = False) -> str:
    bits = []
    if show_module and q.module_code:
        bits.append(f"`{q.module_code}`")
    if q.priority:
        bits.append(q.priority)
    if q.difficulty:
        bits.append(q.difficulty)
    if q.companies:
        bits.append(", ".join(q.companies))
    tail = f" — *{' · '.join(bits)}*" if bits else ""
    src = f" [{q.source}]({q.source_url})" if q.source_url else f" [{q.source}]"
    return f"- {q.title}{tail}{src}"


def _section(title: str, questions: list[Question], limit: int, show_module: bool = False) -> str:
    ranked = sorted(questions, key=_rank)[:limit]
    body = "\n".join(_line(q, show_module) for q in ranked)
    return f"## {title}\n\n_{len(ranked)} of {len(questions)} shown, highest-ROI first._\n\n{body}\n"


async def main() -> None:
    async with SessionLocal() as session:
        modules = list(
            (await session.execute(select(InterviewModule).order_by(InterviewModule.order_index)))
            .scalars()
            .all()
        )
        questions = list((await session.execute(select(Question))).scalars().all())

    by_module: dict[str, list[Question]] = defaultdict(list)
    for q in questions:
        if q.module_code:
            by_module[q.module_code].append(q)

    parts: list[str] = []
    add = parts.append

    total = len(questions)
    reported = sum(1 for q in questions if q.evidence == "reported")
    with_co = sum(1 for q in questions if q.companies)

    add(f"""# AI/ML Interview Curriculum

Generated from the Meridian question bank by `api/scripts/build_curriculum_doc.py`.
Every count here is a query result, not a hand-typed figure — re-run the
generator after any ingestion rather than editing this file.

**{total} canonical questions across {len(modules)} modules.**
{reported} carry `reported` evidence (a named, linkable source);
{with_co} name a company, and none may do so without both `evidence='reported'`
and a `source_url` — that rule is a database check constraint, not a convention.

Evidence tiers: `reported` (a named source ties this question to a company or a
candidate report) · `common` (appears across several independent prep sources) ·
`fundamental` (core knowledge, no company claim made) · `derived` (generated from
a topic outline).
""")

    # ---------------- OUTPUT 1 ----------------
    add("## OUTPUT 1 — Interview Master Map\n")
    add("| Module | Title | Priority | Questions | Target seniority | Submodules |")
    add("| --- | --- | --- | ---: | --- | ---: |")
    for m in modules:
        n = len(by_module.get(m.code, []))
        add(
            f"| {m.code} | {m.title} | {m.priority} | {n} | "
            f"{', '.join(m.target_seniority or [])} | {len(m.submodules or [])} |"
        )
    add("")

    # ---------------- OUTPUT 2 ----------------
    add("## OUTPUT 2 — Complete Question Bank\n")
    add(
        "The full bank lives in the database and is browsable at `/curriculum` in the app, "
        "where each question shows what the interviewer is testing, its follow-ups, its "
        "strong/weak signals, its source link, and your 0-7 mastery. Reproduced here by "
        "module, capped for readability.\n"
    )
    for m in modules:
        qs = by_module.get(m.code, [])
        if not qs:
            continue
        add(f"### Module {m.code} — {m.title} ({len(qs)} questions, {m.priority})\n")
        add(f"_{m.summary}_\n")
        for q in sorted(qs, key=_rank)[:20]:
            add(_line(q))
        if len(qs) > 20:
            add(f"- _…and {len(qs) - 20} more in the app._")
        add("")

    # ---------------- OUTPUTS 3-15 ----------------
    add(_section("OUTPUT 3 — Top 200 Must-Know Questions", questions, 200, show_module=True))

    for out_no, title, codes in [
        (4, "Top Classical ML Questions", ["D"]),
        (5, "Top Deep Learning Questions", ["H"]),
        (6, "Top LLM / GenAI Questions", ["L", "K"]),
        (7, "Top RAG Questions", ["M"]),
        (8, "Top Agentic AI Questions", ["N", "O", "P"]),
        (9, "Top ML System Design Questions", ["R"]),
        (10, "Top GenAI System Design Questions", ["S"]),
        (11, "Top Agentic System Design Questions", ["T"]),
        (12, "Top ML Coding Questions", ["B"]),
        (13, "Top Debugging Questions", ["Z"]),
        (14, "Top ML Case Studies", ["AA"]),
        (15, "Top Project Deep-Dive Questions", ["AD"]),
    ]:
        pool = [q for c in codes for q in by_module.get(c, [])]
        add(_section(f"OUTPUT {out_no} — {title}", pool, 40))

    # ---------------- OUTPUT 16 ----------------
    add("## OUTPUT 16 — Company-Specific Preparation\n")
    add(
        "Only questions whose source explicitly ties them to a company appear here. "
        "This is a short list on purpose: the honest answer to \"what does Meta ask?\" is "
        "much smaller than any curriculum implies, and padding it with plausible-sounding "
        "guesses is what makes company-specific prep worthless.\n"
    )
    co_counts = Counter(c for q in questions for c in (q.companies or []))
    add("| Company | Cited questions |")
    add("| --- | ---: |")
    for co, n in co_counts.most_common():
        add(f"| {co} | {n} |")
    add("")
    for co in TARGET_COMPANIES + [c for c in co_counts if c not in TARGET_COMPANIES]:
        qs = [q for q in questions if co in (q.companies or [])]
        if not qs:
            add(f"### {co}\n\nNo question in the bank has a cited source tying it to {co}. "
                f"That is a gap in the evidence, not a claim that {co} asks nothing here.\n")
            continue
        add(f"### {co} ({len(qs)} cited)\n")
        mods = Counter(q.module_code for q in qs)
        add(f"Concentrated in: {', '.join(f'{m} ({n})' for m, n in mods.most_common())}\n")
        for q in sorted(qs, key=_rank):
            add(_line(q, show_module=True))
        add("")

    # ---------------- OUTPUT 17 ----------------
    for label, sen in [("Senior", "senior"), ("Staff / Principal", "staff")]:
        pool = [q for q in questions if q.seniority == sen]
        if pool:
            add(_section(f"OUTPUT 17 — {label} Questions", pool, 60, show_module=True))

    # ---------------- OUTPUT 18 ----------------
    add("## OUTPUT 18 — Resource Mapping\n")
    add("Which source produced the questions in each module.\n")
    add("| Module | Sources |")
    add("| --- | --- |")
    for m in modules:
        srcs = Counter(q.source for q in by_module.get(m.code, []))
        if not srcs:
            add(f"| {m.code} {m.title} | _(none yet)_ |")
            continue
        add(f"| {m.code} {m.title} | {', '.join(f'{s} ({n})' for s, n in srcs.most_common())} |")
    add("")

    # ---------------- OUTPUT 19 ----------------
    add("""## OUTPUT 19 — Interview Readiness Checklist

Mastery is tracked per question on a 0-7 ladder, not a checkbox:

| Level | Meaning |
| ---: | --- |
| 0 | Never seen |
| 1 | Recognize |
| 2 | Can explain |
| 3 | Can solve |
| 4 | Can reason about trade-offs |
| 5 | Can answer follow-ups |
| 6 | Can design a production system |
| 7 | Can teach it |

**A question counts toward readiness only at level 4 or above.** Below that
it is recognition, and a progress bar that counts recognition as readiness
is the single easiest way to walk into an interview over-confident. The
module percentages in the app use this bar.
""")

    OUT_PATH.write_text("\n".join(parts), encoding="utf-8")
    words = sum(len(p.split()) for p in parts)
    print(f"Wrote {OUT_PATH} — {len(parts)} blocks, ~{words:,} words")
    print(f"  {total} questions, {len(modules)} modules, {reported} reported-evidence")
    print(f"  companies cited: {dict(co_counts.most_common())}")


if __name__ == "__main__":
    asyncio.run(main())
