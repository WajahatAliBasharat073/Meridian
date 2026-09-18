"""Multiple-choice concept drill for a DSA topic, derived from the topic
guide rather than authored or generated.

Why derived and not written: every question, every correct answer and
every distractor here is an existing curated string from `topic_guides`
(its `types`, `operations`, `must_know`, `pitfalls`). Nothing is invented,
so a wrong distractor can't quietly teach a wrong fact -- which is the
usual way an MCQ bank rots. It also means the bank tracks the guide: fix
a complexity in the guide and the drill is fixed with it.

Why MCQ *here* when the topic gate deliberately refuses multiple choice
(see app/grading.py -- "recognising the right answer from a list is not
the same as holding the model in your head"): these test different
things and sit at different layers. The gate proves authorship and
mental model, costs an LLM call, and runs once per topic per 30 days.
This is the factual layer -- complexities, variant selection, which
technique fits, what breaks -- graded deterministically in-process, so
it's free, instant, offline-safe, and cheap enough to repeat. It gates
nothing.

Bank size is not a number anyone picked: one question per curated fact
gives 20 (Binary Search) to 30 (Graphs), because that is how much
surface area each guide actually declares. A session then samples a
fixed 12, stratified across the four kinds -- smaller than the bank on
purpose, so repeated drills don't degenerate into remembering answer
positions.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Any, Literal

QuestionKind = Literal["complexity", "variant", "pitfall", "technique"]

SESSION_SIZE = 12

# Per-kind quota for one session. Sums to SESSION_SIZE; a kind that can't
# fill its quota (a guide with no usable complexities, say) hands the
# remainder back and the others take it up, so a session is always
# SESSION_SIZE long whenever the bank is big enough at all.
SESSION_QUOTA: dict[QuestionKind, int] = {
    "complexity": 3,
    "variant": 3,
    "pitfall": 3,
    "technique": 3,
}

OPTIONS_PER_QUESTION = 4

# A complexity cell that carries no actual complexity. `oop` uses an em
# dash, being a revision topic with nothing to measure.
_NON_COMPLEXITIES = {"", "-", "--", "—", "–", "n/a", "na", "none"}

# Fallback distractors for a guide that declares fewer than
# OPTIONS_PER_QUESTION distinct complexities of its own (Binary Search
# declares three). These are the standard ladder, so they stay plausible
# without being drawn from an unrelated topic's exotica.
_COMPLEXITY_LADDER = [
    "O(1)",
    "O(log n)",
    "O(n)",
    "O(n log n)",
    "O(n^2)",
]

# Tokens too common to signal that two curated strings mean the same
# thing. Kept deliberately small: over-stopping makes the similarity
# guard blind, which is the failure that matters here.
_STOPWORDS = frozenset(
    [
        "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "for", "from",
        "has", "have", "if", "in", "into", "is", "it", "its", "it's", "not", "of", "on",
        "or", "that", "the", "their", "then", "this", "to", "too", "use", "used", "uses",
        "using", "was", "were", "when", "where", "which", "while", "with", "without",
        "you", "your",
    ]
)


@dataclass(frozen=True)
class DrillQuestion:
    """One MCQ. `options` is already in presentation order and
    `answer_index` points into it, both fixed by the session seed."""

    id: str
    kind: QuestionKind
    prompt: str
    options: list[str]
    answer_index: int
    # Shown after grading, never before: the curated note behind the
    # answer, or which topic a wrong option actually belongs to.
    explanation: str = ""


@dataclass
class TopicGuideFixture:
    """The slice of a `topic_guides` row this engine reads. A fixture so
    the engine stays a pure function over plain data, testable without a
    database."""

    topic: str
    display_name: str
    types: list[Any] = field(default_factory=list)
    operations: list[Any] = field(default_factory=list)
    must_know: list[Any] = field(default_factory=list)
    pitfalls: list[Any] = field(default_factory=list)


def _stem(word: str) -> str:
    """Crude suffix stripping, enough to make inflections of the same word
    compare equal.

    Not linguistics -- it exists for one concrete reason: Binary Search
    warns "mid = (lo + hi) / 2 overflowing" and Arrays warns "Integer
    overflow when ... computing mid as (lo + hi)". Without stemming those
    share only the token "mid", slip under every similarity threshold,
    and the Binary Search line gets offered as a wrong answer to an
    Arrays question that lists it as a pitfall.
    """
    for suffix in ("ing", "ed", "es", "s"):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def _token_list(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9']+", text.lower())
    return [_stem(w) for w in words if w not in _STOPWORDS and len(w) > 2]


def _tokens(text: str) -> frozenset[str]:
    return frozenset(_token_list(text))


def _head(text: str) -> str | None:
    """The first significant word. Curated technique and pitfall strings
    lead with the thing they are about -- "Sliding window, both...",
    "Two pointers - opposite ends...", "Kadane's algorithm for..." -- so
    a shared head is a much stronger signal that two strings name the
    same idea than overall word overlap is."""
    words = _token_list(text)
    return words[0] if words else None


def _doc_frequency(guides: list[TopicGuideFixture]) -> dict[str, int]:
    """How many topics each stemmed word appears in, across all pitfalls
    and techniques.

    Used to tell an incidental shared word from a shared *concept*.
    "loop" or "input" show up all over the corpus and mean nothing;
    "window" and "shrink" appear in two topics, so a candidate sharing
    both with something this topic already claims is describing the same
    idea in different words. Same intuition as the IDF weighting the
    curriculum de-duplicator uses.
    """
    freq: dict[str, int] = {}
    for g in guides:
        vocabulary: set[str] = set()
        for text in (*g.pitfalls, *g.must_know):
            vocabulary |= _tokens(str(text))
        for token in vocabulary:
            freq[token] = freq.get(token, 0) + 1
    return freq


# A word in at most this many topics is distinctive enough that sharing
# it is evidence of a shared concept rather than shared English.
_RARE_IN_AT_MOST = 3


def _too_similar(
    candidate: str, avoid: list[str], doc_freq: dict[str, int] | None = None
) -> bool:
    """Whether a borrowed distractor restates something that is true for
    this topic, which would make it a second correct answer.

    This is not cosmetic. The real guides collide: Graphs warns "Marking
    visited on dequeue instead of enqueue" and Stacks & Queues warns
    "Marking BFS nodes visited on dequeue instead of on enqueue"; BST
    warns "Assuming O(log n) without balance" and Binary Trees warns
    "Claiming O(log n) on a tree that is not balanced". Borrowing either
    across those pairs would produce a question with two right answers.
    """
    cand = _tokens(candidate)
    if not cand:
        return True
    cand_head = _head(candidate)
    for other in avoid:
        shared = cand & _tokens(other)
        if not shared:
            continue
        # Jaccard rather than raw overlap: two long strings sharing three
        # incidental words are unrelated, two short ones sharing three are
        # the same statement.
        union = cand | _tokens(other)
        if len(shared) / len(union) >= 0.34 or len(shared) >= 5:
            return True
        # Same technique, different sentence about it. Strings' "Sliding
        # window with a count map (longest/shortest substring problems)"
        # overlaps Arrays' "Sliding window, both fixed-size and
        # variable-size..." on only two words, far under the ratio above
        # -- yet sliding window is squarely an Arrays technique, so
        # borrowing it would offer a second defensible answer.
        if len(shared) >= 2 and (cand_head in shared or _head(other) in shared):
            return True
        # Same concept, nowhere near the head of either sentence. Strings
        # warns "Forgetting to shrink the window when the constraint is
        # violated"; Arrays warns "Off-by-one in loop bounds and in window
        # shrink conditions". They share only "window" and "shrink" -- but
        # both words are rare across the corpus, so sharing both is the
        # concept, not coincidence.
        if doc_freq is not None:
            rare_shared = [t for t in shared if doc_freq.get(t, 0) <= _RARE_IN_AT_MOST]
            if len(rare_shared) >= 2:
                return True
    return False


def _distinct(values: list[str]) -> list[str]:
    """Order-preserving dedup -- bank order must not depend on set
    iteration order, or the same seed would give different sessions."""
    seen: set[str] = set()
    out: list[str] = []
    for v in values:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _complexity_questions(guide: TopicGuideFixture) -> list[DrillQuestion]:
    ops = [o for o in guide.operations if isinstance(o, dict)]
    usable = [
        o
        for o in ops
        if str(o.get("op", "")).strip()
        and str(o.get("complexity", "")).strip().lower() not in _NON_COMPLEXITIES
    ]
    own = _distinct([str(o["complexity"]).strip() for o in usable])

    out: list[DrillQuestion] = []
    for op in usable:
        correct = str(op["complexity"]).strip()
        pool = [c for c in own if c != correct]
        pool += [c for c in _COMPLEXITY_LADDER if c != correct and c not in pool]
        if len(pool) < OPTIONS_PER_QUESTION - 1:
            continue
        note = str(op.get("note", "")).strip()
        out.append(
            DrillQuestion(
                id=f"{guide.topic}:complexity:{len(out)}",
                kind="complexity",
                prompt=f"{guide.display_name} — what is the complexity of: {str(op['op']).strip()}?",
                options=[correct, *pool[: OPTIONS_PER_QUESTION - 1]],
                answer_index=0,
                explanation=note,
            )
        )
    return out


def _variant_questions(guide: TopicGuideFixture) -> list[DrillQuestion]:
    types = [
        t
        for t in guide.types
        if isinstance(t, dict) and str(t.get("name", "")).strip() and str(t.get("note", "")).strip()
    ]
    names = _distinct([str(t["name"]).strip() for t in types])
    if len(names) < OPTIONS_PER_QUESTION:
        return []

    out: list[DrillQuestion] = []
    for t in types:
        correct = str(t["name"]).strip()
        pool = [n for n in names if n != correct]
        out.append(
            DrillQuestion(
                id=f"{guide.topic}:variant:{len(out)}",
                kind="variant",
                prompt=(
                    f"Which {guide.display_name} variant is this? "
                    f"“{str(t['note']).strip()}”"
                ),
                options=[correct, *pool[: OPTIONS_PER_QUESTION - 1]],
                answer_index=0,
                explanation=f"{correct} — {str(t['note']).strip()}",
            )
        )
    return out


def _round_robin_by_owner(items: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Reorder (owner, text) pairs so consecutive entries come from
    different owners.

    The input arrives grouped by topic, so slicing off the front of it
    took all three distractors from whichever topic happened to sit next
    in `seq` -- every wrong option for an Arrays question came from
    Strings. That is a tell: you can pick the odd one out without knowing
    anything about arrays, which is exactly the way an MCQ bank stops
    measuring what it claims to.
    """
    by_owner: dict[str, list[tuple[str, str]]] = {}
    for owner, text in items:
        by_owner.setdefault(owner, []).append((owner, text))
    out: list[tuple[str, str]] = []
    while by_owner:
        for owner in list(by_owner):
            out.append(by_owner[owner].pop(0))
            if not by_owner[owner]:
                del by_owner[owner]
    return out


