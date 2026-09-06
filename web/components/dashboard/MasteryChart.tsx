"use client";

import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ChartCard } from "@/components/dashboard/ChartCard";
import { MASTERY_LEVELS } from "@/lib/mastery";
import type { MasteryCountOut } from "@/lib/types";

const TOOLTIP_STYLE = {
  background: "var(--surface-2)",
  border: "1px solid var(--border)",
  borderRadius: 8,
  fontSize: 12,
};

export function MasteryChart({ distribution }: { distribution: MasteryCountOut[] }) {
  const total = distribution.reduce((sum, d) => sum + d.count, 0);
  const data = MASTERY_LEVELS.map((m) => {
    const found = distribution.find((d) => d.level === m.level);
    return { level: m.shortLabel, label: m.label, count: found?.count ?? 0, color: m.colorVar };
  });

  const l5plus = data[5].count + data[6].count;
  const solvedAlone = data[3].count;
  const takeaway = total
    ? `${l5plus} of ${total} attempted problems are interview-ready (L5+); ${solvedAlone} solved independently but not yet reviewed that far.`
    : "";

  return (
    <ChartCard
      question="Where does my mastery actually sit?"
      takeaway={takeaway}
      isEmpty={total === 0}
      emptyHint="Rate a problem on the Today view and its mastery level shows up here."
    >
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
          <XAxis dataKey="level" tick={{ fill: "var(--text-faint)", fontSize: 11 }} axisLine={{ stroke: "var(--border)" }} tickLine={false} />
          <YAxis allowDecimals={false} tick={{ fill: "var(--text-faint)", fontSize: 11 }} axisLine={false} tickLine={false} width={28} />
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            labelFormatter={(_, payload) => payload?.[0]?.payload?.label ?? ""}
            formatter={(value) => [`${value} problems`, ""]}
            cursor={{ fill: "var(--surface-2)" }}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]} maxBarSize={36}>
            {data.map((d) => (
              <Cell key={d.level} fill={d.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
