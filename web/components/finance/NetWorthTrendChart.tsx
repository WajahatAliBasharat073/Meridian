"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ChartCard } from "@/components/dashboard/ChartCard";
import { formatMoney } from "@/lib/money";
import type { FinanceNetWorthPointOut } from "@/lib/types";

const TOOLTIP_STYLE = {
  background: "var(--surface-2)",
  border: "1px solid var(--border)",
  borderRadius: 8,
  fontSize: 12,
};

export function NetWorthTrendChart({ trend }: { trend: FinanceNetWorthPointOut[] }) {
  const data = trend.map((p) => ({ date: p.snapshot_date, netWorth: p.net_worth }));
  const first = data[0];
  const last = data[data.length - 1];
  const takeaway =
    data.length >= 2
      ? last.netWorth >= first.netWorth
        ? `Net worth is up ${formatMoney(last.netWorth - first.netWorth)} since your first snapshot.`
        : `Net worth is down ${formatMoney(first.netWorth - last.netWorth)} since your first snapshot.`
      : last
        ? `${formatMoney(last.netWorth)} as of your only snapshot so far.`
        : "";

  return (
    <ChartCard
      question="Is net worth improving or declining?"
      takeaway={takeaway}
      isEmpty={data.length === 0}
      emptyHint="Take your first net-worth snapshot from an account balance to start the trend."
    >
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <XAxis
            dataKey="date"
            tick={{ fill: "var(--text-faint)", fontSize: 11 }}
            axisLine={{ stroke: "var(--border)" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "var(--text-faint)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={64}
            tickFormatter={(v: number) => formatMoney(v)}
          />
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            formatter={(value) => [formatMoney(value as number), "Net worth"]}
            cursor={{ stroke: "var(--border)" }}
          />
          <Line
            type="monotone"
            dataKey="netWorth"
            stroke="var(--accent)"
            strokeWidth={2}
            dot={{ r: 3, fill: "var(--accent)" }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
