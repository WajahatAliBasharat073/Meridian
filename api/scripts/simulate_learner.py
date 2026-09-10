"""Drive the curriculum engine for N days against the real question bank.

This is how the rebuild is judged. The old picker's failure was only
visible by running it -- the code looked reasonable -- so the replacement
ships with the means to run it too.

Profiles model who the learner actually is, not just how much they have
done. An "uneven" learner is the realistic case and the hardest: strong
Python, medium ML, weak deep learning, strong LLMs, which is exactly the
shape of someone who has been building with APIs before studying the
fundamentals underneath them.

Usage:
    python -m scripts.simulate_learner --profile beginner --days 10
    python -m scripts.simulate_learner --profile uneven --days 15
    python -m scripts.simulate_learner --profile advanced --days 5 --explain
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import date, timedelta

from sqlalchemy import select

from app.db import SessionLocal
from app.engines.curriculum import (
    CLEARED_AT,
    CurriculumQuestion,
    ProgressFixture,
    build_daily_plan,
    build_learner_state,
)
from app.models.questions import CurriculumTopic, Question
from scripts.curriculum_graph import PHASES

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: Per-profile topic knowledge, as {phase or topic-prefix: mastery 0..1}.
#: "How well does this person already know this area", used to seed
#: progress before day one.
PROFILES: dict[str, dict[str, float]] = {
    # Genuinely new. Nothing seeded.
    "beginner": {},
    # Has done classical ML properly, has not touched deep learning.
    "intermediate": {"phase:0": 1.0, "phase:1": 0.85},
    # Everything through transformers.
    "advanced": {"phase:0": 1.0, "phase:1": 1.0, "phase:2": 0.9, "phase:3": 0.8},
    # Strong where they have built, weak where they have not. The realistic
    # engineer: ships LLM features, never learned backprop.
    "uneven": {
        "python_for_ml": 1.0,
        "numpy_vectorization": 1.0,
        "pandas_data": 1.0,
        "phase:1": 0.5,
        "phase:2": 0.1,
        "llm_architecture": 0.9,
        "llm_inference": 0.9,
        "tool_calling": 0.8,
    },
    # Answers everything but retains little: mastery seeded at 2, below the
    # cleared threshold, so nothing counts and reinforcement should dominate.
    "weak": {"phase:0": 0.0},
}


def seed_progress(
    profile: str, questions: list[CurriculumQuestion], topic_phase: dict[str, int], today: date
) -> dict[int, ProgressFixture]:
    spec = PROFILES[profile]
    if not spec:
        return {}
    out: dict[int, ProgressFixture] = {}
    # Deterministic: take the first N of each topic's questions rather than
    # sampling, so two runs of the same profile are identical.
    by_topic: dict[str, list[CurriculumQuestion]] = {}
    for q in questions:
        if q.topic and q.axis == "knowledge":
            by_topic.setdefault(q.topic, []).append(q)

    for topic, qs in by_topic.items():
        frac = spec.get(topic)
        if frac is None:
            frac = spec.get(f"phase:{topic_phase.get(topic, 9)}")
        if frac is None:
            continue
        qs = sorted(qs, key=lambda q: q.question_id)
        take = int(round(len(qs) * frac))
        for q in qs[:take]:
            out[q.question_id] = ProgressFixture(
                q.question_id, CLEARED_AT + 1, today - timedelta(days=45)
            )
    return out


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="beginner", choices=sorted(PROFILES))
    ap.add_argument("--days", type=int, default=10)
    ap.add_argument("--count", type=int, default=3, help="questions per day")
    ap.add_argument("--explain", action="store_true", help="show reason codes")
    args = ap.parse_args()

    today = date(2026, 9, 10)

    async with SessionLocal() as s:
        topic_rows = list((await s.execute(select(CurriculumTopic))).scalars())
        q_rows = list((await s.execute(select(Question))).scalars())

    from app.engines.curriculum import TopicFixture

    topics = [
        TopicFixture(t.slug, t.name, t.phase, tuple(t.prereqs or []), t.gated, t.order_index)
        for t in sorted(topic_rows, key=lambda t: t.order_index)
    ]
    topic_phase = {t.slug: t.phase for t in topics}
    titles = {q.id: q.title for q in q_rows}
    questions = [
        CurriculumQuestion(
            question_id=q.id,
            topic=q.topic,
            phase=q.phase,
            axis=q.axis or "knowledge",
            cognitive_level=q.cognitive_level if q.cognitive_level is not None else 2,
            primary_format=q.primary_format or "concept",
            preview=bool(q.preview),
            interview_priority=q.priority,
        )
        for q in q_rows
    ]
    with_content = {q.topic for q in questions if q.axis == "knowledge" and q.topic}
    empty = frozenset(t.slug for t in topics if t.slug not in with_content)

    progress = seed_progress(args.profile, questions, topic_phase, today)
    state = build_learner_state(topics, questions, progress, empty)
    print(f"profile: {args.profile}   seeded progress: {len(progress)} questions")
    print(f"start:   phase P{state.reached_phase} ({PHASES[state.reached_phase]})")
    print(f"         current topic: {state.current_topic}")
    print(f"         empty topics treated as satisfied: {len(empty)}")
    print()

    for day in range(args.days):
        d = today + timedelta(days=day)
        plan = build_daily_plan(
            topics, questions, progress, d, count=args.count, empty_topics=empty
        )
        print(f"Day {day + 1}  [P{plan.current_phase} - {plan.current_topic}]")
        if plan.blocked_reason:
            print(f"   BLOCKED: {plan.blocked_reason}")
            break
        for sel in plan.selections:
            title = titles.get(sel.question_id, "?")[:62]
            print(f"   {sel.slot:<10} {str(sel.topic):<26} {title}")
            if args.explain:
                print(f"              score={sel.score}  {[r.value for r in sel.reasons]}")
            # The learner answers and clears it.
            progress[sel.question_id] = ProgressFixture(sel.question_id, CLEARED_AT + 1, d)
        print()

    final = build_learner_state(topics, questions, progress, empty)
    print(f"end:     phase P{final.reached_phase} ({PHASES[final.reached_phase]})")
    print(f"         current topic: {final.current_topic}")


if __name__ == "__main__":
    asyncio.run(main())
