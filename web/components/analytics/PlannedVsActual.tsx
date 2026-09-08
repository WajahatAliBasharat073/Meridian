"use client";

import { Card } from "@/components/ui/card";
import { NoDataYet } from "@/components/analytics/NoDataYet";
import { formatCountdown } from "@/lib/time";
import type { TimeBlockOut } from "@/lib/types";

interface VarianceRow {
  category: string;
  plannedMinutes: number;
  actualMinutes: number;
  varianceMinutes: number;
  ratio: number;
  blockCount: number;
}

/** Estimation-bias table, aggregated strictly from the blocks passed in.
 *
 * It used to substitute a fixed Research/Work/Learning/DSA/Exercise table
 * whenever `blocks` was empty — which was always, since the dashboard
 * rendered it with no props — and closed with a hardcoded "Tasks in DSA
 * frequently finish 42% under planned time". Both are gone: with no blocks
 * it says there is nothing yet, and the closing insight is computed from
 * the rows on screen. */
export function PlannedVsActual({ blocks = [] }: { blocks?: TimeBlockOut[] }) {
  const categoryMap: Record<string, { planned: number; actual: number; blocks: number }> = {};

  for (const b of blocks) {
    if (!categoryMap[b.category]) categoryMap[b.category] = { planned: 0, actual: 0, blocks: 0 };
    categoryMap[b.category].planned += b.planned_minutes || 0;
    categoryMap[b.category].actual += b.actual_minutes || (b.status === "DONE" ? b.planned_minutes : 0);
    categoryMap[b.category].blocks += 1;
  }

  const rows: VarianceRow[] = Object.entries(categoryMap).map(([category, stats]) => ({
    category,
    plannedMinutes: stats.planned,
    actualMinutes: stats.actual,
    varianceMinutes: stats.actual - stats.planned,
    ratio: Math.round((stats.actual / Math.max(1, stats.planned)) * 100) / 100,
    blockCount: stats.blocks,
  }));

  // "Frequently" needs more than one block behind it, so the closing line
  // only appears once a category has a few and the drift is real.
  const MIN_BLOCKS_FOR_INSIGHT = 3;
  const biggestDrift = rows
    .filter((r) => r.blockCount >= MIN_BLOCKS_FOR_INSIGHT && r.plannedMinutes > 0)
    .filter((r) => Math.abs(r.ratio - 1) >= 0.15)
    .sort((a, b) => Math.abs(b.ratio - 1) - Math.abs(a.ratio - 1))[0];

  return (
    <Card className="p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-text">Planned vs Actual Variance</h3>
          <p className="text-xs text-text-muted">
            Detects duration estimation bias to calibrate realistic scheduling.
          </p>
        </div>
      </div>

      {rows.length === 0 ? (
        <NoDataYet
          what="planned-vs-actual time"
          fills="Once blocks are completed with real durations, each category lands here with what you planned, what it actually took, and how far off the estimate was."
        />
      ) : (
      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left">
          <thead>
            <tr className="border-b border-border text-text-faint uppercase tracking-wider font-semibold">
              <th className="py-2.5 px-2">Category</th>
              <th className="py-2.5 px-2 text-right">Planned</th>
              <th className="py-2.5 px-2 text-right">Actual</th>
              <th className="py-2.5 px-2 text-right">Variance</th>
              <th className="py-2.5 px-2 text-right">Accuracy</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60">
            {rows.map((row) => {
              const isOver = row.varianceMinutes > 0;
              const isUnder = row.varianceMinutes < 0;
              return (
                <tr key={row.category} className="hover:bg-surface-2/40 transition-colors">
                  <td className="py-2.5 px-2 font-medium text-text">{row.category}</td>
                  <td className="py-2.5 px-2 text-right text-text-muted tabular-nums font-mono">
                    {formatCountdown(row.plannedMinutes)}
                  </td>
                  <td className="py-2.5 px-2 text-right text-text tabular-nums font-mono font-medium">
                    {formatCountdown(row.actualMinutes)}
                  </td>
                  <td className="py-2.5 px-2 text-right tabular-nums font-mono">
                    <span
                      className={
                        isOver ? "text-status-partial" : isUnder ? "text-danger" : "text-status-done"
                      }
                    >
                      {row.varianceMinutes > 0 ? `+${row.varianceMinutes}m` : `${row.varianceMinutes}m`}
                    </span>
                  </td>
                  <td className="py-2.5 px-2 text-right tabular-nums font-mono">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[11px] font-semibold ${
                        Math.abs(row.ratio - 1) <= 0.1
                          ? "bg-status-done-soft text-status-done"
                          : "bg-surface-2 text-text-muted"
                      }`}
                    >
                      {Math.round(row.ratio * 100)}%
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      )}

      {biggestDrift && (
        <p className="text-[11px] text-text-faint italic border-t border-border pt-2">
          {biggestDrift.category} blocks are finishing{" "}
          {Math.abs(Math.round((biggestDrift.ratio - 1) * 100))}%{" "}
          {biggestDrift.ratio < 1 ? "under" : "over"} planned time across{" "}
          {biggestDrift.blockCount} blocks — worth re-sizing those blocks.
        </p>
      )}
    </Card>
  );
}
