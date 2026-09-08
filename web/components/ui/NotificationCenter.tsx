"use client";

import { useEffect, useState } from "react";
import { Bell, BellOff, Check, Clock, Droplets, Volume2, VolumeX, X } from "lucide-react";
import { subscribeActiveSession, type ActiveSession } from "@/lib/activityStore";
import { logWaterIntake } from "@/lib/hydration";
import {
  dismissNotification,
  getNotifications,
  pushNotification,
  snoozeNotification,
  subscribeNotifications,
  type SmartNotification,
} from "@/lib/notifications";
import { getSoundSettings, saveSoundSettings } from "@/lib/soundEngine";
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

export function NotificationCenter() {
  const [notifications, setNotifications] = useState<SmartNotification[]>([]);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [trayOpen, setTrayOpen] = useState(false);

  useHydrationReminders();

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
    return () => unsub();
  }, []);

  const toggleSound = () => {
    const updated = saveSoundSettings({ enabled: !soundEnabled });
    setSoundEnabled(updated.enabled);
  };

  const activeToasts = notifications.slice(0, 2);

  return (
    <>
      {/* Floating Smart Toasts */}
      {activeToasts.length > 0 && (
        <aside
          aria-label="Notifications"
          className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none"
        >
          {activeToasts.map((n) => (
            <div
              key={n.id}
              role="alert"
              className="pointer-events-auto rounded-xl border border-border-strong bg-surface/95 backdrop-blur-md p-3.5 shadow-elevated animate-in fade-in slide-in-from-top-2 duration-200"
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
                  onClick={() => dismissNotification(n.id)}
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
                    onClick={() => {
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
                <button
                  onClick={() => dismissNotification(n.id)}
                  className="h-7 px-2 text-xs text-text-faint hover:text-text ml-auto"
                >
                  Dismiss
                </button>
              </div>
            </div>
          ))}
        </aside>
      )}

      {/* Tray toggle for full history if open */}
      {trayOpen && (
        <div className="fixed inset-0 z-40 flex justify-end">
          <button
            type="button"
            className="absolute inset-0 bg-black/60 backdrop-blur-xs"
            onClick={() => setTrayOpen(false)}
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
                <Button variant="ghost" size="icon" onClick={() => setTrayOpen(false)}>
                  <X size={16} />
                </Button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto space-y-2">
              {notifications.length === 0 ? (
                <div className="py-12 text-center text-xs text-text-muted">
                  No alerts right now. You are up to date.
                </div>
              ) : (
                notifications.map((n) => (
                  <div key={n.id} className="p-2.5 rounded-lg border border-border bg-surface-2 text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-text">{n.title}</span>
                      <button
                        onClick={() => dismissNotification(n.id)}
                        className="text-text-faint hover:text-text"
                      >
                        <X size={12} />
                      </button>
                    </div>
                    <p className="text-text-muted">{n.body}</p>
                  </div>
                ))
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
      onClick={() => {
        const notifs = getNotifications();
        if (notifs.length > 0) dismissNotification(notifs[0].id);
      }}
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
