"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { Card } from "@/components/ui/card";
import { NoDataYet } from "@/components/analytics/NoDataYet";
import { formatCountdown } from "@/lib/time";

export interface LearningPoint {
  date: string;
  masteryPoints: number;
  studyMinutes: number;
  solvedCount: number;
}

/** Mastery progression over time, plotted only from real recorded points.
 *
 * This used to carry a hardcoded eight-week climb (W1..W8, mastery 24 →
 * 142) plus three fixed headline stats ("+24 pts", "85h 10m", "63 items")
 * and a range switcher that filtered nothing — so every account, including
 * one created today, saw the same two months of progress. The stats are now
 * derived from the points passed in, and the switcher is gone until there
 * is a real series to slice. */
export function LearningCurve({ data = [] }: { data?: LearningPoint[] }) {
  const first = data[0];
  const last = data[data.length - 1];

  // Velocity needs two points to be a change rather than a level.
  const masteryGain = first && last && data.length > 1 ? last.masteryPoints - first.masteryPoints : null;
  const studyMinutes = data.reduce((acc, d) => acc + d.studyMinutes, 0);
  const solvedTotal = last?.solvedCount ?? null;

  return (
    <Card className="p-5 space-y-4">
      <div>
        <h3 className="text-sm font-semibold text-text">Overall Learning Curve</h3>
        <p className="text-xs text-text-muted">
          Progression across ML concepts, deep learning, DSA patterns, and system design.
        </p>
      </div>

      {data.length === 0 ? (
        <NoDataYet
          what="mastery history"
          fills="Log attempts on problems and concepts and this becomes your real curve — mastery gained, hours studied, and how many items have moved up a level."
        />
      ) : (
        <>
          <div className="grid grid-cols-3 gap-3 pt-1">
            <Stat
              label="Mastery Gain"
              value={masteryGain != null ? `${masteryGain >= 0 ? "+" : ""}${masteryGain} pts` : "—"}
              valueClass="text-accent-strong"
            />
            <Stat label="Study Time" value={formatCountdown(studyMinutes)} valueClass="text-text" />
            <Stat
              label="Items Solved"
              value={solvedTotal != null ? `${solvedTotal}` : "—"}
              valueClass="text-status-done"
            />
          </div>

          <div className="h-48 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="learningGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--accent)" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="var(--accent)" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fill: "var(--text-faint)", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: "var(--text-faint)", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (!active || !payload?.length) return null;
                    const d = payload[0].payload as LearningPoint;
                    return (
                      <div className="rounded-lg border border-border bg-surface p-2.5 text-xs shadow-md">
                        <p className="font-semibold text-text">{d.date}</p>
                        <p className="text-accent-strong font-mono">Mastery Index: {d.masteryPoints}</p>
                        <p className="text-text-muted font-mono">
                          {formatCountdown(d.studyMinutes)} study
                        </p>
                        <p className="text-status-done font-mono">
                          {d.solvedCount} problems/concepts
                        </p>
                      </div>
                    );
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="masteryPoints"
                  stroke="var(--accent-strong)"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#learningGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </Card>
  );
}

function Stat({
  label,
  value,
  valueClass,
}: {
  label: string;
  value: string;
  valueClass: string;
}) {
  return (
    <div className="min-w-0">
      <p className="text-xs text-text-faint truncate">{label}</p>
      <p className={`text-xl font-bold tabular-nums font-mono mt-0.5 ${valueClass}`}>{value}</p>
    </div>
  );
}
