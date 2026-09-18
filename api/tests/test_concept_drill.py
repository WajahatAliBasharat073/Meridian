"""Unit coverage for the MCQ concept drill engine.

The interesting cases are all about distractor honesty: a borrowed
distractor that happens to be true for this topic makes a question with
two right answers, and the real guides do collide that way. Those exact
collisions are pinned here.
"""

from __future__ import annotations

from app.engines.concept_drill import (
    OPTIONS_PER_QUESTION,
    SESSION_SIZE,
    DrillQuestion,
    TopicGuideFixture,
    build_bank,
    grade_session,
    sample_session,
)

ARRAY = TopicGuideFixture(
    topic="array",
    display_name="Arrays",
    types=[
        {"name": "Static array", "note": "Fixed capacity; size known at allocation."},
        {"name": "Dynamic array (list, vector)", "note": "Grows by reallocating and copying."},
        {"name": "2D array / matrix", "note": "Row-major layout; traversal order affects cache."},
        {"name": "Prefix-sum array", "note": "Precomputed cumulative sums make any range sum O(1)."},
        {"name": "Sorted array", "note": "Unlocks binary search and two-pointer convergence."},
    ],
    operations=[
        {"op": "Access by index", "note": "Direct address arithmetic.", "complexity": "O(1)"},
        {"op": "Append (dynamic array)", "note": "O(n) on the resize.", "complexity": "O(1) amortised"},
        {"op": "Insert at arbitrary index", "note": "Everything after shifts.", "complexity": "O(n)"},
        {"op": "Binary search", "note": "Requires sorted.", "complexity": "O(log n)"},
        {"op": "Sort", "note": "Comparison-based.", "complexity": "O(n log n)"},
    ],
    must_know=[
        "Kadane's algorithm for maximum subarray",
        "Prefix sums and prefix-sum + hash map for subarray-sum problems",
        "In-place partition / Dutch national flag three-way split",
    ],
    pitfalls=[
        "Mutating a list while iterating over it",
        "Aliasing: assigning a list assigns a reference, not a copy",
        "Copying a subarray inside a loop, turning O(n) into O(n^2)",
    ],
)

GRAPHS = TopicGuideFixture(
    topic="graphs",
    display_name="Graphs",
    types=[{"name": "Adjacency list", "note": "Sparse graphs."}],
    operations=[{"op": "BFS", "note": "Unweighted shortest path.", "complexity": "O(V + E)"}],
    must_know=["Dijkstra, and why it fails with negative edges"],
    pitfalls=["Marking visited on dequeue instead of enqueue, so nodes enter the queue twice"],
)

STACKS = TopicGuideFixture(
    topic="stacks_queues",
    display_name="Stacks & Queues",
    types=[{"name": "Monotonic stack", "note": "Next greater element sweeps."}],
    operations=[{"op": "push / pop", "note": "Amortised.", "complexity": "O(1)"}],
    must_know=["Deque-based sliding window maximum"],
    # Collides with the Graphs pitfall above -- this is the case the
    # similarity guard exists for.
    pitfalls=["Marking BFS nodes visited on dequeue instead of on enqueue, so nodes are processed twice"],
)

OOP = TopicGuideFixture(
    topic="oop",
    display_name="Object-Oriented Programming",
    types=[{"name": "Composition", "note": "Has-a rather than is-a."}],
    # A revision topic with no measurable complexities -- the real guide
    # stores an em dash here.
    operations=[{"op": "n/a", "note": "", "complexity": "—"}],
    must_know=["Composition over inheritance, and the concrete failure inheritance causes"],
    pitfalls=["God classes that own unrelated responsibilities"],
)

STRINGS = TopicGuideFixture(
    topic="strings",
    display_name="Strings",
    types=[{"name": "Immutable string", "note": "Concatenation allocates."}],
    operations=[{"op": "Concatenate in a loop", "note": "Use join.", "complexity": "O(n^2)"}],
    must_know=["KMP prefix function and what it actually computes"],
    pitfalls=["Building strings with += in a loop instead of a buffer + join"],
)

DP = TopicGuideFixture(
    topic="dp",
    display_name="Dynamic Programming",
    types=[{"name": "Tabulation", "note": "Bottom-up over a table."}],
    operations=[{"op": "0-1 knapsack", "note": "Capacity dimension.", "complexity": "O(n*W)"}],
    must_know=["Stating the state and transition in words before writing code"],
    pitfalls=["Jumping to a table before the recurrence is right"],
)

HEAPS = TopicGuideFixture(
    topic="heaps",
    display_name="Heaps & Priority Queues",
    types=[{"name": "Min-heap", "note": "Smallest at the root."}],
    operations=[{"op": "Push", "note": "Sift up.", "complexity": "O(log n)"}],
    must_know=["Size-k min-heap for k largest, size-k max-heap for k smallest"],
    pitfalls=["Assuming heap iteration order is sorted — only repeated pops are"],
)

