"""Reconcile the 34-day topic-wise DSA sheet with the existing problem bank.

Three jobs, in order:

1. **Backfill `topic` on the existing 270 problems** from their `pattern`,
   so every problem lands in a data-structure section even if the sheet
   never mentions it. `pattern` is a solving-technique axis (arrays_hashing,
   dp_1d, …); `topic` is the axis a study plan is ordered by.

2. **Reconcile each sheet row.** Matched by LeetCode number first, then by
   slug, then by normalised title. A match updates topic / companies; no
   match inserts the problem. Company tags never overwrite a
   non-empty list, and a matched row's existing pattern is left alone —
   the sheet's placement is a study order, not a reclassification.

3. **Insert the classics.** Roughly forty rows are algorithms with no
   LeetCode entry (Dijkstra, KMP, Rat in a Maze, MCM, Heap Sort). They get
   `source="classic"`, `lc_number=None`, `url=None` — never an invented
   number or link.

Usage:
    python -m scripts.ingest_dsa_sheet            # dry run
    python -m scripts.ingest_dsa_sheet --apply
"""
from __future__ import annotations

import argparse
import asyncio
import re
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal
from app.models.problems import Problem, TopicGuide
from scripts.dsa_sheet import rows
from scripts.dsa_topic_guides import TOPIC_GUIDES

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Which data-structure section each existing pattern belongs to. Several
# patterns share a topic on purpose: two-pointer and sliding-window
# problems are array/string problems you solve with a technique, not a
# separate structure to learn.
PATTERN_TO_TOPIC: dict[str, str] = {
    "arrays_hashing": "array",
    "two_pointers": "array",
    "sliding_window": "array",
    "intervals": "array",
    "binary_search": "binary_search",
    "stack": "stacks_queues",
    "linked_list": "linked_list",
    "trees": "binary_trees",
    "tries": "tries",
    "heap": "heaps",
    "backtracking": "recursion_backtracking",
    "graphs": "graphs",
    "advanced_graphs": "graphs",
    "dp_1d": "dp",
    "dp_2d": "dp",
    "greedy": "greedy",
    "math_geometry": "bit_math",
    "bit_manipulation": "bit_math",
}


def _norm(title: str) -> str:
    t = title.lower().replace("&", "and")
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


async def _load(session: AsyncSession) -> list[Problem]:
    return list((await session.execute(select(Problem))).scalars().all())


async def main(apply: bool) -> None:
    async with SessionLocal() as session:
        existing = await _load(session)
        by_lc = {p.lc_number: p for p in existing if p.lc_number is not None}
        by_slug = {p.slug: p for p in existing}
        by_title = {_norm(p.title): p for p in existing}

        backfilled = 0
        for p in existing:
            want = PATTERN_TO_TOPIC.get(p.pattern)
            if want and p.topic != want:
                if apply:
                    p.topic = want
                backfilled += 1

        matched, inserted, skipped_dupes = 0, 0, 0
        seen_days_for: dict[int, set[int]] = {}
        seen_slugs: set[str] = set()
        new_rows: list[dict[str, object]] = []

        for r in rows():
            lc, slug = r["lc"], r["slug"]
            hit = None
            if lc is not None and lc in by_lc:
                hit = by_lc[lc]
            elif slug in by_slug:
                hit = by_slug[slug]
            elif _norm(str(r["title"])) in by_title:
                hit = by_title[_norm(str(r["title"]))]

            if hit is not None:
                # The sheet lists a few problems on two different days. Days
                # are not modelled at all any more (the plan is topic-wise,
                # and `sheet_day` was dropped in migration 0018), so a repeat
                # placement is simply counted and ignored.
                if r["day"] not in seen_days_for.setdefault(hit.id, set()):
                    seen_days_for[hit.id].add(int(r["day"]))  # type: ignore[arg-type]
                    if len(seen_days_for[hit.id]) > 1:
                        skipped_dupes += 1
                if apply:
                    hit.topic = str(r["topic"])
                    if not hit.companies:
                        hit.companies = list(r["companies"])  # type: ignore[arg-type]
                        hit.company_extra_count = int(r["extra"])  # type: ignore[arg-type]
                matched += 1
                continue

            if slug in seen_slugs:
                skipped_dupes += 1
                continue
            seen_slugs.add(str(slug))
            new_rows.append(r)
            inserted += 1

        if apply:
            for r in new_rows:
                session.add(
                    Problem(
                        lc_number=r["lc"],
                        title=r["title"],
                        slug=r["slug"],
                        url=(
                            f"https://leetcode.com/problems/{r['slug']}/"
                            if r["lc"] is not None
                            else None
                        ),
                        pattern=r["pattern"],
                        topic=r["topic"],
                        difficulty=r["difficulty"],
                        source=r["source"],
                        companies=r["companies"],
                        company_extra_count=r["extra"],
                    )
                )

        guides_written = 0
        for g in TOPIC_GUIDES:
            found = (
                await session.execute(select(TopicGuide).where(TopicGuide.topic == g["topic"]))
            ).scalar_one_or_none()
            if apply:
                if found is None:
                    session.add(TopicGuide(**g))
                else:
                    for k, v in g.items():
                        setattr(found, k, v)
            guides_written += 1

        print(f"existing problems           : {len(existing)}")
        print(f"  topic backfilled from pattern: {backfilled}")
        print(f"sheet rows                  : {len(rows())}")
        print(f"  matched to existing problem  : {matched}")
        print(f"  new problems to insert       : {inserted}")
        print(f"  repeat placements skipped    : {skipped_dupes}")
        print(f"topic guides                : {guides_written}")

        if inserted:
            # Grouped by topic, never by day: the sheet's day numbering is
            # kept on the row as provenance but is not how any of this is
            # organised or displayed.
            print("\nnew problems, by topic:")
            for guide in TOPIC_GUIDES:
                topic = guide["topic"]
                rows_for = [r for r in new_rows if r["topic"] == topic]
                if not rows_for:
                    continue
                print(f"\n  {guide['display_name']} ({len(rows_for)}):")
                for r in rows_for:
                    tag = f"LC {r['lc']}" if r["lc"] is not None else "classic"
                    print(f"    {r['difficulty']:<6} {tag:<10} {r['title']}")

        if not apply:
            print("\nDry run. Re-run with --apply to write.")
            return

        await session.commit()
        print(f"\nApplied. Bank is now {len(existing) + inserted} problems.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    asyncio.run(main(args.apply))
