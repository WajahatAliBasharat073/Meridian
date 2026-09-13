/**
 * Floating always-on-top focus timer via the Document Picture-in-Picture
 * API (Chrome/Edge 116+). This is the honest answer to "visible above
 * every other window" from a browser-only app: there is no way for a
 * regular tab to render above other native applications -- that needs
 * either a browser extension, a desktop wrapper (Electron/Tauri), or
 * this API, which opens a small always-on-top window the OS itself
 * keeps above other windows, independent of whether this tab has focus.
 * It does not survive the browser being fully closed, and Firefox/Safari
 * don't implement it -- lib/documentTitleTimer.ts's tab-title countdown
 * is the universal fallback every browser gets regardless.
 *
 * Must be invoked directly from a user gesture (a click handler, with no
 * prior `await`) -- that's why ActivityController calls this the moment
 * Focus is pressed, not from a useEffect reacting to the session state.
 */

import { subscribeActiveSession, type ActiveSession } from "./activityStore";
import { formatClock, remainingSeconds } from "./focusTimerDisplay";
import { nowMinutesInKarachi } from "./time";

interface DocumentPictureInPictureWindow extends EventTarget {
  document: Document;
  close(): void;
}

interface DocumentPictureInPictureApi {
  requestWindow(options?: { width?: number; height?: number }): Promise<DocumentPictureInPictureWindow>;
  window: DocumentPictureInPictureWindow | null;
}

declare global {
  interface Window {
    documentPictureInPicture?: DocumentPictureInPictureApi;
  }
}

export function isPipSupported(): boolean {
  return typeof window !== "undefined" && "documentPictureInPicture" in window;
}

let activePipWindow: DocumentPictureInPictureWindow | null = null;
let activeCleanup: (() => void) | null = null;

function renderInto(pipDoc: Document, clockEl: HTMLElement, activityEl: HTMLElement, session: ActiveSession | null) {
  if (!session || (session.state !== "in_progress" && session.state !== "paused")) {
    clockEl.textContent = "--:--";
    activityEl.textContent = "No active session";
    return;
  }
  activityEl.textContent = session.activity;
  if (session.state === "paused") {
    clockEl.textContent = "Paused";
    return;
  }
  const remaining = remainingSeconds(session, nowMinutesInKarachi());
  clockEl.textContent = remaining >= 0 ? formatClock(remaining) : `+${formatClock(-remaining)} over`;
  clockEl.style.color = remaining >= 0 ? "#e8e8ec" : "#f59e0b";
  void pipDoc; // kept for signature symmetry / future per-window theming
}

/** Opens the floating timer, or no-ops if one is already open or the API
 * isn't supported. Safe to call unconditionally from a click handler --
 * every failure mode (unsupported browser, permission denied, popup
 * blocked) resolves to nothing happening rather than an error. */
export async function openFocusPipWindow(): Promise<void> {
  if (!isPipSupported()) return;
  if (activePipWindow) return; // already open -- don't stack a second one

  let pipWindow: DocumentPictureInPictureWindow;
  try {
    pipWindow = await window.documentPictureInPicture!.requestWindow({ width: 260, height: 108 });
  } catch {
    return; // user dismissed the permission/popup prompt, or the browser refused it
  }

  activePipWindow = pipWindow;
  const doc = pipWindow.document;
  doc.title = "Focus Timer";
  const style = doc.createElement("style");
  style.textContent = `
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { height: 100%; }
    body {
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      gap: 4px; background: #17171c; color: #e8e8ec;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif;
    }
    .clock { font-size: 34px; font-weight: 600; font-variant-numeric: tabular-nums; letter-spacing: 0.02em; }
    .activity { font-size: 11px; color: #9a9aa6; max-width: 230px; text-align: center;
      overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  `;
  doc.head.appendChild(style);

  const clockEl = doc.createElement("div");
  clockEl.className = "clock";
  const activityEl = doc.createElement("div");
  activityEl.className = "activity";
  doc.body.appendChild(clockEl);
  doc.body.appendChild(activityEl);

  let current: ActiveSession | null = null;
  const unsubscribe = subscribeActiveSession((s) => {
    current = s;
    if (s === null) {
      // The session ended (completed/skipped) -- nothing left to show.
      pipWindow.close();
    }
  });
  renderInto(doc, clockEl, activityEl, current);
  const tickHandle = setInterval(() => renderInto(doc, clockEl, activityEl, current), 1000);

  const cleanup = () => {
    clearInterval(tickHandle);
    unsubscribe();
    activePipWindow = null;
    activeCleanup = null;
  };
  activeCleanup = cleanup;
  pipWindow.addEventListener("pagehide", cleanup, { once: true });
}

/** Test-only escape hatch -- production code never needs to force-close
 * the window itself (it closes on session end or when the user closes
 * it), but tests need a way to reset the module's singleton state. */
export function _closePipWindowForTests(): void {
  activeCleanup?.();
  activePipWindow = null;
  activeCleanup = null;
}
