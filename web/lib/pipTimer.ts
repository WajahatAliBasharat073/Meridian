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
 *
 * The face is a literal clock, deliberately bare: an SVG ring with hour
 * ticks, a progress arc that sweeps clockwise from 12 o'clock
 * (progressFraction, the same schedule-window math as Today's progress
 * bar), a bright knob at the arc's tip like a watch's second hand, and
 * nothing in the center but the time -- no activity name or category
 * label competing with it in a window this small. Ring/knob colour is
 * still resolved from the block's own category colour (the same CSS
 * custom properties Today uses), just not spelled out as text --
 * resolved once per session from *this* document (the opener), since
 * Document PiP renders into a second `Document` but keeps running in
 * the opener's JS realm, so `document` here is still the main page, not
 * the PiP one.
 */

import { categoryMeta } from "./category";
import { subscribeActiveSession, type ActiveSession } from "./activityStore";
import { formatClock, progressFraction, remainingSeconds } from "./focusTimerDisplay";
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

const FALLBACK_COLOR = "#6f9bc9";
const PAUSED_COLOR = "#7a7a86";
const OVER_COLOR = "#f59e0b";

// categoryMeta().colorVar is a literal "var(--accent)" reference, meant to
// be used inside a stylesheet where the browser resolves it for free. The
// PiP document has no access to this page's stylesheet, so its value has
// to be read out here instead -- getComputedStyle already follows a var()
// chain to its final value, so this is just picking that string apart.
function resolveCategoryColor(category: string): string {
  if (typeof window === "undefined") return FALLBACK_COLOR;
  const ref = categoryMeta(category).colorVar;
  const match = /^var\((--[\w-]+)\)$/.exec(ref);
  if (!match) return ref; // already a literal color, e.g. a hex fallback
  const resolved = getComputedStyle(document.documentElement).getPropertyValue(match[1]).trim();
  return resolved || FALLBACK_COLOR;
}

// Ring geometry, in the SVG's own viewBox units -- independent of the
// window's actual pixel size, since the <svg> scales to fill its box.
const VIEW = 220;
const CENTER = VIEW / 2;
const RING_RADIUS = 86;
const RING_CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS;
const KNOB_RADIUS = 5.5;

const SVG_NS = "http://www.w3.org/2000/svg";

// Point on the ring at `fraction` of the way clockwise from 12 o'clock.
function pointOnRing(fraction: number, radius: number): { x: number; y: number } {
  const angle = fraction * 2 * Math.PI - Math.PI / 2;
  return { x: CENTER + radius * Math.cos(angle), y: CENTER + radius * Math.sin(angle) };
}

function addTicks(svg: SVGSVGElement, doc: Document): void {
  for (let i = 0; i < 12; i++) {
    const major = i % 3 === 0; // 12, 3, 6, 9 o'clock read as the "hours"
    const outer = pointOnRing(i / 12, 100);
    const inner = pointOnRing(i / 12, major ? 91 : 94);
    const line = doc.createElementNS(SVG_NS, "line");
    line.setAttribute("x1", String(outer.x));
    line.setAttribute("y1", String(outer.y));
    line.setAttribute("x2", String(inner.x));
    line.setAttribute("y2", String(inner.y));
    line.setAttribute("class", major ? "tick tick-major" : "tick");
    svg.appendChild(line);
  }
}

interface FaceRefs {
  face: HTMLDivElement;
  progress: SVGCircleElement;
  knob: SVGCircleElement;
  clock: HTMLDivElement;
}

