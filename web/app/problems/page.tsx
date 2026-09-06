"use client";

import { useState } from "react";
import { ExternalLink } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { useProblems } from "@/hooks/useProblems";
import { masteryMeta } from "@/lib/mastery";
import { ApiError } from "@/lib/api";

const PATTERNS = [
  "arrays_hashing",
  "two_pointers",
  "sliding_window",
  "stack",
  "binary_search",
  "linked_list",
  "trees",
  "tries",
  "heap",
  "backtracking",
  "graphs",
  "dp_1d",
  "dp_2d",
  "greedy",
  "intervals",
  "bit_manipulation",
];

const DIFFICULTIES = ["Easy", "Medium", "Hard"];

const DIFFICULTY_COLOR: Record<string, string> = {
  Easy: "var(--status-done)",
  Medium: "var(--status-partial)",
  Hard: "var(--danger)",
};

function FilterSelect({
  value,
  onChange,
  options,
  placeholder,
}: {
  value: string;
  onChange: (v: string) => void;
  options: string[];
  placeholder: string;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="h-10 rounded-lg border border-border bg-surface-2 px-3 text-sm text-text focus:outline-none focus:ring-2 focus:ring-accent"
    >
      <option value="">{placeholder}</option>
      {options.map((o) => (
        <option key={o} value={o}>
          {o.replace(/_/g, " ")}
        </option>
      ))}
    </select>
  );
}

export default function ProblemsPage() {
  const [pattern, setPattern] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const { data, isLoading, isError, error } = useProblems(pattern || undefined, difficulty || undefined);

  const isAuthError = error instanceof ApiError && error.status === 401;

  return (
    <AppShell>
      <main className="mx-auto max-w-3xl px-4 py-6 pb-16">
        <PageHeader
          title="Problems"
          description="The seeded interview-prep curriculum — filter by pattern or difficulty."
        />

        <div className="flex gap-2 mb-4">
          <FilterSelect value={pattern} onChange={setPattern} options={PATTERNS} placeholder="All patterns" />
          <FilterSelect value={difficulty} onChange={setDifficulty} options={DIFFICULTIES} placeholder="All difficulties" />
        </div>

        {isLoading && (
          <div className="space-y-2">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-16" />
            ))}
          </div>
        )}

        {isError && (
          <Alert variant="error">
            {isAuthError ? "Your session expired." : "Couldn't load problems."}
          </Alert>
        )}

        {data && data.length === 0 && (
          <p className="text-sm text-text-faint text-center py-8">No problems match that filter.</p>
        )}

        {data && data.length > 0 && (
          <ul className="space-y-2">
            {data.map((p) => {
              const mastery = p.current_mastery ? masteryMeta(p.current_mastery) : null;
              return (
                <li key={p.problem_id}>
                  <Card className="p-3.5 flex items-center gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xs text-text-faint tabular-nums">#{p.lc_number}</span>
                        <span className="text-sm font-medium text-text truncate">{p.title}</span>
                        {p.is_scheduled_today && <Badge color="var(--accent)">Today</Badge>}
                      </div>
                      <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                        <Badge color="var(--text-faint)">{p.pattern.replace(/_/g, " ")}</Badge>
                        <Badge color={DIFFICULTY_COLOR[p.difficulty] ?? "var(--text-faint)"}>
                          {p.difficulty}
                        </Badge>
                        {mastery ? (
                          <Badge color={mastery.colorVar}>{mastery.shortLabel} · {mastery.label}</Badge>
                        ) : (
                          <span className="text-xs text-text-faint">Not attempted</span>
                        )}
                      </div>
                    </div>
                    <a
                      href={p.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label={`Open ${p.title} on LeetCode`}
                      className="h-11 w-11 shrink-0 flex items-center justify-center text-text-faint hover:text-text rounded-md hover:bg-surface-2"
                    >
                      <ExternalLink size={16} />
                    </a>
                  </Card>
                </li>
              );
            })}
          </ul>
        )}
      </main>
    </AppShell>
  );
}
