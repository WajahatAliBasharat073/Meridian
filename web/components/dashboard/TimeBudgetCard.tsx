"use client";

import { useState } from "react";
import { Plus, X } from "lucide-react";
import { useTimeBudgets, useUpsertTimeBudget, useDeleteTimeBudget } from "@/hooks/useTimeBudgets";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

export function TimeBudgetCard() {
  const { data, isLoading } = useTimeBudgets();
  const upsert = useUpsertTimeBudget();
  const del = useDeleteTimeBudget();
  const [adding, setAdding] = useState(false);
  const [category, setCategory] = useState("");
  const [hours, setHours] = useState("5");

  if (isLoading) return <Card className="p-4 h-40 animate-pulse" />;

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-text">Weekly time budget</h2>
        <Button variant="ghost" size="sm" onClick={() => setAdding((a) => !a)}>
          <Plus size={14} /> {adding ? "Cancel" : "Add"}
        </Button>
      </div>

      {adding && (
        <form
          className="flex gap-2 mb-3"
          onSubmit={(e) => {
            e.preventDefault();
            if (!category.trim() || Number(hours) <= 0) return;
            upsert.mutate(
              { category: category.trim(), minutes_per_week: Math.round(Number(hours) * 60) },
              { onSuccess: () => setAdding(false) }
            );
            setCategory("");
          }}
        >
          <input
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="Category (e.g. Job)"
            className="h-9 flex-1 rounded-lg border border-border bg-surface-2 px-2 text-sm text-text"
          />
          <input
            type="number"
            min={1}
            value={hours}
            onChange={(e) => setHours(e.target.value)}
            className="h-9 w-16 rounded-lg border border-border bg-surface-2 px-2 text-sm text-text tabular-nums"
          />
          <span className="text-xs text-text-faint self-center">hrs/wk</span>
          <Button type="submit" variant="primary" size="sm" disabled={upsert.isPending}>
            Save
          </Button>
        </form>
      )}

      {!data || data.length === 0 ? (
        <p className="text-xs text-text-faint">
          No time budgets set — add one to compare planned vs. actual hours per category.
        </p>
      ) : (
        <div className="space-y-2.5">
          {data.map((b) => {
            const pct = Math.min(100, Math.round((b.actual_minutes_this_week / b.minutes_per_week) * 100));
            const over = b.actual_minutes_this_week > b.minutes_per_week;
            return (
              <div key={b.id} className="group">
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-text-muted">{b.category}</span>
                  <span className="flex items-center gap-2">
                    <span className="text-text-faint tabular-nums">
                      {(b.actual_minutes_this_week / 60).toFixed(1)}h / {(b.minutes_per_week / 60).toFixed(1)}h
                    </span>
                    <button
                      type="button"
                      onClick={() => del.mutate(b.id)}
                      aria-label={`Remove ${b.category} budget`}
                      className="text-text-faint hover:text-danger opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X size={12} />
                    </button>
                  </span>
                </div>
                <div className="h-2 rounded-full bg-surface-2 overflow-hidden">
                  <div
                    className={cn("h-full rounded-full", over ? "bg-danger" : "bg-accent")}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
