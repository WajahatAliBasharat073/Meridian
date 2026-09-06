"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { useToday } from "@/hooks/useToday";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/cn";

export function TodayProgress() {
  const { data, isLoading } = useToday();

  if (isLoading || !data) {
    return <Card className="p-4 h-[104px] animate-pulse" />;
  }

  const total = data.blocks.length;
  const done = data.blocks.filter((b) => b.status === "DONE").length;
  const partial = data.blocks.filter((b) => b.status === "PARTIAL").length;
  const rescheduled = data.blocks.filter((b) => b.status === "RESCHEDULED").length;
  const remaining = total - done - partial - rescheduled;
  const completedPct = total > 0 ? Math.round(((done + partial) / total) * 100) : 0;

  if (total === 0) {
    return (
      <Card className="p-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-text">Nothing scheduled today yet</p>
          <p className="text-xs text-text-muted mt-0.5">Add your first block to start tracking today&apos;s progress.</p>
        </div>
        <Link
          href="/today"
          className="shrink-0 inline-flex items-center gap-1 text-sm font-medium text-accent-strong hover:underline"
        >
          Open Today <ArrowRight size={14} />
        </Link>
      </Card>
    );
  }

  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <p className="text-xs font-medium text-text-faint uppercase tracking-wide">Today&apos;s progress</p>
          <p className="text-2xl font-semibold tracking-tight tabular-nums text-text mt-1">
            {done + partial}
            <span className="text-text-faint text-base font-normal">/{total} done</span>
          </p>
        </div>
        <Link
          href="/today"
          className="shrink-0 inline-flex items-center gap-1 text-sm font-medium text-accent-strong hover:underline mt-1"
        >
          Open Today <ArrowRight size={14} />
        </Link>
      </div>

      <div className="h-2 rounded-full bg-surface-2 overflow-hidden flex">
        {done > 0 && <div className="h-full bg-status-done" style={{ width: `${(done / total) * 100}%` }} />}
        {partial > 0 && (
          <div className="h-full bg-status-partial" style={{ width: `${(partial / total) * 100}%` }} />
        )}
      </div>

      <div className="flex flex-wrap gap-x-4 gap-y-1 mt-3 text-xs text-text-muted">
        <span className={cn("inline-flex items-center gap-1.5")}>
          <span className="h-2 w-2 rounded-full bg-status-done" /> {done} done
        </span>
        {partial > 0 && (
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-status-partial" /> {partial} partial
          </span>
        )}
        <span className="inline-flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-border-strong" /> {remaining} remaining
        </span>
        {rescheduled > 0 && (
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-text-faint" /> {rescheduled} rescheduled
          </span>
        )}
        <span className="ml-auto font-medium text-text">{completedPct}% complete</span>
      </div>
    </Card>
  );
}
