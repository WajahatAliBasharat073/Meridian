import { addWater } from "./api";
import { logBehavioralEvent } from "./notifications";
import { playSound } from "./soundEngine";

/** Logs a glass of water against the real `nutrition_log` row for today.
 *
 * This used to write into a `localStorage` blob the Health page invented its
 * numbers in, which meant "Done — drank water" never reached Postgres and
 * was different in every browser. It now posts to /api/vitals/water, which
 * is additive server-side.
 *
 * Fire-and-forget by design: the notification should dismiss immediately
 * rather than waiting on the network, and a failure is surfaced through the
 * returned promise for callers that care.
 */
export async function logWaterIntake(ml = 250): Promise<number | null> {
  playSound("gentle");
  try {
    const vitals = await addWater(ml);
    logBehavioralEvent("hydration_logged", undefined, { added: ml, total: vitals.water_ml });
    return vitals.water_ml;
  } catch {
    // Offline or logged out — record the intent locally so the behavioural
    // log still shows the nudge worked, and let the caller decide.
    logBehavioralEvent("hydration_logged", undefined, { added: ml, total: null, failed: true });
    return null;
  }
}
