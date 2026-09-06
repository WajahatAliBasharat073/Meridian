"use client";

import { useState } from "react";
import { Check, ChevronLeft, ChevronRight } from "lucide-react";
import { useQuestions, useToggleQuestionCoverage } from "@/hooks/useQuestions";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/cn";
import type { QuestionOut } from "@/lib/types";

export function QuestionFlashcards({ category }: { category: string }) {
  const { data, isLoading } = useQuestions(category);

  if (isLoading) return <Skeleton className="h-48" />;
  if (!data || data.length === 0) return null;

  // Keying by category means this remounts (and re-picks a fresh starting
  // question) when the user navigates to a different category page.
  return <QuestionFlashcardsLoaded key={category} data={data} />;
}

function QuestionFlashcardsLoaded({ data }: { data: QuestionOut[] }) {
  const toggle = useToggleQuestionCoverage();
  // Lazy initializer reads `data` once, at mount — lands on the first
  // not-yet-covered question rather than always starting at #1.
  const [index, setIndex] = useState(() => {
    const firstUncovered = data.findIndex((q) => !q.covered);
    return firstUncovered === -1 ? 0 : firstUncovered;
  });

  const covered = data.filter((q) => q.covered).length;
  const current = data[Math.min(index, data.length - 1)];

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-medium text-text-faint uppercase tracking-wide">
          Interview questions
        </h3>
        <span className="text-xs text-text-faint tabular-nums">
          {covered}/{data.length} covered
        </span>
      </div>

      {/* Jump strip — click any dot to go straight to that question. */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {data.map((q, i) => (
          <button
            key={q.question_id}
            type="button"
            onClick={() => setIndex(i)}
            aria-label={`Question ${i + 1}${q.covered ? " (covered)" : ""}`}
            aria-current={i === index ? "true" : undefined}
            className={cn(
              "h-2.5 w-2.5 rounded-full transition-all",
              i === index
                ? "ring-2 ring-accent ring-offset-1 ring-offset-surface"
                : "",
              q.covered ? "bg-status-done" : "bg-border-strong"
            )}
          />
        ))}
      </div>

      <Card className="p-5">
        <div className="flex items-start justify-between gap-3 mb-4">
          <span className="text-xs text-text-faint tabular-nums shrink-0">
            {index + 1} / {data.length}
          </span>
          <span className="text-[10px] text-text-faint uppercase tracking-wide shrink-0">
            {current.source}
          </span>
        </div>

        <p className="text-base text-text leading-relaxed mb-5 min-h-[3rem]">{current.title}</p>

        <div className="flex items-center justify-between gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setIndex((i) => Math.max(0, i - 1))}
            disabled={index === 0}
          >
            <ChevronLeft size={15} />
            Prev
          </Button>

          <Button
            variant={current.covered ? "secondary" : "primary"}
            size="sm"
            onClick={() => toggle.mutate(current.question_id)}
            disabled={toggle.isPending}
            className={cn(current.covered && "border-status-done/40 text-status-done")}
          >
            {current.covered && <Check size={15} />}
            {current.covered ? "Covered" : "Mark covered"}
          </Button>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => setIndex((i) => Math.min(data.length - 1, i + 1))}
            disabled={index === data.length - 1}
          >
            Next
            <ChevronRight size={15} />
          </Button>
        </div>
      </Card>
    </div>
  );
}
