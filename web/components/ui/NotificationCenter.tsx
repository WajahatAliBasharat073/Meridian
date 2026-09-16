"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Bell, BellOff, Check, CheckCheck, Clock, Droplets, Volume2, VolumeX, X } from "lucide-react";
import { subscribeActiveSession, type ActiveSession } from "@/lib/activityStore";
import { cn } from "@/lib/cn";
import { startDocumentTitleTimer } from "@/lib/documentTitleTimer";
import { logWaterIntake } from "@/lib/hydration";
import {
  dismissAllNotifications,
  dismissNotification,
  pushNotification,
  setTrayOpen as setTrayOpenShared,
  snoozeNotification,
  subscribeNotifications,
  subscribeTrayOpen,
  toggleTray,
  type SmartNotification,
} from "@/lib/notifications";
import { requestOsNotificationPermission } from "@/lib/osNotifications";
import {
  evaluateReminders,
  loadSentState,
  saveSentState,
  type ReminderKind,
} from "@/lib/sessionReminders";
import { getSoundSettings, saveSoundSettings } from "@/lib/soundEngine";
import { nowMinutesInKarachi } from "@/lib/time";
import { useToday } from "@/hooks/useToday";
import { Button } from "@/components/ui/button";

// How often a reminder repeats during a continuous active session — every
// hour is the cadence behind "roughly a glass of water an hour", so a
// 2-3 hour session naturally gets 2-3 nudges rather than one at the end.
const HYDRATION_INTERVAL_MINUTES = 60;

/** Watches the active focus session (any session, any block) and fires a
 * hydration reminder every `HYDRATION_INTERVAL_MINUTES` of continuous
 * worked time. Lives at the app-shell level rather than inside a
 * particular block's UI so it fires regardless of which block a session
 * happens to be running against. */
function useHydrationReminders() {
  useEffect(() => {
    let current: ActiveSession | null = null;
    const state: { blockId: number | null; alerted: Set<number> } = { blockId: null, alerted: new Set() };

    const unsub = subscribeActiveSession((s) => {
      current = s;
    });

    const check = () => {
      const session = current;
      if (!session) {
        state.blockId = null;
        state.alerted = new Set();
        return;
      }
      if (state.blockId !== session.blockId) {
        state.blockId = session.blockId;
        state.alerted = new Set();
      }
      if (session.state !== "in_progress") return;

      const worked =
        session.totalElapsedSeconds + Math.max(0, Math.floor((Date.now() - session.startTime) / 1000));
      const workedMinutes = Math.floor(worked / 60);
      const threshold = Math.floor(workedMinutes / HYDRATION_INTERVAL_MINUTES) * HYDRATION_INTERVAL_MINUTES;

      if (threshold > 0 && !state.alerted.has(threshold)) {
        state.alerted.add(threshold);
        pushNotification({
          kind: "hydration",
          title: "Hydration check",
          body: `${threshold} minutes into "${session.activity}" — drink a glass of water.`,
          soundType: "gentle",
          activityId: session.blockId,
          activityTitle: session.activity,
          actions: [
            { label: "Done — drank water", action: "log_water" },
            { label: "Not now", action: "dismiss" },
          ],
        });
      }
    };

    const interval = setInterval(check, 30_000);
    return () => {
      unsub();
      clearInterval(interval);
    };
  }, []);
}

// Every notification the reminder schedule below can fire, and the
// in-app toast copy for each -- kept together so the wording for a
// given ReminderKind can't drift out of sync with the kind itself.
const REMINDER_COPY: Record<
  ReminderKind,
  { kind: "activity_pre" | "activity_start" | "activity_nudge"; title: string; body: (activity: string) => string }
> = {
  pre: {
    kind: "activity_pre",
    title: "Upcoming session",
    body: (activity) => `${activity} starts in 5 minutes.`,
  },
  start: {
    kind: "activity_start",
    title: "Session started",
    body: (activity) => `${activity} — start focusing now.`,
  },
  nudge: {
    kind: "activity_nudge",
    title: "Still not started",
    body: (activity) => `You haven't pressed Focus for "${activity}" yet.`,
  },
};

/** Fires the 5-minute pre-session notice, the session-start notice, and
 * (once) a follow-up nudge if Focus still hasn't been pressed a few
 * minutes later -- see lib/sessionReminders.ts for the actual timing
 * rules, kept pure and unit-tested there. This hook just ticks the
 * clock, reads today's real schedule (shared with whatever page called
 * useToday -- react-query dedupes it), and persists which reminders
 * have already fired so a re-render or tab switch never re-sends one. */
