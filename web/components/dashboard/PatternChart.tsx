"use client";

import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ChartCard } from "@/components/dashboard/ChartCard";
import type { PatternCoverageOut } from "@/lib/types";

const TOOLTIP_STYLE = {
  background: "var(--surface-2)",
  border: "1px solid var(--border)",
  borderRadius: 8,
  fontSize: 12,
};

export function PatternChart({ coverage }: { coverage: PatternCoverageOut[] }) {
  const scheduled = coverage.filter((c) => c.scheduled_count > 0);
  const data = scheduled.map((c) => ({
    pattern: c.pattern.replace(/_/g, " "),
    pct: Math.round(c.ratio * 100),
    scheduled: c.scheduled_count,
    l5plus: c.l5_plus_count,
  }));

  const weakest = data[0];
  const takeaway = weakest
    ? `${weakest.pattern} is weakest: ${weakest.l5plus} of ${weakest.scheduled} scheduled problems at L5+ (${weakest.pct}%).`
    : "";

  const height = Math.max(180, data.length * 32);

  return (
    <ChartCard
      question="Which pattern is weakest?"
      takeaway={takeaway}
      isEmpty={data.length === 0}
      emptyHint="Once problems are scheduled in your curriculum, pattern-by-pattern coverage shows up here."
    >
      <ResponsiveContainer width="100%" height={Math.max(240, height)}>
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 24, left: 0, bottom: 0 }}>
          <XAxis
            type="number"
            domain={[0, 100]}
            tick={{ fill: "var(--text-faint)", fontSize: 11 }}
            axisLine={{ stroke: "var(--border)" }}
            tickLine={false}
            unit="%"
          />
          <YAxis
            type="category"
            dataKey="pattern"
            tick={{ fill: "var(--text-muted)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={100}
          />
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            formatter={(value, _name, item) => [
              `${item.payload.l5plus} of ${item.payload.scheduled} at L5+ (${value}%)`,
              "",
            ]}
            cursor={{ fill: "var(--surface-2)" }}
          />
          <Bar dataKey="pct" fill="var(--accent)" radius={[0, 4, 4, 0]} maxBarSize={18} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