def _borrowed_questions(
    guide: TopicGuideFixture,
    kind: QuestionKind,
    own_items: list[str],
    others: list[tuple[str, str]],
    prompt: str,
    doc_freq: dict[str, int],
    avoid: list[str] | None = None,
) -> list[DrillQuestion]:
    """Questions whose distractors are borrowed from other topics --
    used for pitfalls and techniques, where the curated string *is* the
    answer and there is nothing within the topic to contrast it against.

    `others` is (display_name, text) so the explanation can say where a
    wrong option actually came from, which is the useful part of getting
    it wrong.
    """
    disallowed = avoid if avoid is not None else own_items
    pool = _round_robin_by_owner(
        [
            (owner, text)
            for owner, text in others
            if not _too_similar(text, disallowed, doc_freq)
        ]
    )
    if len(pool) < OPTIONS_PER_QUESTION - 1:
        return []

    out: list[DrillQuestion] = []
    for index, item in enumerate(own_items):
        # Walk a different window of the pool per question, so two
        # questions of the same kind don't share their distractors.
        # The stride is deliberately one *more* than the number of
        # distractors taken: stepping by exactly that number divides
        # evenly into a small pool, which wraps the window back onto an
        # earlier question's exact set.
        offset = (index * OPTIONS_PER_QUESTION) % len(pool)
        rotated = pool[offset:] + pool[:offset]
        # ...and take at most one per owner, so the wrong options can't
        # all be from one topic.
        picked: list[tuple[str, str]] = []
        used_owners: set[str] = set()
        for owner, text in rotated:
            if owner in used_owners:
                continue
            picked.append((owner, text))
            used_owners.add(owner)
            if len(picked) == OPTIONS_PER_QUESTION - 1:
                break
        if len(picked) < OPTIONS_PER_QUESTION - 1:
            continue
        out.append(
            DrillQuestion(
                id=f"{guide.topic}:{kind}:{len(out)}",
                kind=kind,
                prompt=prompt,
                options=[item, *[text for _, text in picked]],
                answer_index=0,
                explanation=(
                    "The other options are real, but belong to: "
                    + ", ".join(owner for owner, _ in picked)
                    + "."
                ),
            )
        )
    return out


