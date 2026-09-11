"""Per-topic curriculum gap report.

`validate_curriculum.py` answers "is P0 healthy overall?" (phase-level).
This answers the narrower, more actionable question LEARNING_SYSTEM_AUDIT.md
demonstrated by hand for two topics: for THIS topic, which of the six
generic angles a topic can be tested from are actually covered, and which
have zero questions?

The six angles are a fixed rubric applied uniformly to every topic --
this deliberately does NOT invent bespoke per-topic content (a script
guessing "topic X needs a question about Y" for 105 different topics
would be fabricating curriculum expertise it doesn't have). What it can
honestly do is check, by keyword, whether *any* existing question for a
topic touches each angle, and say plainly when one has zero coverage.

Usage:
    python -m scripts.curriculum_gap_report
    python -m scripts.curriculum_gap_report --json
    python -m scripts.curriculum_gap_report --topic backpropagation
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from typing import TypedDict

from sqlalchemy import select

from app.db import SessionLocal
from app.models.questions import CurriculumTopic, Question

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# A topic below this many knowledge questions is worth a report at all;
# above it, assume enough volume exists that per-angle gaps are noise.
REPORT_THRESHOLD = 4
# Below this many, treat every angle as unproven rather than trusting a
# single question to have covered it well.
MIN_QUESTIONS_TO_TRUST_COVERAGE = 6

ASPECTS: dict[str, tuple[str, ...]] = {
    "intuition": (r"\bintuitiv", r"\bin plain (terms|words)\b", r"\bwhy does\b", r"\bwhat is the idea\b"),
    "mechanism / derivation": (
        r"\bhow does\b", r"\bderiv", r"\bstep.?by.?step\b", r"\bcomput(e|ation)\b", r"\balgorithm\b",
    ),
    "edge cases / limitations": (
        r"\bedge case\b", r"\bfails?\b", r"\bbreaks?\b", r"\blimitation", r"\bwhen (does|would)\b.*\bnot\b",
    ),
    "debugging": (
        r"\bdebug", r"\bnot working\b", r"\bvanish", r"\bexplod", r"\bnan\b", r"\bdiverg", r"\bwrong\b",
    ),
    "practical implementation": (r"\bimplement", r"\bwrite\b.*\bcode\b", r"\bcode\b"),
    "comparison to alternatives": (r"\bvs\.?\b", r"\bversus\b", r"\bcompared to\b", r"\bdifference between\b", r"\bwhy not\b"),
}


class TopicGapReport(TypedDict):
    topic: str
    name: str
    phase: int
    current_questions: int
    recommended_minimum: int
    coverage_trusted: bool
    missing_aspects: list[str]
    priority: str


def _covered_aspects(titles: list[str]) -> dict[str, bool]:
    joined = " | ".join(t.lower() for t in titles)
    return {aspect: any(re.search(p, joined) for p in patterns) for aspect, patterns in ASPECTS.items()}


async def collect(topic_filter: str | None = None) -> list[TopicGapReport]:
    async with SessionLocal() as s:
        topics = list((await s.execute(select(CurriculumTopic))).scalars())
        questions = list((await s.execute(select(Question))).scalars())

    by_topic: dict[str, list[Question]] = {}
    for q in questions:
        if q.axis == "knowledge" and q.topic:
            by_topic.setdefault(q.topic, []).append(q)

    reports: list[TopicGapReport] = []
    for t in sorted(topics, key=lambda t: (t.phase, t.slug)):
        if not t.gated:
            continue
        if topic_filter and t.slug != topic_filter:
            continue
        qs = by_topic.get(t.slug, [])
        if len(qs) > REPORT_THRESHOLD and not topic_filter:
            continue

        titles = [q.title for q in qs]
        coverage = _covered_aspects(titles) if len(qs) >= 1 else dict.fromkeys(ASPECTS, False)
        trusted = len(qs) >= MIN_QUESTIONS_TO_TRUST_COVERAGE
        missing = [a for a, present in coverage.items() if not present]

        reports.append(
            {
                "topic": t.slug,
                "name": t.name,
                "phase": t.phase,
                "current_questions": len(qs),
                "recommended_minimum": 6 if len(qs) == 0 else max(REPORT_THRESHOLD, 4),
                "coverage_trusted": trusted,
                "missing_aspects": missing,
                "priority": "P0" if t.phase == 0 else ("P1" if len(qs) == 0 else "P2"),
            }
        )
    return reports


def render(reports: list[TopicGapReport]) -> None:
    if not reports:
        print("No gated topics below the reporting threshold -- nothing to flag.")
        return

    for r in reports:
        print(f"\nTopic: {r['name']} ({r['topic']}, phase {r['phase']})")
        print(f"Current questions: {r['current_questions']}")
        print(f"Recommended minimum: {r['recommended_minimum']}")
        if not r["coverage_trusted"]:
            label = "no questions at all" if r["current_questions"] == 0 else "too few to trust coverage"
            print(f"Coverage: NOT ESTABLISHED ({label})")
        if r["missing_aspects"]:
            print("Missing angles:")
            for a in r["missing_aspects"]:
                print(f"  - {a}")
        print(f"Priority: {r['priority']}")

    print(f"\n{len(reports)} topic(s) flagged.")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--topic", default=None, help="Report on one topic slug regardless of its size.")
    args = parser.parse_args()

    reports = await collect(topic_filter=args.topic)

    if args.json:
        print(json.dumps(reports, indent=2))
    else:
        render(reports)


if __name__ == "__main__":
    asyncio.run(main())
