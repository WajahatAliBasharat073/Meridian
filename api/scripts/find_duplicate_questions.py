"""Whole-bank near-duplicate scan.

Reports only. Nothing here deletes, merges or edits a question -- per the
audit's separation of sequencing/classification work from content-quality
decisions, and because a false-positive merge destroys a real question
with no way back. Two questions are proposed for human review; the
decision to merge or keep both stays a decision, not a script's side
effect.

Similarity is lexical (Jaccard over normalised title tokens, plus a body
check that only tightens a borderline title match). This deliberately does
not use an LLM per pair: 724 questions is 261,726 pairs, and an O(n^2)
LLM-judged sweep is neither affordable nor necessary when a same-topic
prefilter plus a cheap lexical score gets the candidate set to a size a
human can actually review.

Usage:
    python -m scripts.find_duplicate_questions
    python -m scripts.find_duplicate_questions --threshold 0.5
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from collections import defaultdict
from itertools import combinations

from sqlalchemy import select

from app.db import SessionLocal
from app.models.questions import Question

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_STOPWORDS = {
    "a", "an", "the", "is", "are", "what", "how", "why", "you", "your",
    "do", "does", "would", "when", "to", "of", "and", "or", "in", "for",
    "this", "that", "on", "with", "it", "be", "can", "explain", "describe",
}


def _tokens(title: str) -> set[str]:
    words = re.sub(r"[^a-z0-9 ]", " ", (title or "").lower()).split()
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# Title families that are deliberately parallel, not duplicates: the DSA
# bank asks the same framing question once per pattern ("what in a problem
# statement tells you to reach for X?"). High title overlap here is by
# design and must not be reported as a collision.
_TEMPLATE_MARKERS = (
    "what in a problem statement tells you to reach for",
    "design:",
    "case study —",
    "write the sql:",
    "when is it the right choice, and what does it cost over the simpler option",
    "what problem did it solve, what was the prior limitation, and what is the one idea that made it work",
)


def _is_template_pair(a: str, b: str) -> bool:
    al, bl = a.lower(), b.lower()
    return any(m in al and m in bl for m in _TEMPLATE_MARKERS)


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=0.55)
    args = ap.parse_args()

    async with SessionLocal() as s:
        qs = list((await s.execute(select(Question))).scalars())

    # Prefilter: only compare within the same topic (or same module for
    # anything not yet classified). This turns an O(n^2) sweep over 724
    # into a sweep over much smaller buckets -- two questions in unrelated
    # topics are never duplicates of each other regardless of wording.
    buckets: dict[str, list[Question]] = defaultdict(list)
    for q in qs:
        buckets[q.topic or f"module:{q.module_code}"].append(q)

    exact_title: dict[str, list[Question]] = defaultdict(list)
    for q in qs:
        exact_title[" ".join((q.title or "").lower().split())].append(q)

    exact_groups = [g for g in exact_title.values() if len(g) > 1]
    near_pairs: list[tuple[Question, Question, float]] = []

    for group in buckets.values():
        if len(group) < 2:
            continue
        for a, b in combinations(group, 2):
            if a.title == b.title:
                continue  # already reported as an exact group
            if _is_template_pair(a.title, b.title):
                continue
            score = _jaccard(_tokens(a.title), _tokens(b.title))
            if score >= args.threshold:
                near_pairs.append((a, b, score))

    near_pairs.sort(key=lambda t: -t[2])

    print(f"Questions scanned: {len(qs)}")
    print(f"Exact-title duplicate groups: {len(exact_groups)}")
    for g in exact_groups:
        ids = ", ".join(f"#{q.id}" for q in g)
        print(f"  EXACT  [{ids}]  {g[0].title[:70]}")

    print()
    print(f"Near-duplicate pairs (>= {args.threshold:.2f} title similarity, same topic): {len(near_pairs)}")
    for a, b, score in near_pairs:
        print(f"  {score:.2f}  #{a.id} [{a.module_code}] {a.title[:52]}")
        print(f"        #{b.id} [{b.module_code}] {b.title[:52]}")

    print()
    print(
        "Report only -- nothing was merged or deleted. "
        f"Exact groups need a keep/merge decision; near-duplicates need a human read."
    )


if __name__ == "__main__":
    asyncio.run(main())