function useSessionReminders() {
  const { data } = useToday();

  useEffect(() => {
    void requestOsNotificationPermission();
  }, []);

  useEffect(() => {
    const blocks = data?.blocks;
    if (!blocks) return;

    const check = () => {
      const { due, nextState } = evaluateReminders(nowMinutesInKarachi(), blocks, loadSentState());
      for (const { kind, block } of due) {
        const copy = REMINDER_COPY[kind];
        pushNotification({
          kind: copy.kind,
          title: copy.title,
          body: copy.body(block.activity),
          soundType: kind === "nudge" ? "reminder" : "gentle",
          activityId: block.id,
          activityTitle: block.activity,
        });
      }
      if (due.length > 0) saveSentState(nextState);
    };

    check();
    const interval = setInterval(check, 20_000);
    return () => clearInterval(interval);
  }, [data?.blocks]);
}

export function NotificationCenter() {
  const router = useRouter();
  const [notifications, setNotifications] = useState<SmartNotification[]>([]);
  const [soundEnabled, setSoundEnabled] = useState(true);
  // Shared with NotificationBellButton (mounted separately, in TopNav) via
  // lib/notifications.ts's subscribeTrayOpen/setTrayOpen -- see that
  // file's comment for why this can't just be local useState.
  const [trayOpen, setTrayOpen] = useState(false);

  useHydrationReminders();
  useSessionReminders();

  useEffect(() => startDocumentTitleTimer(), []);

  useEffect(() => {
    // Read after mount on purpose. A lazy useState initialiser would read
    // localStorage during render, and the server has no localStorage — so
    // the first client render would disagree with the server's HTML and
    // React would throw a hydration mismatch. The rule's suggestion is the
    // wrong trade here; one extra render on mount is the correct cost.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setSoundEnabled(getSoundSettings().enabled);
    const unsub = subscribeNotifications((notifs) => {
      setNotifications(notifs);
    });
    const unsubTray = subscribeTrayOpen(setTrayOpen);
    return () => {
      unsub();
      unsubTray();
    };
  }, []);

  const toggleSound = () => {
    const updated = saveSoundSettings({ enabled: !soundEnabled });
    setSoundEnabled(updated.enabled);
  };

  // Clicking a notification's own text (not its buttons) jumps to the
  // block it's about -- scrolls the Today timeline to it and briefly
  // highlights it (see the hash-driven effect in components/today/
  // Timeline.tsx). Acting on it this way also counts as handling it, so
  // it's dismissed at the same time; a notification with no activityId
  // (nothing on the schedule to jump to) just isn't clickable.
  const goToNotification = (n: SmartNotification) => {
    if (n.activityId == null) return;
    setTrayOpenShared(false);
    dismissNotification(n.id);
    router.push(`/today#block-${n.activityId}`);
  };

  const activeToasts = notifications.slice(0, 2);

  return (
    <>
      {/* Floating Smart Toasts */}
      {activeToasts.length > 0 && (
        <aside
          aria-label="Notifications"
          // top-4 on mobile (TopNav's header is desktop-only, hidden below
          // md), top-20 on md+ so the stack clears the 64px sticky header
          // instead of rendering over it at z-50 -- which is exactly what
          // was hiding the bell button behind these toasts.
          className="fixed top-4 md:top-20 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none"
        >
          {activeToasts.length > 1 && (
            <button
              type="button"
              onClick={() => dismissAllNotifications()}
              className="pointer-events-auto self-end flex items-center gap-1.5 h-7 px-2.5 rounded-lg text-[11px] font-medium text-text-faint bg-surface/95 backdrop-blur-md border border-border-strong shadow-elevated hover:text-text hover:bg-surface-2"
            >
              <CheckCheck size={12} />
              Clear all ({notifications.length})
            </button>
          )}

          {activeToasts.map((n) => {
            const clickable = n.activityId != null;
            return (
              <div
                key={n.id}
                role="alert"
                onClick={clickable ? () => goToNotification(n) : undefined}
                className={cn(
                  "pointer-events-auto rounded-xl border border-border-strong bg-surface/95 backdrop-blur-md p-3.5 shadow-elevated animate-in fade-in slide-in-from-top-2 duration-200",
                  clickable && "cursor-pointer hover:border-accent/50"
                )}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5 mb-1">
                      <span className="text-xs font-semibold tracking-wide uppercase text-accent-strong">
                        {n.title}
                      </span>
                      <span className="text-[10px] text-text-faint ml-auto">now</span>
                    </div>
                    <p className="text-xs text-text leading-relaxed">{n.body}</p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      dismissNotification(n.id);
                    }}
                    aria-label="Dismiss alert"
                    className="text-text-faint hover:text-text p-1 rounded-md"
                  >
                    <X size={14} />
                  </button>
                </div>

                {/* Action Buttons */}
                <div className="mt-2.5 pt-2 border-t border-border flex items-center gap-1.5 flex-wrap">
                  {n.actions?.map((act, i) => (
                    <button
                      key={i}
                      onClick={(e) => {
                        e.stopPropagation();
                        if (act.action === "snooze") {
                          snoozeNotification(n.id, act.minutes || 10);
                        } else if (act.action === "log_water") {
                          logWaterIntake(250);
                          dismissNotification(n.id);
                        } else {
                          dismissNotification(n.id);
                        }
                      }}
                      className="h-7 px-2.5 rounded-lg text-xs font-medium bg-surface-2 hover:bg-surface-hover text-text border border-border transition-colors flex items-center gap-1"
                    >
                      {act.action === "snooze" && <Clock size={11} />}
                      {act.action === "start" && <Check size={11} />}
                      {act.action === "log_water" && <Droplets size={11} />}
                      {act.label}
                    </button>
                  ))}
                  {clickable && (
                    <span className="text-[11px] text-accent-strong ml-auto">Click to go there →</span>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      dismissNotification(n.id);
                    }}
                    className={cn("h-7 px-2 text-xs text-text-faint hover:text-text", !clickable && "ml-auto")}
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            );
          })}
        </aside>
      )}

      {/* Tray toggle for full history if open */}
      {trayOpen && (
        <div className="fixed inset-0 z-40 flex justify-end">
          <button
            type="button"
            className="absolute inset-0 bg-black/60 backdrop-blur-xs"
            onClick={() => setTrayOpenShared(false)}
            aria-label="Close notification tray"
          />
          <div className="relative w-80 max-w-[90vw] h-full bg-surface border-l border-border p-4 flex flex-col z-50">
            <div className="flex items-center justify-between pb-3 border-b border-border mb-3">
              <div className="flex items-center gap-2">
                <Bell size={16} className="text-accent-strong" />
                <h3 className="text-sm font-semibold text-text">Activity Alerts</h3>
              </div>
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleSound}
                  title={soundEnabled ? "Mute chimes" : "Enable chimes"}
                >
                  {soundEnabled ? <Volume2 size={15} /> : <VolumeX size={15} className="text-danger" />}
                </Button>
                <Button variant="ghost" size="icon" onClick={() => setTrayOpenShared(false)}>
                  <X size={16} />
                </Button>
              </div>
            </div>

            {notifications.length > 0 && (
              <button
                type="button"
                onClick={() => dismissAllNotifications()}
                className="flex items-center justify-center gap-1.5 h-8 mb-3 rounded-lg text-xs font-medium text-text-muted border border-border hover:bg-surface-2 hover:text-text transition-colors"
              >
                <CheckCheck size={13} />
                Clear all ({notifications.length})
              </button>
            )}

            <div className="flex-1 overflow-y-auto space-y-2">
              {notifications.length === 0 ? (
                <div className="py-12 text-center text-xs text-text-muted">
                  No alerts right now. You are up to date.
                </div>
              ) : (
                notifications.map((n) => {
                  const clickable = n.activityId != null;
                  return (
                    <div
                      key={n.id}
                      onClick={clickable ? () => goToNotification(n) : undefined}
                      className={cn(
                        "p-2.5 rounded-lg border border-border bg-surface-2 text-xs",
                        clickable && "cursor-pointer hover:border-accent/50"
                      )}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-text">{n.title}</span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            dismissNotification(n.id);
                          }}
                          className="text-text-faint hover:text-text"
                        >
                          <X size={12} />
                        </button>
                      </div>
                      <p className="text-text-muted">{n.body}</p>
                      {clickable && (
                        <p className="text-[10px] text-accent-strong mt-1">Click to go there →</p>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export function NotificationBellButton() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const unsub = subscribeNotifications((notifs) => setCount(notifs.length));
    return () => unsub();
  }, []);

  return (
    <button
      onClick={toggleTray}
      className="relative h-9 w-9 rounded-lg flex items-center justify-center text-text-muted hover:text-text hover:bg-surface-2 transition-colors"
      aria-label={`Notifications ${count > 0 ? `(${count} active)` : ""}`}
      title={count > 0 ? `${count} active alerts` : "No pending alerts"}
    >
      <Bell size={16} />
      {count > 0 && (
        <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-accent animate-pulse" />
      )}
    </button>
  );
}