function buildFace(doc: Document): FaceRefs {
  const face = doc.createElement("div");
  face.className = "face";

  const svg = doc.createElementNS(SVG_NS, "svg");
  svg.setAttribute("class", "ring");
  svg.setAttribute("viewBox", `0 0 ${VIEW} ${VIEW}`);

  const track = doc.createElementNS(SVG_NS, "circle");
  track.setAttribute("class", "track");
  track.setAttribute("cx", String(CENTER));
  track.setAttribute("cy", String(CENTER));
  track.setAttribute("r", String(RING_RADIUS));
  svg.appendChild(track);

  addTicks(svg, doc);

  const progress = doc.createElementNS(SVG_NS, "circle");
  progress.setAttribute("class", "progress");
  progress.setAttribute("cx", String(CENTER));
  progress.setAttribute("cy", String(CENTER));
  progress.setAttribute("r", String(RING_RADIUS));
  progress.setAttribute("stroke-dasharray", String(RING_CIRCUMFERENCE));
  progress.setAttribute("transform", `rotate(-90 ${CENTER} ${CENTER})`);
  svg.appendChild(progress);

  const knob = doc.createElementNS(SVG_NS, "circle");
  knob.setAttribute("class", "knob");
  knob.setAttribute("r", String(KNOB_RADIUS));
  svg.appendChild(knob);

  face.appendChild(svg);

  const center = doc.createElement("div");
  center.className = "center";
  const clock = doc.createElement("div");
  clock.className = "clock";
  center.append(clock);
  face.appendChild(center);

  doc.body.appendChild(face);
  return { face, progress, knob, clock };
}

function setRingColor(refs: FaceRefs, color: string): void {
  refs.face.style.setProperty("--ring-color", color);
}

function setProgress(refs: FaceRefs, fraction: number): void {
  const clamped = Math.min(1, Math.max(0, fraction));
  refs.progress.setAttribute("stroke-dashoffset", String(RING_CIRCUMFERENCE * (1 - clamped)));
  const tip = pointOnRing(clamped, RING_RADIUS);
  refs.knob.setAttribute("cx", String(tip.x));
  refs.knob.setAttribute("cy", String(tip.y));
  refs.knob.style.opacity = clamped <= 0.002 ? "0" : "1"; // hide right at 12 o'clock, nothing to point at yet
}

function renderInto(refs: FaceRefs, session: ActiveSession | null): void {
  if (!session || (session.state !== "in_progress" && session.state !== "paused")) {
    refs.face.classList.remove("over", "paused");
    setRingColor(refs, FALLBACK_COLOR);
    setProgress(refs, 0);
    refs.clock.classList.remove("long");
    refs.clock.textContent = "--:--";
    return;
  }

  const nowMin = nowMinutesInKarachi();
  setProgress(refs, progressFraction(session, nowMin));

  if (session.state === "paused") {
    refs.face.classList.remove("over");
    refs.face.classList.add("paused");
    setRingColor(refs, PAUSED_COLOR);
    refs.clock.classList.remove("long");
    refs.clock.textContent = "Paused";
    return;
  }

  refs.face.classList.remove("paused");
  const remaining = remainingSeconds(session, nowMin);
  const over = remaining < 0;
  refs.face.classList.toggle("over", over);
  setRingColor(refs, over ? OVER_COLOR : resolveCategoryColor(session.category));
  const text = over ? `+${formatClock(-remaining)}` : formatClock(remaining);
  refs.clock.textContent = text;
  refs.clock.classList.toggle("long", text.length > 6);
}

