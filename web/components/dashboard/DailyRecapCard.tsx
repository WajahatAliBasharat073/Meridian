"use client";

import { Lightbulb } from "lucide-react";
import { useDailyRecap } from "@/hooks/useDailyRecap";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/cn";

function formatRecapDate(iso: string): string {
  const d = new Date(`${iso}T00:00:00`);
  return d.toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric" });
}

export function DailyRecapCard() {
  const { data, isLoading } = useDailyRecap();

  if (isLoading || !data) {
    return <Card className="p-4 h-[132px] animate-pulse" />;
  }

  if (data.total_blocks === 0) {
    return (
      <Card className="p-4">
        <p className="text-xs font-medium text-text-faint uppercase tracking-wide mb-1">
          {formatRecapDate(data.recap_date)}
        </p>
        <p className="text-sm text-text-muted">Nothing was scheduled that day.</p>
      </Card>
    );
  }

  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <p className="text-xs font-medium text-text-faint uppercase tracking-wide">
            {formatRecapDate(data.recap_date)}
          </p>
          <p className="text-sm font-medium text-text mt-1">{data.headline}</p>
        </div>
        {data.completion_pct != null && (
          <span className="shrink-0 text-2xl font-semibold tabular-nums text-text">
            {data.completion_pct}%
          </span>
        )}
      </div>

      {data.category_breakdown.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {data.category_breakdown.map((c) => {
            const pct = c.total > 0 ? Math.round((c.done / c.total) * 100) : 0;
            return (
              <span
                key={c.category}
                className={cn(
                  "text-[11px] rounded-full px-2 py-1 border",
                  pct >= 70
                    ? "border-status-done/30 bg-status-done/10 text-status-done"
                    : pct >= 40
                      ? "border-status-partial/30 bg-status-partial/10 text-status-partial"
                      : "border-danger/30 bg-danger/10 text-danger"
                )}
              >
                {c.category} {c.done}/{c.total}
              </span>
            );
          })}
        </div>
      )}

      {data.suggestions.length > 0 && (
        <div className="border-t border-border pt-3 space-y-2">
          {data.suggestions.map((s, i) => (
            <p key={i} className="flex gap-2 text-xs text-text-muted leading-relaxed">
              <Lightbulb size={13} className="shrink-0 mt-0.5 text-accent" />
              {s}
            </p>
          ))}
        </div>
      )}
    </Card>
  );
}
