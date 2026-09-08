"use client";

import { useMemo } from "react";
import { formatCountdown, timeStringToMinutes } from "@/lib/time";
import type { TimeBlockOut } from "@/lib/types";

function getPhase(startStr: string): "morning" | "job" | "prep" | "night" {
  const min = timeStringToMinutes(startStr);
  if (min < 9 * 60) return "morning";
  if (min < 17 * 60 + 5) return "job";
  if (min < 20 * 60 + 40) return "prep";
  return "night";
}

const PHASE_META = {
  morning: { label: "Morning",    icon: "🌅", color: "var(--status-partial)" },
  job:     { label: "Remote Job", icon: "💼", color: "var(--accent)" },
  prep:    { label: "Prep",       icon: "💻", color: "hsl(258,80%,65%)" },
  night:   { label: "Night",      icon: "🌙", color: "var(--text-faint)" },
} as const;

function blockDone(b: TimeBlockOut): number {
  if (b.status === "DONE")    return b.actual_minutes ?? b.planned_minutes;
  if (b.status === "PARTIAL") return b.actual_minutes ?? Math.round(b.planned_minutes / 2);
  return 0;
}

export function TimeProgress({ blocks }: { blocks: TimeBlockOut[] }) {
  const { phases, totalPlanned, totalDone } = useMemo(() => {
    type PhaseKey = keyof typeof PHASE_META;
    const phaseMap: Record<PhaseKey, { planned: number; done: number }> = {
      morning: { planned: 0, done: 0 },
      job:     { planned: 0, done: 0 },
      prep:    { planned: 0, done: 0 },
      night:   { planned: 0, done: 0 },
    };
    for (const b of blocks) {
      const ph = getPhase(b.start) as PhaseKey;
      phaseMap[ph].planned += b.planned_minutes;
      phaseMap[ph].done    += blockDone(b);
    }
    const totalPlanned = Object.values(phaseMap).reduce((s, p) => s + p.planned, 0);
    const totalDone    = Object.values(phaseMap).reduce((s, p) => s + p.done, 0);
    return { phases: phaseMap, totalPlanned, totalDone };
  }, [blocks]);

  const overallPct = totalPlanned > 0 ? Math.min(100, Math.round((totalDone / totalPlanned) * 100)) : 0;
  const totalRemaining = Math.max(0, totalPlanned - totalDone);

  const doneBlocks      = blocks.filter((b) => b.status === "DONE").length;
  const partialBlocks   = blocks.filter((b) => b.status === "PARTIAL").length;
  const remainingBlocks = blocks.filter((b) => b.status === "NOT DONE").length;

  return (
    <div className="rounded-xl border border-border bg-surface shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 pt-3.5 pb-3 border-b border-border/50 flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-text-faint">Day Progress</span>
        <span
          className="text-xs font-bold tabular-nums px-2.5 py-0.5 rounded-full border"
          style={{
            color:           overallPct >= 80 ? "var(--status-done)"   : overallPct >= 40 ? "var(--accent-strong)" : "var(--text-muted)",
            borderColor:     overallPct >= 80 ? "var(--status-done)"   : overallPct >= 40 ? "var(--accent)"        : "var(--border)",
            backgroundColor: overallPct >= 80
              ? "color-mix(in srgb, var(--status-done) 10%, transparent)"
              : overallPct >= 40 ? "var(--accent-soft)" : "var(--surface-2)",
          }}
        >
          {overallPct}% complete
        </span>
      </div>

      <div className="p-4 space-y-4">
        {/* Segmented overall bar */}
        <div>
          <div className="h-3 rounded-full bg-surface-2 overflow-hidden flex gap-0.5">
            {(["morning", "job", "prep", "night"] as const).map((ph) => {
              const phData = phases[ph];
              if (phData.planned === 0) return null;
              const phWidth   = Math.round((phData.planned / Math.max(1, totalPlanned)) * 100);
              const phDonePct = Math.min(100, Math.round((phData.done / Math.max(1, phData.planned)) * 100));
              return (
                <div
                  key={ph}
                  className="relative rounded-sm overflow-hidden"
                  style={{ width: `${phWidth}%`, backgroundColor: "color-mix(in srgb, var(--border) 60%, transparent)" }}
                  title={`${PHASE_META[ph].label}: ${phDonePct}% done`}
                >
                  <div
                    className="absolute inset-y-0 left-0 transition-all duration-700"
                    style={{ width: `${phDonePct}%`, backgroundColor: PHASE_META[ph].color }}
                  />
                </div>
              );
            })}
          </div>
          <div className="flex items-center justify-between mt-2 text-[11px] text-text-faint">
            <span>
              <span className="text-text font-medium tabular-nums">{formatCountdown(totalDone)}</span>{" "}done
            </span>
            <span>
              <span className="tabular-nums">{formatCountdown(totalRemaining)}</span>{" "}remaining
              {" "}of{" "}
              <span className="tabular-nums">{formatCountdown(totalPlanned)}</span>
            </span>
          </div>
        </div>

        {/* Per-phase mini cards */}
        {/* Two columns, not four: these sit in a ~400px sticky panel, where
            four tracks left ~85px each — enough to wrap "Remote Job" onto a
            second line and shove its percentage outside the card. */}
        <div className="grid grid-cols-2 gap-2">
          {(["morning", "job", "prep", "night"] as const).map((ph) => {
            const phData = phases[ph];
            const meta   = PHASE_META[ph];
            if (phData.planned === 0) return null;
            const pct = Math.min(100, Math.round((phData.done / Math.max(1, phData.planned)) * 100));
            return (
              <div key={ph} className="rounded-lg bg-surface-2/60 border border-border p-2.5 space-y-2 min-w-0">
                <div className="flex items-center justify-between gap-1.5 min-w-0">
                  <span className="text-[11px] font-medium text-text-muted flex items-center gap-1 min-w-0">
                    <span className="shrink-0">{meta.icon}</span>
                    <span className="truncate">{meta.label}</span>
                  </span>
                  <span
                    className="text-[11px] font-bold tabular-nums shrink-0"
                    style={{ color: meta.color }}
                  >
                    {pct}%
                  </span>
                </div>
                <div className="h-1.5 rounded-full bg-surface-3 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{ width: `${pct}%`, backgroundColor: meta.color }}
                  />
                </div>
                <p className="text-[10px] text-text-faint tabular-nums">
                  {formatCountdown(phData.done)} / {formatCountdown(phData.planned)}
                </p>
              </div>
            );
          })}
        </div>

        {/* Block counts */}
        <div className="flex items-center gap-4 pt-1 border-t border-border/40 text-[11px]">
          <span className="flex items-center gap-1.5 text-text-muted">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: "var(--status-done)" }} />
            <span className="tabular-nums font-medium text-text">{doneBlocks}</span> done
          </span>
          {partialBlocks > 0 && (
            <span className="flex items-center gap-1.5 text-text-muted">
              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: "var(--status-partial)" }} />
              <span className="tabular-nums font-medium text-text">{partialBlocks}</span> partial
            </span>
          )}
          <span className="flex items-center gap-1.5 text-text-muted">
            <span className="h-2 w-2 rounded-full bg-surface-3 border border-border" />
            <span className="tabular-nums font-medium text-text">{remainingBlocks}</span> left
          </span>
          <span className="ml-auto text-text-faint">{blocks.length} total</span>
        </div>
      </div>
    </div>
  );
}
