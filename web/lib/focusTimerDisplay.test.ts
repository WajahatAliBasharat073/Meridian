import { describe, expect, it } from "vitest";
import { formatClock, remainingSeconds } from "./focusTimerDisplay";
import type { ActiveSession } from "./activityStore";

function session(overrides: Partial<ActiveSession> = {}): ActiveSession {
  return {
    blockId: 1,
    activity: "💻 Interview Prep — Coding",
    category: "InterviewPrep",
    state: "in_progress",
    startTime: Date.now(),
    totalElapsedSeconds: 0,
    plannedMinutes: 60,
    targetEndMinutes: 900, // 15:00
    extensionMinutes: 0,
    ...overrides,
  };
}

describe("formatClock", () => {
  it("formats under an hour as mm:ss", () => {
    expect(formatClock(0)).toBe("0:00");
    expect(formatClock(5)).toBe("0:05");
    expect(formatClock(65)).toBe("1:05");
    expect(formatClock(599)).toBe("9:59");
  });

  it("formats an hour or more as h:mm:ss", () => {
    expect(formatClock(3600)).toBe("1:00:00");
    expect(formatClock(3725)).toBe("1:02:05");
  });

  it("clamps a negative input to zero rather than showing a negative clock", () => {
    expect(formatClock(-30)).toBe("0:00");
  });
});

describe("remainingSeconds", () => {
  it("is a pure function of the block's scheduled end and the current wall-clock minute", () => {
    const s = session({ targetEndMinutes: 900 }); // 15:00
    expect(remainingSeconds(s, 840)).toBe(3600); // 14:00 -> 1h remaining
    expect(remainingSeconds(s, 895)).toBe(300); // 14:55 -> 5m remaining
  });

  it("goes negative past the scheduled end rather than clamping, so overtime is detectable", () => {
    const s = session({ targetEndMinutes: 900 });
    expect(remainingSeconds(s, 905)).toBe(-300);
  });

  it("depends only on absolute time, not on any elapsed-tick count -- the same session " +
    "queried at the same wall-clock minute always gives the same answer, whether that's " +
    "the first check after Focus was pressed or the first check after the tab was " +
    "backgrounded for an hour and its timers were throttled", () => {
    const s = session({ targetEndMinutes: 900, startTime: Date.now() - 999_000 });
    expect(remainingSeconds(s, 895)).toBe(remainingSeconds(s, 895));
    expect(remainingSeconds(s, 895)).toBe(300);
  });
});
