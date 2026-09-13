import { describe, expect, it } from "vitest";
import {
  evaluateReminders,
  NUDGE_INTERVAL_MINUTES,
  NUDGE_STOP_AT_FRACTION,
  PRE_SESSION_MINUTES,
  STALE_AFTER_MINUTES,
  type SentState,
} from "./sessionReminders";
import { timeStringToMinutes } from "./time";
import type { TimeBlockOut } from "./types";

function block(overrides: Partial<TimeBlockOut> = {}): TimeBlockOut {
  return {
    id: 1,
    seq: 1,
    start: "14:00:00",
    end: "15:00:00",
    activity: "💻 Interview Prep — Coding",
    tier: "T2",
    category: "InterviewPrep",
    planned_minutes: 60,
    status: "NOT DONE",
    actual_minutes: null,
    what_to_do: null,
    notes: null,
    is_current: true,
    has_focus_session: false,
    ...overrides,
  };
}

const START_MIN = timeStringToMinutes("14:00:00"); // 840

describe("evaluateReminders", () => {
  it("fires the pre-session notice exactly within the 5-minute window before start", () => {
    const b = block();
    expect(evaluateReminders(START_MIN - PRE_SESSION_MINUTES, [b], {}).due).toEqual([
      { kind: "pre", block: b },
    ]);
    expect(evaluateReminders(START_MIN - 1, [b], {}).due).toEqual([{ kind: "pre", block: b }]);
  });

  it("does not fire the pre-session notice before the window opens or once start has passed", () => {
    const b = block();
    expect(evaluateReminders(START_MIN - PRE_SESSION_MINUTES - 1, [b], {}).due).toEqual([]);
    expect(evaluateReminders(START_MIN, [b], {}).due.some((d) => d.kind === "pre")).toBe(false);
  });

  it("fires the start notification once the block's scheduled start arrives", () => {
    const b = block();
    const { due } = evaluateReminders(START_MIN, [b], {});
    expect(due).toEqual([{ kind: "start", block: b }]);
  });

  it("does not fire the start notification if Focus was already pressed for this block", () => {
    const b = block({ has_focus_session: true });
    const { due } = evaluateReminders(START_MIN, [b], {});
    expect(due).toEqual([]);
  });

  it("fires the first nudge NUDGE_INTERVAL_MINUTES after start if Focus still hasn't been pressed", () => {
    const b = block();
    // Start notification already recorded as sent (as it would be after
    // the first evaluateReminders call at start time).
    const sentState: SentState = { [b.id]: { start: true } };
    const { due } = evaluateReminders(START_MIN + NUDGE_INTERVAL_MINUTES, [b], sentState);
    expect(due).toEqual([{ kind: "nudge", block: b }]);
  });

  it("does not fire the nudge before its threshold", () => {
    const b = block();
    const sentState: SentState = { [b.id]: { start: true } };
    expect(
      evaluateReminders(START_MIN + NUDGE_INTERVAL_MINUTES - 1, [b], sentState).due
    ).toEqual([]);
  });

  it("never fires a nudge in the same tick a start notification first fires", () => {
    // Reopening the tab for the first time well after both thresholds --
    // "start" and "nudge" should never land as one simultaneous burst;
    // the nudge waits for a tick where "start" was already sent.
    const b = block();
    const { due } = evaluateReminders(START_MIN + NUDGE_INTERVAL_MINUTES, [b], {});
    expect(due).toEqual([{ kind: "start", block: b }]);
  });

  it("repeats the nudge every NUDGE_INTERVAL_MINUTES, one at a time, while still unstarted", () => {
    const b = block();
    let state: SentState = { [b.id]: { start: true } };

    const first = evaluateReminders(START_MIN + NUDGE_INTERVAL_MINUTES, [b], state);
    expect(first.due).toEqual([{ kind: "nudge", block: b }]);
    state = first.nextState;

    // Immediately after: not due again yet.
    expect(evaluateReminders(START_MIN + NUDGE_INTERVAL_MINUTES, [b], state).due).toEqual([]);
    expect(
      evaluateReminders(START_MIN + 2 * NUDGE_INTERVAL_MINUTES - 1, [b], state).due
    ).toEqual([]);

    // A full interval later: due again.
    const second = evaluateReminders(START_MIN + 2 * NUDGE_INTERVAL_MINUTES, [b], state);
    expect(second.due).toEqual([{ kind: "nudge", block: b }]);
  });

  it("catches up with exactly one nudge, not a backlog burst, after several intervals unattended", () => {
    const b = block();
    const state: SentState = { [b.id]: { start: true } };
    // Five intervals' worth of time passed at once (e.g. tab was closed).
    const { due, nextState } = evaluateReminders(
      START_MIN + 5 * NUDGE_INTERVAL_MINUTES,
      [b],
      state
    );
    expect(due).toEqual([{ kind: "nudge", block: b }]);
    // The next nudge should be due one interval later, not immediately.
    expect(
      evaluateReminders(START_MIN + 5 * NUDGE_INTERVAL_MINUTES, [b], nextState).due
    ).toEqual([]);
    expect(
      evaluateReminders(START_MIN + 6 * NUDGE_INTERVAL_MINUTES, [b], nextState).due
    ).toEqual([{ kind: "nudge", block: b }]);
  });

  it("stops the nudge cycle automatically once half the block's planned duration has elapsed", () => {
    const b = block({ planned_minutes: 20 }); // half = 10 minutes after start
    const state: SentState = { [b.id]: { start: true } };
    // Still within the first half: due.
    expect(evaluateReminders(START_MIN + 9, [b], state).due).toEqual([{ kind: "nudge", block: b }]);
    // At/after the halfway point: the cycle has stopped, even though
    // Focus was still never pressed.
    expect(evaluateReminders(START_MIN + 10, [b], state).due).toEqual([]);
    expect(evaluateReminders(START_MIN + 15, [b], state).due).toEqual([]);
  });

  it("uses NUDGE_STOP_AT_FRACTION consistently with the 50%-of-duration rule", () => {
    expect(NUDGE_STOP_AT_FRACTION).toBe(0.5);
  });

  it("stops nudging permanently once Focus is pressed, mid-cycle", () => {
    const b = block({ has_focus_session: true });
    const sentState: SentState = { [b.id]: { start: true, nudgeCount: 2 } };
    const { due } = evaluateReminders(START_MIN + 3 * NUDGE_INTERVAL_MINUTES, [b], sentState);
    expect(due).toEqual([]);
  });

  it("never re-fires a reminder kind already recorded as sent (no duplicates)", () => {
    const b = block();
    let state: SentState = {};

    const first = evaluateReminders(START_MIN, [b], state);
    expect(first.due).toEqual([{ kind: "start", block: b }]);
    state = first.nextState;

    // Re-checking at the same instant, or any later instant, must not
    // re-fire "start" now that it's recorded.
    const second = evaluateReminders(START_MIN, [b], state);
    expect(second.due).toEqual([]);
    const third = evaluateReminders(START_MIN + 1, [b], state);
    expect(third.due).toEqual([]);
  });

  it("treats a block whose start is long past as stale, and stops proposing a start notification for it", () => {
    const b = block();
    expect(evaluateReminders(START_MIN + STALE_AFTER_MINUTES, [b], {}).due).toEqual([]);
  });

  it("garbage-collects sent-state entries for blocks no longer in today's schedule", () => {
    const b = block({ id: 42 });
    const staleState: SentState = { 999: { start: true, pre: true, nudgeCount: 3 } };
    const { nextState } = evaluateReminders(START_MIN, [b], staleState);
    expect(nextState[999]).toBeUndefined();
    expect(nextState[42]).toEqual({ start: true });
  });

  it("evaluates multiple blocks independently", () => {
    const early = block({ id: 1, start: "09:00:00" });
    const late = block({ id: 2, start: "14:00:00", activity: "📚 English Vocabulary" });
    const nowMin = timeStringToMinutes("09:00:00");
    const { due } = evaluateReminders(nowMin, [early, late], {});
    expect(due).toEqual([{ kind: "start", block: early }]);
  });
});
