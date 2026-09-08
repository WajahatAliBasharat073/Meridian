/**
 * Behavioral Analytics & Pattern Computation Engine
 * Computes strictly evidence-backed behavioral metrics from real logged events.
 * Adheres to Section 10 of Meridian requirements:
 * "Never make unsupported assumptions. Only make stronger conclusions with enough supporting data."
 */

import { getBehavioralEvents, type BehavioralEvent } from "./notifications";
import type { TimeBlockOut } from "./types";

export interface BehavioralMetrics {
  sampleSize: number;
  medianResponseTimeSec: number | null;
  snoozeRatePct: number | null;
  skipRatePct: number | null;
  completionRatePct: number | null;
  durationBiasByCategory: { category: string; ratio: number; sampleCount: number }[];
  bestFocusWindow: { window: string; completionRate: number; sampleCount: number } | null;
  claims: BehavioralClaim[];
}

export interface BehavioralClaim {
  id: string;
  claim: string;
  sampleSize: number;
  confidence: "low" | "medium" | "high";
  suggestedAction?: string;
}

export function computeBehavioralMetrics(blocks: TimeBlockOut[] = []): BehavioralMetrics {
  const events = getBehavioralEvents();

  // 1. Notification response times
  const responseTimes = events
    .filter((e) => e.responseTimeMs != null)
    .map((e) => e.responseTimeMs! / 1000);

  let medianResponseTimeSec: number | null = null;
  if (responseTimes.length >= 3) {
    const sorted = [...responseTimes].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    medianResponseTimeSec = Math.round(
      sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2
    );
  }

  // 2. Notification Snooze & Skip Rates
  const notifDisplayed = events.filter((e) => e.type === "notification_displayed").length;
  const notifSnoozed = events.filter((e) => e.type === "notification_snoozed").length;
  const notifDismissed = events.filter((e) => e.type === "notification_dismissed").length;

  const snoozeRatePct =
    notifDisplayed >= 5 ? Math.round((notifSnoozed / notifDisplayed) * 100) : null;
  const skipRatePct =
    notifDisplayed >= 5 ? Math.round((notifDismissed / notifDisplayed) * 100) : null;

  // 3. Time Blocks Completion & Duration Bias
  const completedBlocks = blocks.filter((b) => b.status === "DONE");
  const completionRatePct =
    blocks.length > 0 ? Math.round((completedBlocks.length / blocks.length) * 100) : null;

  // Duration bias: actual / planned per category
  const categoryDurations: Record<string, { planned: number; actual: number; count: number }> = {};
  for (const b of blocks) {
    if (b.status === "DONE" && b.actual_minutes && b.planned_minutes) {
      if (!categoryDurations[b.category]) {
        categoryDurations[b.category] = { planned: 0, actual: 0, count: 0 };
      }
      categoryDurations[b.category].planned += b.planned_minutes;
      categoryDurations[b.category].actual += b.actual_minutes;
      categoryDurations[b.category].count += 1;
    }
  }

  const durationBiasByCategory = Object.entries(categoryDurations).map(([category, stats]) => ({
    category,
    ratio: Math.round((stats.actual / Math.max(1, stats.planned)) * 100) / 100,
    sampleCount: stats.count,
  }));

  // 4. Focus Windows by Start Hour
  const hourBuckets: Record<string, { total: number; done: number }> = {
    "05:00–08:00": { total: 0, done: 0 },
    "08:00–12:00": { total: 0, done: 0 },
    "12:00–16:00": { total: 0, done: 0 },
    "16:00–20:00": { total: 0, done: 0 },
    "20:00–23:59": { total: 0, done: 0 },
  };

  for (const b of blocks) {
    if (!b.start) continue;
    const hour = parseInt(b.start.split(":")[0], 10);
    let bucket = "20:00–23:59";
    if (hour >= 5 && hour < 8) bucket = "05:00–08:00";
    else if (hour >= 8 && hour < 12) bucket = "08:00–12:00";
    else if (hour >= 12 && hour < 16) bucket = "12:00–16:00";
    else if (hour >= 16 && hour < 20) bucket = "16:00–20:00";

    hourBuckets[bucket].total += 1;
    if (b.status === "DONE") hourBuckets[bucket].done += 1;
  }

  let bestFocusWindow: { window: string; completionRate: number; sampleCount: number } | null = null;
  for (const [window, stats] of Object.entries(hourBuckets)) {
    if (stats.total >= 3) {
      const rate = Math.round((stats.done / stats.total) * 100);
      if (!bestFocusWindow || rate > bestFocusWindow.completionRate) {
        bestFocusWindow = { window, completionRate: rate, sampleCount: stats.total };
      }
    }
  }

  // 5. Generate Grounded Claims
  const claims: BehavioralClaim[] = [];

  if (bestFocusWindow && bestFocusWindow.sampleCount >= 4) {
    const confidence =
      bestFocusWindow.sampleCount >= 10 ? "high" : bestFocusWindow.sampleCount >= 6 ? "medium" : "low";
    claims.push({
      id: "claim_focus_window",
      claim: `Blocks in ${bestFocusWindow.window} complete at ${bestFocusWindow.completionRate}% vs average`,
      sampleSize: bestFocusWindow.sampleCount,
      confidence,
      suggestedAction: "Schedule high-difficulty learning or deep research during this window.",
    });
  }

  for (const bias of durationBiasByCategory) {
    if (bias.sampleCount >= 3 && Math.abs(bias.ratio - 1) >= 0.15) {
      const direction = bias.ratio > 1 ? "over" : "under";
      const pct = Math.round(Math.abs(bias.ratio - 1) * 100);
      const confidence = bias.sampleCount >= 10 ? "high" : bias.sampleCount >= 5 ? "medium" : "low";
      claims.push({
        id: `claim_bias_${bias.category}`,
        claim: `${bias.category} sessions run ${pct}% ${direction} planned duration`,
        sampleSize: bias.sampleCount,
        confidence,
        suggestedAction:
          direction === "over"
            ? `Add 15–20 minutes buffer when scheduling ${bias.category}.`
            : `Consider condensing scheduled blocks for ${bias.category}.`,
      });
    }
  }

  if (medianResponseTimeSec != null && responseTimes.length >= 5) {
    if (medianResponseTimeSec <= 6) {
      claims.push({
        id: "claim_quick_dismiss",
        claim: `You frequently interact with or dismiss alerts within ${medianResponseTimeSec}s during active periods`,
        sampleSize: responseTimes.length,
        confidence: responseTimes.length >= 12 ? "high" : "medium",
        suggestedAction: "Use gentle chime sounds to minimize visual interruption.",
      });
    }
  }

  return {
    sampleSize: events.length + blocks.length,
    medianResponseTimeSec,
    snoozeRatePct,
    skipRatePct,
    completionRatePct,
    durationBiasByCategory,
    bestFocusWindow,
    claims,
  };
}
