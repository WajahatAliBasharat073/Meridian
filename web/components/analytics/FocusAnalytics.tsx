"use client";

import { Clock, Flame, ShieldAlert, Sparkles, TrendingUp } from "lucide-react";
import { Card } from "@/components/ui/card";
import { NoDataYet } from "@/components/analytics/NoDataYet";

/** Focus/deep-work stats.
 *
 * Every value must be passed in from real recorded sessions. This
 * previously carried defaults (`avgFocusMinutes = 48`, `completedCount = 24`,
 * `bestWindow = "08:00 AM — 11:00 AM"`) and was rendered with no props at
 * all, so the page showed a confident "Gold Focus Window ... n = 28
 * sessions" for an account with zero sessions. There are no defaults now:
 * without data it says so. */
export function FocusAnalytics({
  avgFocusMinutes,
  longestFocusMinutes,
  completedCount,
  interruptedCount,
  bestWindow,
  bestWindowCompletionPct,
  bestWindowSampleSize,
}: {
  avgFocusMinutes?: number;
  longestFocusMinutes?: number;
  completedCount?: number;
  interruptedCount?: number;
  bestWindow?: string;
  bestWindowCompletionPct?: number;
  bestWindowSampleSize?: number;
}) {
  const hasSessions = (completedCount ?? 0) + (interruptedCount ?? 0) > 0;

  const completionRate =
    completedCount != null && interruptedCount != null && hasSessions
      ? Math.round((completedCount / (completedCount + interruptedCount)) * 100)
      : null;

  return (
    <Card className="p-5 space-y-4">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <TrendingUp size={16} className="text-accent-strong" />
          <h3 className="text-sm font-semibold text-text">Focus &amp; Deep Work Analytics</h3>
        </div>
        <p className="text-xs text-text-muted">
          Session velocity and concentration durability based on logged blocks.
        </p>
      </div>

      {!hasSessions ? (
        <NoDataYet
          what="focus sessions"
          fills="Start a block with Focus on Today and these fill in from what you actually run — session length, longest stretch, and how often a session gets interrupted."
        />
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <Stat
              icon={<Clock size={13} />}
              label="Avg Session"
              value={avgFocusMinutes != null ? `${avgFocusMinutes}m` : "—"}
            />
            <Stat
              icon={<Flame size={13} className="text-warning" />}
              label="Longest Sprint"
              value={longestFocusMinutes != null ? `${longestFocusMinutes}m` : "—"}
            />
            <Stat
              icon={<Sparkles size={13} className="text-status-done" />}
              label="Completed"
              value={String(completedCount ?? 0)}
              sub={completionRate != null ? `${completionRate}% adherence` : undefined}
              valueClass="text-status-done"
            />
            <Stat
              icon={<ShieldAlert size={13} className="text-danger" />}
              label="Interrupted"
              value={String(interruptedCount ?? 0)}
              sub="Snoozed or skipped"
              valueClass="text-danger"
            />
          </div>

          {/* Only claim a "best window" when a real one was measured, and
              always show the sample size it rests on. */}
          {bestWindow && bestWindowSampleSize != null && bestWindowSampleSize > 0 && (
            <div className="p-3.5 rounded-xl border border-accent/20 bg-accent-soft/40 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-accent-strong">
                  Strongest Focus Window
                </span>
                <p className="text-sm font-semibold text-text mt-0.5">{bestWindow}</p>
                {bestWindowCompletionPct != null && (
                  <p className="text-xs text-text-muted mt-0.5">
                    Completion rate reaches {bestWindowCompletionPct}% in this window.
                  </p>
                )}
              </div>
              <div className="hidden sm:block text-right shrink-0">
                <span className="text-xs px-2.5 py-1 rounded-full bg-surface text-accent-strong border border-border font-mono font-medium">
                  n = {bestWindowSampleSize} session{bestWindowSampleSize === 1 ? "" : "s"}
                </span>
              </div>
            </div>
          )}
        </>
      )}
    </Card>
  );
}

function Stat({
  icon,
  label,
  value,
  sub,
  valueClass,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub?: string;
  valueClass?: string;
}) {
  return (
    <div className="p-3 rounded-xl bg-surface-2/60 border border-border min-w-0">
      <div className="flex items-center gap-1.5 text-xs text-text-faint mb-1 min-w-0">
        <span className="shrink-0">{icon}</span>
        <span className="truncate">{label}</span>
      </div>
      <p className={`text-2xl font-bold tabular-nums font-mono ${valueClass ?? "text-text"}`}>
        {value}
      </p>
      {sub && <p className="text-[10px] text-text-faint mt-1 truncate">{sub}</p>}
    </div>
  );
}
