"use client";

import { useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { NoDataYet } from "@/components/analytics/NoDataYet";
import { formatCountdown } from "@/lib/time";

export interface HeatmapDay {
  date: string; // "YYYY-MM-DD"
  minutes: number;
}

/** GitHub-style consistency grid.
 *
 * Takes real completed-minutes-per-day and nothing else. It previously
 * synthesized a full year from `(date * 37 + month * 19) % 100` and
 * reported the result as "313 active days · 820h logged" — indistinguishable
 * on screen from genuine history, on an account only days old. Any day
 * without a real row is simply empty here. */
export function ConsistencyHeatmap({ days }: { days?: HeatmapDay[] }) {
  const [hoveredDay, setHoveredDay] = useState<HeatmapDay | null>(null);

  const byDate = useMemo(() => {
    const m = new Map<string, number>();
    for (const d of days ?? []) m.set(d.date, d.minutes);
    return m;
  }, [days]);

  // Always render the last 52 weeks of *real* calendar dates; a date with
  // no recorded activity stays at level 0 rather than being invented.
  const weeks = useMemo(() => {
    const today = new Date();
    const cells: HeatmapDay[] = [];
    for (let i = 363; i >= 0; i--) {
      const d = new Date(today);
      d.setDate(today.getDate() - i);
      const dateStr = d.toISOString().slice(0, 10);
      cells.push({ date: dateStr, minutes: byDate.get(dateStr) ?? 0 });
    }
    const cols: HeatmapDay[][] = [];
    for (let i = 0; i < cells.length; i += 7) cols.push(cells.slice(i, i + 7));
    return cols;
  }, [byDate]);

  const flat = weeks.flat();
  const totalMinutes = flat.reduce((acc, d) => acc + d.minutes, 0);
  const activeDays = flat.filter((d) => d.minutes > 0).length;

  const levelFor = (minutes: number): 0 | 1 | 2 | 3 | 4 => {
    if (minutes >= 360) return 4;
    if (minutes >= 240) return 3;
    if (minutes >= 120) return 2;
    if (minutes > 0) return 1;
    return 0;
  };

  const getColor = (level: number) => {
    switch (level) {
      case 4:
        return "bg-[#4fae72]";
      case 3:
        return "bg-[#7ab55a]";
      case 2:
        return "bg-[#a4b93f]";
      case 1:
        return "bg-[#2d4d38]";
      default:
        return "bg-surface-2";
    }
  };

  return (
    <Card className="p-5 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="min-w-0">
          <h3 className="text-sm font-semibold text-text">Execution Consistency</h3>
          <p className="text-xs text-text-muted">
            Meaningful output only (Work, Learning, Research, Exercise, Routines).
          </p>
        </div>
        {activeDays > 0 && (
          <div className="flex items-center gap-4 text-xs shrink-0">
            <div>
              <span className="font-semibold text-text tabular-nums">{activeDays}</span>
              <span className="text-text-faint ml-1">active days</span>
            </div>
            <div>
              <span className="font-semibold text-text tabular-nums font-mono">
                {formatCountdown(totalMinutes)}
              </span>
              <span className="text-text-faint ml-1">logged</span>
            </div>
          </div>
        )}
      </div>

      {activeDays === 0 ? (
        <NoDataYet
          what="completed activity"
          fills="Each square fills in once you complete blocks on Today. One day of real work will show up here as one square."
        />
      ) : (
        <>
          <div className="overflow-x-auto pb-2">
            <div className="inline-flex gap-1">
              {weeks.map((week, wIdx) => (
                <div key={wIdx} className="flex flex-col gap-1">
                  {week.map((day) => (
                    <div
                      key={day.date}
                      onMouseEnter={() => setHoveredDay(day)}
                      onMouseLeave={() => setHoveredDay(null)}
                      className={`w-3 h-3 rounded-[3px] transition-colors cursor-pointer ${getColor(
                        levelFor(day.minutes)
                      )} hover:ring-2 hover:ring-accent-strong`}
                      title={`${day.date}: ${formatCountdown(day.minutes)}`}
                    />
                  ))}
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between text-[11px] text-text-faint">
            <span>
              {hoveredDay
                ? `${hoveredDay.date} · ${formatCountdown(hoveredDay.minutes)}`
                : "Hover any block to inspect daily volume"}
            </span>
            <span className="flex items-center gap-1">
              Less
              {[0, 1, 2, 3, 4].map((l) => (
                <span key={l} className={`w-2.5 h-2.5 rounded-[2px] ${getColor(l)}`} />
              ))}
              More
            </span>
          </div>
        </>
      )}
    </Card>
  );
}
