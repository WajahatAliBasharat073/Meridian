"use client";

import { useState } from "react";
import { Gauge } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useTheoryPace } from "@/hooks/useQuestions";
import { cn } from "@/lib/cn";
import type { TheoryPaceProjectionOut } from "@/lib/types";

function formatMinutes(m: number): string {
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  const rem = m % 60;
  return rem === 0 ? `${h}h` : `${h}h ${rem}m`;
}

function formatDays(d: number | null): string {
  if (d == null) return "—";
  if (d === 0) return "already clear";
  if (d < 30) return `${d} day${d === 1 ? "" : "s"}`;
  const months = Math.round((d / 30) * 10) / 10;
  return `~${months} month${months === 1 ? "" : "s"} (${d}d)`;
}

/** Real pace, real projections — never a guess. Refuses to estimate at
 * all until at least a handful of questions have logged real minutes; see
 * MIN_QUESTIONS_FOR_INSIGHT in api/app/engines/theory_pace.py. Log time
 * when rating a question on "Today's Theory Focus" to build this up. */
export function TheoryPaceCard() {
  const { data, isLoading, isError } = useTheoryPace();
  const [selected, setSelected] = useState<number | null>(null);

  if (isLoading) return <Skeleton className="h-40" />;
  if (isError || !data) return null;

  const baseline = data.projections.find((p) => p.daily_count === data.baseline_daily_count);
  const activeCount = selected ?? data.baseline_daily_count;
  const active = data.projections.find((p) => p.daily_count === activeCount) ?? baseline;

  return (
    <Card className="p-5">
      <div className="flex items-center justify-between gap-2 mb-1">
        <h3 className="text-sm font-semibold text-text inline-flex items-center gap-2">
          <Gauge size={15} className="text-accent-strong" />
          Your Study Pace
        </h3>
        {data.enough_data && (
          <span className="text-xs text-text-faint tabular-nums">
            {data.avg_minutes_per_question}m avg / question
          </span>
        )}
      </div>

      {!data.enough_data ? (
        <div className="rounded-xl border border-dashed border-border bg-surface-2/30 p-4 text-center mt-3">
          <p className="text-sm text-text-muted">
            Not enough logged time yet — {data.questions_with_data} of{" "}
            {data.min_questions_needed} questions needed.
          </p>
          <p className="text-xs text-text-faint mt-1 max-w-md mx-auto leading-relaxed">
            Log how many minutes a question actually took when you rate it on{" "}
            <span className="text-text-muted">Today&apos;s Theory Focus</span>, and this fills in
            with your real pace instead of a guess.
          </p>
          {data.backlog_count > 0 && (
            <p className="text-xs text-text-faint mt-2">
              {data.backlog_count} questions in the bank aren&apos;t interview-ready yet.
            </p>
          )}
        </div>
      ) : (
        <>
          <p className="text-xs text-text-muted mb-3">
            {data.backlog_count} questions aren&apos;t interview-ready yet, from{" "}
            {data.questions_with_data} you&apos;ve timed so far.
          </p>

          <div className="flex flex-wrap gap-1.5 mb-3">
            {data.projections.map((p) => (
              <ProjectionButton
                key={p.daily_count}
                projection={p}
                isBaseline={p.daily_count === data.baseline_daily_count}
                isActive={p.daily_count === activeCount}
                onClick={() => setSelected(p.daily_count)}
              />
            ))}
          </div>

          {active && (
            <div className="rounded-xl border border-border bg-surface-2/50 p-3.5">
              <p className="text-sm text-text leading-relaxed">
                At <span className="font-semibold">{active.daily_count}/day</span>:{" "}
                <span className="font-semibold tabular-nums">
                  {formatMinutes(active.daily_minutes)}
                </span>{" "}
                a day, backlog cleared in{" "}
                <span className="font-semibold tabular-nums">
                  {formatDays(active.days_to_clear_backlog)}
                </span>
                .
              </p>
              {active.daily_count !== data.baseline_daily_count && (
                <p className="text-xs text-text-faint mt-1.5">
                  vs your {data.baseline_daily_count}/day baseline:{" "}
                  <span
                    className={cn(
                      "font-medium tabular-nums",
                      active.minutes_delta_vs_baseline > 0 ? "text-status-partial" : "text-status-done"
                    )}
                  >
                    {active.minutes_delta_vs_baseline > 0 ? "+" : ""}
                    {active.minutes_delta_vs_baseline} min/day
                  </span>
                  {active.days_saved_vs_baseline != null && active.days_saved_vs_baseline !== 0 && (
                    <>
                      {" · "}
                      <span
                        className={cn(
                          "font-medium tabular-nums",
                          active.days_saved_vs_baseline > 0 ? "text-status-done" : "text-status-partial"
                        )}
                      >
                        {active.days_saved_vs_baseline > 0
                          ? `${active.days_saved_vs_baseline}d sooner`
                          : `${Math.abs(active.days_saved_vs_baseline)}d later`}
                      </span>
                    </>
                  )}
                </p>
              )}
            </div>
          )}
        </>
      )}
    </Card>
  );
}

function ProjectionButton({
  projection,
  isBaseline,
  isActive,
  onClick,
}: {
  projection: TheoryPaceProjectionOut;
  isBaseline: boolean;
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={
        isBaseline
          ? "Your current daily count"
          : `${formatMinutes(projection.daily_minutes)}/day`
      }
      className={cn(
        "h-9 px-3 rounded-lg text-xs font-medium border transition-colors",
        isActive
          ? "border-accent bg-accent-soft text-accent-strong"
          : "border-border text-text-muted hover:bg-surface-2 hover:text-text"
      )}
    >
      {projection.daily_count}/day
      {isBaseline && <span className="text-text-faint"> · now</span>}
    </button>
  );
}
