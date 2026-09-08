"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  BarChart3,
  BrainCircuit,
  Clock,
  Cpu,
  LayoutDashboard,
  Target,
} from "lucide-react";
import { useDashboardSummary } from "@/hooks/useDashboardSummary";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useWeeklyReview } from "@/hooks/useWeeklyReview";
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
import { TimeCurve } from "@/components/analytics/TimeCurve";
import { PlannedVsActual } from "@/components/analytics/PlannedVsActual";
import { FocusAnalytics } from "@/components/analytics/FocusAnalytics";
import { ConsistencyHeatmap } from "@/components/analytics/ConsistencyHeatmap";
import { BehavioralDashboard } from "@/components/analytics/BehavioralDashboard";
import { LearningCurve } from "@/components/analytics/LearningCurve";

type InsightsTab = "overview" | "time_focus" | "learning" | "behavior";

export default function DashboardPage() {
  const { data, isLoading, isError, error, refetch } = useDashboardSummary();
  // Real category minutes for the time-allocation chart. Without this the
  // chart has no source at all and correctly renders its empty state — it
  // must never fall back to invented numbers.
  const { data: weekly } = useWeeklyReview();
  const { email } = useCurrentUser();
  const name = email ? email.split("@")[0] : null;
  const [activeTab, setActiveTab] = useState<InsightsTab>("overview");

  const isNewAccount =
    data != null &&
    data.attempted_count === 0 &&
    data.reviews_due_count === 0 &&
    data.reviews_overdue_count === 0;

  return (
    <PageContainer width="wide">
      <PageHeader
        eyebrow="Intelligence & Rollups"
        title={name ? `System Insights · ${name}` : "Insights"}
        description="Empirical analytics across your time allocation, focus velocity, learning curves, and behavioral patterns."
        action={
          <div className="hidden sm:block">
            <LifeClock />
          </div>
        }
      />

      {/* Navigation Tabs */}
      <div className="flex items-center gap-1.5 p-1 rounded-xl bg-surface-2 border border-border mb-6 overflow-x-auto">
        <button
          onClick={() => setActiveTab("overview")}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap ${
            activeTab === "overview"
              ? "bg-surface text-text shadow-xs border border-border"
              : "text-text-muted hover:text-text"
          }`}
        >
          <LayoutDashboard size={14} /> Overview
        </button>
        <button
          onClick={() => setActiveTab("time_focus")}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap ${
            activeTab === "time_focus"
              ? "bg-surface text-text shadow-xs border border-border"
              : "text-text-muted hover:text-text"
          }`}
        >
          <Clock size={14} /> Time & Focus
        </button>
        <button
          onClick={() => setActiveTab("learning")}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap ${
            activeTab === "learning"
              ? "bg-surface text-text shadow-xs border border-border"
              : "text-text-muted hover:text-text"
          }`}
        >
          <BrainCircuit size={14} /> Learning Curve
        </button>
        <button
          onClick={() => setActiveTab("behavior")}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap ${
            activeTab === "behavior"
              ? "bg-surface text-text shadow-xs border border-border"
              : "text-text-muted hover:text-text"
          }`}
        >
          <Cpu size={14} /> Behavioral Patterns
        </button>
      </div>

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
              Your account is new — these analytics automatically populate as you execute blocks on Today.
            </Alert>
          )}

          <div className="sm:hidden">
            <LifeClock />
          </div>

          {/* TAB 1: OVERVIEW */}
          {activeTab === "overview" && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <KpiCard
                  value={data.readiness_pct != null ? `${data.readiness_pct}%` : "—"}
                  label="Mastery Readiness"
                  accent="var(--accent-strong)"
                />
                <KpiCard
                  value={`${data.attempted_count}/${data.total_problems}`}
                  label="Curriculum Completed"
                />
                <KpiCard value={String(data.reviews_due_count)} label="Reviews Due Today" />
                <KpiCard
                  value={String(data.reviews_overdue_count)}
                  label="Reviews Overdue"
                  accent={data.reviews_overdue_count > 0 ? "var(--danger)" : undefined}
                />
              </div>

              {/* GitHub-style Consistency Heatmap */}
              <ConsistencyHeatmap />

              <div className="grid md:grid-cols-2 gap-4">
                <TodayProgress />
                <DailyRecapCard />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <WeeklyOverviewCard />
                <TimeBudgetCard />
              </div>
            </div>
          )}

          {/* TAB 2: TIME & FOCUS */}
          {activeTab === "time_focus" && (
            <div className="space-y-6">
              <FocusAnalytics />
              <TimeCurve
                categoryMinutes={weekly?.category_minutes}
                periodLabel={
                  weekly ? `${weekly.window_start} → ${weekly.window_end}` : undefined
                }
              />
              <PlannedVsActual />
            </div>
          )}

          {/* TAB 3: LEARNING CURVE */}
          {activeTab === "learning" && (
            <div className="space-y-6">
              <LearningCurve />
              <div className="grid md:grid-cols-2 gap-4">
                <MasteryChart distribution={data.mastery_distribution} />
                <PatternChart coverage={data.pattern_coverage} />
              </div>
              <QuestionCoverageCard />
              <AttemptsTrendChart days={data.attempts_by_day} />
            </div>
          )}

          {/* TAB 4: BEHAVIORAL PATTERNS */}
          {activeTab === "behavior" && (
            <div className="space-y-6">
              <BehavioralDashboard />
            </div>
          )}

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
