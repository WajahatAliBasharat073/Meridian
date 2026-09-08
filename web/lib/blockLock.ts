import { timeStringToMinutes } from "@/lib/time";
import type { TimeBlockOut } from "@/lib/types";

/** Client-side mirror of api/app/engines/block_lock.py — same threshold,
 * same rule. This copy is for UI responsiveness only (disabling a button
 * before the click even lands); the server enforces it independently and
 * is the actual authority, so a stale or manipulated client can't bypass
 * it by skipping this check. */
export const BLOCK_LOCK_THRESHOLD = 0.7;

export function isBlockLocked(block: TimeBlockOut, nowMinutes: number): boolean {
  if (block.has_focus_session || block.planned_minutes <= 0) return false;
  const elapsed = nowMinutes - timeStringToMinutes(block.start);
  if (elapsed < 0) return false;
  return elapsed >= BLOCK_LOCK_THRESHOLD * block.planned_minutes;
}

/** How far into the lock the block is, for a "locks in Nm" style message
 * before it actually locks. Null once already locked or not applicable. */
export function minutesUntilLock(block: TimeBlockOut, nowMinutes: number): number | null {
  if (block.has_focus_session || block.planned_minutes <= 0) return null;
  const lockAt = timeStringToMinutes(block.start) + BLOCK_LOCK_THRESHOLD * block.planned_minutes;
  const remaining = lockAt - nowMinutes;
  return remaining > 0 ? remaining : null;
}

export const LOCK_MESSAGE =
  "Locked — most of this block's window passed without starting Focus on it. Use Skip to acknowledge it and move on.";

/** Client-side mirror of block_lock.py's is_too_early_to_complete — same
 * 5-minute guard window. UI responsiveness only; the server enforces it
 * independently. */
export const EARLY_COMPLETION_GUARD_MINUTES = 5;

export function isTooEarlyToComplete(block: TimeBlockOut, nowMinutes: number): boolean {
  const remaining = timeStringToMinutes(block.end) - nowMinutes;
  return remaining > EARLY_COMPLETION_GUARD_MINUTES;
}

export const EARLY_COMPLETION_MESSAGE =
  "Too early to mark this done — wait until the last 5 minutes of its window (or after it ends).";
