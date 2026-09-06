"use client";

import { formatCountdown } from "@/lib/time";
import type { TimeBlockOut } from "@/lib/types";

export function TimeProgress({ blocks }: { blocks: TimeBlockOut[] }) {
  const planned = blocks.reduce((sum, b) => sum + b.planned_minutes, 0);
  const completed = blocks.reduce((sum, b) => {
    if (b.status === "DONE") return sum + (b.actual_minutes ?? b.planned_minutes);
    if (b.status === "PARTIAL") return sum + (b.actual_minutes ?? Math.round(b.planned_minutes / 2));
    return sum;
  }, 0);

  const pct = planned > 0 ? Math.min(100, Math.round((completed / planned) * 100)) : 0;

  return (
    <div>
      <div className="h-2 rounded-full bg-surface-2 overflow-hidden">
        <div className="h-full rounded-full bg-accent transition-all" style={{ width: `${pct}%` }} />
      </div>
      <p className="text-xs text-text-muted mt-2">
        <span className="tabular-nums text-text font-medium">{formatCountdown(completed)}</span> completed
        of <span className="tabular-nums">{formatCountdown(planned)}</span> planned
        <span className="text-text-faint"> · {pct}%</span>
      </p>
    </div>
  );
}