const FACE_STYLES = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { height: 100%; }
  body {
    display: flex; align-items: center; justify-content: center;
    background: radial-gradient(circle at 50% 32%, #1c1c24 0%, #101014 78%);
    font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    overflow: hidden;
  }
  .face {
    --ring-color: ${FALLBACK_COLOR};
    position: relative;
    width: min(88vw, 88vh);
    height: min(88vw, 88vh);
    filter: drop-shadow(0 10px 26px rgba(0, 0, 0, 0.5));
  }
  .ring { width: 100%; height: 100%; overflow: visible; display: block; }
  .tick { stroke: rgba(232, 232, 236, 0.16); stroke-width: 1.6; stroke-linecap: round; }
  .tick-major { stroke: rgba(232, 232, 236, 0.36); stroke-width: 2.4; }
  .track { fill: none; stroke: rgba(255, 255, 255, 0.07); stroke-width: 9; }
  .progress {
    fill: none;
    stroke: var(--ring-color);
    stroke-width: 9;
    stroke-linecap: round;
    transition: stroke-dashoffset 0.9s linear, stroke 0.4s ease;
  }
  .knob {
    fill: var(--ring-color);
    stroke: #101014;
    stroke-width: 2;
    transition: cx 0.9s linear, cy 0.9s linear, fill 0.4s ease, opacity 0.3s ease;
    filter: drop-shadow(0 0 5px var(--ring-color));
  }
  .center {
    position: absolute; inset: 12%;
    display: flex; align-items: center; justify-content: center;
    text-align: center;
  }
  .clock {
    font-size: 45px; font-weight: 700; font-variant-numeric: tabular-nums;
    letter-spacing: 0.01em; color: #eef0f4; line-height: 1;
    white-space: nowrap;
  }
  /* Longer strings ("+12:07:02" once overrun passes an hour) shrink to fit
     the ring's inner circle rather than spilling past it. */
  .clock.long { font-size: 30px; }
  .face.over .clock { color: var(--ring-color); }
  .face.paused .clock { font-size: 26px; color: #b7b7c1; }
  @keyframes pulse-glow {
    0%, 100% { filter: drop-shadow(0 0 3px var(--ring-color)); }
    50% { filter: drop-shadow(0 0 13px var(--ring-color)); }
  }
  .face.over .progress, .face.over .knob { animation: pulse-glow 1.5s ease-in-out infinite; }
`;

let activePipWindow: DocumentPictureInPictureWindow | null = null;
let activeCleanup: (() => void) | null = null;

/** Opens the floating timer, or no-ops if one is already open or the API
 * isn't supported. Safe to call unconditionally from a click handler --
 * every failure mode (unsupported browser, permission denied, popup
 * blocked) resolves to nothing happening *visibly*, but is logged rather
 * than swallowed outright -- "the button does nothing" was previously
 * indistinguishable from "it's working, just check the taskbar", which
 * makes the difference between an actual bug and a browser permission
 * impossible to tell from the outside. Check the console. */
export async function openFocusPipWindow(): Promise<void> {
  if (!isPipSupported()) {
    console.warn(
      "[pipTimer] window.documentPictureInPicture isn't available in this browser " +
        "(needs Chrome/Edge 116+, and some Chromium forks don't ship it) -- " +
        "the floating timer can't open here."
    );
    return;
  }
  if (activePipWindow) return; // already open -- don't stack a second one

  let pipWindow: DocumentPictureInPictureWindow;
  try {
    pipWindow = await window.documentPictureInPicture!.requestWindow({ width: 260, height: 260 });
  } catch (err) {
    console.warn(
      "[pipTimer] requestWindow() was rejected -- the browser blocked it or a " +
        "permission prompt was dismissed. It's already open behind another " +
        "window in rare cases; check the taskbar/Alt-Tab before assuming it " +
        "failed silently.",
      err
    );
    return;
  }

  activePipWindow = pipWindow;
  const doc = pipWindow.document;
  doc.title = "Focus Timer";
  const style = doc.createElement("style");
  style.textContent = FACE_STYLES;
  doc.head.appendChild(style);

  const refs = buildFace(doc);

  let current: ActiveSession | null = null;
  // subscribeActiveSession calls its listener once, synchronously, with
  // whatever the session already is at subscribe time -- that first call
  // is a snapshot, not a transition, and must not be read as "the session
  // just ended." Only close on a *later* null, i.e. an in-progress session
  // actually completing/being skipped; a PiP window opened with no
  // session to begin with stays open and shows its own empty face.
  let sawSession = false;
  const unsubscribe = subscribeActiveSession((s) => {
    current = s;
    if (s !== null) sawSession = true;
    else if (sawSession) pipWindow.close();
  });
  renderInto(refs, current);
  const tickHandle = setInterval(() => renderInto(refs, current), 1000);

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
