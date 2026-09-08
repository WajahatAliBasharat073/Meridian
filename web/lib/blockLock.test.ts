import { describe, expect, it } from "vitest";
import {
  BLOCK_LOCK_THRESHOLD,
  EARLY_COMPLETION_GUARD_MINUTES,
  isBlockLocked,
  isTooEarlyToComplete,
  minutesUntilLock,
} from "./blockLock";
import type { TimeBlockOut } from "./types";

/** These are client-side *mirrors* of api/app/engines/block_lock.py. The
 * server is the authority, but a mirror that disagrees with it is worse than
 * no mirror at all — it disables a button the server would have allowed, or
 * enables one the server will reject with a 423. So these tests pin the
 * mirror to the same numbers the Python tests pin the engine to. */
function block(overrides: Partial<TimeBlockOut> = {}): TimeBlockOut {
  return {
    id: 1,
    seq: 1,
    start: "09:00:00",
    end: "10:00:00",
    activity: "Deep work",
    tier: "T2",
    category: "Job",
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

const at = (h: number, m: number) => h * 60 + m;

describe("isBlockLocked — the 70% no-focus rule", () => {
  it("does not lock before the block starts", () => {
    expect(isBlockLocked(block(), at(8, 59))).toBe(false);
  });

  it("does not lock just after the start", () => {
    expect(isBlockLocked(block(), at(9, 5))).toBe(false);
  });

  it("does not lock one minute before the threshold", () => {
    // 60-minute block, 70% = 42 minutes.
    expect(isBlockLocked(block(), at(9, 41))).toBe(false);
  });

  it("locks exactly at the threshold", () => {
    expect(isBlockLocked(block(), at(9, 42))).toBe(true);
  });

  it("never locks once a focus session exists", () => {
    expect(isBlockLocked(block({ has_focus_session: true }), at(12, 0))).toBe(false);
  });

  it("never locks a zero-length block", () => {
    expect(isBlockLocked(block({ planned_minutes: 0 }), at(23, 0))).toBe(false);
  });

  it("matches the Python engine's threshold", () => {
    expect(BLOCK_LOCK_THRESHOLD).toBe(0.7);
  });
});

describe("minutesUntilLock", () => {
  it("counts down to the lock moment", () => {
    expect(minutesUntilLock(block(), at(9, 30))).toBe(12);
  });

  it("is null once already locked", () => {
    expect(minutesUntilLock(block(), at(9, 50))).toBeNull();
  });

  it("is null when a session already exists", () => {
    expect(minutesUntilLock(block({ has_focus_session: true }), at(9, 0))).toBeNull();
  });
});

describe("isTooEarlyToComplete — the last-5-minutes rule", () => {
  it("is too early with half the window left", () => {
    expect(isTooEarlyToComplete(block(), at(9, 30))).toBe(true);
  });

  it("is still too early with six minutes left", () => {
    expect(isTooEarlyToComplete(block(), at(9, 54))).toBe(true);
  });

  it("allows completion at exactly five minutes left", () => {
    expect(isTooEarlyToComplete(block(), at(9, 55))).toBe(false);
  });

  it("allows completion inside the guard window", () => {
    expect(isTooEarlyToComplete(block(), at(9, 58))).toBe(false);
  });

  it("allows completion exactly at the end", () => {
    expect(isTooEarlyToComplete(block(), at(10, 0))).toBe(false);
  });

  it("allows completion after the block has ended", () => {
    expect(isTooEarlyToComplete(block(), at(10, 30))).toBe(false);
  });

  it("matches the Python engine's guard window", () => {
    expect(EARLY_COMPLETION_GUARD_MINUTES).toBe(5);
  });
});

describe("the two rules together", () => {
  it("leaves a window where neither rule blocks completion", () => {
    // With focus started, the 70% lock never applies; the last five minutes
    // are then completable. This is the normal, honest path.
    const engaged = block({ has_focus_session: true });
    expect(isBlockLocked(engaged, at(9, 56))).toBe(false);
    expect(isTooEarlyToComplete(engaged, at(9, 56))).toBe(false);
  });

  it("blocks a never-started block at the end of its window", () => {
    // Past 70% with no session: the lock catches it even though the
    // early-completion guard would now allow it.
    expect(isBlockLocked(block(), at(9, 56))).toBe(true);
  });
});