def build_bank(
    guide: TopicGuideFixture, other_guides: list[TopicGuideFixture]
) -> list[DrillQuestion]:
    """Every question this topic's curated facts support, in stable order.

    One per operation (complexity), per type (variant), per pitfall and
    per must-know technique -- so the bank is as large as the guide is
    detailed, 20 to 30 in practice, and never padded with near-duplicates.
    """
    pitfall_pool = [
        (g.display_name, str(p).strip())
        for g in other_guides
        if g.topic != guide.topic
        for p in g.pitfalls
        if str(p).strip()
    ]
    technique_pool = [
        (g.display_name, str(m).strip())
        for g in other_guides
        if g.topic != guide.topic
        for m in g.must_know
        if str(m).strip()
    ]

    own_pitfalls = _distinct([str(p).strip() for p in guide.pitfalls if str(p).strip()])
    own_techniques = _distinct([str(m).strip() for m in guide.must_know if str(m).strip()])

    # A distractor must not be true for this topic, and "true for this
    # topic" spans both lists: a borrowed *pitfall* about window shrinking
    # is wrong to offer when this topic's *techniques* include sliding
    # windows, so each guard sees everything the topic claims.
    doc_freq = _doc_frequency(other_guides or [guide])
    own_everything = own_pitfalls + own_techniques

    return [
        *_complexity_questions(guide),
        *_variant_questions(guide),
        *_borrowed_questions(
            guide,
            "pitfall",
            own_pitfalls,
            pitfall_pool,
            f"Which of these is a documented pitfall for {guide.display_name}?",
            doc_freq,
            avoid=own_everything,
        ),
        *_borrowed_questions(
            guide,
            "technique",
            own_techniques,
            technique_pool,
            f"Which of these is a core technique to hold for {guide.display_name}?",
            doc_freq,
            avoid=own_everything,
        ),
    ]


