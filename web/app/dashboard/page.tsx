"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { useDashboardSummary } from "@/hooks/useDashboardSummary";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { MasteryChart } from "@/components/dashboard/MasteryChart";
import { PatternChart } from "@/components/dashboard/PatternChart";
import { AttemptsTrendChart } from "@/components/dashboard/AttemptsTrendChart";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiError } from "@/lib/api";

export default function DashboardPage() {
  const { data, isLoading, isError, error, refetch } = useDashboardSummary();
  const { email } = useCurrentUser();
  const name = email ? email.split("@")[0] : null;

  const isAuthError = error instanceof ApiError && error.status === 401;
  const isNewAccount = data ? data.attempted_count === 0 && data.reviews_due_count === 0 && data.reviews_overdue_count === 0 : false;

  return (
    <AppShell>
      <main className="mx-auto max-w-5xl px-4 py-6 pb-16">
        <header className="mb-6">
          <p className="text-xs font-medium uppercase tracking-wide text-text-faint">Dashboard</p>
          <h1 className="text-2xl font-semibold text-text mt-1">
            Welcome back{name ? `, ${name}` : ""}
          </h1>
          <p className="text-sm text-text-muted mt-1">
            An overview of where your interview prep stands right now.
          </p>
        </header>

        {isLoading && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-20" />
            ))}
          </div>
        )}

        {isError && (
          <div className="space-y-3">
            <Alert variant="error">
              {isAuthError ? "Your session expired." : "Couldn't load your dashboard."}
            </Alert>
            {isAuthError ? (
              <a href="/login">
                <Button variant="primary" size="md">Sign in again</Button>
              </a>
            ) : (
              <Button variant="secondary" size="md" onClick={() => refetch()}>Retry</Button>
            )}
          </div>
        )}

        {data && (
          <div className="space-y-6">
            {isNewAccount && (
              <Alert variant="info">
                Your account is new — these numbers will fill in as you rate problems on
                Today. There&apos;s nothing broken here, just nothing recorded yet.
              </Alert>
            )}

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <KpiCard
                value={data.readiness_pct != null ? `${data.readiness_pct}%` : "—"}
                label="Readiness (L5+ / total)"
                accent="var(--accent-strong)"
              />
              <KpiCard
                value={`${data.attempted_count}/${data.total_problems}`}
                label="Problems attempted"
              />
              <KpiCard
                value={String(data.reviews_due_count)}
                label="Reviews due today"
              />
              <KpiCard
                value={String(data.reviews_overdue_count)}
                label="Reviews overdue"
                accent={data.reviews_overdue_count > 0 ? "var(--danger)" : undefined}
              />
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <MasteryChart distribution={data.mastery_distribution} />
              <PatternChart coverage={data.pattern_coverage} />
            </div>

            <AttemptsTrendChart days={data.attempts_by_day} />

            <Link href="/today">
              <Button variant="secondary" size="lg" className="w-full justify-between">
                Go to Today — see what to do right now
                <ArrowRight size={16} />
              </Button>
            </Link>
          </div>
        )}
      </main>
    </AppShell>
  );
}
