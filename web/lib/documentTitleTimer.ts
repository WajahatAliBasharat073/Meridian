/**
 * Shows the live countdown in the browser tab title -- the one "always
 * visible without the tab being focused" signal every browser supports
 * unconditionally (it's what renders in the taskbar/dock preview and the
 * tab strip). Works everywhere; lib/pipTimer.ts's floating window is the
 * enhancement for browsers that support it, this is the universal floor.
 */

import { subscribeActiveSession, type ActiveSession } from "./activityStore";
import { formatClock, remainingSeconds } from "./focusTimerDisplay";
import { nowMinutesInKarachi } from "./time";

let baseTitle = "Meridian";
let tickHandle: ReturnType<typeof setInterval> | null = null;
let unsubscribe: (() => void) | null = null;
let started = false;

function render(session: ActiveSession | null) {
  if (typeof document === "undefined") return;
  if (!session || session.state !== "in_progress") {
    document.title = baseTitle;
    return;
  }
  const remaining = remainingSeconds(session, nowMinutesInKarachi());
  const clock = remaining >= 0 ? formatClock(remaining) : `+${formatClock(-remaining)}`;
  document.title = `${clock} · ${session.activity}`;
}

/** Idempotent -- safe to call from more than one mounted component; only
 * the first call actually starts the ticking interval. */
export function startDocumentTitleTimer(): () => void {
  if (started) return () => {};
  started = true;
  if (typeof document !== "undefined") baseTitle = document.title;

  let current: ActiveSession | null = null;
  unsubscribe = subscribeActiveSession((s) => {
    current = s;
    render(current);
  });
  tickHandle = setInterval(() => render(current), 1000);

  return () => {
    if (tickHandle) clearInterval(tickHandle);
    unsubscribe?.();
    tickHandle = null;
    unsubscribe = null;
    started = false;
    if (typeof document !== "undefined") document.title = baseTitle;
  };
}
