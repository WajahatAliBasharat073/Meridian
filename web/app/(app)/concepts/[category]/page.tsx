"use client";

import { useState } from "react";
import Link from "next/link";
import { notFound, useParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Select } from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { QueryError } from "@/components/ui/query-state";
import { ConceptCard } from "@/components/concepts/ConceptCard";
import { QuestionFlashcards } from "@/components/concepts/QuestionFlashcards";
import { ResourceList } from "@/components/concepts/ResourceList";
import { useConcepts } from "@/hooks/useConcepts";
import { categoryMeta } from "@/lib/conceptCategories";

const PHASES = ["foundation", "core", "advanced"];

export default function ConceptCategoryPage() {
  const params = useParams<{ category: string }>();
  const meta = categoryMeta(params.category);
  const [phase, setPhase] = useState("");
  const { data, isLoading, isError, error } = useConcepts(params.category, phase || undefined);

  if (!meta) notFound();

  const Icon = meta.icon;
  const rated = data?.filter((c) => c.current_mastery != null).length ?? 0;

  return (
    <PageContainer width="wide">
      <Link
        href="/concepts"
        className="inline-flex items-center gap-1.5 text-sm text-text-faint hover:text-text mb-4"
      >
        <ArrowLeft size={14} />
        All sections
      </Link>

      <PageHeader
        eyebrow="Career"
        title={meta.label}
        description={meta.description}
        action={
          <span className="hidden sm:flex h-11 w-11 rounded-lg bg-accent-soft text-accent-strong items-center justify-center">
            <Icon size={20} />
          </span>
        }
      />

      {isError && <QueryError error={error} fallback="Couldn't load this section." />}

      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-text">Topics</h2>
          <Select
            value={phase}
            onChange={(e) => setPhase(e.target.value)}
            aria-label="Filter by phase"
            className="w-40"
          >
            <option value="">All phases</option>
            {PHASES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </Select>
        </div>

        {isLoading && (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
        )}

        {data && data.length === 0 && (
          <Card className="p-4 text-sm text-text-muted">No topics match that filter.</Card>
        )}

        {data && data.length > 0 && (
          <>
            <p className="text-xs text-text-faint mb-2">
              {rated}/{data.length} rated
            </p>
            <div className="space-y-2">
              {data.map((c) => (
                <ConceptCard key={c.concept_id} concept={c} />
              ))}
            </div>
          </>
        )}
      </div>

      <div className="space-y-5">
        <QuestionFlashcards category={meta.key} />
        <ResourceList category={meta.key} title={`${meta.label} resources`} />
      </div>
    </PageContainer>
  );
}
