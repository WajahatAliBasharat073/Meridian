"""Curriculum integrity check. Run it in CI; it exits non-zero on failure.

Structural rules only. This does not judge whether a question is any good
-- that is a content review, deliberately kept separate (see
CURRICULUM_AUDIT.md section 14) -- it checks that the knowledge model is
coherent and that the scheduler cannot be asked for something impossible.

Phase completeness is measured on the **knowledge axis only**. That
distinction is the whole point: P0 currently holds 108 questions, of which
96 are DSA, behavioural and project deep dives. Counting those would
report P0 as healthy while the actual foundations -- Python, NumPy,
Pandas, calculus -- remain almost entirely missing.

Usage:
    python -m scripts.validate_curriculum
    python -m scripts.validate_curriculum --json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections import Counter, defaultdict

from sqlalchemy import select

from app.db import SessionLocal
from app.models.questions import CurriculumTopic, Question
from scripts.curriculum_graph import PHASES

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: A phase needs at least this many knowledge questions, and at least one
#: genuine entry point (L0-L1), before it can be considered teachable.
MIN_KNOWLEDGE_PER_PHASE = 20
MIN_ENTRY_POINTS = 3


async def collect() -> dict:
    async with SessionLocal() as s:
        topics = list((await s.execute(select(CurriculumTopic))).scalars())
        questions = list((await s.execute(select(Question))).scalars())

    by_slug = {t.slug: t for t in topics}
    errors: list[str] = []
    warnings: list[str] = []

    # ---- V1/V2: every question maps, every prereq resolves -------------
    no_topic = [q.id for q in questions if not q.topic]
    unknown_topic = [q.id for q in questions if q.topic and q.topic not in by_slug]
    no_phase = [q.id for q in questions if q.phase is None]
    bad_level = [
        q.id
        for q in questions
        if q.cognitive_level is not None and not (0 <= q.cognitive_level <= 5)
    ]
    bad_axis = [q.id for q in questions if q.axis not in ("knowledge", "format")]

    invalid_prereqs: list[str] = []
    for t in topics:
        for p in t.prereqs or []:
            if p not in by_slug:
                invalid_prereqs.append(f"{t.slug} -> {p}")

    # ---- V3: acyclic ---------------------------------------------------
    cycles: list[str] = []
    WHITE, GREY, BLACK = 0, 1, 2
    color = dict.fromkeys(by_slug, WHITE)

    def visit(slug: str, stack: list[str]) -> None:
        if color.get(slug) == GREY:
            cycles.append(" -> ".join(stack + [slug]))
            return
        if color.get(slug) == BLACK:
            return
        color[slug] = GREY
        for p in by_slug[slug].prereqs or []:
            if p in by_slug:
                visit(p, stack + [slug])
        color[slug] = BLACK

    for slug in by_slug:
        visit(slug, [])

    # ---- V4: phase monotonic ------------------------------------------
    phase_inversions = [
        f"{t.slug}(P{t.phase}) requires {p}(P{by_slug[p].phase})"
        for t in topics
        for p in (t.prereqs or [])
        if p in by_slug and by_slug[p].phase > t.phase
    ]

    # ---- phase completeness, knowledge axis only -----------------------
    knowledge = [q for q in questions if q.axis == "knowledge"]
    fmt = [q for q in questions if q.axis == "format"]
    per_phase: dict[int, list] = defaultdict(list)
    for q in knowledge:
        if q.phase is not None:
            per_phase[q.phase].append(q)

    phase_report = {}
    for p in sorted(PHASES):
        qs = per_phase.get(p, [])
        entry = [q for q in qs if (q.cognitive_level or 9) <= 1]
        if len(qs) < MIN_KNOWLEDGE_PER_PHASE:
            status = "INCOMPLETE"
        elif len(entry) < MIN_ENTRY_POINTS:
            status = "NO_ENTRY_POINTS"
        else:
            status = "READY"
        phase_report[f"P{p}"] = {
            "name": PHASES[p],
            "knowledge": len(qs),
            "entry_points": len(entry),
            "status": status,
        }
        if status != "READY":
            warnings.append(
                f"P{p} {PHASES[p]}: {status} "
                f"({len(qs)} knowledge questions, {len(entry)} entry points)"
            )

    # ---- topics with no content ---------------------------------------
    per_topic = Counter(q.topic for q in knowledge if q.topic)
    empty_topics = sorted(t.slug for t in topics if t.gated and per_topic.get(t.slug, 0) == 0)

    if no_topic:
        errors.append(f"{len(no_topic)} question(s) have no topic")
    if unknown_topic:
        errors.append(f"{len(unknown_topic)} question(s) reference an unknown topic")
    if no_phase:
        errors.append(f"{len(no_phase)} question(s) have no phase")
    if bad_level:
        errors.append(f"{len(bad_level)} question(s) have an invalid cognitive level")
    if bad_axis:
        errors.append(f"{len(bad_axis)} question(s) have an invalid axis")
    if invalid_prereqs:
        errors.append(f"invalid prerequisite references: {invalid_prereqs}")
    if cycles:
        errors.append(f"circular dependencies: {cycles}")
    if phase_inversions:
        errors.append(f"phase inversions: {phase_inversions}")
    if empty_topics:
        warnings.append(
            f"{len(empty_topics)} gated topic(s) have no knowledge questions: "
            f"{', '.join(empty_topics[:12])}"
            + (" ..." if len(empty_topics) > 12 else "")
        )

    review = [q for q in questions if q.classification_confidence == "module_default"]

    return {
        "totals": {
            "questions": len(questions),
            "knowledge": len(knowledge),
            "format": len(fmt),
            "unmapped": len(no_topic),
            "topics": len(topics),
        },
        "integrity": {
            "questions_without_topic": len(no_topic),
            "questions_without_phase": len(no_phase),
            "invalid_prerequisites": len(invalid_prereqs),
            "circular_dependencies": len(cycles),
            "phase_inversions": len(phase_inversions),
            "invalid_cognitive_levels": len(bad_level),
            "invalid_axis": len(bad_axis),
        },
        "phases": phase_report,
        "empty_topics": empty_topics,
        "needs_review": len(review),
        "errors": errors,
        "warnings": warnings,
        "ok": not errors,
    }


def render(r: dict) -> None:
    t = r["totals"]
    print("Curriculum Validation")
    print("---------------------")
    print(f"Questions:              {t['questions']:>6}")
    print(f"Knowledge:              {t['knowledge']:>6}")
    print(f"Format:                 {t['format']:>6}")
    print(f"Unmapped:               {t['unmapped']:>6}")
    print(f"Topics:                 {t['topics']:>6}")
    print()
    for k, v in r["integrity"].items():
        print(f"{k.replace('_', ' ').capitalize():<28}{v:>6}")
    print()
    for code, info in r["phases"].items():
        print(
            f"{code} {info['name']:<36} {info['status']:<16}"
            f"({info['knowledge']} knowledge, {info['entry_points']} entry)"
        )
    print()
    print(f"Classifications needing review: {r['needs_review']}")
    if r["warnings"]:
        print()
        print("Warnings:")
        for w in r["warnings"]:
            print(f"  ! {w}")
    if r["errors"]:
        print()
        print("ERRORS:")
        for e in r["errors"]:
            print(f"  x {e}")
    print()
    print("RESULT:", "PASS" if r["ok"] else "FAIL")


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()
    report = await collect()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        render(report)
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    asyncio.run(main())
