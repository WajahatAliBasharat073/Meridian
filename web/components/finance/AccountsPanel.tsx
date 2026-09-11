"use client";

import { useState } from "react";
import { Landmark, Plus, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { QueryError } from "@/components/ui/query-state";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useCreateFinanceAccount, useDeleteFinanceAccount, useFinanceAccounts } from "@/hooks/useFinance";
import { formatMoney } from "@/lib/money";
import type { AccountType } from "@/lib/types";

const ACCOUNT_TYPES: { value: AccountType; label: string }[] = [
  { value: "cash", label: "Cash" },
  { value: "bank", label: "Bank" },
  { value: "savings", label: "Savings" },
  { value: "investment", label: "Investment" },
  { value: "receivable", label: "Receivable" },
  { value: "credit", label: "Credit card" },
  { value: "loan", label: "Loan" },
  { value: "other", label: "Other" },
];

export function AccountsPanel() {
  const { data: accounts, isLoading, isError, error, refetch } = useFinanceAccounts();
  const createAccount = useCreateFinanceAccount();
  const deleteAccount = useDeleteFinanceAccount();
  const [adding, setAdding] = useState(false);
  const [name, setName] = useState("");
  const [accountType, setAccountType] = useState<AccountType>("bank");
  const [openingBalance, setOpeningBalance] = useState("0");

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
    return <QueryError error={error} onRetry={() => refetch()} fallback="Couldn't load your accounts." />;
  }

  const rows = accounts ?? [];

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    createAccount.mutate(
      { name: name.trim(), account_type: accountType, opening_balance: Number(openingBalance) || 0 },
      {
        onSuccess: () => {
          setName("");
          setOpeningBalance("0");
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
            <Plus size={15} /> Add Account
          </Button>
        )}
      </div>

      {adding && (
        <Card className="p-5 border-accent/40 bg-gradient-to-b from-surface to-surface-2">
          <form onSubmit={handleCreate} className="space-y-3">
            <h3 className="text-sm font-semibold text-text">New Account</h3>
            <div className="grid sm:grid-cols-3 gap-2">
              <Input
                placeholder="e.g. Everyday Checking"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
              <Select
                value={accountType}
                onChange={(e) => setAccountType(e.target.value as AccountType)}
              >
                {ACCOUNT_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </Select>
              <Input
                type="number"
                placeholder="Opening balance"
                value={openingBalance}
                onChange={(e) => setOpeningBalance(e.target.value)}
              />
            </div>
            <div className="flex justify-end gap-2 pt-1">
              <Button type="button" variant="ghost" size="sm" onClick={() => setAdding(false)}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" size="sm" disabled={createAccount.isPending || !name.trim()}>
                {createAccount.isPending ? "Saving…" : "Add Account"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {rows.length === 0 && !adding ? (
        <EmptyState
          icon={Landmark}
          title="No accounts yet"
          description="Add a bank account, cash wallet, or credit card to start tracking real balances."
          action={
            <Button variant="primary" size="md" onClick={() => setAdding(true)}>
              Add your first account
            </Button>
          }
        />
      ) : (
        <ul className="space-y-2">
          {rows.map((a) => (
            <li key={a.id}>
              <Card className="p-4 flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-text">{a.name}</span>
                    <Badge color={a.is_liability ? "var(--danger)" : "var(--status-done)"}>
                      {ACCOUNT_TYPES.find((t) => t.value === a.account_type)?.label ?? a.account_type}
                    </Badge>
                    {!a.is_active && <Badge color="var(--text-faint)">Inactive</Badge>}
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-sm font-mono tabular-nums text-text">
                    {formatMoney(a.current_balance, a.currency)}
                  </span>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Delete account"
                    onClick={() => deleteAccount.mutate(a.id)}
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
