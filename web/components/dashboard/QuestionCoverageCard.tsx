"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { useQuestionsSummary } from "@/hooks/useQuestions";
import { Card } from "@/components/ui/card";

const CATEGORY_LABEL: Record<string, string> = {
  classical_ml: "Classical ML",
  deep_learning: "Deep Learning",
  llm_genai: "LLMs & GenAI",
  mlops: "MLOps & Production",
  ml_system_design: "ML System Design",
  agentic_ai: "Agentic AI Systems",
};

export function QuestionCoverageCard() {
  const { data, isLoading } = useQuestionsSummary();

  if (isLoading || !data) {
    return <Card className="p-4 h-[220px] animate-pulse" />;
  }

  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <p className="text-xs font-medium text-text-faint uppercase tracking-wide">
            Interview question bank
          </p>
          <p className="text-2xl font-semibold tracking-tight tabular-nums text-text mt-1">
            {data.pct != null ? `${data.pct}%` : "—"}
            <span className="text-text-faint text-base font-normal ml-1.5">
              ({data.covered_count}/{data.total_count} covered)
            </span>
          </p>
        </div>
        <Link
          href="/concepts"
          className="shrink-0 inline-flex items-center gap-1 text-sm font-medium text-accent-strong hover:underline mt-1"
        >
          Open <ArrowRight size={14} />
        </Link>
      </div>

      <div className="space-y-2">
        {data.by_category.map((c) => (
          <div key={c.category}>
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-text-muted">{CATEGORY_LABEL[c.category] ?? c.category}</span>
              <span className="text-text-faint tabular-nums">
                {c.covered_count}/{c.total_count}
              </span>
            </div>
            <div className="h-1.5 rounded-full bg-surface-2 overflow-hidden">
              <div className="h-full rounded-full bg-accent" style={{ width: `${c.pct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
