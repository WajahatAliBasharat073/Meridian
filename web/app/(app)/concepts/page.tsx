"use client";

import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Skeleton } from "@/components/ui/skeleton";
import { QueryError } from "@/components/ui/query-state";
import { CategoryTile } from "@/components/concepts/CategoryTile";
import { useConcepts } from "@/hooks/useConcepts";
import { useQuestionsSummary } from "@/hooks/useQuestions";
import { CONCEPT_CATEGORIES } from "@/lib/conceptCategories";

export default function ConceptsPage() {
  const { data: concepts, isLoading: conceptsLoading, isError, error } = useConcepts();
  const { data: summary, isLoading: summaryLoading } = useQuestionsSummary();

  const isLoading = conceptsLoading || summaryLoading;

  return (
    <PageContainer width="wide">
      <PageHeader
        eyebrow="Career"
        title="ML & GenAI"
        description="Interview-prep roadmap for ML/AI and system-design rounds. Pick a section — topics to rate, questions to work through."
      />

      {isError && <QueryError error={error} fallback="Couldn't load the roadmap." />}

      {isLoading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      )}

      {!isLoading && concepts && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {CONCEPT_CATEGORIES.map((meta) => {
            const catConcepts = concepts.filter((c) => c.category === meta.key);
            const questionStats = summary?.by_category.find((c) => c.category === meta.key);
            return (
              <CategoryTile
                key={meta.key}
                meta={meta}
                topicsRated={catConcepts.filter((c) => c.current_mastery != null).length}
                topicsTotal={catConcepts.length}
                questionsCovered={questionStats?.covered_count ?? 0}
                questionsTotal={questionStats?.total_count ?? 0}
              />
            );
          })}
        </div>
      )}
    </PageContainer>
  );
}