def sample_session(
    bank: list[DrillQuestion], seed: int, size: int = SESSION_SIZE
) -> list[DrillQuestion]:
    """A stratified sample of `size` questions, plus option shuffling,
    both fixed by `seed`.

    Deterministic on purpose: the session is never stored, so grading
    regenerates it from (topic, seed) and compares. Stratified so a
    session can't come out as twelve pitfalls and no complexities.
    """
    rng = random.Random(seed)
    by_kind: dict[QuestionKind, list[DrillQuestion]] = {}
    for q in bank:
        by_kind.setdefault(q.kind, []).append(q)
    for questions in by_kind.values():
        rng.shuffle(questions)

    picked: list[DrillQuestion] = []
    leftovers: list[DrillQuestion] = []
    for kind, quota in SESSION_QUOTA.items():
        available = by_kind.get(kind, [])
        picked.extend(available[:quota])
        leftovers.extend(available[quota:])

    # A kind that couldn't fill its quota is covered by whatever the
    # richer kinds had spare, so the session length stays fixed.
    rng.shuffle(leftovers)
    picked.extend(leftovers[: max(0, size - len(picked))])
    picked = picked[:size]
    rng.shuffle(picked)

    out: list[DrillQuestion] = []
    for q in picked:
        order = list(range(len(q.options)))
        rng.shuffle(order)
        out.append(
            DrillQuestion(
                id=q.id,
                kind=q.kind,
                prompt=q.prompt,
                options=[q.options[i] for i in order],
                answer_index=order.index(q.answer_index),
                explanation=q.explanation,
            )
        )
    return out


@dataclass(frozen=True)
class GradedQuestion:
    id: str
    prompt: str
    options: list[str]
    answer_index: int
    chosen_index: int | None
    correct: bool
    explanation: str


@dataclass(frozen=True)
class DrillResult:
    score: float
    correct_count: int
    total: int
    graded: list[GradedQuestion]


def grade_session(session: list[DrillQuestion], chosen: list[int | None]) -> DrillResult:
    """Deterministic, in-process, no LLM. An unanswered question is
    wrong, same as the closed-book stage treats a blank."""
    graded: list[GradedQuestion] = []
    for i, q in enumerate(session):
        pick = chosen[i] if i < len(chosen) else None
        if pick is not None and not (0 <= pick < len(q.options)):
            pick = None
        graded.append(
            GradedQuestion(
                id=q.id,
                prompt=q.prompt,
                options=q.options,
                answer_index=q.answer_index,
                chosen_index=pick,
                correct=pick == q.answer_index,
                explanation=q.explanation,
            )
        )
    hits = sum(1 for g in graded if g.correct)
    return DrillResult(
        score=hits / len(graded) if graded else 0.0,
        correct_count=hits,
        total=len(graded),
        graded=graded,
    )
