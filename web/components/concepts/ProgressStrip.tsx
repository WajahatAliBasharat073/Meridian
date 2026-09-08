"use client";

/** Two-segment progress bar for the question bank.
 *
 * One number cannot describe this honestly. "Attempted" counts anything
 * you have rated at all (mastery >= 1); "ready" counts only mastery >= 4,
 * where you can hold the question under follow-up pressure. A single bar
 * showing attempted would say you have "done" questions you can merely
 * recognise; a single bar showing ready would hide all the work in
 * progress. So both are drawn, ready filled and attempted hatched behind
 * it, and the legend states the bar for each.
 */
export function ProgressStrip({
  total,
  started,
  ready,
  className,
}: {
  total: number;
  started: number;
  ready: number;
  className?: string;
}) {
  const readyPct = total > 0 ? (ready / total) * 100 : 0;
  const startedPct = total > 0 ? (started / total) * 100 : 0;
  const untouched = Math.max(0, total - started);

  return (
    <div className={className}>
      <div className="flex flex-wrap items-baseline gap-x-6 gap-y-2 mb-3">
        <Stat value={total} label="questions" />
        <Stat value={started} label="attempted" tone="text-accent-strong" />
        <Stat value={ready} label="interview-ready" tone="text-status-done" />
        <Stat value={untouched} label="not started" tone="text-text-faint" />
        <span className="ml-auto text-xs text-text-faint tabular-nums">
          {total > 0 ? `${readyPct.toFixed(readyPct < 10 ? 1 : 0)}% ready` : "—"}
        </span>
      </div>

      <div
        className="h-2 rounded-full bg-surface-2 overflow-hidden relative"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={total}
        aria-valuenow={ready}
        aria-label={`${ready} of ${total} questions at interview-ready level; ${started} attempted`}
      >
        {/* Attempted sits behind, at lower opacity, so the gap between
            "touched it" and "can defend it" is visible at a glance. */}
        <div
          className="absolute inset-y-0 left-0 bg-accent/35 transition-[width] duration-500"
          style={{ width: `${startedPct}%` }}
        />
        <div
          className="absolute inset-y-0 left-0 bg-status-done transition-[width] duration-500"
          style={{ width: `${readyPct}%` }}
        />
      </div>

      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-[10px] text-text-faint">
        <Legend className="bg-status-done" label="Ready — level 4+, can defend the trade-offs" />
        <Legend className="bg-accent/35" label="Attempted — rated at level 1-3" />
        <Legend className="bg-surface-2 border border-border" label="Not started" />
      </div>
    </div>
  );
}

function Stat({ value, label, tone }: { value: number; label: string; tone?: string }) {
  return (
    <div className="min-w-0">
      <span className={`text-2xl font-semibold tabular-nums ${tone ?? "text-text"}`}>{value}</span>
      <span className="text-xs text-text-faint ml-1.5">{label}</span>
    </div>
  );
}

function Legend({ className, label }: { className: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={`h-2 w-2 rounded-sm shrink-0 ${className}`} />
      {label}
    </span>
  );
}
