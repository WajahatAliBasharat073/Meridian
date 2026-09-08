/**
 * Smart Notification & Behavioral Event System
 * Tracks notifications, handles actions (Start, Snooze, Skip, Dismiss),
 * plays notification sounds, and logs behavioral events.
 */

import { playSound, type SoundType } from "./soundEngine";

export type NotificationKind =
  | "activity_pre"
  | "activity_start"
  | "activity_complete"
  | "hydration"
  | "meal"
  | "break"
  | "wind_down";

export interface SmartNotification {
  id: string;
  kind: NotificationKind;
  title: string;
  body: string;
  soundType: SoundType;
  timestamp: number; // Date.now()
  activityId?: number;
  activityTitle?: string;
  actions?: {
    label: string;
    action: "start" | "snooze" | "skip" | "dismiss" | "open" | "log_water";
    minutes?: number;
  }[];
  dismissed?: boolean;
}

export type BehavioralEventType =
  | "notification_created"
  | "notification_displayed"
  | "notification_opened"
  | "notification_dismissed"
  | "notification_snoozed"
  | "activity_started"
  | "activity_completed"
  | "activity_skipped"
  | "activity_rescheduled"
  | "activity_paused"
  | "hydration_logged";

export interface BehavioralEvent {
  id: string;
  type: BehavioralEventType;
  timestamp: number;
  targetId?: string | number;
  metadata?: Record<string, unknown>;
  responseTimeMs?: number;
}

const NOTIFICATIONS_STORAGE = "meridian_notifications";
const BEHAVIORAL_EVENTS_STORAGE = "meridian_behavioral_events";
const NOTIFICATION_SETTINGS_STORAGE = "meridian_notification_settings";

export interface NotificationSettings {
  enabled: boolean;
  activityReminders: boolean;
  hydrationAlerts: boolean;
  mealAlerts: boolean;
  breakReminders: boolean;
  windDownReminder: boolean;
}

const DEFAULT_SETTINGS: NotificationSettings = {
  enabled: true,
  activityReminders: true,
  hydrationAlerts: true,
  mealAlerts: true,
  breakReminders: true,
  windDownReminder: true,
};

type Listener = (notifications: SmartNotification[]) => void;
const listeners: Set<Listener> = new Set();

export function subscribeNotifications(listener: Listener): () => void {
  listeners.add(listener);
  listener(getNotifications());
  return () => {
    listeners.delete(listener);
  };
}

function notifyListeners() {
  const current = getNotifications();
  listeners.forEach((fn) => fn(current));
}

export function getNotificationSettings(): NotificationSettings {
  if (typeof window === "undefined") return DEFAULT_SETTINGS;
  try {
    const raw = localStorage.getItem(NOTIFICATION_SETTINGS_STORAGE);
    return raw ? { ...DEFAULT_SETTINGS, ...JSON.parse(raw) } : DEFAULT_SETTINGS;
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export function saveNotificationSettings(settings: Partial<NotificationSettings>): NotificationSettings {
  const current = getNotificationSettings();
  const updated = { ...current, ...settings };
  try {
    localStorage.setItem(NOTIFICATION_SETTINGS_STORAGE, JSON.stringify(updated));
  } catch {}
  return updated;
}

export function getNotifications(): SmartNotification[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(NOTIFICATIONS_STORAGE);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function pushNotification(
  notification: Omit<SmartNotification, "id" | "timestamp" | "dismissed">
): SmartNotification | null {
  const settings = getNotificationSettings();
  if (!settings.enabled) return null;

  // Check category settings
  if (notification.kind.startsWith("activity_") && !settings.activityReminders) return null;
  if (notification.kind === "hydration" && !settings.hydrationAlerts) return null;
  if (notification.kind === "meal" && !settings.mealAlerts) return null;
  if (notification.kind === "break" && !settings.breakReminders) return null;
  if (notification.kind === "wind_down" && !settings.windDownReminder) return null;

  const fullNotification: SmartNotification = {
    ...notification,
    id: `notif_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
    timestamp: Date.now(),
    dismissed: false,
  };

  const current = getNotifications();
  // Don't push exact duplicate within 5 minutes
  const recentDuplicate = current.find(
    (n) =>
      n.title === fullNotification.title &&
      n.kind === fullNotification.kind &&
      Date.now() - n.timestamp < 5 * 60 * 1000
  );
  if (recentDuplicate) return null;

  const updated = [fullNotification, ...current].slice(0, 30);
  try {
    localStorage.setItem(NOTIFICATIONS_STORAGE, JSON.stringify(updated));
  } catch {}

  // Play sound
  playSound(fullNotification.soundType);

  // Log behavioral event
  logBehavioralEvent("notification_displayed", fullNotification.id, {
    kind: fullNotification.kind,
  });

  notifyListeners();
  return fullNotification;
}

export function dismissNotification(id: string): void {
  const current = getNotifications();
  const target = current.find((n) => n.id === id);
  if (target) {
    const responseTime = Date.now() - target.timestamp;
    logBehavioralEvent("notification_dismissed", id, { kind: target.kind }, responseTime);
  }
  const updated = current.filter((n) => n.id !== id);
  try {
    localStorage.setItem(NOTIFICATIONS_STORAGE, JSON.stringify(updated));
  } catch {}
  notifyListeners();
}

export function snoozeNotification(id: string, minutes = 10): void {
  const current = getNotifications();
  const target = current.find((n) => n.id === id);
  if (target) {
    const responseTime = Date.now() - target.timestamp;
    logBehavioralEvent("notification_snoozed", id, { kind: target.kind, minutes }, responseTime);
  }
  dismissNotification(id);
}

// ----------------- Behavioral Event Log -----------------

export function logBehavioralEvent(
  type: BehavioralEventType,
  targetId?: string | number,
  metadata?: Record<string, unknown>,
  responseTimeMs?: number
): void {
  if (typeof window === "undefined") return;
  const event: BehavioralEvent = {
    id: `ev_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
    type,
    timestamp: Date.now(),
    targetId,
    metadata,
    responseTimeMs,
  };

  try {
    const raw = localStorage.getItem(BEHAVIORAL_EVENTS_STORAGE);
    const list: BehavioralEvent[] = raw ? JSON.parse(raw) : [];
    list.unshift(event);
    localStorage.setItem(BEHAVIORAL_EVENTS_STORAGE, JSON.stringify(list.slice(0, 200)));
  } catch {}
}

export function getBehavioralEvents(): BehavioralEvent[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(BEHAVIORAL_EVENTS_STORAGE);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}
