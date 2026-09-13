/**
 * Schedule-driven session reminders: a 5-minute pre-session notice, a
 * notification when the block actually starts, and a repeating nudge
 * every few minutes after that if Focus still hasn't been pressed --
 * capped automatically once half the block's planned duration has
 * elapsed, since nudging about a session that's already half over stops
 * being useful and starts being noise.
 *
 * Deliberately a pure function over (now, blocks, sentState) rather than
 * its own interval/timer -- the caller (useSessionReminders in
 * NotificationCenter.tsx) already has a ticking clock via useToday's
 * poll, and keeping this pure makes every rule here directly unit
 * testable with fixed timestamps instead of fake timers.
 */

import { timeStringToMinutes } from "./time";
import type { TimeBlockOut } from "./types";

export const PRE_SESSION_MINUTES = 5;
export const NUDGE_INTERVAL_MINUTES = 3;
// Once this fraction of the block's planned duration has passed since
// its scheduled start, the nudge cycle stops on its own even if Focus
// was never pressed -- there's too little of the session left for a
// reminder to be worth sending.
export const NUDGE_STOP_AT_FRACTION = 0.5;
// A block whose scheduled start is further in the past than this is
// treated as stale for the *start* notification -- e.g. the tab was
// closed all afternoon and reopened hours later. Without this guard,
// reopening the app would fire a batch of "session started"
// notifications for blocks whose windows are long over, which is noise,
// not a reminder. (The nudge cycle has its own, duration-relative stop
// condition above and doesn't use this constant.)
export const STALE_AFTER_MINUTES = 15;

export type ReminderKind = "pre" | "start" | "nudge";

export interface DueReminder {
  kind: ReminderKind;
  block: TimeBlockOut;
}

/** Per block id: whether "pre" and "start" have fired, and how many
 * nudges have fired so far (a count, not a flag, since the nudge
 * repeats). Persisted to localStorage by the caller; block ids are real
 * per-day DB rows (a new schedule generates new ids), so this naturally
 * resets day to day. */
export interface BlockReminderState {
  pre?: true;
  start?: true;
  nudgeCount?: number;
}
export type SentState = Record<number, BlockReminderState>;

export function evaluateReminders(
  nowMin: number,
  blocks: TimeBlockOut[],
  sentState: SentState
): { due: DueReminder[]; nextState: SentState } {
  const due: DueReminder[] = [];
  const nextState: SentState = {};

  for (const block of blocks) {
    const startMin = timeStringToMinutes(block.start);
    const sentForBlock = sentState[block.id] ?? {};
    const nextForBlock: BlockReminderState = { ...sentForBlock };

    const alreadyStarted = block.has_focus_session;
    const startStale = nowMin >= startMin + STALE_AFTER_MINUTES;

    if (
      !sentForBlock.pre &&
      !alreadyStarted &&
      nowMin >= startMin - PRE_SESSION_MINUTES &&
      nowMin < startMin
    ) {
      due.push({ kind: "pre", block });
      nextForBlock.pre = true;
    }

    if (!sentForBlock.start && !alreadyStarted && nowMin >= startMin && !startStale) {
      due.push({ kind: "start", block });
      nextForBlock.start = true;
    }

    // The nudge cycle only ever follows a start notification from a
    // *prior* check, never the same tick it fires in -- reopening the
    // tab well after both thresholds have passed should still feel like
    // "you missed the start, and you still haven't begun," one message
    // after the other, not two identical-instant notifications at once.
    const nudgeStopMin = startMin + block.planned_minutes * NUDGE_STOP_AT_FRACTION;
    if (sentForBlock.start && !alreadyStarted && nowMin < nudgeStopMin) {
      const minutesSinceStart = nowMin - startMin;
      const expectedNudges = Math.floor(minutesSinceStart / NUDGE_INTERVAL_MINUTES);
      const alreadySent = sentForBlock.nudgeCount ?? 0;
      if (expectedNudges > alreadySent) {
        due.push({ kind: "nudge", block });
        // Jump straight to the expected count rather than +1 -- if the
        // tab was closed across several intervals, send exactly one
        // nudge now and resume the normal cadence from here, instead of
        // firing a backlog burst.
        nextForBlock.nudgeCount = expectedNudges;
      }
    }

    if (Object.keys(nextForBlock).length > 0) {
      nextState[block.id] = nextForBlock;
    }
  }

  return { due, nextState };
}

const SENT_STATE_STORAGE = "meridian_session_reminder_state";

export function loadSentState(): SentState {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(SENT_STATE_STORAGE);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export function saveSentState(state: SentState): void {
  try {
    localStorage.setItem(SENT_STATE_STORAGE, JSON.stringify(state));
  } catch {}
}
