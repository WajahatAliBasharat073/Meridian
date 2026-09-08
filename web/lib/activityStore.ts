/**
 * Living Activity State Machine & Session Store
 * Manages active focus sessions, timers, pause/resume, snooze, extend, and status transitions.
 */

import { startFocusSession, updateFocusSession } from "./api";
import { logBehavioralEvent } from "./notifications";
import { playSound } from "./soundEngine";

export type ActivityLifecycleState =
  | "upcoming"
  | "current"
  | "in_progress"
  | "paused"
  | "completed"
  | "delayed"
  | "skipped"
  | "snoozed"
  | "cancelled";

export interface ActiveSession {
  blockId: number;
  activity: string;
  category: string;
  state: ActivityLifecycleState;
  startTime: number; // Date.now() when started
  pausedTime?: number;
  totalElapsedSeconds: number;
  plannedMinutes: number;
  targetEndMinutes: number; // e.g. minutes in day (0-1440)
  extensionMinutes: number;
  focusRating?: number; // 1-5
  notes?: string;
  /** Row id in `focus_sessions` once the server has recorded this start.
   * Local-first: the timer never waits on the network, but the actual
   * start time is persisted so punctuality can be measured later. */
  dbSessionId?: number;
  /** Minutes after the block's scheduled start that Focus was pressed,
   * as computed and stored by the server. Positive = started late. */
  startDelayMinutes?: number;
}

const ACTIVE_SESSION_STORAGE = "meridian_active_session";

type SessionListener = (session: ActiveSession | null) => void;
const sessionListeners: Set<SessionListener> = new Set();

export function subscribeActiveSession(listener: SessionListener): () => void {
  sessionListeners.add(listener);
  listener(getActiveSession());
  return () => {
    sessionListeners.delete(listener);
  };
}

function notifySessionListeners() {
  const current = getActiveSession();
  sessionListeners.forEach((fn) => fn(current));
}

export function getActiveSession(): ActiveSession | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(ACTIVE_SESSION_STORAGE);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function saveActiveSession(session: ActiveSession | null): void {
  try {
    if (session) {
      localStorage.setItem(ACTIVE_SESSION_STORAGE, JSON.stringify(session));
    } else {
      localStorage.removeItem(ACTIVE_SESSION_STORAGE);
    }
  } catch {}
  notifySessionListeners();
}

/**
 * Start an activity session
 */
export function startActivitySession(
  blockId: number,
  activity: string,
  category: string,
  plannedMinutes: number,
  targetEndMinutes: number
): ActiveSession {
  const session: ActiveSession = {
    blockId,
    activity,
    category,
    state: "in_progress",
    startTime: Date.now(),
    totalElapsedSeconds: 0,
    plannedMinutes,
    targetEndMinutes,
    extensionMinutes: 0,
  };

  saveActiveSession(session);
  playSound("gentle");
  logBehavioralEvent("activity_started", blockId, { activity, category, plannedMinutes });

  // Fire-and-forget: record the *actual* start time server-side. The live
  // timer stays local so it can't be blocked or delayed by the network,
  // but "scheduled 17:05, actually started 17:34" becomes a stored fact.
  void startFocusSession(blockId)
    .then((row) => {
      const live = getActiveSession();
      if (live && live.blockId === blockId) {
        saveActiveSession({
          ...live,
          dbSessionId: row.id,
          startDelayMinutes: row.start_delay_minutes ?? undefined,
        });
      }
    })
    .catch(() => {
      // Offline or backend down — the local session still runs; only the
      // punctuality record is lost, and we don't pretend otherwise.
    });

  return session;
}

/**
 * Pause the active session
 */
export function pauseActiveSession(): ActiveSession | null {
  const session = getActiveSession();
  if (!session || session.state !== "in_progress") return null;

  const now = Date.now();
  const additionalSeconds = Math.floor((now - session.startTime) / 1000);

  const updated: ActiveSession = {
    ...session,
    state: "paused",
    pausedTime: now,
    totalElapsedSeconds: session.totalElapsedSeconds + additionalSeconds,
  };

  saveActiveSession(updated);
  if (updated.dbSessionId) {
    void updateFocusSession(updated.dbSessionId, {
      state: "paused",
      elapsed_seconds: updated.totalElapsedSeconds,
    }).catch(() => {});
  }
  logBehavioralEvent("activity_paused", session.blockId, {
    activity: session.activity,
    elapsedSeconds: updated.totalElapsedSeconds,
  });
  return updated;
}

/**
 * Resume a paused session
 */
export function resumeActiveSession(): ActiveSession | null {
  const session = getActiveSession();
  if (!session || session.state !== "paused") return null;

  const updated: ActiveSession = {
    ...session,
    state: "in_progress",
    startTime: Date.now(),
    pausedTime: undefined,
  };

  saveActiveSession(updated);
  if (updated.dbSessionId) {
    void updateFocusSession(updated.dbSessionId, { state: "in_progress" }).catch(() => {});
  }
  playSound("gentle");
  return updated;
}

/**
 * Extend the session by X minutes
 */
export function extendActiveSession(minutes = 15): ActiveSession | null {
  const session = getActiveSession();
  if (!session) return null;

  const updated: ActiveSession = {
    ...session,
    extensionMinutes: session.extensionMinutes + minutes,
    plannedMinutes: session.plannedMinutes + minutes,
  };

  saveActiveSession(updated);
  return updated;
}

/**
 * Shorten the session by X minutes
 */
export function shortenActiveSession(minutes = 15): ActiveSession | null {
  const session = getActiveSession();
  if (!session) return null;

  const newPlanned = Math.max(5, session.plannedMinutes - minutes);
  const updated: ActiveSession = {
    ...session,
    plannedMinutes: newPlanned,
  };

  saveActiveSession(updated);
  return updated;
}

/**
 * Complete the active session
 */
export function completeActiveSession(focusRating = 5, notes?: string): {
  session: ActiveSession;
  actualMinutes: number;
} | null {
  const session = getActiveSession();
  if (!session) return null;

  let totalSeconds = session.totalElapsedSeconds;
  if (session.state === "in_progress") {
    totalSeconds += Math.floor((Date.now() - session.startTime) / 1000);
  }

  const actualMinutes = Math.max(1, Math.round(totalSeconds / 60));

  const completed: ActiveSession = {
    ...session,
    state: "completed",
    totalElapsedSeconds: totalSeconds,
    focusRating,
    notes,
  };

  if (session.dbSessionId) {
    void updateFocusSession(session.dbSessionId, {
      state: "completed",
      elapsed_seconds: totalSeconds,
      focus_rating: focusRating,
      notes,
    }).catch(() => {});
  }

  // Clear from active store
  saveActiveSession(null);

  playSound("completion");
  logBehavioralEvent("activity_completed", session.blockId, {
    activity: session.activity,
    category: session.category,
    actualMinutes,
    plannedMinutes: session.plannedMinutes,
    focusRating,
  });

  return { session: completed, actualMinutes };
}

/**
 * Skip an activity
 */
export function skipActiveSession(reason?: string): ActiveSession | null {
  const session = getActiveSession();
  if (session) {
    logBehavioralEvent("activity_skipped", session.blockId, {
      activity: session.activity,
      category: session.category,
      reason,
    });
    if (session.dbSessionId) {
      void updateFocusSession(session.dbSessionId, {
        state: "abandoned",
        notes: reason,
      }).catch(() => {});
    }
    saveActiveSession(null);
  }
  return session;
}
