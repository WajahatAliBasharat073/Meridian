import type { SolveMethod } from "./types";

/** Shared so the logging form and every read-only display name a method the
 * same way. Order is deliberate: most independent first, so the list itself
 * reads as a ladder. */
export const SOLVE_METHODS: {
  value: SolveMethod;
  label: string;
  hint: string;
  /** True when the attempt needed outside help. Drives the "unaided" counts
   * — the thing a progress number is worthless without. */
  assisted: boolean;
}[] = [
  { value: "independent", label: "Solved independently", hint: "No help at all", assisted: false },
  {
    value: "recalled_pattern",
    label: "Recalled the pattern",
    hint: "Recognised it from earlier practice",
    assisted: false,
  },
  { value: "after_hint", label: "After a hint", hint: "Needed a nudge, then got it", assisted: true },
  {
    value: "after_editorial",
    label: "After reading the solution",
    hint: "Read the editorial",
    assisted: true,
  },
  { value: "after_video", label: "After a video", hint: "Watched an explanation", assisted: true },
  {
    value: "brute_force_only",
    label: "Brute force only",
    hint: "Working, but not optimal",
    assisted: false,
  },
  { value: "not_solved", label: "Didn't solve it", hint: "Attempted, didn't get there", assisted: true },
];

export const SOLVE_METHOD_LABELS: Record<SolveMethod, string> = SOLVE_METHODS.reduce(
  (acc, m) => ({ ...acc, [m.value]: m.label }),
  {} as Record<SolveMethod, string>
);

export function isAssisted(method: SolveMethod): boolean {
  return SOLVE_METHODS.find((m) => m.value === method)?.assisted ?? false;
}
