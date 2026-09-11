"use client";

import { useState } from "react";
import { PiggyBank, Plus, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { QueryError } from "@/components/ui/query-state";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useDeleteFinanceBudget,
  useFinanceBudgets,
  useFinanceCategories,
  useUpsertFinanceBudget,
} from "@/hooks/useFinance";
import { formatMoney } from "@/lib/money";

export function BudgetsPanel() {
  const { data: budgets, isLoading, isError, error, refetch } = useFinanceBudgets();
  const { data: categories } = useFinanceCategories();
  const upsertBudget = useUpsertFinanceBudget();
  const deleteBudget = useDeleteFinanceBudget();

  const [adding, setAdding] = useState(false);
  const [categoryId, setCategoryId] = useState<number | "">("");
  const [monthlyAmount, setMonthlyAmount] = useState("");

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-16" />
        ))}
      </div>
    );
  }

  if (isError) {
    return <QueryError error={error} onRetry={() => refetch()} fallback="Couldn't load your budgets." />;
  }

  const rows = budgets ?? [];
  const budgetedCategoryIds = new Set(rows.map((b) => b.category_id));
  const availableCategories = (categories ?? []).filter(
    (c) => c.kind === "expense" && !budgetedCategoryIds.has(c.id)
  );

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (categoryId === "" || !monthlyAmount) return;
    upsertBudget.mutate(
      { category_id: categoryId, monthly_amount: Number(monthlyAmount) },
      {
        onSuccess: () => {
          setCategoryId("");
          setMonthlyAmount("");
          setAdding(false);
        },
      }
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        {!adding && availableCategories.length > 0 && (
          <Button variant="primary" size="md" onClick={() => setAdding(true)} className="gap-1.5">
            <Plus size={15} /> Set a Budget
          </Button>
        )}
      </div>

      {adding && (
        <Card className="p-5 border-accent/40 bg-gradient-to-b from-surface to-surface-2">
          <form onSubmit={handleCreate} className="space-y-3">
            <h3 className="text-sm font-semibold text-text">New Monthly Budget</h3>
            <div className="grid sm:grid-cols-2 gap-2">
              <Select
                value={categoryId}
                onChange={(e) => setCategoryId(e.target.value ? Number(e.target.value) : "")}
                required
              >
                <option value="">Category…</option>
                {availableCategories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </Select>
              <Input
                type="number"
                placeholder="Monthly amount"
                value={monthlyAmount}
                onChange={(e) => setMonthlyAmount(e.target.value)}
                required
              />
            </div>
            <div className="flex justify-end gap-2 pt-1">
              <Button type="button" variant="ghost" size="sm" onClick={() => setAdding(false)}>
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="sm"
                disabled={upsertBudget.isPending || categoryId === "" || !monthlyAmount}
              >
                {upsertBudget.isPending ? "Saving…" : "Set Budget"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {rows.length === 0 && !adding ? (
        <EmptyState
          icon={PiggyBank}
          title="No budgets set"
          description="Set a monthly limit per category to see planned-vs-actual spending and overspending alerts."
          action={
            <Button variant="primary" size="md" onClick={() => setAdding(true)}>
              Set your first budget
            </Button>
          }
        />
      ) : (
        <ul className="space-y-2">
          {rows.map((b) => (
            <li key={b.id}>
              <Card className="p-4">
                <div className="flex items-center justify-between gap-3 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-text">{b.category_name}</span>
                    {b.over_budget && <Badge color="var(--danger)">Over budget</Badge>}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono tabular-nums text-text-muted">
                      {formatMoney(b.actual)} / {formatMoney(b.planned)}
                    </span>
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label="Delete budget"
                      onClick={() => deleteBudget.mutate(b.id)}
                    >
                      <Trash2 size={15} className="text-text-faint" />
                    </Button>
                  </div>
                </div>
                <div className="h-2 rounded-full bg-surface-2 overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${Math.min(b.utilization_pct, 100)}%`,
                      backgroundColor: b.over_budget ? "var(--danger)" : "var(--status-done)",
                    }}
                  />
                </div>
                <p className="text-[11px] text-text-faint mt-1.5">
                  {b.over_budget
                    ? `${formatMoney(Math.abs(b.remaining))} over this month`
                    : `${formatMoney(b.remaining)} remaining this month`}
                </p>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
