/**
 * The problem-solving checklist shown beside the DSA topic browser --
 * pure reference content plus localStorage persistence for which boxes
 * are ticked. Not tied to any particular problem_id: there is no
 * "current problem" concept in this app (problems are browsed, not
 * opened into a dedicated solve screen), so this is a general-purpose
 * companion meant to sit beside wherever the user is actually writing
 * code (their editor, LeetCode, a notebook) and get manually reset
 * between problems.
 *
 * Steps 1-6 and their item wording are the user's own -- verbatim.
 * Step 0 and Step 7 are additions: the given checklist runs from
 * "clarify constraints" straight through to "verify the code", which
 * covers Nielsen/UMPIRE's Match-Plan-Implement-Review stages well but
 * has no explicit Understand stage before it (confirming you're solving
 * the problem as asked, not as assumed -- the single most common way a
 * technically correct solution fails) and no Evaluate stage after it
 * (recapping the complexity you promised still holds, and the
 * verbalize/follow-up habits interviewers actually grade). `notes` are
 * reference sub-points from the original list that were never
 * individually-checkable bullets themselves.
 */

export interface ChecklistItem {
  id: string;
  text: string;
  notes?: string[];
}

export interface ChecklistStep {
  id: string;
  title: string;
  timeEstimate: string;
  added?: boolean;
  items: ChecklistItem[];
}

