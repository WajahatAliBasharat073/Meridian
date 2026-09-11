"use client";

import { useState } from "react";
import { Plus, Receipt, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { QueryError } from "@/components/ui/query-state";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useFinanceAccounts, useFinanceCategories, useFinanceGoals } from "@/hooks/useFinance";
import {
  useCreateFinanceTransaction,
  useDeleteFinanceTransaction,
  useFinanceTransactions,
} from "@/hooks/useFinance";
import { formatMoney } from "@/lib/money";
import type { TransactionStatus, TransactionType } from "@/lib/types";

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export function TransactionsPanel() {
  const { data: accounts } = useFinanceAccounts();
  const { data: categories } = useFinanceCategories();
  const { data: goals } = useFinanceGoals();
  const { data: transactions, isLoading, isError, error, refetch } = useFinanceTransactions();
  const createTransaction = useCreateFinanceTransaction();
  const deleteTransaction = useDeleteFinanceTransaction();

  const [adding, setAdding] = useState(false);
  const [type, setType] = useState<TransactionType>("expense");
  const [accountId, setAccountId] = useState<number | "">("");
  const [categoryId, setCategoryId] = useState<number | "">("");
  const [amount, setAmount] = useState("");
  const [occurredOn, setOccurredOn] = useState(todayIso());
  const [status, setStatus] = useState<TransactionStatus>("actual");
  const [description, setDescription] = useState("");
  const [goalId, setGoalId] = useState<number | "">("");
  const activeGoals = (goals ?? []).filter((g) => g.status === "active");

  const accountById = new Map((accounts ?? []).map((a) => [a.id, a]));
  const categoryById = new Map((categories ?? []).map((c) => [c.id, c]));
  const relevantCategories = (categories ?? []).filter((c) => c.kind === type);

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-14" />
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <QueryError error={error} onRetry={() => refetch()} fallback="Couldn't load your transactions." />
    );
  }

  const rows = transactions ?? [];
  const noAccounts = (accounts ?? []).length === 0;

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (accountId === "" || categoryId === "" || !amount) return;
    createTransaction.mutate(
      {
        account_id: accountId,
        category_id: categoryId,
        type,
        amount: Number(amount),
        occurred_on: occurredOn,
        status,
        description: description.trim() || undefined,
        goal_id: goalId === "" ? undefined : goalId,
      },
      {
        onSuccess: () => {
          setAmount("");
          setDescription("");
          setGoalId("");
          setAdding(false);
        },
      }
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        {!adding && !noAccounts && (
          <Button variant="primary" size="md" onClick={() => setAdding(true)} className="gap-1.5">
            <Plus size={15} /> Add Transaction
          </Button>
        )}
      </div>

      {noAccounts && (
        <EmptyState
          icon={Receipt}
          title="Add an account first"
          description="A transaction always belongs to an account -- create one on the Accounts tab, then come back here."
        />
      )}

      {adding && (
        <Card className="p-5 border-accent/40 bg-gradient-to-b from-surface to-surface-2">
          <form onSubmit={handleCreate} className="space-y-3">
            <h3 className="text-sm font-semibold text-text">New Transaction</h3>
            <div className="grid sm:grid-cols-2 gap-2">
              <Select
                value={type}
                onChange={(e) => {
                  setType(e.target.value as TransactionType);
                  setCategoryId("");
                }}
              >
                <option value="expense">Expense</option>
                <option value="income">Income</option>
              </Select>
              <Select
                value={status}
                onChange={(e) => setStatus(e.target.value as TransactionStatus)}
              >
                <option value="actual">Actual (already happened)</option>
                <option value="planned">Planned (expected)</option>
              </Select>
              <Select
                value={accountId}
                onChange={(e) => setAccountId(e.target.value ? Number(e.target.value) : "")}
                required
              >
                <option value="">Account…</option>
                {(accounts ?? []).map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name}
                  </option>
                ))}
              </Select>
              <Select
                value={categoryId}
                onChange={(e) => setCategoryId(e.target.value ? Number(e.target.value) : "")}
                required
              >
                <option value="">Category…</option>
                {relevantCategories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </Select>
              <Input
                type="number"
                placeholder="Amount"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
              />
              <Input
                type="date"
                value={occurredOn}
                onChange={(e) => setOccurredOn(e.target.value)}
                required
              />
            </div>
            <Input
              placeholder="Description (optional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            {activeGoals.length > 0 && (
              <Select
                value={goalId}
                onChange={(e) => setGoalId(e.target.value ? Number(e.target.value) : "")}
              >
                <option value="">Not a goal contribution</option>
                {activeGoals.map((g) => (
                  <option key={g.id} value={g.id}>
                    Counts toward: {g.title}
                  </option>
                ))}
              </Select>
            )}
            <div className="flex justify-end gap-2 pt-1">
              <Button type="button" variant="ghost" size="sm" onClick={() => setAdding(false)}>
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="sm"
                disabled={createTransaction.isPending || accountId === "" || categoryId === "" || !amount}
              >
                {createTransaction.isPending ? "Saving…" : "Add Transaction"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {rows.length === 0 && !adding && !noAccounts ? (
        <EmptyState
          icon={Receipt}
          title="No transactions yet"
          description="Record an income or expense to start seeing real numbers in your dashboard."
          action={
            <Button variant="primary" size="md" onClick={() => setAdding(true)}>
              Add your first transaction
            </Button>
          }
        />
      ) : (
        <ul className="space-y-2">
          {rows.map((t) => (
            <li key={t.id}>
              <Card className="p-4 flex items-center justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge color={categoryById.get(t.category_id) ? "var(--accent)" : "var(--text-faint)"}>
                      {categoryById.get(t.category_id)?.name ?? "Unknown"}
                    </Badge>
                    <span className="text-xs text-text-faint">
                      {accountById.get(t.account_id)?.name ?? "Unknown account"}
                    </span>
                    {t.status === "planned" && <Badge color="var(--warning)">Planned</Badge>}
                    {t.goal_id != null && (
                      <Badge color="var(--accent-strong)">
                        Goal: {(goals ?? []).find((g) => g.id === t.goal_id)?.title ?? "—"}
                      </Badge>
                    )}
                    <span className="text-[11px] text-text-faint tabular-nums ml-auto sm:ml-0">
                      {t.occurred_on}
                    </span>
                  </div>
                  {t.description && (
                    <p className="text-xs text-text-muted mt-1 truncate">{t.description}</p>
                  )}
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span
                    className="text-sm font-mono tabular-nums"
                    style={{ color: t.type === "income" ? "var(--status-done)" : "var(--text)" }}
                  >
                    {t.type === "income" ? "+" : "-"}
                    {formatMoney(t.amount, t.currency)}
                  </span>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Delete transaction"
                    onClick={() => deleteTransaction.mutate(t.id)}
                  >
                    <Trash2 size={15} className="text-text-faint" />
                  </Button>
                </div>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
