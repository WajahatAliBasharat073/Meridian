"use client";

import { useState } from "react";
import {
  Camera,
  LayoutDashboard,
  Landmark,
  PiggyBank,
  Receipt,
  Target,
} from "lucide-react";
import { AccountsPanel } from "@/components/finance/AccountsPanel";
import { BudgetsPanel } from "@/components/finance/BudgetsPanel";
import { CategoryBreakdownChart } from "@/components/finance/CategoryBreakdownChart";
import { GoalsPanel } from "@/components/finance/GoalsPanel";
import { InsightsCard } from "@/components/finance/InsightsCard";
import { NetWorthTrendChart } from "@/components/finance/NetWorthTrendChart";
import { TransactionsPanel } from "@/components/finance/TransactionsPanel";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { QueryError } from "@/components/ui/query-state";
import { Skeleton } from "@/components/ui/skeleton";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { useFinanceDashboard, useTakeNetWorthSnapshot } from "@/hooks/useFinance";
import { formatMoney } from "@/lib/money";

type FinanceTab = "overview" | "accounts" | "transactions" | "budgets" | "goals";

const TABS: { id: FinanceTab; label: string; icon: typeof LayoutDashboard }[] = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "accounts", label: "Accounts", icon: Landmark },
  { id: "transactions", label: "Transactions", icon: Receipt },
  { id: "budgets", label: "Budgets", icon: PiggyBank },
  { id: "goals", label: "Goals", icon: Target },
];

export default function FinancePage() {
  const [tab, setTab] = useState<FinanceTab>("overview");
  const { data, isLoading, isError, error, refetch } = useFinanceDashboard();
  const takeSnapshot = useTakeNetWorthSnapshot();

  return (
    <PageContainer width="wide">
      <PageHeader
        eyebrow="Money"
        title="Finance"
        description="Income, expenses, budgets, and savings goals — manual-entry, privacy-first."
        action={
          <Button
            variant="secondary"
            size="md"
            onClick={() => takeSnapshot.mutate()}
            disabled={takeSnapshot.isPending}
            className="gap-1.5"
          >
            <Camera size={15} />
            {takeSnapshot.isPending ? "Saving…" : "Snapshot Net Worth"}
          </Button>
        }
      />

      <div className="flex items-center gap-1.5 p-1 rounded-xl bg-surface-2 border border-border mb-6 overflow-x-auto">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap ${
              tab === id
                ? "bg-surface text-text shadow-xs border border-border"
                : "text-text-muted hover:text-text"
            }`}
          >
            <Icon size={14} /> {label}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <>
          {isLoading && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {Array.from({ length: 4 }).map((_, i) => (
                  <Skeleton key={i} className="h-24" />
                ))}
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <Skeleton className="h-80" />
                <Skeleton className="h-80" />
              </div>
            </div>
          )}

          {isError && (
            <QueryError error={error} onRetry={() => refetch()} fallback="Couldn't load your finances." />
          )}

          {data && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <KpiCard value={formatMoney(data.income)} label="Income this month" />
                <KpiCard value={formatMoney(data.expenses)} label="Expenses this month" />
                <KpiCard
                  value={formatMoney(data.savings)}
                  label="Savings this month"
                  accent={data.savings >= 0 ? "var(--status-done)" : "var(--danger)"}
                />
                <KpiCard
                  value={data.savings_rate_pct != null ? `${data.savings_rate_pct}%` : "—"}
                  label="Savings rate"
                />
              </div>

              <InsightsCard insights={data.insights} />

              <div className="grid md:grid-cols-2 gap-4">
                <NetWorthTrendChart trend={data.net_worth_trend} />
                <CategoryBreakdownChart breakdown={data.category_breakdown} />
              </div>

              {data.upcoming_commitments.length > 0 && (
                <Card className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-text">
                      Upcoming commitments (next 30 days)
                    </h3>
                    <span className="text-xs font-mono tabular-nums text-text-muted">
                      {formatMoney(data.upcoming_total)} total
                    </span>
                  </div>
                  <ul className="space-y-2">
                    {data.upcoming_commitments.map((r) => (
                      <li key={r.id} className="flex items-center justify-between text-sm">
                        <span className="text-text-muted">
                          {r.description}{" "}
                          <span className="text-text-faint text-xs">· due {r.next_due_date}</span>
                        </span>
                        <span className="font-mono tabular-nums text-text">
                          {formatMoney(r.amount, r.currency)}
                        </span>
                      </li>
                    ))}
                  </ul>
                </Card>
              )}

              {data.net_worth == null && (
                <Card className="p-6 text-center border-dashed">
                  <p className="text-sm text-text-muted">
                    No net-worth snapshot yet — add your accounts, then click &ldquo;Snapshot Net
                    Worth&rdquo; above to
                    start the trend.
                  </p>
                </Card>
              )}
            </div>
          )}
        </>
      )}

      {tab === "accounts" && <AccountsPanel />}
      {tab === "transactions" && <TransactionsPanel />}
      {tab === "budgets" && <BudgetsPanel />}
      {tab === "goals" && <GoalsPanel />}
    </PageContainer>
  );
}
