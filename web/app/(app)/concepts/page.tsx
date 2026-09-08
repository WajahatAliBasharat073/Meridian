"use client";

import Link from "next/link";
import { ArrowRight, BookOpen } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { QueryError } from "@/components/ui/query-state";
import { CategoryTile } from "@/components/concepts/CategoryTile";
import { DailyTheoryCard } from "@/components/today/DailyTheoryCard";
import { TheoryPaceCard } from "@/components/today/TheoryPaceCard";
import { ProgressStrip } from "@/components/concepts/ProgressStrip";
import { useConcepts } from "@/hooks/useConcepts";
import { useQuestionsSummary } from "@/hooks/useQuestions";
import { CATEGORY_GROUPS, CONCEPT_CATEGORIES, categoriesInGroup } from "@/lib/conceptCategories";
import { RESOURCES } from "@/lib/resources";

export default function ConceptsPage() {
  const { data: concepts, isLoading: conceptsLoading, isError, error } = useConcepts();
  const { data: summary, isLoading: summaryLoading } = useQuestionsSummary();

  const isLoading = conceptsLoading || summaryLoading;

  const countsByCategory = new Map(
    (summary?.by_category ?? []).map((c) => [c.category, c] as const)
  );
  const shownTotal = CONCEPT_CATEGORIES.reduce(
    (acc, meta) => acc + (countsByCategory.get(meta.key)?.total_count ?? 0),
    0
  );
  const bankTotal = summary?.total_count ?? 0;
  // Any category in the bank that has no tile here would be unreachable —
  // the previous version silently hid 61% of the bank that way, so the
  // gap is surfaced rather than assumed to be zero.
  const orphaned = (summary?.by_category ?? []).filter(
    (c) => !CONCEPT_CATEGORIES.some((m) => m.key === c.category)
  );
  const resourceCount = Object.values(RESOURCES).reduce((a, r) => a + r.length, 0);

  return (
    <PageContainer width="xl">
      <PageHeader
        eyebrow="Career"
        title="ML & GenAI"
        description="The interview-prep roadmap. Every section holds topics to rate and questions to work through — grouped the way a real loop is structured."
      />

      {isError && <QueryError error={error} fallback="Couldn't load the roadmap." />}

      {isLoading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 9 }).map((_, i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      )}

      {!isLoading && summary && (
        <Card className="p-4 mb-6">
          <ProgressStrip
            total={shownTotal}
            started={summary.started_count}
            ready={summary.covered_count}
          />

          <div className="flex flex-wrap items-center gap-x-6 gap-y-3 mt-4 pt-4 border-t border-border">
            <div>
              <span className="text-sm font-semibold tabular-nums text-text">
                {CONCEPT_CATEGORIES.length}
              </span>
              <span className="text-xs text-text-faint ml-1.5">sections</span>
            </div>
            <div>
              <span className="text-sm font-semibold tabular-nums text-text">{resourceCount}</span>
              <span className="text-xs text-text-faint ml-1.5">linked resources</span>
            </div>
            {shownTotal !== bankTotal && (
              <div>
                <span className="text-sm font-semibold tabular-nums text-status-partial">
                  {bankTotal - shownTotal}
                </span>
                <span className="text-xs text-text-faint ml-1.5">not shown here</span>
              </div>
            )}
            <div className="flex items-center gap-2 ml-auto flex-wrap">
              <Link
                href="/curriculum"
                className="h-9 px-3 inline-flex items-center gap-1.5 rounded-lg border border-border text-xs font-medium text-text-muted hover:text-text hover:bg-surface-2 transition-colors"
              >
                32-module curriculum
                <ArrowRight size={14} />
              </Link>
              <Link
                href="/resources"
                className="h-9 px-3 inline-flex items-center gap-1.5 rounded-lg border border-border text-xs font-medium text-text-muted hover:text-text hover:bg-surface-2 transition-colors"
              >
                <BookOpen size={14} />
                All resources
              </Link>
            </div>
          </div>

          {orphaned.length > 0 && (
            <p className="text-xs text-status-partial mt-3 pt-3 border-t border-border">
              {orphaned.reduce((a, c) => a + c.total_count, 0)} questions are in categories with no
              section here ({orphaned.map((c) => c.category).join(", ")}) — they are reachable only
              from the curriculum browser.
            </p>
          )}
        </Card>
      )}

      {!isLoading && concepts && (
        <div className="grid grid-cols-1 xl:grid-cols-[380px_1fr] gap-6 items-start">
          {/* ══ SIDEBAR — today's recommendation + pace (sticky on xl+) ══
              Same widgets as Today, reachable here too since planning a
              study session usually starts on this page rather than
              mid-schedule. Side column rather than a full-width strip up
              top, so it doesn't push every section down the page. */}
          <div className="xl:sticky xl:top-4 space-y-4 xl:max-h-[calc(100vh-6rem)] xl:overflow-y-auto xl:pr-1">
            <DailyTheoryCard />
            <TheoryPaceCard />
          </div>

          <div className="space-y-8 min-w-0">
            {CATEGORY_GROUPS.map((group) => {
              const metas = categoriesInGroup(group.name);
              if (metas.length === 0) return null;
              const groupTotal = metas.reduce(
                (acc, m) => acc + (countsByCategory.get(m.key)?.total_count ?? 0),
                0
              );
              const groupReady = metas.reduce(
                (acc, m) => acc + (countsByCategory.get(m.key)?.covered_count ?? 0),
                0
              );
              return (
                <section key={group.name}>
                  <div className="flex items-baseline justify-between gap-3 mb-3 flex-wrap">
                    <div className="min-w-0">
                      <h2 className="text-sm font-semibold text-text">{group.name}</h2>
                      <p className="text-xs text-text-muted mt-0.5">{group.blurb}</p>
                    </div>
                    <span className="text-xs text-text-faint tabular-nums shrink-0">
                      {groupReady}/{groupTotal} ready
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {metas.map((meta) => {
                      const catConcepts = concepts.filter((c) => c.category === meta.key);
                      const stats = countsByCategory.get(meta.key);
                      return (
                        <CategoryTile
                          key={meta.key}
                          meta={meta}
                          topicsRated={catConcepts.filter((c) => c.current_mastery != null).length}
                          topicsTotal={catConcepts.length}
                          questionsCovered={stats?.covered_count ?? 0}
                          questionsStarted={stats?.started_count ?? 0}
                          questionsTotal={stats?.total_count ?? 0}
                          resourceCount={(RESOURCES[meta.key] ?? []).length}
                        />
                      );
                    })}
                  </div>
                </section>
              );
            })}
          </div>
        </div>
      )}
    </PageContainer>
  );
}
