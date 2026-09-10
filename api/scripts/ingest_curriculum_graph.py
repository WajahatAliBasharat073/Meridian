"""Seed the topic graph, then classify every question onto it.

Two jobs, both idempotent and both dry-run by default:

1. Upsert `curriculum_topics` from scripts/curriculum_graph.py, which is
   the authored source of truth for the knowledge model.

2. Give every existing question an axis, topic, phase, cognitive level and
   format -- *without touching the question text*. The audit is explicit
   that content decisions (keep / merge / retire) stay separate from
   sequencing, so nothing here rewrites, merges or deletes a question.

Classification is deterministic and records how certain it was:

  exact           the bank's own (module, submodule) label mapped directly
  keyword         a title keyword rule matched
  module_default  nothing matched; fell back to the module's centre of
                  gravity, and is listed for review

That last tier is reported, not hidden. Roughly a third of the bank has a
submodule label too coarse to place precisely -- module D alone has 62
questions labelled only "Regression" -- and claiming the fallback is as
certain as an exact match would be invented precision.

Usage:
    python -m scripts.ingest_curriculum_graph            # dry run
    python -m scripts.ingest_curriculum_graph --apply
    python -m scripts.ingest_curriculum_graph --review   # low-confidence list
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from collections import Counter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal
from app.models.questions import CurriculumTopic, Question
from scripts.curriculum_graph import (
    FORMAT_BY_QUESTION_TYPE,
    KEYWORD_FIRST_MODULES,
    OVERRIDE_KEYWORDS,
    KEYWORD_RULES,
    LEVEL_BY_DIFFICULTY,
    LEVEL_FORMAT_FLOOR,
    LEVEL_KEYWORD_RULES,
    MODULE_DEFAULT,
    PHASES,
    SUBMODULE_MAP,
    TOPIC_BY_SLUG,
    TOPICS,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Which question types are a *format* rather than knowledge. A format
# question still gets a topic (that is what gates it); it just never
# defines where the learner is.
FORMAT_TYPES = {"case_study", "behavioral", "project_deep_dive", "system_design", "coding"}


def classify(q: Question) -> tuple[str, str, str]:
    """-> (topic_slug, confidence, matched_rule)

    Submodule label first, because it is the bank's own considered
    grouping and is right 435 times out of 724. The exception is a module
    whose submodules are coarse buckets rather than topics (see
    KEYWORD_FIRST_MODULES): there the title names the algorithm outright
    and the bucket does not, so the title wins.
    """
    key = (q.module_code or "", q.submodule or "")
    haystack = f"{q.title} {q.tests_for or ''}".lower()

    for pattern, slug in OVERRIDE_KEYWORDS:
        if re.search(pattern, haystack):
            return slug, "keyword", f"override:{pattern}"

    keyword_hit: tuple[str, str] | None = None
    for pattern, slug in KEYWORD_RULES:
        if re.search(pattern, haystack):
            keyword_hit = (slug, pattern)
            break

    if (q.module_code or "") in KEYWORD_FIRST_MODULES and keyword_hit:
        return keyword_hit[0], "keyword", keyword_hit[1]

    if key in SUBMODULE_MAP:
        return SUBMODULE_MAP[key], "exact", f"submodule:{q.submodule}"

    if keyword_hit:
        return keyword_hit[0], "keyword", keyword_hit[1]

    return MODULE_DEFAULT.get(q.module_code or "", "what_is_ml"), "module_default", "fallback"


def cognitive_level(q: Question, fmt: str) -> int:
    """L0 recognition .. L5 design/synthesis.

    Seeded from difficulty, then overridden by an explicit verb in the
    title -- "implement" is application whatever its difficulty says, and
    "design ... at scale" is synthesis even when tagged intermediate.
    """
    level = LEVEL_BY_DIFFICULTY.get(q.difficulty or "", 2)
    title = (q.title or "").lower()
    for pattern, lvl in LEVEL_KEYWORD_RULES:
        if re.search(pattern, title):
            level = lvl
            break
    level = max(level, LEVEL_FORMAT_FLOOR.get(fmt, 0))
    return max(0, min(5, level))


async def run(session: AsyncSession, apply: bool, show_review: bool) -> None:
    # ---- 1. topics ----------------------------------------------------
    existing = {t.slug: t for t in (await session.execute(select(CurriculumTopic))).scalars()}
    added = updated = 0
    for i, t in enumerate(TOPICS):
        row = existing.get(t.slug)
        fields = dict(
            name=t.name,
            phase=t.phase,
            phase_name=PHASES[t.phase],
            prereqs=list(t.prereqs),
            gated=t.gated,
            note=t.note or None,
            order_index=i,
        )
        if row is None:
            if apply:
                session.add(CurriculumTopic(slug=t.slug, **fields))
            added += 1
        else:
            if apply:
                for k, v in fields.items():
                    setattr(row, k, v)
            updated += 1

    # ---- 2. questions -------------------------------------------------
    questions = list((await session.execute(select(Question))).scalars())
    conf_counts: Counter[str] = Counter()
    axis_counts: Counter[str] = Counter()
    phase_counts: Counter[int] = Counter()
    level_counts: Counter[int] = Counter()
    review: list[tuple[Question, str]] = []

    for q in questions:
        slug, confidence, rule = classify(q)
        topic = TOPIC_BY_SLUG[slug]
        axis = "format" if (q.question_type in FORMAT_TYPES) else "knowledge"
        fmt = FORMAT_BY_QUESTION_TYPE.get(q.question_type or "", "concept")
        level = cognitive_level(q, fmt)

        conf_counts[confidence] += 1
        axis_counts[axis] += 1
        phase_counts[topic.phase] += 1
        level_counts[level] += 1
        if confidence == "module_default":
            review.append((q, rule))

        if apply:
            q.axis = axis
            q.topic = slug
            q.phase = topic.phase
            q.cognitive_level = level
            q.primary_format = fmt
            q.classification_confidence = confidence

    # ---- report -------------------------------------------------------
    print(f"topics: {added} new, {updated} updated ({len(TOPICS)} total)")
    print()
    print(f"questions classified: {len(questions)}")
    print("  by axis      :", ", ".join(f"{k}={v}" for k, v in axis_counts.most_common()))
    print("  by confidence:", ", ".join(f"{k}={v}" for k, v in conf_counts.most_common()))
    print()
    print("  by phase:")
    for p in sorted(phase_counts):
        print(f"    P{p} {PHASES[p]:<36} {phase_counts[p]:>4}")
    print("  by cognitive level:")
    for lv in sorted(level_counts):
        print(f"    L{lv} {level_counts[lv]:>4}")

    pct = 100 * conf_counts["module_default"] / max(1, len(questions))
    print()
    print(f"  needs review (module_default): {conf_counts['module_default']} ({pct:.0f}%)")

    if show_review:
        print()
        print("  low-confidence questions:")
        for q, _ in review[:60]:
            print(f"    [{q.module_code:<3} {str(q.submodule)[:22]:<22}] {q.title[:58]}")
        if len(review) > 60:
            print(f"    ... and {len(review) - 60} more")

    if not apply:
        print("\nDry run. Re-run with --apply to write.")
        return
    await session.commit()
    print("\nApplied.")


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--review", action="store_true", help="list low-confidence classifications")
    args = ap.parse_args()
    async with SessionLocal() as session:
        await run(session, args.apply, args.review)


if __name__ == "__main__":
    asyncio.run(main())
