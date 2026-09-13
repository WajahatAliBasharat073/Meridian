/**
 * Session -> destination mapping for the "Focus" action (ActivityController's
 * Start Activity / Start Focus Session buttons). Pressing Focus starts the
 * timer as before, and — when the session it started has a configured
 * destination — also navigates there, so starting "English Vocabulary" lands
 * you on the vocabulary review flow instead of leaving you looking at a
 * countdown on Today.
 *
 * A route is keyed on `TimeBlock.category` (the real values are declared
 * once in lib/category.ts). Two categories hold more than one kind of
 * work, distinguished only by the block's free-text `activity`:
 * "InterviewPrep" covers both DSA practice and ML/GenAI study, and
 * "English" covers both grammar and vocabulary. A route may add
 * `activityIncludes` (matched case-insensitively) to pick a more specific
 * destination before falling back to that category's default route --
 * or, if there's no default (English has none), an unmatched activity
 * resolves to null rather than being routed to the wrong page.
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

// The real schedule (scripts/restructure_workday.py) only ever produces
// two InterviewPrep tracks, and names them consistently: "... — Coding"
// (today's scheduled DSA problem + review queue) and "... — Theory" (one
// ML/GenAI curriculum module, sometimes suffixed with the specific topic,
// e.g. "Theory: ML System Design" or "Theory (part 2)"). A prior version
// of this file tried to detect DSA by matching topic keywords
// (sliding window, graph, etc.) against the activity text, but the real
// blocks never contain those words at all -- only "Coding" or "Theory"
// -- so every Coding block silently fell through to the ML fallback.
// Matching on "Theory" instead, and making DSA the InterviewPrep default,
// covers every activity string the real schedule actually produces:
// "Coding", "Coding (part N)", "Theory", "Theory (part N)",
// "Theory: <topic>", and "Timed Mock + Weak-Pattern Review" (a DSA
// review session, not ML theory).
const ML_THEORY_ACTIVITY_MARKERS = ["theory"];

// "English" also covers two distinct tracks since the schedule split
// English into grammar + vocabulary ("📚 English Grammar Learning" vs.
// "📚 English Vocabulary") -- only vocabulary has a page in the app so
// far, so a Grammar block correctly resolves to null (no destination,
// not a misroute to the vocabulary page) until a grammar page exists.
const VOCABULARY_ACTIVITY_MARKERS = ["vocabulary"];

export const FOCUS_ROUTES: FocusRoute[] = [
  { category: "Thesis", destination: "/research", label: "Thesis & Research" },
  {
    category: "English",
    activityIncludes: VOCABULARY_ACTIVITY_MARKERS,
    destination: "/vocabulary",
    label: "English Vocabulary",
  },
  { category: "Reading", destination: "/reading", label: "Reading Log" },
  {
    category: "InterviewPrep",
    activityIncludes: ML_THEORY_ACTIVITY_MARKERS,
    destination: "/concepts",
    label: "AI & ML",
  },
  { category: "InterviewPrep", destination: "/problems", label: "DSA Prep" },
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
