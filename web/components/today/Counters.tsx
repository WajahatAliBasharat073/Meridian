import type { TodayCounters } from "@/lib/types";

function Counter({ value, label, accent }: { value: string; label: string; accent?: string }) {
  return (
    <div className="flex-1 text-center py-3">
      <div className="text-2xl font-semibold tabular-nums" style={{ color: accent ?? "var(--text)" }}>
        {value}
      </div>
      <div className="text-[11px] uppercase tracking-wide text-text-faint mt-0.5">{label}</div>
    </div>
  );
}

export function Counters({ counters }: { counters: TodayCounters }) {
  return (
    <div className="rounded-xl border border-border bg-surface flex divide-x divide-border">
      <Counter
        value={String(counters.overdue_reviews)}
        label="Overdue reviews"
        accent={counters.overdue_reviews > 0 ? "var(--danger)" : undefined}
      />
      <Counter value={String(counters.blocks_remaining)} label="Blocks left" />
      <Counter
        value={counters.readiness_pct != null ? `${counters.readiness_pct}%` : "—"}
        label="Readiness"
      />
    </div>
  );
}