# Enough owners that the borrowed pool exceeds one question's window --
# with only three borrowable items in total, every question would be
# forced onto the same three distractors and the rotation below couldn't
# be observed at all.
ALL = [ARRAY, GRAPHS, STACKS, OOP, STRINGS, DP, HEAPS]


def test_bank_has_one_question_per_curated_fact() -> None:
    bank = build_bank(ARRAY, ALL)
    kinds = [q.kind for q in bank]
    assert kinds.count("complexity") == len(ARRAY.operations)
    assert kinds.count("variant") == len(ARRAY.types)
    assert kinds.count("pitfall") == len(ARRAY.pitfalls)
    assert kinds.count("technique") == len(ARRAY.must_know)


def test_every_question_has_four_distinct_options_and_a_valid_answer() -> None:
    for guide in ALL:
        for q in build_bank(guide, ALL):
            assert len(q.options) == OPTIONS_PER_QUESTION, q.prompt
            assert len(set(q.options)) == OPTIONS_PER_QUESTION, q.prompt
            assert 0 <= q.answer_index < len(q.options)


def test_a_distractor_is_never_a_pitfall_that_is_also_true_for_this_topic() -> None:
    # Graphs and Stacks & Queues both warn about marking visited on
    # dequeue. Borrowing either one across those two topics would give a
    # question two correct answers.
    for guide, other in ((GRAPHS, STACKS), (STACKS, GRAPHS)):
        for q in build_bank(guide, ALL):
            if q.kind != "pitfall":
                continue
            borrowed = [o for i, o in enumerate(q.options) if i != q.answer_index]
            assert not any("dequeue" in o for o in borrowed), (
                f"{guide.topic} borrowed {other.topic}'s colliding pitfall: {borrowed}"
            )


def test_borrowed_distractors_come_from_different_topics() -> None:
    # The first cut took all three distractors off the front of a pool
    # grouped by topic, so every wrong option for an Arrays question came
    # from Strings -- answerable by spotting the odd one out, without
    # knowing arrays. Each wrong option must come from a distinct topic.
    owners_by_text = {
        text: g.display_name for g in ALL for text in (*g.pitfalls, *g.must_know)
    }
    for q in build_bank(ARRAY, ALL):
        if q.kind not in ("pitfall", "technique"):
            continue
        borrowed = [o for i, o in enumerate(q.options) if i != q.answer_index]
        owners = [owners_by_text[b] for b in borrowed]
        assert len(set(owners)) == len(owners), f"{q.prompt}: all from {owners}"


def test_two_questions_of_a_kind_do_not_reuse_the_same_distractors() -> None:
    by_kind: dict[str, list[frozenset[str]]] = {}
    for q in build_bank(ARRAY, ALL):
        if q.kind not in ("pitfall", "technique"):
            continue
        borrowed = frozenset(o for i, o in enumerate(q.options) if i != q.answer_index)
        by_kind.setdefault(q.kind, []).append(borrowed)
    for kind, sets in by_kind.items():
        assert len(sets) == len(set(sets)), f"{kind} questions share a distractor set"


def test_complexity_questions_are_skipped_where_there_is_no_complexity() -> None:
    bank = build_bank(OOP, ALL)
    assert [q for q in bank if q.kind == "complexity"] == []
    # ...but the topic still yields a drill from its other facts, rather
    # than coming back empty because one category had nothing to measure.
    assert {q.kind for q in bank} == {"pitfall", "technique"}


def test_correct_answer_is_not_always_the_first_option() -> None:
    bank = build_bank(ARRAY, ALL)
    positions = {sample_session(bank, seed=s, size=8)[0].answer_index for s in range(12)}
    assert len(positions) > 1


def test_same_seed_gives_the_same_session_and_different_seeds_differ() -> None:
    bank = build_bank(ARRAY, ALL)
    a = sample_session(bank, seed=7)
    b = sample_session(bank, seed=7)
    c = sample_session(bank, seed=8)
    assert [q.id for q in a] == [q.id for q in b]
    assert [q.options for q in a] == [q.options for q in b]
    assert [q.id for q in a] != [q.id for q in c]


def test_session_is_stratified_across_kinds_when_the_bank_allows() -> None:
    bank = build_bank(ARRAY, ALL)
    session = sample_session(bank, seed=3)
    kinds = {q.kind for q in session}
    # Arrays has all four kinds available, so a session must not collapse
    # onto one of them.
    assert kinds == {"complexity", "variant", "pitfall", "technique"}


def test_session_is_capped_at_the_requested_size() -> None:
    bank = build_bank(ARRAY, ALL)
    assert len(sample_session(bank, seed=1)) == min(SESSION_SIZE, len(bank))
    assert len(sample_session(bank, seed=1, size=5)) == 5


