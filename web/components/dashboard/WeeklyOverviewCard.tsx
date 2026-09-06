"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { useWeeklyReview } from "@/hooks/useWeeklyReview";
import { Card } from "@/components/ui/card";
import { formatCountdown } from "@/lib/time";

export function WeeklyOverviewCard() {
  const { data, isLoading } = useWeeklyReview();

  if (isLoading || !data) return <Card className="p-4 h-48 animate-pulse" />;

  if (data.category_minutes.length === 0) {
    return (
      <Card className="p-4">
        <p className="text-xs font-medium text-text-faint uppercase tracking-wide mb-1">This week</p>
        <p className="text-sm text-text-muted">Not enough data yet — complete a few blocks this week.</p>
      </Card>
    );
  }

  const max = data.category_minutes[0].minutes || 1;

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs font-medium text-text-faint uppercase tracking-wide">
          This week — {formatCountdown(data.total_minutes_logged)} logged
        </p>
        <Link href="/weekly-review" className="text-xs text-accent-strong hover:underline inline-flex items-center gap-1">
          Full review <ArrowRight size={12} />
        </Link>
      </div>
      <div className="space-y-2">
        {data.category_minutes.slice(0, 5).map((c) => (
          <div key={c.category} className="flex items-center gap-2">
            <span className="text-xs text-text-muted w-24 shrink-0 truncate">{c.category}</span>
            <div className="flex-1 h-2 rounded-full bg-surface-2 overflow-hidden">
              <div
                className="h-full rounded-full bg-accent"
                style={{ width: `${Math.round((c.minutes / max) * 100)}%` }}
              />
            </div>
            <span className="text-[11px] text-text-faint tabular-nums w-10 text-right shrink-0">
              {formatCountdown(c.minutes)}
            </span>
          </div>
        ))}
      </div>
    </Card>
  );
}
