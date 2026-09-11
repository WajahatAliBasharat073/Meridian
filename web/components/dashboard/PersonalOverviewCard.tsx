"use client";

import { Compass } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useOverview } from "@/hooks/useOverview";

/** The cross-domain aggregator ARCHITECTURE_AUDIT.md found missing --
 * today's command center is schedule-shaped, this dashboard is
 * DSA-mastery-shaped, and neither used to reach into goals or finance.
 * Every line here is a read of an already-computed, already-tested
 * engine result (readiness_pct, month_summary, build_overview_highlights)
 * -- nothing new is calculated in this component. */
export function PersonalOverviewCard() {
  const { data, isLoading } = useOverview();

  if (isLoading) return <Skeleton className="h-32" />;
  if (!data || data.highlights.length === 0) return null;

  return (
    <Card className="p-4">
      <h3 className="text-sm font-semibold text-text mb-3 flex items-center gap-2">
        <Compass size={15} className="text-accent" /> Across everything
      </h3>
      <ul className="space-y-2">
        {data.highlights.map((line) => (
          <li key={line} className="text-sm text-text-muted leading-relaxed pl-3 border-l-2 border-accent/40">
            {line}
          </li>
        ))}
      </ul>
    </Card>
  );
}