def test_grading_counts_hits_and_treats_unanswered_as_wrong() -> None:
    session = [
        DrillQuestion(
            id="q1", kind="complexity", prompt="p1", options=["a", "b"], answer_index=1
        ),
        DrillQuestion(
            id="q2", kind="variant", prompt="p2", options=["a", "b"], answer_index=0
        ),
        DrillQuestion(
            id="q3", kind="pitfall", prompt="p3", options=["a", "b"], answer_index=0
        ),
    ]
    result = grade_session(session, [1, 1, None])
    assert result.correct_count == 1
    assert result.total == 3
    assert result.score == 1 / 3
    assert [g.correct for g in result.graded] == [True, False, False]
    assert result.graded[2].chosen_index is None


def test_grading_rejects_an_out_of_range_choice_rather_than_crashing() -> None:
    session = [
        DrillQuestion(id="q1", kind="complexity", prompt="p", options=["a", "b"], answer_index=0)
    ]
    result = grade_session(session, [99])
    assert result.correct_count == 0
    assert result.graded[0].chosen_index is None


def test_a_distractor_never_names_a_technique_this_topic_also_uses() -> None:
    # Strings' "Sliding window with a count map (longest/shortest
    # substring problems)" overlaps Arrays' own "Sliding window, both
    # fixed-size and variable-size..." on only two words -- under the
    # ratio guard -- but sliding window is squarely an Arrays technique,
    # so offering it as a wrong answer gives the question two defensible
    # answers.
    arrays = TopicGuideFixture(
        topic="array",
        display_name="Arrays",
        must_know=["Sliding window, both fixed-size and variable-size with shrink condition"],
        pitfalls=["Mutating a list while iterating over it"],
    )
    strings = TopicGuideFixture(
        topic="strings",
        display_name="Strings",
        must_know=["Sliding window with a count map (longest/shortest substring problems)"],
        pitfalls=["Building strings with += in a loop instead of a buffer + join"],
    )
    for q in build_bank(arrays, [arrays, strings, GRAPHS, DP, HEAPS, OOP]):
        if q.kind != "technique":
            continue
        borrowed = [o for i, o in enumerate(q.options) if i != q.answer_index]
        assert not any("Sliding window" in o for o in borrowed), borrowed


def test_inflected_wording_of_the_same_pitfall_is_still_caught() -> None:
    # Binary Search warns "mid = (lo + hi) / 2 overflowing"; Arrays warns
    # "Integer overflow when ... computing mid as (lo + hi)". Untokenised,
    # "overflow" and "overflowing" don't match, leaving one shared word and
    # letting Binary Search's line be offered as a wrong answer to an
    # Arrays question that lists exactly that pitfall.
    arrays = TopicGuideFixture(
        topic="array",
        display_name="Arrays",
        pitfalls=["Integer overflow when summing or when computing mid as (lo + hi)"],
        must_know=["Kadane's algorithm for maximum subarray"],
    )
    binary_search = TopicGuideFixture(
        topic="binary_search",
        display_name="Binary Search",
        pitfalls=["mid = (lo + hi) / 2 overflowing - use lo + (hi - lo) // 2"],
        must_know=["Binary search on the answer with a monotonic predicate"],
    )
    for q in build_bank(arrays, [arrays, binary_search, GRAPHS, DP, HEAPS, OOP, STRINGS]):
        if q.kind != "pitfall":
            continue
        borrowed = [o for i, o in enumerate(q.options) if i != q.answer_index]
        assert not any("overflow" in o for o in borrowed), borrowed


def test_a_shared_concept_is_caught_even_when_the_wording_starts_differently() -> None:
    # Strings warns "Forgetting to shrink the window when the constraint
    # is violated"; Arrays warns "Off-by-one in loop bounds and in window
    # shrink conditions" and lists sliding windows as a technique. They
    # share only "window" and "shrink", neither at the head of either
    # sentence -- but both words are rare across the corpus, so sharing
    # both means the same concept, and offering the Strings line as a
    # wrong answer for Arrays gives the question two defensible answers.
    arrays = TopicGuideFixture(
        topic="array",
        display_name="Arrays",
        pitfalls=["Off-by-one in loop bounds and in window shrink conditions"],
        must_know=["Sliding window, both fixed-size and variable-size with shrink condition"],
    )
    strings = TopicGuideFixture(
        topic="strings",
        display_name="Strings",
        pitfalls=["Forgetting to shrink the window when the constraint is violated"],
        must_know=["KMP prefix function and what it actually computes"],
    )
    for q in build_bank(arrays, [arrays, strings, GRAPHS, DP, HEAPS, OOP, STACKS]):
        if q.kind not in ("pitfall", "technique"):
            continue
        borrowed = [o for i, o in enumerate(q.options) if i != q.answer_index]
        assert not any("shrink" in o for o in borrowed), borrowed