export const DSA_CHECKLIST: ChecklistStep[] = [
  {
    id: "s0",
    title: "Understand & Restate",
    timeEstimate: "30s–1 min",
    added: true,
    items: [
      {
        id: "s0-restate",
        text: "Restate the problem back in your own words before anything else -- confirms you're solving the actual problem, not an assumed one.",
      },
      {
        id: "s0-ambiguity",
        text: "Clarify ambiguous wording explicitly:",
        notes: [
          "Contiguous vs. subsequence",
          "Inclusive vs. exclusive ranges",
          "0-indexed vs. 1-indexed",
          '"Distinct" vs. "unique"',
          "Ascending vs. descending order assumed",
        ],
      },
      {
        id: "s0-signature",
        text: "Confirm the exact function signature expected, and whether in-place mutation is allowed.",
      },
    ],
  },
  {
    id: "s1",
    title: "Clarify & Determine Constraints",
    timeEstimate: "1–2 mins",
    items: [
      {
        id: "s1-datatypes",
        text: "Identify exact data types of inputs and return values (e.g., int vs. float, return list vs. modify in-place).",
      },
      {
        id: "s1-complexity",
        text: "Check input size N to fix target time complexity:",
        notes: [
          "N ≤ 12       ➔ O(2^N) or O(N!) (Backtracking / Recursion)",
          "N ≤ 1,000    ➔ O(N^2) (Nested Loops / Dynamic Programming)",
          "N ≤ 10^5     ➔ O(N) or O(N log N) (Hash Maps, Two Pointers, Binary Search, Sorting)",
          "N ≥ 10^9     ➔ O(log N) or O(1) (Binary Search, Math formulas)",
        ],
      },
      {
        id: "s1-structural",
        text: "Ask structural questions:",
        notes: [
          "Are values sorted or unsorted?",
          "Are there negative numbers, zeroes, or duplicate values?",
          "Does relative order matter in the final output?",
          "Is memory restricted (O(1) auxiliary space requirement)?",
        ],
      },
    ],
  },
  {
    id: "s2",
    title: "Manual Examples & Edge Case Enumeration",
    timeEstimate: "2 mins",
    items: [
      {
        id: "s2-happypath",
        text: 'Trace a standard "Happy Path" example manually to build intuition.',
      },
      {
        id: "s2-edgecases",
        text: "Explicitly define boundary & edge cases:",
        notes: [
          'Empty input ([] or "") or single element ([1]).',
          "Extremely small / extremely large inputs (integer overflow risks).",
          "Inputs with all duplicate values ([5, 5, 5]) or already sorted/reversed values.",
          "Null / None inputs or negative inputs.",
        ],
      },
    ],
  },
  {
    id: "s3",
    title: "Pattern Matching & Solution Design",
    timeEstimate: "3 mins",
    items: [
      {
        id: "s3-bruteforce",
        text: "State the Brute Force approach first (e.g., O(N^2)) and identify the bottleneck.",
      },
      {
        id: "s3-patterns",
        text: "Map problem characteristics to core DSA patterns:",
        notes: [
          "Subarrays / Substrings (Contiguous) ➔ Sliding Window / Prefix Sum",
          "Fast Lookups / Unique Items ➔ Hash Set / Hash Map",
          "Sorted Data / Boundary Search ➔ Binary Search / Two Pointers",
          "Top K Elements / Dynamic Min-Max ➔ Heap / Priority Queue",
          "Pathfinding / Graphs / Trees ➔ BFS (Shortest Path) / DFS (Exploration)",
          "Overlapping Decisions ➔ Dynamic Programming (Memoization / Tabulation)",
          "Nested Structures / Balancing ➔ Stack / Queue",
        ],
      },
      {
        id: "s3-optimize",
        text: "Formulate the Optimized Solution (Target O(N) or O(N log N)).",
      },
    ],
  },
  {
    id: "s4",
    title: "Communicate Time-Space Trade-offs",
    timeEstimate: "1 min",
    items: [
      {
        id: "s4-state",
        text: "Explicitly state Time and Auxiliary Space Complexity to interviewer before typing code.",
      },
      {
        id: "s4-tradeoffs",
        text: 'Discuss alternative trade-offs (e.g., "We can achieve O(N) time with O(N) space using a set, or O(N log N) time with O(1) space by sorting first").',
      },
      {
        id: "s4-consent",
        text: "Obtain interviewer consent before writing code.",
      },
    ],
  },
  {
    id: "s5",
    title: "FAANG-Standard Clean Code",
    timeEstimate: "5–8 mins",
    items: [
      { id: "s5-guards", text: "Add guard clauses at top for empty/invalid inputs." },
      {
        id: "s5-hints",
        text: "Include type hints (numbers: list[int] -> tuple[int, int]) and docstrings.",
      },
      {
        id: "s5-shadow",
        text: "Avoid shadowing Python built-ins (sum, min, max, list, set, input).",
      },
      {
        id: "s5-iteration",
        text: "Use direct Pythonic iteration (for num in numbers:) over index loops (for i in range(len(nums)):).",
      },
      {
        id: "s5-elif",
        text: "Avoid elif when dual tracking independent variables (e.g., min and max).",
      },
      {
        id: "s5-names",
        text: "Use self-explanatory variable names (unique_numbers instead of arr, num_counts instead of c).",
      },
    ],
  },
  {
    id: "s6",
    title: "Manual Dry Run & Defensive Verification",
    timeEstimate: "2–3 mins",
    items: [
      {
        id: "s6-noclaim",
        text: "DO NOT declare finished immediately. Manually walk through code line-by-line using your Step 2 example.",
      },
      {
        id: "s6-table",
        text: "Create a dry-run state table in code comments (tracking loop indices and variable states).",
      },
      {
        id: "s6-smallest",
        text: "Test the smallest / simplest possible case explicitly (empty, single element) -- not just the happy path. Many bugs only surface at the boundary.",
      },
      {
        id: "s6-boundary",
        text: "Check boundary conditions: index bounds (len(arr) - 1), loop termination conditions (left <= right vs. left < right), and initialization values (0, 1, float('inf')).",
      },
      {
        id: "s6-safety",
        text: "Confirm edge case safety (ensure no index-out-of-bounds or zero-division errors occur).",
      },
    ],
  },
  {
    id: "s7",
    title: "Reflect, Verbalize & Extend",
    timeEstimate: "1–2 mins",
    added: true,
    items: [
      {
        id: "s7-recap",
        text: "Recap the final Time/Space complexity out loud and confirm it still matches what you promised in Step 4 -- a quiet regression here is a common failure mode.",
      },
      {
        id: "s7-narrate",
        text: "Narrate your reasoning while typing, don't code in silence -- interviewers grade the thinking, not just the output.",
      },
      {
        id: "s7-followup",
        text: "Mention follow-up angles time permitting: how would this scale to a stream/distributed input, or under a different constraint (memory-limited, sorted input, many duplicates)?",
      },
      {
        id: "s7-feedback",
        text: "Ask directly if there's anything the interviewer would like you to go deeper on.",
      },
    ],
  },
];

const CHECKED_STORAGE = "meridian_dsa_checklist_checked";
const PANEL_OPEN_STORAGE = "meridian_dsa_checklist_open";

export function getCheckedItems(): Record<string, boolean> {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(CHECKED_STORAGE);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export function setCheckedItems(checked: Record<string, boolean>): void {
  try {
    localStorage.setItem(CHECKED_STORAGE, JSON.stringify(checked));
  } catch {}
}

export function getPanelOpen(defaultValue = false): boolean {
  if (typeof window === "undefined") return defaultValue;
  try {
    const raw = localStorage.getItem(PANEL_OPEN_STORAGE);
    return raw === null ? defaultValue : raw === "1";
  } catch {
    return defaultValue;
  }
}

export function setPanelOpen(open: boolean): void {
  try {
    localStorage.setItem(PANEL_OPEN_STORAGE, open ? "1" : "0");
  } catch {}
}

export function totalChecklistItemCount(): number {
  return DSA_CHECKLIST.reduce((sum, step) => sum + step.items.length, 0);
}
