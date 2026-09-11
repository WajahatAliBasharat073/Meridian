/**
 * Session -> destination mapping for the "Focus" action (ActivityController's
 * Start Activity / Start Focus Session buttons). Pressing Focus starts the
 * timer as before, and — when the session it started has a configured
 * destination — also navigates there, so starting "English Vocabulary" lands
 * you on the vocabulary review flow instead of leaving you looking at a
 * countdown on Today.
 *
 * A route is keyed on `TimeBlock.category` (the real values are declared
 * once in lib/category.ts). One category can hold two kinds of work --
 * "InterviewPrep" covers both DSA practice and ML/GenAI study, distinguished
 * only by the block's free-text `activity` -- so a route may add
 * `activityIncludes` (matched case-insensitively) to pick a more specific
 * destination before falling back to that category's default route.
 *
 * To add a new destination later: add one object to FOCUS_ROUTES. Nothing
 * else in this file, and nothing in ActivityController, needs to change.
 */

export interface FocusRoute {
  category: string;
  /** Case-insensitive substrings checked against the block's `activity`
   * text. When present, this route only applies if one matches; omit it
   * for a category's catch-all default. */
  activityIncludes?: string[];
  destination: string;
  label: string;
}

// DSA-flavoured activity text under the shared "InterviewPrep" category --
// drawn from the DSA module's own pattern list (Module A's submodules:
// arrays/hashing, two pointers, sliding window, stack, binary search,
// linked lists, intervals, trees, tries/heaps, backtracking, graphs, DP,
// math/geometry/bit manipulation) plus the obvious generic terms.
const DSA_ACTIVITY_MARKERS = [
  "dsa",
  "leetcode",
  "two pointer",
  "sliding window",
  "binary search",
  "linked list",
  "backtrack",
  "dynamic programming",
  "greedy",
  "graph",
  "tree",
  "heap",
  "trie",
  "stack",
  "bit manipulation",
  "array",
  "hashing",
];

export const FOCUS_ROUTES: FocusRoute[] = [
  { category: "Thesis", destination: "/research", label: "Thesis & Research" },
  { category: "English", destination: "/vocabulary", label: "English Vocabulary" },
  { category: "Reading", destination: "/reading", label: "Reading Log" },
  {
    category: "InterviewPrep",
    activityIncludes: DSA_ACTIVITY_MARKERS,
    destination: "/problems",
    label: "DSA Prep",
  },
  { category: "InterviewPrep", destination: "/concepts", label: "AI & ML" },
  // Example of extending this later without touching the Focus button:
  // { category: "SystemDesign", destination: "/system-design", label: "System Design" },
];

/** null when nothing is configured for this category -- callers must
 * treat that as "stay put", not an error (a session with no mapped page,
 * e.g. Prayer or Recovery, is expected, not a bug). */
export function resolveFocusDestination(category: string, activity: string): string | null {
  const activityLower = activity.toLowerCase();

  const specific = FOCUS_ROUTES.find(
    (r) =>
      r.category === category &&
      r.activityIncludes != null &&
      r.activityIncludes.some((marker) => activityLower.includes(marker))
  );
  if (specific) return specific.destination;

  const fallback = FOCUS_ROUTES.find((r) => r.category === category && r.activityIncludes == null);
  return fallback?.destination ?? null;
}
