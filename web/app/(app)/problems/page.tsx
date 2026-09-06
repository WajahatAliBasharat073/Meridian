"use client";

import { useMemo, useState } from "react";
import { ExternalLink } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { QueryError } from "@/components/ui/query-state";
import { useProblems } from "@/hooks/useProblems";
import { masteryMeta } from "@/lib/mastery";

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
  "advanced_graphs",
  "dp_1d",
  "dp_2d",
  "greedy",
  "intervals",
  "math_geometry",
  "bit_manipulation",
];

const DIFFICULTIES = ["Easy", "Medium", "Hard"];

const DIFFICULTY_COLOR: Record<string, string> = {
  Easy: "var(--status-done)",
  Medium: "var(--status-partial)",
  Hard: "var(--danger)",
};

export default function ProblemsPage() {
  const [pattern, setPattern] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const { data, isLoading, isError, error } = useProblems(
    pattern || undefined,
    difficulty || undefined
  );

  const stats = useMemo(() => {
    if (!data) return null;
    const total = data.length;
    const solved = data.filter((p) => p.current_mastery != null).length;
    const byDifficulty = DIFFICULTIES.map((d) => {
      const inDifficulty = data.filter((p) => p.difficulty === d);
      return {
        difficulty: d,
        solved: inDifficulty.filter((p) => p.current_mastery != null).length,
        total: inDifficulty.length,
      };
    }).filter((d) => d.total > 0);
    return { total, solved, unsolved: total - solved, byDifficulty };
  }, [data]);

  return (
    <PageContainer>
      <PageHeader
        eyebrow="Career"
        title="Problems"
        description="The seeded interview-prep curriculum. Filter by pattern or difficulty — mastery comes from attempts you log on Today."
      />

      <div className="flex flex-col sm:flex-row gap-2 mb-4">
        <Select
          value={pattern}
          onChange={(e) => setPattern(e.target.value)}
          aria-label="Filter by pattern"
          className="sm:flex-1"
        >
          <option value="">All patterns</option>
          {PATTERNS.map((o) => (
            <option key={o} value={o}>
              {o.replace(/_/g, " ")}
            </option>
          ))}
        </Select>
        <Select
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
          aria-label="Filter by difficulty"
          className="sm:w-44"
        >
          <option value="">All difficulties</option>
          {DIFFICULTIES.map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </Select>
      </div>

      {stats && (
        <Card className="p-4 mb-4">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
            <div>
              <span className="text-2xl font-semibold tabular-nums text-text">{stats.total}</span>
              <span className="text-xs text-text-faint ml-1.5">
                {pattern || difficulty ? "matching filter" : "total"}
              </span>
            </div>
            <div>
              <span className="text-2xl font-semibold tabular-nums text-status-done">{stats.solved}</span>
              <span className="text-xs text-text-faint ml-1.5">solved</span>
            </div>
            <div>
              <span className="text-2xl font-semibold tabular-nums text-text-faint">{stats.unsolved}</span>
              <span className="text-xs text-text-faint ml-1.5">unsolved</span>
            </div>
            {stats.byDifficulty.length > 1 && (
              <div className="flex flex-wrap items-center gap-2 ml-auto">
                {stats.byDifficulty.map((d) => (
                  <Badge key={d.difficulty} color={DIFFICULTY_COLOR[d.difficulty]}>
                    {d.difficulty} {d.solved}/{d.total}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        </Card>
      )}

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-16" />
          ))}
        </div>
      )}

      {isError && <QueryError error={error} fallback="Couldn't load problems." />}

      {data && data.length === 0 && (
        <p className="text-sm text-text-muted text-center py-12">No problems match that filter.</p>
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
                        <Badge color={mastery.colorVar}>
                          {mastery.shortLabel} · {mastery.label}
                        </Badge>
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
                    className="h-11 w-11 shrink-0 flex items-center justify-center text-text-faint hover:text-text rounded-lg hover:bg-surface-2"
                  >
                    <ExternalLink size={16} />
                  </a>
                </Card>
              </li>
            );
          })}
        </ul>
      )}
    </PageContainer>
  );
}
