"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { useDashboardSummary } from "@/hooks/useDashboardSummary";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { LifeClock } from "@/components/dashboard/LifeClock";
import { TodayProgress } from "@/components/dashboard/TodayProgress";
import { DailyRecapCard } from "@/components/dashboard/DailyRecapCard";
import { QuestionCoverageCard } from "@/components/dashboard/QuestionCoverageCard";
import { TimeBudgetCard } from "@/components/dashboard/TimeBudgetCard";
import { WeeklyOverviewCard } from "@/components/dashboard/WeeklyOverviewCard";
import { MasteryChart } from "@/components/dashboard/MasteryChart";
import { PatternChart } from "@/components/dashboard/PatternChart";
import { AttemptsTrendChart } from "@/components/dashboard/AttemptsTrendChart";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { QueryError } from "@/components/ui/query-state";
import { Skeleton } from "@/components/ui/skeleton";

export default function DashboardPage() {
  const { data, isLoading, isError, error, refetch } = useDashboardSummary();
  const { email } = useCurrentUser();
  const name = email ? email.split("@")[0] : null;

  const isNewAccount =
    data != null &&
    data.attempted_count === 0 &&
    data.reviews_due_count === 0 &&
    data.reviews_overdue_count === 0;

  return (
    <PageContainer width="wide">
      <PageHeader
        eyebrow="Overview"
        title={name ? `Welcome back, ${name}` : "Dashboard"}
        description="Your actual schedule — prep, work, prayer, recovery — from what you've logged. Nothing here is estimated."
        action={
          <div className="hidden sm:block">
            <LifeClock />
          </div>
        }
      />

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
        <QueryError
          error={error}
          onRetry={() => refetch()}
          fallback="Couldn't load your dashboard."
        />
      )}

      {data && (
        <div className="space-y-6">
          {isNewAccount && (
            <Alert variant="info">
              Your account is new — these numbers fill in as you rate problems on Today.
            </Alert>
          )}

          <div className="sm:hidden">
            <LifeClock />
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <TodayProgress />
            <DailyRecapCard />
          </div>

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
            <KpiCard value={String(data.reviews_due_count)} label="Reviews due today" />
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

          <div className="grid md:grid-cols-2 gap-4">
            <WeeklyOverviewCard />
            <TimeBudgetCard />
          </div>

          <QuestionCoverageCard />

          <AttemptsTrendChart days={data.attempts_by_day} />

          <Card className="p-4 sm:hidden">
            <p className="text-sm text-text-muted mb-3">Ready to execute the day?</p>
            <Link href="/today">
              <Button variant="primary" size="lg" className="w-full justify-between">
                Go to Today
                <ArrowRight size={16} />
              </Button>
            </Link>
          </Card>
        </div>
      )}
    </PageContainer>
  );
}
