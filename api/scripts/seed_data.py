"""Static seed data. Every problem below is a real LeetCode problem —
number, title, slug and pattern are not invented (build prompt 2.3: "never
fabricate... No invented LeetCode numbers, URLs"). This is a representative
subset (NeetCode 150 / Blind 75 overlap) covering 16 patterns, not the
user's actual 270-problem curriculum, which wasn't supplied — see
README.md's note on the missing source workbook.

Company frequency data does not exist for this subset either, so it is
left out entirely rather than guessed (design doc 5.2: "Netflix and OpenAI:
no data exists. NULL, never invented" — the same rule applies here to
every problem, not just those two companies, since no real frequency
survey backs this seed set).

Columns: (lc_number, title, slug, pattern, difficulty, is_neetcode150, is_blind75)
"""

PROBLEMS: list[tuple[int, str, str, str, str, bool, bool]] = [
    # arrays_hashing
    (1, "Two Sum", "two-sum", "arrays_hashing", "Easy", True, True),
    (217, "Contains Duplicate", "contains-duplicate", "arrays_hashing", "Easy", True, False),
    (242, "Valid Anagram", "valid-anagram", "arrays_hashing", "Easy", True, False),
    (49, "Group Anagrams", "group-anagrams", "arrays_hashing", "Medium", True, True),
    (238, "Product of Array Except Self", "product-of-array-except-self", "arrays_hashing", "Medium", True, True),
    (128, "Longest Consecutive Sequence", "longest-consecutive-sequence", "arrays_hashing", "Medium", True, True),
    # two_pointers
    (125, "Valid Palindrome", "valid-palindrome", "two_pointers", "Easy", True, False),
    (15, "3Sum", "3sum", "two_pointers", "Medium", True, True),
    (11, "Container With Most Water", "container-with-most-water", "two_pointers", "Medium", True, True),
    (42, "Trapping Rain Water", "trapping-rain-water", "two_pointers", "Hard", True, True),
    # sliding_window
    (121, "Best Time to Buy and Sell Stock", "best-time-to-buy-and-sell-stock", "sliding_window", "Easy", True, True),
    (3, "Longest Substring Without Repeating Characters", "longest-substring-without-repeating-characters", "sliding_window", "Medium", True, True),
    (424, "Longest Repeating Character Replacement", "longest-repeating-character-replacement", "sliding_window", "Medium", True, False),
    (76, "Minimum Window Substring", "minimum-window-substring", "sliding_window", "Hard", True, True),
    (567, "Permutation in String", "permutation-in-string", "sliding_window", "Medium", True, False),
    # stack
    (20, "Valid Parentheses", "valid-parentheses", "stack", "Easy", True, True),
    (155, "Min Stack", "min-stack", "stack", "Medium", True, False),
    (150, "Evaluate Reverse Polish Notation", "evaluate-reverse-polish-notation", "stack", "Medium", True, False),
    (22, "Generate Parentheses", "generate-parentheses", "stack", "Medium", True, True),
    (739, "Daily Temperatures", "daily-temperatures", "stack", "Medium", True, False),
    (853, "Car Fleet", "car-fleet", "stack", "Medium", True, False),
    # binary_search
    (704, "Binary Search", "binary-search", "binary_search", "Easy", True, False),
    (74, "Search a 2D Matrix", "search-a-2d-matrix", "binary_search", "Medium", True, False),
    (875, "Koko Eating Bananas", "koko-eating-bananas", "binary_search", "Medium", True, False),
    (153, "Find Minimum in Rotated Sorted Array", "find-minimum-in-rotated-sorted-array", "binary_search", "Medium", True, True),
    (33, "Search in Rotated Sorted Array", "search-in-rotated-sorted-array", "binary_search", "Medium", True, True),
    # linked_list
    (206, "Reverse Linked List", "reverse-linked-list", "linked_list", "Easy", True, True),
    (21, "Merge Two Sorted Lists", "merge-two-sorted-lists", "linked_list", "Easy", True, True),
    (143, "Reorder List", "reorder-list", "linked_list", "Medium", True, False),
    (19, "Remove Nth Node From End of List", "remove-nth-node-from-end-of-list", "linked_list", "Medium", True, False),
    (141, "Linked List Cycle", "linked-list-cycle", "linked_list", "Easy", True, True),
    (23, "Merge k Sorted Lists", "merge-k-sorted-lists", "linked_list", "Hard", True, True),
    # trees
    (226, "Invert Binary Tree", "invert-binary-tree", "trees", "Easy", True, True),
    (104, "Maximum Depth of Binary Tree", "maximum-depth-of-binary-tree", "trees", "Easy", True, False),
    (100, "Same Tree", "same-tree", "trees", "Easy", True, False),
    (572, "Subtree of Another Tree", "subtree-of-another-tree", "trees", "Easy", True, False),
    (235, "Lowest Common Ancestor of a Binary Search Tree", "lowest-common-ancestor-of-a-binary-search-tree", "trees", "Medium", True, False),
    (102, "Binary Tree Level Order Traversal", "binary-tree-level-order-traversal", "trees", "Medium", True, True),
    (98, "Validate Binary Search Tree", "validate-binary-search-tree", "trees", "Medium", True, True),
    (230, "Kth Smallest Element in a BST", "kth-smallest-element-in-a-bst", "trees", "Medium", True, False),
    (105, "Construct Binary Tree from Preorder and Inorder Traversal", "construct-binary-tree-from-preorder-and-inorder-traversal", "trees", "Medium", True, False),
    # tries
    (208, "Implement Trie (Prefix Tree)", "implement-trie-prefix-tree", "tries", "Medium", True, False),
    (211, "Design Add and Search Words Data Structure", "design-add-and-search-words-data-structure", "tries", "Medium", True, False),
    # heap
    (703, "Kth Largest Element in a Stream", "kth-largest-element-in-a-stream", "heap", "Easy", True, False),
    (1046, "Last Stone Weight", "last-stone-weight", "heap", "Easy", True, False),
    (973, "K Closest Points to Origin", "k-closest-points-to-origin", "heap", "Medium", True, False),
    (215, "Kth Largest Element in an Array", "kth-largest-element-in-an-array", "heap", "Medium", True, True),
    (621, "Task Scheduler", "task-scheduler", "heap", "Medium", True, False),
    # backtracking
    (78, "Subsets", "subsets", "backtracking", "Medium", True, True),
    (39, "Combination Sum", "combination-sum", "backtracking", "Medium", True, True),
    (46, "Permutations", "permutations", "backtracking", "Medium", True, False),
    (90, "Subsets II", "subsets-ii", "backtracking", "Medium", True, False),
    (79, "Word Search", "word-search", "backtracking", "Medium", True, True),
    # graphs
    (200, "Number of Islands", "number-of-islands", "graphs", "Medium", True, True),
    (133, "Clone Graph", "clone-graph", "graphs", "Medium", True, True),
    (417, "Pacific Atlantic Water Flow", "pacific-atlantic-water-flow", "graphs", "Medium", True, False),
    (207, "Course Schedule", "course-schedule", "graphs", "Medium", True, True),
    (684, "Redundant Connection", "redundant-connection", "graphs", "Medium", True, False),
    (127, "Word Ladder", "word-ladder", "graphs", "Hard", True, True),
    # dp_1d
    (70, "Climbing Stairs", "climbing-stairs", "dp_1d", "Easy", True, False),
    (198, "House Robber", "house-robber", "dp_1d", "Medium", True, True),
    (213, "House Robber II", "house-robber-ii", "dp_1d", "Medium", True, False),
    (5, "Longest Palindromic Substring", "longest-palindromic-substring", "dp_1d", "Medium", True, True),
    (91, "Decode Ways", "decode-ways", "dp_1d", "Medium", True, False),
    (322, "Coin Change", "coin-change", "dp_1d", "Medium", True, True),
    (152, "Maximum Product Subarray", "maximum-product-subarray", "dp_1d", "Medium", True, True),
    (139, "Word Break", "word-break", "dp_1d", "Medium", True, True),
    (300, "Longest Increasing Subsequence", "longest-increasing-subsequence", "dp_1d", "Medium", True, True),
    # dp_2d
    (62, "Unique Paths", "unique-paths", "dp_2d", "Medium", True, False),
    (1143, "Longest Common Subsequence", "longest-common-subsequence", "dp_2d", "Medium", True, False),
    # greedy
    (53, "Maximum Subarray", "maximum-subarray", "greedy", "Medium", True, True),
    (55, "Jump Game", "jump-game", "greedy", "Medium", True, True),
    # intervals
    (57, "Insert Interval", "insert-interval", "intervals", "Medium", True, False),
    (56, "Merge Intervals", "merge-intervals", "intervals", "Medium", True, True),
    (435, "Non-overlapping Intervals", "non-overlapping-intervals", "intervals", "Medium", True, False),
    # bit_manipulation
    (191, "Number of 1 Bits", "number-of-1-bits", "bit_manipulation", "Easy", True, False),
    (338, "Counting Bits", "counting-bits", "bit_manipulation", "Easy", True, False),
    (190, "Reverse Bits", "reverse-bits", "bit_manipulation", "Easy", True, False),
    (268, "Missing Number", "missing-number", "bit_manipulation", "Easy", True, True),
    (371, "Sum of Two Integers", "sum-of-two-integers", "bit_manipulation", "Medium", True, False),
]

