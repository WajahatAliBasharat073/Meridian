/** All block times are wall-clock "HH:MM:SS" strings for Asia/Karachi,
 * already resolved server-side (design doc 5.1) — no timezone math here. */

export function timeStringToMinutes(t: string): number {
  const [h, m] = t.split(":").map(Number);
  return h * 60 + m;
}

export function formatTime12h(t: string): string {
  const [hStr, mStr] = t.split(":");
  const h = Number(hStr);
  const period = h >= 12 ? "PM" : "AM";
  const h12 = h % 12 === 0 ? 12 : h % 12;
  return `${h12}:${mStr} ${period}`;
}

/** Minutes remaining until `endTime` (HH:MM:SS), from `nowMinutes`
 * (minutes since local midnight). Negative once past end. */
export function minutesUntil(endTime: string, nowMinutes: number): number {
  return timeStringToMinutes(endTime) - nowMinutes;
}

export function nowMinutesInKarachi(): number {
  const now = new Date(
    new Date().toLocaleString("en-US", { timeZone: "Asia/Karachi" })
  );
  return now.getHours() * 60 + now.getMinutes() + now.getSeconds() / 60;
}

export function formatCountdown(totalMinutes: number): string {
  const clamped = Math.max(0, totalMinutes);
  const h = Math.floor(clamped / 60);
  const m = Math.floor(clamped % 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}
