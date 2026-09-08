"use client";

import { useState } from "react";
import { ChevronRight } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { QueryError } from "@/components/ui/query-state";
import { QuestionFlashcards } from "@/components/concepts/QuestionFlashcards";
import { useInterviewModules } from "@/hooks/useQuestions";
import { cn } from "@/lib/cn";
import type { InterviewModuleOut } from "@/lib/types";

const PRIORITY_COLOR: Record<string, string> = {
  P0: "var(--danger)",
  P1: "var(--status-partial)",
  P2: "var(--accent)",
  P3: "var(--text-faint)",
};

const PRIORITY_MEANING: Record<string, string> = {
  P0: "In nearly every loop",
  P1: "Often, or the senior differentiator",
  P2: "Role-dependent",
  P3: "Specialised",
};

export default function CurriculumPage() {
  const { data, isLoading, isError, error, refetch } = useInterviewModules();
  const [openModule, setOpenModule] = useState<string | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<string | null>(null);

  const modules = data ?? [];
  const shown = priorityFilter ? modules.filter((m) => m.priority === priorityFilter) : modules;
  const withQuestions = modules.filter((m) => m.question_count > 0).length;
  const totalQuestions = modules.reduce((acc, m) => acc + m.question_count, 0);

  return (
    <PageContainer width="wide">
      <PageHeader
        eyebrow="Career"
        title="Interview Curriculum"
        description="The AI/ML interview master map. 32 modules, prioritised by how often they actually appear in a loop — prepare P0 first."
      />

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-20" />
          ))}
        </div>
      )}

      {isError && (
        <QueryError error={error} onRetry={() => refetch()} fallback="Couldn't load the curriculum." />
      )}

      {data && (
        <>
          <Card className="p-4 mb-4">
            <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
              <div>
                <span className="text-2xl font-semibold tabular-nums text-text">
                  {modules.length}
                </span>
                <span className="text-xs text-text-faint ml-1.5">modules</span>
              </div>
              <div>
                <span className="text-2xl font-semibold tabular-nums text-accent-strong">
                  {totalQuestions}
                </span>
                <span className="text-xs text-text-faint ml-1.5">questions</span>
              </div>
              {/* Stated plainly: the map is complete, the bank is not. */}
              <div>
                <span className="text-2xl font-semibold tabular-nums text-status-partial">
                  {modules.length - withQuestions}
                </span>
                <span className="text-xs text-text-faint ml-1.5">modules still empty</span>
              </div>
              <div className="flex items-center gap-1.5 ml-auto flex-wrap">
                {["P0", "P1", "P2", "P3"].map((p) => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => setPriorityFilter((cur) => (cur === p ? null : p))}
                    title={PRIORITY_MEANING[p]}
                    className={cn(
                      "h-7 px-2.5 rounded-md text-[11px] font-medium border transition-colors",
                      priorityFilter === p
                        ? "border-accent bg-accent-soft text-accent-strong"
                        : "border-border text-text-muted hover:bg-surface-2"
                    )}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          </Card>

          <ul className="space-y-2">
            {shown.map((m) => (
              <li key={m.code}>
                <ModuleRow
                  module={m}
                  open={openModule === m.code}
                  onToggle={() => setOpenModule((cur) => (cur === m.code ? null : m.code))}
                />
              </li>
            ))}
          </ul>
        </>
      )}
    </PageContainer>
  );
}

function ModuleRow({
  module,
  open,
  onToggle,
}: {
  module: InterviewModuleOut;
  open: boolean;
  onToggle: () => void;
}) {
  return (
    <Card className="p-3.5">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        className="w-full flex items-start gap-3 text-left"
      >
        <span className="h-8 w-8 shrink-0 rounded-lg bg-surface-2 border border-border flex items-center justify-center text-xs font-mono font-semibold text-text-muted">
          {module.code}
        </span>

        <span className="min-w-0 flex-1">
          <span className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium text-text">{module.title}</span>
            <Badge color={PRIORITY_COLOR[module.priority]}>{module.priority}</Badge>
            {module.question_count === 0 ? (
              <span className="text-xs text-text-faint">No questions yet</span>
            ) : (
              <span className="text-xs text-text-faint tabular-nums">
                {module.ready_count}/{module.question_count} ready
              </span>
            )}
          </span>
          {module.summary && (
            <span className="block text-xs text-text-muted mt-1 leading-relaxed">
              {module.summary}
            </span>
          )}
        </span>

        <ChevronRight
          size={16}
          className={cn(
            "shrink-0 mt-1 text-text-faint transition-transform",
            open && "rotate-90"
          )}
        />
      </button>

      {open && (
        <div className="mt-3 pt-3 border-t border-border space-y-4">
          <div>
            <p className="text-[10px] uppercase tracking-wide text-text-faint mb-1.5">
              Submodules ({module.submodules.length}) · targets{" "}
              {module.target_seniority.join(", ")}
            </p>
            <div className="flex flex-wrap gap-1.5">
              {module.submodules.map((s) => (
                <span
                  key={s}
                  className="text-[11px] px-2 py-0.5 rounded-md bg-surface-2 border border-border text-text-muted"
                >
                  {s}
                </span>
              ))}
            </div>
          </div>

          {module.question_count > 0 ? (
            <QuestionFlashcards module={module.code} />
          ) : (
            <p className="text-xs text-text-faint rounded-lg border border-dashed border-border p-3">
              The map for this module is written, but no questions have been ingested into it yet.
              Nothing is shown here rather than filling it with generated filler.
            </p>
          )}
        </div>
      )}
    </Card>
  );
}
