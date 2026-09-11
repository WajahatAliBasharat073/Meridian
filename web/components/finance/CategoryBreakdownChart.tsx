"use client";

import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ChartCard } from "@/components/dashboard/ChartCard";
import { formatMoney } from "@/lib/money";
import type { FinanceCategorySpend } from "@/lib/types";

const TOOLTIP_STYLE = {
  background: "var(--surface-2)",
  border: "1px solid var(--border)",
  borderRadius: 8,
  fontSize: 12,
};

export function CategoryBreakdownChart({ breakdown }: { breakdown: FinanceCategorySpend[] }) {
  const data = breakdown.slice(0, 8).map((c) => ({ category: c.category_name, amount: c.amount }));
  const top = data[0];
  const takeaway = top
    ? `${top.category} is this month's largest expense category at ${formatMoney(top.amount)}.`
    : "";
  const height = Math.max(180, data.length * 32);

  return (
    <ChartCard
      question="Where did this month's money go?"
      takeaway={takeaway}
      isEmpty={data.length === 0}
      emptyHint="Record an expense transaction to see spending broken down by category."
    >
      <ResponsiveContainer width="100%" height={Math.max(240, height)}>
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 24, left: 0, bottom: 0 }}>
          <XAxis
            type="number"
            tick={{ fill: "var(--text-faint)", fontSize: 11 }}
            axisLine={{ stroke: "var(--border)" }}
            tickLine={false}
            tickFormatter={(v: number) => formatMoney(v)}
          />
          <YAxis
            type="category"
            dataKey="category"
            tick={{ fill: "var(--text-muted)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={110}
          />
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            formatter={(value) => [formatMoney(value as number), "Spent"]}
            cursor={{ fill: "var(--surface-2)" }}
          />
          <Bar dataKey="amount" fill="var(--accent)" radius={[0, 4, 4, 0]} maxBarSize={18} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
