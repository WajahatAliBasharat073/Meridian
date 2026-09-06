"use client";

import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ChartCard } from "@/components/dashboard/ChartCard";
import type { AttemptsByDayOut } from "@/lib/types";

const TOOLTIP_STYLE = {
  background: "var(--surface-2)",
  border: "1px solid var(--border)",
  borderRadius: 8,
  fontSize: 12,
};

function shortDay(iso: string): string {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("en-US", { weekday: "short" });
}

export function AttemptsTrendChart({ days }: { days: AttemptsByDayOut[] }) {
  const data = days.map((d) => ({ day: shortDay(d.day), date: d.day, count: d.count }));
  const total = data.reduce((sum, d) => sum + d.count, 0);
  const avg = data.length ? (total / data.length).toFixed(1) : "0";

  const takeaway = total
    ? `${total} attempts over the last ${data.length} days — averaging ${avg} per day.`
    : `No attempts in the last ${data.length} days.`;

  return (
    <ChartCard
      question="Am I attempting problems consistently?"
      takeaway={takeaway}
      isEmpty={total === 0}
      emptyHint="Rate a problem on Today and it starts filling in this trend."
    >
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
          <XAxis dataKey="day" tick={{ fill: "var(--text-faint)", fontSize: 11 }} axisLine={{ stroke: "var(--border)" }} tickLine={false} />
          <YAxis allowDecimals={false} tick={{ fill: "var(--text-faint)", fontSize: 11 }} axisLine={false} tickLine={false} width={28} />
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            labelFormatter={(_, payload) => payload?.[0]?.payload?.date ?? ""}
            formatter={(value) => [`${value} attempts`, ""]}
            cursor={{ fill: "var(--surface-2)" }}
          />
          <Bar dataKey="count" fill="var(--accent)" radius={[4, 4, 0, 0]} maxBarSize={24} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
