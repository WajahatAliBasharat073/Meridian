"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Card } from "@/components/ui/card";
import { NoDataYet } from "@/components/analytics/NoDataYet";
import { formatCountdown } from "@/lib/time";

interface TimeCategoryData {
  category: string;
  minutes: number;
  color: string;
}

const CATEGORY_COLORS: Record<string, string> = {
  Work: "#6f9bc9",
  Learning: "#4fae72",
  Research: "#a9c7e6",
  DSA: "#dba23f",
  Health: "#e2645f",
  Personal: "#8b9ad1",
  Prayer: "#e0a84d",
  Recovery: "#7ab55a",
};

/** Where recorded minutes actually went, by category.
 *
 * Three fabrications lived here and are gone: a six-category fallback
 * series (Work 1710m, Research 490m, …) used whenever no real minutes were
 * passed; a `trendPct` invented per row (`category === "Research" ? 18 : …`)
 * and shown in the tooltip as "vs prior period"; and a footer asserting
 * "+18% this month" and "92% of target". A period switcher was also on
 * screen that did not change the data behind it — the caller names the
 * period instead, so the label can't disagree with what's plotted. */
export function TimeCurve({
  categoryMinutes = [],
  periodLabel,
}: {
  categoryMinutes?: { category: string; minutes: number }[];
  periodLabel?: string;
}) {
  const data: TimeCategoryData[] = categoryMinutes
    .filter((c) => c.minutes > 0)
    .map((c) => ({
      category: c.category,
      minutes: c.minutes,
      color: CATEGORY_COLORS[c.category] || "#6f9bc9",
    }))
    .sort((a, b) => b.minutes - a.minutes);

  const totalMinutes = data.reduce((acc, curr) => acc + curr.minutes, 0);

  return (
    <Card className="p-5 space-y-4">
      <div>
        <h3 className="text-sm font-semibold text-text">Overall Time Allocation</h3>
        <p className="text-xs text-text-muted">
          Where your hours are actually invested across life domains.
        </p>
      </div>

      {data.length === 0 ? (
        <NoDataYet
          what="logged time"
          fills="Complete blocks on Today and the minutes split out by category here — Work, Learning, DSA, Health and the rest, largest first."
        />
      ) : (
        <>
          <div className="flex items-baseline gap-3 pt-1 flex-wrap">
            <span className="text-2xl font-bold tabular-nums font-mono text-text">
              {formatCountdown(totalMinutes)}
            </span>
            <span className="text-xs text-text-faint">
              logged{periodLabel ? ` · ${periodLabel}` : ""}
            </span>
          </div>

          <div className="h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data}
                layout="vertical"
                margin={{ left: 10, right: 20, top: 0, bottom: 0 }}
              >
                <XAxis type="number" hide />
                <YAxis
                  type="category"
                  dataKey="category"
                  tick={{ fill: "var(--text-muted)", fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                  width={75}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (!active || !payload?.length) return null;
                    const d = payload[0].payload as TimeCategoryData;
                    const share = Math.round((d.minutes / Math.max(1, totalMinutes)) * 100);
                    return (
                      <div className="rounded-lg border border-border bg-surface p-2 text-xs shadow-md">
                        <p className="font-semibold text-text">{d.category}</p>
                        <p className="text-accent-strong tabular-nums font-mono">
                          {formatCountdown(d.minutes)}
                        </p>
                        <p className="text-text-faint text-[10px]">
                          {share}% of logged time
                        </p>
                      </div>
                    );
                  }}
                />
                <Bar dataKey="minutes" radius={[0, 4, 4, 0]}>
                  {data.map((entry) => (
                    <Cell key={entry.category} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </Card>
  );
}
