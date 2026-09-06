"use client";

import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { QueryError } from "@/components/ui/query-state";
import { useWeeklyReview } from "@/hooks/useWeeklyReview";
import { formatCountdown } from "@/lib/time";

const MOOD_LABEL: Record<string, string> = {
  difficult: "Difficult",
  normal: "Normal",
  good: "Good",
  excellent: "Excellent",
};

export default function WeeklyReviewPage() {
  const { data, isLoading, isError, error } = useWeeklyReview();

  return (
    <PageContainer>
      <PageHeader
        eyebrow="Insights"
        title="Weekly Review"
        description="The last 7 days, from what you actually logged — nothing here is estimated."
      />

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      )}

      {isError && <QueryError error={error} fallback="Couldn't load this week's review." />}

      {data && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Card className="p-4">
              <p className="text-2xl font-semibold tabular-nums text-text">
                {formatCountdown(data.total_minutes_logged)}
              </p>
              <p className="text-xs text-text-faint mt-1">logged this week</p>
            </Card>
            <Card className="p-4">
              <p className="text-2xl font-semibold tabular-nums text-text">
                {data.days_active}/{data.days_in_window}
              </p>
              <p className="text-xs text-text-faint mt-1">active days</p>
            </Card>
            <Card className="p-4">
              <p className="text-2xl font-semibold tabular-nums text-text">
                {data.completion_pct != null ? `${data.completion_pct}%` : "—"}
              </p>
              <p className="text-xs text-text-faint mt-1">blocks completed</p>
            </Card>
            <Card className="p-4">
              <p className="text-2xl font-semibold tabular-nums text-text">
                {data.avg_focus_session_minutes != null ? `${data.avg_focus_session_minutes}m` : "—"}
              </p>
              <p className="text-xs text-text-faint mt-1">avg. focus session</p>
            </Card>
          </div>

          {data.category_minutes.length > 0 && (
            <Card className="p-4">
              <h2 className="text-sm font-semibold text-text mb-3">Where the time went</h2>
              <div className="space-y-2.5">
                {data.category_minutes.map((c) => {
                  const max = data.category_minutes[0].minutes || 1;
                  const pct = Math.round((c.minutes / max) * 100);
                  return (
                    <div key={c.category}>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-text-muted">{c.category}</span>
                        <span className="text-text-faint tabular-nums">{formatCountdown(c.minutes)}</span>
                      </div>
                      <div className="h-2 rounded-full bg-surface-2 overflow-hidden">
                        <div className="h-full rounded-full bg-accent" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          )}

          {data.mood_distribution.length > 0 && (
            <Card className="p-4">
              <h2 className="text-sm font-semibold text-text mb-3">How the days felt</h2>
              <div className="flex gap-2 flex-wrap">
                {data.mood_distribution.map((m) => (
                  <span
                    key={m.mood}
                    className="text-xs rounded-full border border-border px-3 py-1.5 text-text-muted"
                  >
                    {MOOD_LABEL[m.mood] ?? m.mood} · {m.count}
                  </span>
                ))}
              </div>
            </Card>
          )}

          <div className="grid md:grid-cols-2 gap-4">
            <Card className="p-4">
              <h2 className="text-sm font-semibold text-text mb-2">What went well</h2>
              {data.what_went_well.length === 0 ? (
                <p className="text-xs text-text-faint">Not enough data yet this week.</p>
              ) : (
                <ul className="space-y-1.5">
                  {data.what_went_well.map((s, i) => (
                    <li key={i} className="text-sm text-text-muted">
                      ✓ {s}
                    </li>
                  ))}
                </ul>
              )}
            </Card>
            <Card className="p-4">
              <h2 className="text-sm font-semibold text-text mb-2">What to improve</h2>
              {data.what_to_improve.length === 0 ? (
                <p className="text-xs text-text-faint">Nothing flagged this week.</p>
              ) : (
                <ul className="space-y-1.5">
                  {data.what_to_improve.map((s, i) => (
                    <li key={i} className="text-sm text-text-muted">
                      → {s}
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
