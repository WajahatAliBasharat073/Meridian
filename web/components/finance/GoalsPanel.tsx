"use client";

import { useState } from "react";
import { CheckCircle2, Plus, Target, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { QueryError } from "@/components/ui/query-state";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useCreateFinanceGoal,
  useDeleteFinanceGoal,
  useFinanceGoals,
  useUpdateFinanceGoal,
} from "@/hooks/useFinance";
import { formatMoney } from "@/lib/money";
import type { FinanceGoalCategory } from "@/lib/types";

const GOAL_CATEGORIES: { value: FinanceGoalCategory; label: string }[] = [
  { value: "emergency_fund", label: "Emergency fund" },
  { value: "short_term", label: "Short-term goal" },
  { value: "long_term", label: "Long-term goal" },
  { value: "custom", label: "Custom" },
];

export function GoalsPanel() {
  const { data: goals, isLoading, isError, error, refetch } = useFinanceGoals();
  const createGoal = useCreateFinanceGoal();
  const updateGoal = useUpdateFinanceGoal();
  const deleteGoal = useDeleteFinanceGoal();

  const [adding, setAdding] = useState(false);
  const [title, setTitle] = useState("");
  const [targetAmount, setTargetAmount] = useState("");
  const [targetDate, setTargetDate] = useState("");
  const [category, setCategory] = useState<FinanceGoalCategory>("custom");

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 2 }).map((_, i) => (
          <Skeleton key={i} className="h-24" />
        ))}
      </div>
    );
  }

  if (isError) {
    return <QueryError error={error} onRetry={() => refetch()} fallback="Couldn't load your goals." />;
  }

  const rows = goals ?? [];

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !targetAmount) return;
    createGoal.mutate(
      {
        title: title.trim(),
        target_amount: Number(targetAmount),
        target_date: targetDate || undefined,
        category,
      },
      {
        onSuccess: () => {
          setTitle("");
          setTargetAmount("");
          setTargetDate("");
          setAdding(false);
        },
      }
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        {!adding && (
          <Button variant="primary" size="md" onClick={() => setAdding(true)} className="gap-1.5">
            <Plus size={15} /> Add Goal
          </Button>
        )}
      </div>

      {adding && (
        <Card className="p-5 border-accent/40 bg-gradient-to-b from-surface to-surface-2">
          <form onSubmit={handleCreate} className="space-y-3">
            <h3 className="text-sm font-semibold text-text">New Savings Goal</h3>
            <Input
              placeholder="e.g. Emergency fund, New laptop"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
            <div className="grid sm:grid-cols-3 gap-2">
              <Input
                type="number"
                placeholder="Target amount"
                value={targetAmount}
                onChange={(e) => setTargetAmount(e.target.value)}
                required
              />
              <Input
                type="date"
                placeholder="Target date (optional)"
                value={targetDate}
                onChange={(e) => setTargetDate(e.target.value)}
              />
              <Select value={category} onChange={(e) => setCategory(e.target.value as FinanceGoalCategory)}>
                {GOAL_CATEGORIES.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </Select>
            </div>
            <div className="flex justify-end gap-2 pt-1">
              <Button type="button" variant="ghost" size="sm" onClick={() => setAdding(false)}>
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="sm"
                disabled={createGoal.isPending || !title.trim() || !targetAmount}
              >
                {createGoal.isPending ? "Saving…" : "Add Goal"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {rows.length === 0 && !adding ? (
        <EmptyState
          icon={Target}
          title="No savings goals yet"
          description="Set a target amount and deadline, then tag transactions to it from the Transactions tab to track real progress."
          action={
            <Button variant="primary" size="md" onClick={() => setAdding(true)}>
              Add your first goal
            </Button>
          }
        />
      ) : (
        <ul className="space-y-2">
          {rows.map((g) => (
            <li key={g.id}>
              <Card className="p-4">
                <div className="flex items-center justify-between gap-3 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-text">{g.title}</span>
                    <Badge color="var(--accent)">
                      {GOAL_CATEGORIES.find((c) => c.value === g.category)?.label ?? g.category}
                    </Badge>
                    {g.status !== "active" && (
                      <Badge color={g.status === "completed" ? "var(--status-done)" : "var(--text-faint)"}>
                        {g.status === "completed" ? "Completed" : "Abandoned"}
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-1">
                    {g.status === "active" && (
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label="Mark goal complete"
                        onClick={() => updateGoal.mutate({ goalId: g.id, input: { status: "completed" } })}
                      >
                        <CheckCircle2 size={15} className="text-text-faint" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label="Delete goal"
                      onClick={() => deleteGoal.mutate(g.id)}
                    >
                      <Trash2 size={15} className="text-text-faint" />
                    </Button>
                  </div>
                </div>
                <div className="h-2 rounded-full bg-surface-2 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-accent"
                    style={{ width: `${Math.min(g.progress_pct, 100)}%` }}
                  />
                </div>
                <div className="flex items-center justify-between mt-1.5">
                  <p className="text-[11px] text-text-faint">
                    {formatMoney(g.current_amount, g.currency)} of {formatMoney(g.target_amount, g.currency)} (
                    {g.progress_pct.toFixed(0)}%)
                  </p>
                  {g.required_monthly_contribution != null && (
                    <p className="text-[11px] text-text-faint">
                      Save {formatMoney(g.required_monthly_contribution, g.currency)}/mo to hit{" "}
                      {g.target_date}
                    </p>
                  )}
                </div>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
