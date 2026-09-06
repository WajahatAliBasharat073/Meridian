import type { MasteryLevel } from "./types";

export interface MasteryMeta {
  level: MasteryLevel;
  label: string;
  shortLabel: string;
  colorVar: string;
  intervalDays: number;
}

// Mirrors app/domain.py's LADDER_DAYS and the L0-L6 labels from the build
// prompt (5.1). Colour never stands alone — every use pairs this with
// `label`.
export const MASTERY_LEVELS: MasteryMeta[] = [
  { level: "L0", label: "Seen", shortLabel: "L0", colorVar: "var(--mastery-l0)", intervalDays: 1 },
  { level: "L1", label: "Understood", shortLabel: "L1", colorVar: "var(--mastery-l1)", intervalDays: 1 },
  { level: "L2", label: "Solved w/ help", shortLabel: "L2", colorVar: "var(--mastery-l2)", intervalDays: 3 },
  { level: "L3", label: "Solved alone", shortLabel: "L3", colorVar: "var(--mastery-l3)", intervalDays: 7 },
  { level: "L4", label: "Can explain", shortLabel: "L4", colorVar: "var(--mastery-l4)", intervalDays: 14 },
  { level: "L5", label: "Interview ready", shortLabel: "L5", colorVar: "var(--mastery-l5)", intervalDays: 30 },
  { level: "L6", label: "Mastered", shortLabel: "L6", colorVar: "var(--mastery-l6)", intervalDays: 60 },
];

export function masteryMeta(level: MasteryLevel): MasteryMeta {
  const found = MASTERY_LEVELS.find((m) => m.level === level);
  if (!found) throw new Error(`Unknown mastery level: ${level}`);
  return found;
}
