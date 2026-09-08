"""Study content for the "learn the structure before you solve its problems"
section that renders above each topic's problem list.

Hand-written reference material: definitions, variants, operation
complexities, the techniques that actually unlock the topic, and the
mistakes that cost people interviews. No URLs, no book or video
references, no citations — nothing here is attributed to a source it did
not come from. Complexities are stated only where they are exactly right;
an omitted complexity is better than a wrong one in a study aid.

`oop` is in this list as a *revision* topic (needs_revision=True) rather
than a new one: it is knowledge that was there and lapsed, so it needs a
refresher pass, not a first read.

Two lists per topic, deliberately different:

* `types` / `operations` / `must_know` / `pitfalls` are **reading** — the
  landscape of the topic, including things you should know *about* without
  ever implementing them ("static array", "red-black tree").
* `gate_requirements` is **doing** — the short list you must be able to
  write or show to unlock the problems. Only things that are genuinely
  demonstrable in code, and never an item that belongs to another topic's
  gate (binary search is not an array requirement). Using the reading list
  as the gate produced nonsense like "implement a static array", and a bar
  that high just gets overridden, which teaches nothing.
"""
from __future__ import annotations

TOPIC_GUIDES: list[dict] = [
    {
        "topic": "array",
        "display_name": "Arrays",
        "seq": 1,
        "one_liner": "A fixed-layout block of contiguous memory addressed by index, "
        "which is why random access is free and insertion in the middle is not.",
        "learn_first": (
            "Know why indexing is O(1) and why an insert or delete anywhere but the end "
            "is O(n) — every array trick exists to avoid that shift. Understand how a "
            "dynamic array's amortised O(1) append works (doubling on resize), because "
            "that is the difference between an O(n) and an O(n^2) solution. Then learn "
            "the four ways to walk an array — one pointer, two pointers, a window, and a "
            "prefix accumulation — before touching the problem list, because almost every "
            "array problem is one of those four in disguise."
        ),
        "types": [
            {"name": "Static array", "note": "Fixed capacity; size known at allocation."},
            {
                "name": "Dynamic array (list, vector)",
                "note": "Grows by reallocating and copying — appends are amortised O(1).",
            },
            {
                "name": "2D array / matrix",
                "note": "Row-major layout; traversal order affects cache behaviour.",
            },
            {
                "name": "Prefix-sum array",
                "note": "Precomputed cumulative sums make any range sum O(1).",
            },
            {
                "name": "Difference array",
                "note": "Stores deltas so a range update is O(1), reconstructed at the end.",
            },
            {
                "name": "Sorted array",
                "note": "Unlocks binary search and two-pointer convergence.",
            },
        ],
        "operations": [
            {"op": "Access by index", "complexity": "O(1)", "note": "Direct address arithmetic."},
            {
                "op": "Append (dynamic array)",
                "complexity": "O(1) amortised",
                "note": "O(n) on the resize itself.",
            },
            {
                "op": "Insert / delete at arbitrary index",
                "complexity": "O(n)",
                "note": "Everything after the index shifts.",
            },
            {"op": "Linear scan / search", "complexity": "O(n)", "note": "Unsorted data."},
            {
                "op": "Binary search",
                "complexity": "O(log n)",
                "note": "Requires the array to be sorted.",
            },
            {"op": "Sort", "complexity": "O(n log n)", "note": "Comparison-based."},
        ],
        "must_know": [
            "Two pointers — opposite ends converging, and same-direction fast/slow",
            "Sliding window, both fixed-size and variable-size with shrink condition",
            "Prefix sums and prefix-sum + hash map for subarray-sum problems",
            "Kadane's algorithm for maximum subarray",
            "In-place partition / Dutch national flag three-way split",
            "Cyclic sort and index-as-hash for 1..n value ranges",
            "Sorting as a preprocessing step, then two pointers or greedy",
        ],
        "pitfalls": [
            "Off-by-one in loop bounds and in window shrink conditions",
            "Mutating a list while iterating over it",
            "Integer overflow when summing or when computing mid as (lo + hi)",
            "Assuming input is sorted when the statement never said so",
            "Copying a subarray inside a loop, turning O(n) into O(n^2)",
            "Aliasing: assigning a list assigns a reference, not a copy",
        ],
        "gate_requirements": [
            "Two pointers converging from both ends (in-place reverse, or pair-sum in a "
            "sorted array)",
            "Variable-size sliding window with an explicit shrink condition",
            "Prefix-sum array, plus an O(1) range-sum query built on it",
            "Kadane's maximum-subarray scan",
            "In-place three-way partition (Dutch national flag)",
        ],
        "needs_revision": False,
    },
    {
        "topic": "strings",
        "display_name": "Strings",
        "seq": 2,
        "one_liner": "An array of characters that is usually immutable, which makes "
        "naive concatenation quietly quadratic.",
        "learn_first": (
            "Know whether strings are immutable in your language — in Python and Java "
            "they are, so building a result with += inside a loop is O(n^2) and you use a "
            "list plus join or a StringBuilder instead. Understand character encoding "
            "enough to know that a character is not always one byte. Then learn frequency "
            "counting and the two-pointer/window forms, which together cover most string "
            "problems before any real pattern-matching algorithm is needed."
        ),
        "types": [
            {
                "name": "Immutable string",
                "note": "Every 'modification' allocates a new string.",
            },
            {
                "name": "Mutable buffer",
                "note": "StringBuilder / list of chars / bytearray for O(1) appends.",
            },
            {
                "name": "Character-frequency map",
                "note": "Fixed 26-slot array or hash map — the anagram workhorse.",
            },
            {
                "name": "Rolling hash",
                "note": "Treats a window as a number so the next window is O(1).",
            },
            {"name": "Suffix structures", "note": "Suffix array / trie for multi-query matching."},
        ],
        "operations": [
            {"op": "Index a character", "complexity": "O(1)", "note": "For fixed-width encodings."},
            {"op": "Concatenate", "complexity": "O(n + m)", "note": "Allocates and copies both."},
            {"op": "Substring extraction", "complexity": "O(k)", "note": "k = substring length."},
            {"op": "Naive substring search", "complexity": "O(n·m)", "note": "Recheck per offset."},
            {"op": "KMP substring search", "complexity": "O(n + m)", "note": "Prefix-function."},
            {"op": "Sort characters", "complexity": "O(n log n)", "note": "Anagram canonical form."},
        ],
        "must_know": [
            "Frequency counting with a fixed-size array for lowercase-only inputs",
            "Sliding window with a count map (longest/shortest substring problems)",
            "Two pointers for palindrome checks and in-place reversal",
            "Canonical form (sorted chars or count tuple) for grouping anagrams",
            "KMP prefix function and what it actually computes",
            "Rabin-Karp rolling hash and why collisions must still be verified",
            "Expand-around-centre for palindromic substrings",
        ],
        "pitfalls": [
            "Building strings with += in a loop instead of a buffer + join",
            "Assuming ASCII / lowercase when the statement allows Unicode or mixed case",
            "Forgetting to shrink the window when the constraint is violated",
            "Comparing hashes without a final character-by-character check",
            "Treating an empty string or single character as an edge case only after failing",
        ],
        "gate_requirements": [
            "Anagram check by frequency count (fixed-size array), not by sorting",
            "Sliding window over a string with a count map",
            "Two-pointer palindrome check, ignoring non-alphanumerics",
            "Building a result with a buffer and join rather than += in a loop",
            "KMP prefix-function table",
        ],
        "needs_revision": False,
    },
    {
        "topic": "binary_search",
        "display_name": "Binary Search",
        "seq": 3,
        "one_liner": "Halving a monotonic search space — over an array's indices, or "
        "over the answer's value range.",
        "learn_first": (
            "Write the plain version until the invariant is automatic: which half is "
            "discarded, whether the bound is inclusive, and what lo means when the loop "
            "ends. Then learn the two variants that matter more than the plain one: "
            "lower_bound / upper_bound (first index satisfying a predicate), and binary "
            "search on the answer, where you binary-search a value range and use a "
            "feasibility check as the predicate. Aggressive Cows, Allocate Pages and "
            "Painter's Partition are all the same problem in that second form, and "
            "recognising that is worth more than solving them separately."
        ),
        "types": [
            {"name": "Classic index search", "note": "Find an exact value in a sorted array."},
            {
                "name": "Lower / upper bound",
                "note": "First position where a monotonic predicate flips.",
            },
            {
                "name": "Binary search on the answer",
                "note": "Search the value range; predicate is a feasibility check.",
            },
            {
                "name": "Rotated / modified array search",
                "note": "Decide which half is sorted, then recurse into it.",
            },
            {
                "name": "Search in a 2D matrix",
                "note": "Flatten to one index, or staircase from a corner.",
            },
        ],
        "operations": [
            {"op": "Search sorted array", "complexity": "O(log n)", "note": "Halves each step."},
            {
                "op": "Binary search on answer",
                "complexity": "O(n log R)",
                "note": "R = value range; n per feasibility check.",
            },
            {
                "op": "Lower bound / upper bound",
                "complexity": "O(log n)",
                "note": "Same loop, different bound update.",
            },
            {
                "op": "Median of two sorted arrays",
                "complexity": "O(log(min(n, m)))",
                "note": "Partition search, not a merge.",
            },
        ],
        "must_know": [
            "One canonical template you never re-derive under pressure",
            "lower_bound / upper_bound and how they answer count and insert-position",
            "Binary search on the answer with a monotonic predicate",
            "Identifying the sorted half in a rotated array",
            "Staircase search from the top-right corner of a sorted matrix",
            "Proving monotonicity before applying binary search at all",
        ],
        "pitfalls": [
            "mid = (lo + hi) / 2 overflowing — use lo + (hi - lo) // 2",
            "Infinite loops from a bound that never moves (lo = mid instead of mid + 1)",
            "Mixing inclusive and exclusive hi within one function",
            "Applying it to a predicate that is not actually monotonic",
            "Returning the wrong bound at loop exit because the invariant was never stated",
        ],
        "gate_requirements": [
            "Iterative binary search with the loop invariant written down",
            "lower_bound and upper_bound (first index where a predicate flips)",
            "Binary search on the answer with a feasibility predicate (Aggressive Cows / "
            "Allocate Pages)",
            "Search in a rotated sorted array",
        ],
        "needs_revision": False,
    },
    {
        "topic": "recursion_backtracking",
        "display_name": "Recursion & Backtracking",
        "seq": 4,
        "one_liner": "A function defined in terms of smaller instances; backtracking is "
        "recursion that undoes its choice on the way out.",
        "learn_first": (
            "Get the three parts explicit before any problem: base case, the choice made "
            "at this level, and the state that must be restored after the recursive call "
            "returns. Understand the call stack well enough to know your recursion depth "
            "and where a stack overflow comes from. Learn to draw the decision tree and "
            "read its size — that is where the O(2^n) or O(n!) bound comes from, and it "
            "is also where pruning gets you a passing solution."
        ),
        "types": [
            {"name": "Linear recursion", "note": "One call per level — factorial, list walk."},
            {"name": "Binary / tree recursion", "note": "Two or more calls — subsets, tree walks."},
            {"name": "Backtracking", "note": "Choose, recurse, un-choose; explores a state tree."},
            {"name": "Divide and conquer", "note": "Split, solve halves, combine — merge sort."},
            {"name": "Tail recursion", "note": "Call in final position; convertible to a loop."},
        ],
        "operations": [
            {"op": "Generate all subsets", "complexity": "O(n · 2^n)", "note": "2^n subsets."},
            {"op": "Generate all permutations", "complexity": "O(n · n!)", "note": "n! orderings."},
            {"op": "Merge sort", "complexity": "O(n log n)", "note": "O(n) extra space."},
            {
                "op": "N-Queens",
                "complexity": "exponential",
                "note": "Heavily reduced by pruning; no tight simple bound.",
            },
            {
                "op": "Recursion stack space",
                "complexity": "O(depth)",
                "note": "Depth, not node count.",
            },
        ],
        "must_know": [
            "The choose / recurse / un-choose skeleton written from memory",
            "Subsets, permutations and combinations as three distinct templates",
            "Pruning with a validity check before recursing, not after",
            "Deduplicating by sorting and skipping equal siblings",
            "Grid backtracking with a visited marker set and cleared in place",
            "Converting recursion to iteration with an explicit stack",
            "Memoisation as the bridge from backtracking to dynamic programming",
        ],
        "pitfalls": [
            "Forgetting to undo the choice, so state leaks into sibling branches",
            "Appending the mutable path itself instead of a copy of it",
            "Missing or unreachable base case — infinite recursion",
            "Pruning after the recursive call, which saves nothing",
            "Ignoring recursion depth limits on large inputs",
        ],
        "gate_requirements": [
            "Subsets via the choose / recurse / un-choose skeleton",
            "Permutations of a list",
            "Combination sum with duplicates skipped by sorting",
            "Grid backtracking with visited marked and restored in place (rat in a maze)",
            "Merge sort",
        ],
        "needs_revision": False,
    },
    {
        "topic": "linked_list",
        "display_name": "Linked List",
        "seq": 5,
        "one_liner": "Nodes holding a value and a pointer, so insertion is O(1) once "
        "you hold the node — and finding it is O(n).",
        "learn_first": (
            "Be fluent with pointer rewiring on paper: insert, delete, and reverse, "
            "including what breaks if you reassign in the wrong order. Learn the dummy-head "
            "trick and the prev/curr/next triple, because they remove almost all of the "
            "edge cases people fail on. Understand the fast/slow pointer idea and what it "
            "gives you — middle, cycle detection, cycle entry, nth-from-end — before the "
            "problem list, since a large share of these problems is that one technique."
        ),
        "types": [
            {"name": "Singly linked", "note": "One next pointer; no way back."},
            {"name": "Doubly linked", "note": "prev + next; O(1) delete given the node — LRU."},
            {"name": "Circular", "note": "Tail points to head; used for round-robin buffers."},
            {"name": "With sentinel / dummy head", "note": "Removes head-insertion special cases."},
            {"name": "Multilevel / flattened", "note": "Nodes carry a child or down pointer."},
        ],
        "operations": [
            {"op": "Access by position", "complexity": "O(n)", "note": "No random access."},
            {"op": "Insert / delete at head", "complexity": "O(1)", "note": "Pointer rewire only."},
            {
                "op": "Insert / delete given the node (doubly)",
                "complexity": "O(1)",
                "note": "Needs prev, hence doubly.",
            },
            {"op": "Search", "complexity": "O(n)", "note": "Sequential only."},
            {"op": "Reverse", "complexity": "O(n)", "note": "O(1) extra space iteratively."},
            {"op": "Merge two sorted lists", "complexity": "O(n + m)", "note": "Splice, no copy."},
        ],
        "must_know": [
            "prev / curr / next iterative reversal",
            "Dummy-head node for merges, deletions and partitions",
            "Fast and slow pointers: middle, cycle detection, kth from end",
            "Floyd's cycle detection, including finding the cycle's entry node",
            "Reversing a sublist and reversing in k-sized groups",
            "Merging k lists with a heap, or by pairwise merging",
            "Doubly linked list + hash map as the LRU cache structure",
        ],
        "pitfalls": [
            "Losing the rest of the list by overwriting next before saving it",
            "Not handling head / single-node / empty-list cases",
            "Returning the old head after a reversal instead of the new one",
            "Dereferencing fast.next.next without checking fast.next",
            "Creating an accidental cycle and hanging the traversal",
        ],
        "gate_requirements": [
            "Singly linked node and traversal",
            "Doubly linked node and traversal in both directions",
            "Circular list construction and a traversal that terminates",
            "Insert at head, at a given position, and at tail",
            "Delete at head, at a given position, and at tail",
            "Iterative reversal with prev / curr / next",
            "Fast and slow pointers: find the middle, and detect a cycle",
        ],
        "needs_revision": False,
    },
    {
        "topic": "stacks_queues",
        "display_name": "Stacks & Queues",
        "seq": 6,
        "one_liner": "Two access disciplines — last-in-first-out and first-in-first-out — "
        "that make certain orderings free.",
        "learn_first": (
            "Know the operations and their costs cold, then learn what the disciplines are "
            "*for*: a stack remembers the most recent unresolved thing (matching, undo, "
            "the monotonic-stack family), and a queue processes in arrival order (BFS, "
            "level order, stream windows). The monotonic stack is the single highest-value "
            "idea here — next greater element, stock span, largest rectangle and trapping "
            "rain water are all the same maintenance rule — so understand why it is "
            "amortised O(n) before solving them."
        ),
        "types": [
            {"name": "Stack", "note": "LIFO; push/pop at one end."},
            {"name": "Queue", "note": "FIFO; enqueue at back, dequeue at front."},
            {"name": "Deque", "note": "Both ends O(1); the sliding-window-maximum structure."},
            {"name": "Monotonic stack / deque", "note": "Kept sorted by discarding dominated items."},
            {"name": "Priority queue", "note": "Ordered by priority, not arrival — a heap."},
            {"name": "Circular buffer", "note": "Fixed-capacity queue over an array."},
        ],
        "operations": [
            {"op": "Push / pop / peek (stack)", "complexity": "O(1)", "note": "Amortised on arrays."},
            {"op": "Enqueue / dequeue (queue)", "complexity": "O(1)", "note": "With a deque."},
            {"op": "Search", "complexity": "O(n)", "note": "Neither structure is for searching."},
            {
                "op": "Monotonic stack sweep",
                "complexity": "O(n)",
                "note": "Each element pushed and popped at most once.",
            },
            {"op": "LRU get / put", "complexity": "O(1)", "note": "Hash map + doubly linked list."},
        ],
        "must_know": [
            "Monotonic increasing and decreasing stack, and which one a problem needs",
            "Next greater / next smaller element as one template",
            "Largest rectangle in a histogram via the same sweep",
            "Deque-based sliding window maximum",
            "Stack from two queues and queue from two stacks (and the amortised cost)",
            "BFS with a queue, including level-size batching for level order",
            "Balanced-bracket matching and expression evaluation",
        ],
        "pitfalls": [
            "Popping an empty stack — check before every pop",
            "Pushing values when the algorithm needs indices (or vice versa)",
            "Using list.pop(0) as a dequeue, which is O(n) per call",
            "Forgetting to drain the stack after the main loop ends",
            "Marking BFS nodes visited on dequeue instead of on enqueue, so they duplicate",
        ],
        "gate_requirements": [
            "Stack with push / pop / peek and an empty check",
            "Queue with O(1) enqueue and dequeue (not list.pop(0))",
            "Queue built from two stacks, or a stack built from two queues",
            "Monotonic stack sweep solving next-greater-element",
            "Min stack returning the minimum in O(1)",
        ],
        "needs_revision": False,
    },
    {
        "topic": "binary_trees",
        "display_name": "Binary Trees",
        "seq": 7,
        "one_liner": "Nodes with up to two children — a recursive structure whose "
        "problems are almost all a traversal plus a return value.",
        "learn_first": (
            "Write all four traversals from memory — preorder, inorder, postorder, level "
            "order — and know which one a problem needs before writing code: bottom-up "
            "aggregation is postorder, top-down propagation is preorder, breadth is a "
            "queue. Then learn to think of every tree problem as 'what does each node "
            "return to its parent', because height, diameter, balance, and max path sum "
            "are all one postorder function with a different return type. Know the "
            "difference between height and depth, and why a skewed tree makes O(log n) "
            "claims false."
        ),
        "types": [
            {"name": "Full / proper", "note": "Every node has 0 or 2 children."},
            {"name": "Complete", "note": "Filled level by level, left to right — heap shape."},
            {"name": "Perfect", "note": "All levels full; exactly 2^h - 1 nodes."},
            {"name": "Balanced", "note": "Subtree heights differ by at most 1 — keeps ops O(log n)."},
            {"name": "Skewed / degenerate", "note": "Effectively a linked list; operations O(n)."},
            {"name": "Threaded", "note": "Null pointers reused as successor links — Morris walk."},
        ],
        "operations": [
            {"op": "Traversal (any order)", "complexity": "O(n)", "note": "Visits every node once."},
            {
                "op": "Search / insert (unordered tree)",
                "complexity": "O(n)",
                "note": "No ordering to exploit.",
            },
            {"op": "Height / diameter", "complexity": "O(n)", "note": "One postorder pass."},
            {
                "op": "Recursive traversal space",
                "complexity": "O(h)",
                "note": "h = height; O(n) when skewed.",
            },
            {
                "op": "Morris traversal",
                "complexity": "O(n) time, O(1) space",
                "note": "Rewires threads temporarily.",
            },
            {"op": "Level order", "complexity": "O(n)", "note": "O(w) space, w = max width."},
        ],
        "must_know": [
            "All four traversals, recursive and iterative",
            "Postorder aggregation: return a tuple/struct up to the parent",
            "Level order with level-size batching (views, zigzag, kth level)",
            "Vertical-order maps with horizontal distance for top and bottom view",
            "LCA by recursive split, and the parent-pointer / depth-lifting variants",
            "Constructing a tree from two traversals, and why one alone is ambiguous",
            "Morris traversal for O(1) space",
        ],
        "pitfalls": [
            "Claiming O(log n) on a tree that is not balanced",
            "Confusing height (edges below) with depth (edges above)",
            "Returning the diameter where the parent needs the height, or vice versa",
            "Mutating a shared accumulator across branches without resetting it",
            "Missing the null / single-node base case",
            "Deep recursion on a skewed tree overflowing the stack",
        ],
        "gate_requirements": [
            "Node definition plus preorder, inorder and postorder traversals",
            "One traversal written iteratively with an explicit stack",
            "Level-order traversal using level-size batching",
            "Height and diameter computed in a single postorder pass",
            "Lowest common ancestor by recursive split",
        ],
        "needs_revision": False,
    },
    {
        "topic": "bst",
        "display_name": "Binary Search Tree",
        "seq": 8,
        "one_liner": "A binary tree with the ordering invariant left < node < right, "
        "which makes an inorder walk produce sorted output.",
        "learn_first": (
            "Internalise the invariant as a *range* condition, not a parent comparison: "
            "each node is valid only within an interval inherited from its ancestors, "
            "which is why validating a BST by comparing with the immediate parent is "
            "wrong. Know that inorder traversal yields sorted order — that single fact "
            "solves kth smallest, validate, recover, predecessor/successor and flatten. "
            "Then understand that every O(log n) claim depends on balance, and what "
            "self-balancing trees do about it."
        ),
        "types": [
            {"name": "Plain BST", "note": "No balancing; degrades to O(n) on sorted insertion."},
            {"name": "AVL tree", "note": "Height-balanced by rotations; strict, fast lookups."},
            {"name": "Red-black tree", "note": "Looser balance, cheaper writes; standard in libraries."},
            {"name": "Balanced-from-sorted-array", "note": "Middle as root, recurse — O(n) build."},
            {"name": "Augmented BST", "note": "Subtree counts stored to answer rank/kth in O(h)."},
        ],
        "operations": [
            {
                "op": "Search / insert / delete (balanced)",
                "complexity": "O(log n)",
                "note": "Height-bound.",
            },
            {
                "op": "Search / insert / delete (skewed)",
                "complexity": "O(n)",
                "note": "Sorted input with no balancing.",
            },
            {"op": "Inorder traversal", "complexity": "O(n)", "note": "Produces sorted order."},
            {"op": "Min / max", "complexity": "O(h)", "note": "Leftmost / rightmost descent."},
            {
                "op": "Predecessor / successor",
                "complexity": "O(h)",
                "note": "One descent with a candidate.",
            },
            {"op": "Build balanced from sorted array", "complexity": "O(n)", "note": "Divide at mid."},
        ],
        "must_know": [
            "Validation by min/max range propagation, not parent comparison",
            "Inorder traversal as the sorted-sequence primitive",
            "Kth smallest / largest via inorder with a counter, or subtree sizes",
            "Deletion's three cases, including two-children replacement by successor",
            "LCA in a BST by descending while both keys sit on one side",
            "Predecessor and successor with and without parent pointers",
            "Recovering a BST with exactly two swapped nodes from the inorder dips",
        ],
        "pitfalls": [
            "Validating against the parent only, which accepts invalid trees",
            "Assuming O(log n) without balance — sequential inserts give a linked list",
            "Using <= somewhere and < elsewhere, mishandling duplicates",
            "Forgetting to reconnect the child when deleting a one-child node",
            "Treating a BST inorder as sorted after an in-place structural change mid-walk",
        ],
        "gate_requirements": [
            "Insert and search that honour the ordering invariant",
            "Delete, including the two-children case via the inorder successor",
            "Validation by min/max range propagation, not parent comparison",
            "Inorder traversal, showing it yields sorted output",
            "Predecessor and successor of a given key",
        ],
        "needs_revision": False,
    },
    {
        "topic": "heaps",
        "display_name": "Heaps & Priority Queues",
        "seq": 9,
        "one_liner": "A complete binary tree kept in an array where each parent beats "
        "its children, giving O(1) access to the extreme element.",
        "learn_first": (
            "Understand the array encoding (children at 2i+1 / 2i+2) and the two repair "
            "operations, sift-up and sift-down — everything else follows. Know why "
            "building a heap from n items is O(n) while n pushes are O(n log n). Most "
            "importantly, learn the selection idiom before the problems: for the k "
            "largest you keep a min-heap of size k, which feels backwards until you see "
            "why. Two heaps back-to-back give you a running median."
        ),
        "types": [
            {"name": "Min-heap", "note": "Smallest at the root; the default in most libraries."},
            {"name": "Max-heap", "note": "Largest at the root; often faked by negating keys."},
            {"name": "Bounded size-k heap", "note": "The top-k / kth-largest selection idiom."},
            {"name": "Two-heap median structure", "note": "Max-heap of the low half, min-heap of the high."},
            {"name": "Indexed / lazy-deletion heap", "note": "Handles updates by re-pushing and skipping stale entries."},
        ],
        "operations": [
            {"op": "Peek min / max", "complexity": "O(1)", "note": "It is the root."},
            {"op": "Push", "complexity": "O(log n)", "note": "Sift up."},
            {"op": "Pop extreme", "complexity": "O(log n)", "note": "Swap with last, sift down."},
            {"op": "Heapify an existing array", "complexity": "O(n)", "note": "Bottom-up sift-down."},
            {"op": "Heap sort", "complexity": "O(n log n)", "note": "In-place, not stable."},
            {"op": "Search for an arbitrary value", "complexity": "O(n)", "note": "No ordering across siblings."},
        ],
        "must_know": [
            "Size-k min-heap for k largest, size-k max-heap for k smallest",
            "Two heaps balanced by size for a streaming median",
            "K-way merge by seeding the heap with one item per list",
            "Heapify in O(n) versus n pushes in O(n log n)",
            "Negating keys (or a comparator) to get a max-heap from a min-heap library",
            "Lazy deletion for problems that need to invalidate entries",
            "When a sorted array or a bucket count beats a heap outright",
        ],
        "pitfalls": [
            "Reaching for a max-heap when the k-selection idiom wants a min-heap",
            "Assuming heap iteration order is sorted — only repeated pops are",
            "Comparing tuples whose second element is not comparable, on a tie",
            "Forgetting a heap gives no O(log n) lookup or arbitrary delete",
            "Rebuilding the heap inside a loop instead of maintaining it",
        ],
        "gate_requirements": [
            "Array-backed heap with sift-up and sift-down",
            "Push, pop and peek",
            "Heapify an existing array in O(n)",
            "The size-k heap idiom for k-largest (and why it is a min-heap)",
            "Two heaps maintaining a running median",
        ],
        "needs_revision": False,
    },
    {
        "topic": "tries",
        "display_name": "Tries (Prefix Trees)",
        "seq": 10,
        "one_liner": "A tree keyed by character position, so a lookup costs the length "
        "of the word rather than the size of the dictionary.",
        "learn_first": (
            "Build one from scratch — a node holding a child map and an is_end flag — and "
            "insert, search and startsWith on it, before any problem. The point to grasp "
            "is that cost depends on word length, not dictionary size, and that shared "
            "prefixes are stored once. Then look at the space trade-off honestly: a trie "
            "over a large alphabet with fixed arrays wastes a lot of memory, which is why "
            "a hash map of children or a compressed trie exists."
        ),
        "types": [
            {"name": "Standard trie", "note": "One node per character; is_end marks a word."},
            {"name": "Compressed / radix trie", "note": "Merges single-child chains into one edge."},
            {"name": "Array-of-children trie", "note": "Fixed 26 slots — fast, memory-hungry."},
            {"name": "Hash-map-of-children trie", "note": "Sparse-friendly for large alphabets."},
            {"name": "Binary trie", "note": "Keys as bit strings — the max-XOR structure."},
        ],
        "operations": [
            {"op": "Insert a word", "complexity": "O(L)", "note": "L = word length."},
            {"op": "Search a word", "complexity": "O(L)", "note": "Independent of dictionary size."},
            {"op": "Prefix existence", "complexity": "O(L)", "note": "Stop without needing is_end."},
            {
                "op": "Collect all words with a prefix",
                "complexity": "O(L + output)",
                "note": "Descend, then DFS.",
            },
            {"op": "Space", "complexity": "O(total characters)", "note": "Shared prefixes stored once."},
        ],
        "must_know": [
            "Node = children map + is_end, and why is_end cannot be inferred from leafness",
            "Insert / search / startsWith as three near-identical descents",
            "Prefix DFS for autocomplete-style enumeration",
            "Binary trie over bits for maximum-XOR pair queries",
            "Trie + DFS/memo for word break and word search on a board",
            "When a hash set of words is simply the better answer",
        ],
        "pitfalls": [
            "Treating any leaf as a word, or any word as a leaf (prefix words break both)",
            "Sharing one mutable children dict across nodes by accident",
            "Assuming lowercase-only input and indexing out of a 26-slot array",
            "Deleting a word by removing nodes another word still needs",
            "Rebuilding the trie per query instead of once up front",
        ],
        "gate_requirements": [
            "Node with a children map and an is_end flag",
            "Insert, search, and startsWith",
            "Enumerate every word under a given prefix",
            "Delete a word without breaking other words that share its prefix",
        ],
        "needs_revision": False,
    },
    {
        "topic": "graphs",
        "display_name": "Graphs",
        "seq": 11,
        "one_liner": "Vertices joined by edges — the general structure that trees, "
        "grids and dependency lists are all special cases of.",
        "learn_first": (
            "First, representation: adjacency list versus matrix, and the cost difference "
            "that follows. Then write BFS and DFS as templates you never re-derive, and "
            "note that a grid is a graph whose neighbours are computed rather than "
            "stored. After that the classification matters more than any single "
            "algorithm: directed or not, weighted or not, negative weights or not, "
            "cyclic or not — because that is what selects BFS, Dijkstra, Bellman-Ford, "
            "topological sort or union-find. Solving graph problems without that "
            "classification habit is how people apply Dijkstra to an unweighted graph."
        ),
        "types": [
            {"name": "Directed / undirected", "note": "Decides cycle detection and edge storage."},
            {"name": "Weighted / unweighted", "note": "Unweighted shortest path is plain BFS."},
            {"name": "DAG", "note": "Acyclic and directed — topological order and DAG DP exist."},
            {"name": "Adjacency list", "note": "O(V + E) space; the default for sparse graphs."},
            {"name": "Adjacency matrix", "note": "O(V^2) space; O(1) edge lookup — Floyd-Warshall."},
            {"name": "Implicit / grid graph", "note": "Neighbours derived from coordinates."},
            {"name": "Disjoint-set forest", "note": "Union-find for connectivity and Kruskal."},
        ],
        "operations": [
            {"op": "BFS / DFS traversal", "complexity": "O(V + E)", "note": "Adjacency list."},
            {
                "op": "Unweighted shortest path",
                "complexity": "O(V + E)",
                "note": "BFS; layers are distances.",
            },
            {
                "op": "Dijkstra (binary heap)",
                "complexity": "O((V + E) log V)",
                "note": "Non-negative weights only.",
            },
            {
                "op": "Bellman-Ford",
                "complexity": "O(V·E)",
                "note": "Handles negative edges; detects negative cycles.",
            },
            {"op": "Floyd-Warshall", "complexity": "O(V^3)", "note": "All pairs; matrix form."},
            {"op": "Topological sort", "complexity": "O(V + E)", "note": "Kahn's or DFS postorder."},
            {
                "op": "Kruskal / Prim MST",
                "complexity": "O(E log V)",
                "note": "Sorting edges / heap respectively.",
            },
            {
                "op": "Union-find operation",
                "complexity": "near O(1) amortised",
                "note": "With union by rank and path compression.",
            },
        ],
        "must_know": [
            "BFS and DFS templates, iterative and recursive, on lists and grids",
            "Cycle detection: undirected via parent check, directed via recursion colours",
            "Topological sort both ways — Kahn's in-degree queue and DFS postorder",
            "Dijkstra, and why it fails with negative edges",
            "Bellman-Ford for negative weights and negative-cycle detection",
            "Union-find with path compression for connectivity and Kruskal's MST",
            "Multi-source BFS (all sources enqueued at distance 0)",
            "Bipartite checking by two-colouring",
        ],
        "pitfalls": [
            "Marking visited on dequeue instead of enqueue, so nodes enter the queue twice",
            "Using DFS for a shortest path in an unweighted graph",
            "Applying Dijkstra with negative weights",
            "Forgetting to add both directions for an undirected edge",
            "In an undirected graph, treating the immediate parent as a cycle",
            "Ignoring disconnected components — one traversal is not the whole graph",
            "Recursive DFS overflowing the stack on a large or path-like graph",
        ],
        "gate_requirements": [
            "Build an adjacency list from an edge list, directed and undirected",
            "BFS with visited marked on enqueue",
            "DFS, both recursive and iterative",
            "Cycle detection in a directed graph using recursion colours",
            "Topological sort via Kahn's in-degree queue",
            "Dijkstra with a heap",
            "Union-find with path compression",
        ],
        "needs_revision": False,
    },
    {
        "topic": "dp",
        "display_name": "Dynamic Programming",
        "seq": 12,
        "one_liner": "Recursion with overlapping subproblems solved once — a state "
        "definition, a transition, and a base case.",
        "learn_first": (
            "Do not start from tabulation. Start by writing the brute-force recursion, "
            "confirm the subproblems overlap, then memoise it — that path makes the state "
            "and transition obvious, and only then is the bottom-up table a mechanical "
            "rewrite. Learn to say your state out loud ('dp[i][w] is the best value using "
            "the first i items with capacity w') because a vague state is the actual cause "
            "of most stuck DP attempts. Then learn the standard families, since knapsack, "
            "LCS, LIS, and interval DP cover most of what appears in interviews."
        ),
        "types": [
            {"name": "Top-down memoisation", "note": "Recursion + cache; mirrors the recurrence."},
            {"name": "Bottom-up tabulation", "note": "Iterative table; no recursion depth limit."},
            {"name": "1D DP", "note": "One index of state — Fibonacci, climbing stairs, LIS, Kadane."},
            {"name": "2D DP", "note": "Two indices — knapsack, LCS, edit distance, grid paths."},
            {"name": "Interval DP", "note": "Range [i..j] with a split point — MCM, palindrome cuts."},
            {"name": "Rolling-array DP", "note": "Keeps only the last row(s), cutting space to O(n)."},
            {"name": "Bitmask DP", "note": "State is a subset — small-n assignment/TSP problems."},
        ],
        "operations": [
            {"op": "0-1 knapsack", "complexity": "O(n·W)", "note": "n items, capacity W."},
            {"op": "LCS / edit distance", "complexity": "O(n·m)", "note": "Two-string table."},
            {"op": "LIS (DP)", "complexity": "O(n^2)", "note": "O(n log n) with patience/binary search."},
            {"op": "Coin change (min coins)", "complexity": "O(n·amount)", "note": "Unbounded choice."},
            {"op": "Matrix chain multiplication", "complexity": "O(n^3)", "note": "Interval DP with a split."},
            {"op": "Kadane's maximum subarray", "complexity": "O(n)", "note": "One pass, O(1) space."},
        ],
        "must_know": [
            "Brute force to memoisation to tabulation, in that order",
            "Stating the state and transition in words before writing code",
            "0-1 versus unbounded knapsack, and the loop-order difference between them",
            "Subset-sum / target-sum as knapsack in disguise",
            "LCS family: substring versus subsequence, and edit distance",
            "LIS in O(n^2) and the O(n log n) patience variant",
            "Interval DP with a split point (MCM, palindrome partitioning II)",
            "Space reduction to one or two rows",
            "Reconstructing the answer from the table, not just its value",
        ],
        "pitfalls": [
            "Jumping to a table before the recurrence is right",
            "A state that does not capture everything the transition needs",
            "Wrong iteration order, so a cell is read before it is computed",
            "Reusing a 1D array in the wrong direction and turning 0-1 into unbounded",
            "Off-by-one between 0-indexed input and 1-indexed table padding",
            "Initialising with 0 where the identity should be -infinity (or vice versa)",
            "Memoising on an incomplete key, silently returning another state's answer",
        ],
        "gate_requirements": [
            "One problem solved three ways in order: brute force, memoised, tabulated",
            "0-1 knapsack, with the state definition written out in words",
            "LCS table plus reconstruction of the actual subsequence",
            "Coin change (minimum coins), and why the loop order matters",
            "A 2D table reduced to one or two rows",
        ],
        "needs_revision": False,
    },
    {
        "topic": "greedy",
        "display_name": "Greedy",
        "seq": 13,
        "one_liner": "Take the locally best choice and never reconsider — correct only "
        "when the problem has the right structure.",
        "learn_first": (
            "The algorithms here are trivial; the skill is knowing when greedy is even "
            "allowed. Learn what the exchange argument is and be able to sketch one, and "
            "learn to recognise the two properties that justify greedy: the greedy-choice "
            "property and optimal substructure. Then learn the sorting keys, because most "
            "greedy problems are 'sort by the right thing, then sweep' — by end time for "
            "activity selection, by value/weight for fractional knapsack, by deadline for "
            "job sequencing. Knowing why 0-1 knapsack is *not* greedy is as important as "
            "any of them."
        ),
        "types": [
            {"name": "Sort-then-sweep", "note": "Nearly all of them; the sort key is the insight."},
            {"name": "Interval scheduling", "note": "Sort by end time to maximise count."},
            {"name": "Exchange-argument greedy", "note": "Proven by swapping into greedy order without loss."},
            {"name": "Heap-driven greedy", "note": "Best choice re-evaluated each step — Dijkstra, Prim."},
            {"name": "Fractional relaxation", "note": "Divisible items make ratio-greedy optimal."},
        ],
        "operations": [
            {"op": "Sort + single sweep", "complexity": "O(n log n)", "note": "Sort dominates."},
            {"op": "Activity selection", "complexity": "O(n log n)", "note": "Sort by finish time."},
            {"op": "Fractional knapsack", "complexity": "O(n log n)", "note": "Sort by value/weight."},
            {"op": "Heap-based greedy step", "complexity": "O(log n)", "note": "Per extraction."},
            {"op": "Coin change (canonical system)", "complexity": "O(n)", "note": "Greedy fails on arbitrary sets."},
        ],
        "must_know": [
            "Exchange argument as the standard proof of a greedy choice",
            "Sort by end time for maximum non-overlapping intervals",
            "Value-to-weight ratio for the fractional (not 0-1) knapsack",
            "Deadline-driven job sequencing with a slot structure or union-find",
            "Two-pointer greedy matching (assign cookies, boats to save people)",
            "Recognising when the greedy answer must be replaced by DP",
        ],
        "pitfalls": [
            "Assuming greedy works because it passes the sample input",
            "Applying greedy coin change to a non-canonical coin set",
            "Treating 0-1 knapsack as greedy by ratio",
            "Sorting by the intuitive key (start time, size) instead of the provable one",
            "Ties broken arbitrarily when the tie-break is load-bearing",
        ],
        "gate_requirements": [
            "Activity selection sorted by finish time",
            "Fractional knapsack by value-to-weight ratio",
            "A written exchange argument justifying one of your greedy choices",
            "A case where greedy fails and DP is required, demonstrated with an input",
        ],
        "needs_revision": False,
    },
    {
        "topic": "bit_math",
        "display_name": "Bit Manipulation & Math",
        "seq": 14,
        "one_liner": "Treating numbers as bit patterns, plus the number-theory results "
        "that turn a loop into a formula.",
        "learn_first": (
            "Learn the six operators and what each does to a single bit, then the handful "
            "of idioms built on them: x & (x-1) clears the lowest set bit, x & -x isolates "
            "it, XOR cancels equal values and is its own inverse. That XOR property alone "
            "solves the single-number family. On the maths side, know fast modular "
            "exponentiation, GCD by Euclid, and why you take a modulus at every step "
            "rather than at the end. Also know your language's integer semantics — "
            "Python's arbitrary precision and negative-shift behaviour differ from C++ "
            "and Java, and problems are written with the fixed-width version in mind."
        ),
        "types": [
            {"name": "Bitwise operators", "note": "AND, OR, XOR, NOT, left shift, right shift."},
            {"name": "Bitmask as a set", "note": "Bit i means element i is present — subset enumeration."},
            {"name": "Two's complement", "note": "How negatives are represented; explains x & -x."},
            {"name": "Modular arithmetic", "note": "Keeps large results in range; needed for 1e9+7 answers."},
            {"name": "Fast exponentiation", "note": "Square-and-multiply by the exponent's bits."},
        ],
        "operations": [
            {"op": "Any single bitwise operation", "complexity": "O(1)", "note": "Fixed-width words."},
            {"op": "Count set bits (Brian Kernighan)", "complexity": "O(set bits)", "note": "x &= x - 1 per loop."},
            {"op": "Power of two check", "complexity": "O(1)", "note": "x > 0 and x & (x - 1) == 0."},
            {"op": "Fast exponentiation", "complexity": "O(log n)", "note": "Square and multiply."},
            {"op": "GCD (Euclid)", "complexity": "O(log min(a, b))", "note": "Repeated modulo."},
            {"op": "Enumerate all subsets of n items", "complexity": "O(2^n)", "note": "Mask 0..2^n - 1."},
            {"op": "Sieve of Eratosthenes", "complexity": "O(n log log n)", "note": "Primes up to n."},
        ],
        "must_know": [
            "XOR cancellation for single-number and missing-number problems",
            "x & (x - 1) and x & -x, and what each is used for",
            "Get / set / clear / toggle bit i",
            "Bitmask subset enumeration, including iterating submasks",
            "Fast modular exponentiation and modular arithmetic discipline",
            "Euclid's GCD and the LCM relation",
            "Maximum XOR pair via a binary trie",
        ],
        "pitfalls": [
            "Operator precedence — bitwise binds looser than comparison in most languages",
            "Right-shifting a negative number and expecting logical shift",
            "Assuming 32-bit overflow semantics in Python, where ints are unbounded",
            "Taking the modulus only at the end, after overflow already happened",
            "Confusing logical (and/or) with bitwise (&/|) operators",
            "Off-by-one between bit index and bit position",
        ],
        "gate_requirements": [
            "get / set / clear / toggle bit i",
            "Count set bits using x &= x - 1",
            "Power-of-two check with no loop",
            "XOR to find the one non-duplicated element",
            "Fast modular exponentiation",
            "Euclid's GCD",
            "Enumerate all subsets of n items with a bitmask",
        ],
        "needs_revision": False,
    },
    {
        "topic": "oop",
        "display_name": "Object-Oriented Programming (revision)",
        "seq": 15,
        "one_liner": "Designing with objects that own their state and expose behaviour — "
        "the vocabulary every low-level-design round is conducted in.",
        "learn_first": (
            "This is a revision pass, so go for recall over reading: define encapsulation, "
            "abstraction, inheritance and polymorphism in one sentence each, then write a "
            "small class hierarchy and deliberately break it to see why composition is "
            "usually preferred over inheritance. Re-derive SOLID by naming the smell each "
            "principle fixes rather than memorising the acronym. Since you work in Python, "
            "refresh the specifics an interviewer will actually probe: dunder methods, "
            "properties, ABCs versus duck typing, dataclasses, class versus instance "
            "attributes, and MRO with multiple inheritance. A design round is graded on "
            "whether your objects have clear responsibilities, not on reciting the pillars."
        ),
        "types": [
            {"name": "Encapsulation", "note": "State private, access through behaviour — invariants stay enforceable."},
            {"name": "Abstraction", "note": "Expose intent, hide mechanism; the interface is the contract."},
            {"name": "Inheritance", "note": "Is-a reuse; couples the subclass to the parent's internals."},
            {"name": "Polymorphism", "note": "One call site, many implementations — the point of interfaces."},
            {"name": "Composition", "note": "Has-a reuse; the default answer over inheritance."},
            {"name": "Interface vs abstract class", "note": "Contract only, versus contract plus shared implementation."},
        ],
        "operations": [
            {"op": "Single Responsibility", "complexity": "—", "note": "One reason to change per class."},
            {"op": "Open/Closed", "complexity": "—", "note": "Extend by adding types, not editing switches."},
            {"op": "Liskov Substitution", "complexity": "—", "note": "A subclass must honour the base's contract."},
            {"op": "Interface Segregation", "complexity": "—", "note": "Small interfaces; no forced no-op methods."},
            {"op": "Dependency Inversion", "complexity": "—", "note": "Depend on abstractions, inject the concrete."},
            {"op": "Python specifics", "complexity": "—", "note": "Dunders, properties, ABCs, dataclasses, MRO."},
        ],
        "must_know": [
            "The four pillars stated crisply, with a real example of each",
            "Composition over inheritance, and the concrete failure inheritance causes",
            "SOLID as five smells and their fixes, not as an acronym",
            "Interface versus abstract class, and when each is the right tool",
            "Method overriding versus overloading, and dynamic dispatch",
            "A handful of patterns interviewers reach for: strategy, factory, observer, singleton (and its costs)",
            "Python: __init__ / __repr__ / __eq__ / __hash__, properties, ABCs, dataclasses, MRO",
            "Turning a vague prompt into classes with named responsibilities and clear ownership",
        ],
        "pitfalls": [
            "Deep inheritance chains where composition was the answer",
            "God classes that own unrelated responsibilities",
            "Subclasses that violate the base contract (Liskov) and surprise callers",
            "Mutable default arguments and mutable class attributes shared across instances",
            "Exposing fields publicly, then being unable to enforce an invariant later",
            "Reciting the pillars in a design round instead of naming responsibilities and interfaces",
        ],
        "gate_requirements": [
            "A small class hierarchy demonstrating encapsulation and polymorphism",
            "The same design redone with composition, with the trade-off stated",
            "An abstract base class or interface plus a concrete implementation",
            "__init__, __repr__, __eq__ and __hash__ on one class, and why __hash__ must "
            "agree with __eq__",
            "A Liskov violation, then the fix",
        ],
        "needs_revision": True,
    },
]