# Cues are this seed's own summary, not quoted from any external source.
PATTERNS: list[tuple[str, str]] = [
    ("arrays_hashing", "Need O(1) lookup/count, or a frequency map, over a flat collection."),
    ("two_pointers", "Sorted (or sortable) sequence; converging or same-direction pointers."),
    ("sliding_window", "Contiguous subarray/substring with a size or validity condition."),
    ("stack", "Nested structure, matching pairs, or 'next greater/smaller' queries."),
    ("binary_search", "Monotonic search space, even if not an obviously sorted array."),
    ("linked_list", "Pointer manipulation, cycle detection, or in-place reversal."),
    ("trees", "Recursive structure with a parent/child relationship to traverse."),
    ("tries", "Prefix matching across many strings."),
    ("heap", "Repeatedly need the current min/max as the set changes."),
    ("backtracking", "Build a candidate incrementally, prune, and undo a choice."),
    ("graphs", "Explicit or implicit graph — grid, adjacency list, or dependency order."),
    ("dp_1d", "Optimal choice at position i depends on a fixed window of prior positions."),
    ("dp_2d", "Optimal choice depends on two indices — grid or two-sequence comparison."),
    ("greedy", "A locally optimal choice at each step provably yields the global optimum."),
    ("intervals", "Overlapping ranges — sort by start or end, then sweep."),
    ("bit_manipulation", "Constant-space arithmetic via bit tricks."),
]

OPERATING_RULES: list[tuple[str, str, str]] = [
    (
        "minimum_viable_day",
        "On a day with under 20 minutes of real bandwidth: clear at most a "
        "handful of overdue reviews or five vocabulary words. Do not start a "
        "new problem. A Minimum Viable Day still counts as a day kept.",
        "bandwidth",
    ),
    (
        "review_cap_overflow",
        "The daily review cap defaults to 12. Overflow order is failed "
        "reviews first, then oldest-overdue, then due-today; the remainder "
        "pushes one day and its overdue_days counter increments. Nothing is "
        "ever silently dropped.",
        "repetition",
    ),
    (
        "pattern_interleaving",
        "Never more than 2 consecutive recommended problems from the same "
        "pattern once past the foundation phase — blocked practice inflates "
        "apparent mastery.",
        "recommender",
    ),
]
