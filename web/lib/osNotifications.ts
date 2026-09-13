/**
 * Real OS-level notifications (the browser `Notification` API), layered
 * on top of the existing in-app toast system (lib/notifications.ts).
 *
 * The in-app system only renders while this tab is open and mounted --
 * it cannot reach you in VS Code, a browser you've switched away from, or
 * the desktop. A granted `Notification` is delivered by the OS itself
 * (Windows Action Center, macOS Notification Center, ...), so it shows up
 * regardless of which window currently has focus. It still requires the
 * browser process to be running with this tab open somewhere -- there is
 * no service worker / push subscription here, so a fully closed browser
 * receives nothing. That's a real, disclosed limit of a browser-only
 * app, not a bug: reaching a fully closed browser needs a backend push
 * service (VAPID keys, a service worker) that doesn't exist in this
 * codebase yet.
 */

export type OsNotificationPermission = NotificationPermission | "unsupported";

function isSupported(): boolean {
  return typeof window !== "undefined" && "Notification" in window;
}

export function getOsNotificationPermission(): OsNotificationPermission {
  if (!isSupported()) return "unsupported";
  return Notification.permission;
}

/** Best-effort permission request. Browsers only honor this from a secure
 * context and may silently ignore it outside a user gesture -- both are
 * fine here, since every call site treats "not granted" as "just skip
 * the OS notification," never as an error. */
export async function requestOsNotificationPermission(): Promise<OsNotificationPermission> {
  if (!isSupported()) return "unsupported";
  if (Notification.permission !== "default") return Notification.permission;
  try {
    return await Notification.requestPermission();
  } catch {
    return Notification.permission;
  }
}

export function sendOsNotification(title: string, body: string): void {
  if (!isSupported() || Notification.permission !== "granted") return;
  try {
    new Notification(title, { body, icon: "/icon.png", tag: title });
  } catch {
    // Some platforms (older Android WebViews, certain locked-down
    // desktop policies) throw on construction even when permission
    // reads "granted" -- never let a notification failure break the
    // feature it's decorating.
  }
}
