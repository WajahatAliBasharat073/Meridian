/** Pure formatting helpers shared by the document-title ticker and the
 * floating Picture-in-Picture timer (lib/pipTimer.ts) -- kept separate
 * from both so the math is unit-testable without touching the DOM. */

import type { ActiveSession } from "./activityStore";

/** Seconds remaining until the block's scheduled end (session.targetEndMinutes),
 * matching ActivityController's own "countdown to scheduled end, not to
 * planned duration" rule. Negative once the window has been overrun. */
export function remainingSeconds(session: ActiveSession, nowMinutesInDay: number): number {
  return Math.round((session.targetEndMinutes - nowMinutesInDay) * 60);
}

/** How far through the scheduled window [0, 1] we are right now, matching
 * ActivityController's own progress-bar rule: progress is against the
 * *scheduled* window (plannedMinutes, extended if the session was
 * extended), not against work actually logged, and it holds at 1 rather
 * than continuing past it once the window is overrun. */
export function progressFraction(session: ActiveSession, nowMinutesInDay: number): number {
  const windowSec = Math.max(1, session.plannedMinutes * 60);
  const remaining = remainingSeconds(session, nowMinutesInDay);
  const elapsed = windowSec - Math.max(0, remaining);
  return Math.min(1, Math.max(0, elapsed / windowSec));
}

/** "12:34" (or "1:02:34" past an hour). A negative input is clamped to 0 --
 * callers that need to show overtime separately check the sign themselves
 * before formatting the absolute value. */
export function formatClock(totalSeconds: number): string {
  const clamped = Math.max(0, totalSeconds);
  const h = Math.floor(clamped / 3600);
  const m = Math.floor((clamped % 3600) / 60);
  const s = Math.floor(clamped % 60);
  const mm = h > 0 ? String(m).padStart(2, "0") : String(m);
  const ss = String(s).padStart(2, "0");
  return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
}
