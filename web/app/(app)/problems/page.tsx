"use client";

import { useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ChevronDown, Filter, Lock, ShieldCheck } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { QueryError } from "@/components/ui/query-state";
import { ProblemRow, DIFFICULTY_COLOR } from "@/components/problems/ProblemRow";
import { TopicGuideCard } from "@/components/problems/TopicGuideCard";
import { GateBadge, VerifyTopicDialog } from "@/components/problems/VerifyTopicDialog";
import { TopicLearningLog } from "@/components/problems/TopicLearningLog";
import { useProblemsByTopic } from "@/hooks/useProblems";
import { overrideTopicGate } from "@/lib/api";
import { cn } from "@/lib/cn";
import type { TopicSectionOut } from "@/lib/types";

const DIFFICULTIES = ["Easy", "Medium", "Hard"];

export default function ProblemsPage() {
  const { data, isLoading, isError, error, refetch } = useProblemsByTopic();
  const [difficulty, setDifficulty] = useState("");
  const [hideSolved, setHideSolved] = useState(false);
  const [openTopic, setOpenTopic] = useState<string | null>(null);
  const [verifying, setVerifying] = useState<{ topic: string; displayName: string } | null>(null);

  const sections = useMemo(() => data ?? [], [data]);

  const overall = useMemo(() => {
    if (sections.length === 0) return null;
    return {
      total: sections.reduce((a, s) => a + s.total, 0),
      solved: sections.reduce((a, s) => a + s.solved, 0),
      unaided: sections.reduce((a, s) => a + s.unaided, 0),
      remaining: sections.reduce((a, s) => a + s.remaining, 0),
      topics: sections.filter((s) => s.total > 0).length,
      verified: sections.filter((s) => s.gate?.state === "unlocked").length,
    };
  }, [sections]);

  return (
    <PageContainer width="wide">
      <PageHeader
        eyebrow="Career"
        title="DSA by Topic"
        description="Organised by data structure, not by day. Each topic's problems stay locked until you've implemented the structure and defended it closed-book — the guide always stays open."
      />

      {overall && (
        <Card className="p-4 mb-4">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
            <div>
              <span className="text-2xl font-semibold tabular-nums text-text">{overall.total}</span>
              <span className="text-xs text-text-faint ml-1.5">problems</span>
            </div>
            <div>
              <span className="text-2xl font-semibold tabular-nums text-text-faint">
                {overall.topics}
              </span>
              <span className="text-xs text-text-faint ml-1.5">topics</span>
            </div>
            <div>
              <span className="text-2xl font-semibold tabular-nums text-status-done">
                {overall.solved}
              </span>
              <span className="text-xs text-text-faint ml-1.5">attempted</span>
            </div>
            {/* Separate from "attempted" on purpose: a count that mixes in
                problems you only got after the editorial isn't progress. */}
            <div>
              <span className="text-2xl font-semibold tabular-nums text-accent-strong">
                {overall.unaided}
              </span>
              <span className="text-xs text-text-faint ml-1.5">unaided</span>
            </div>
            <div>
              <span className="text-2xl font-semibold tabular-nums text-status-partial">
                {overall.remaining}
              </span>
              <span className="text-xs text-text-faint ml-1.5">remaining</span>
            </div>
            {/* How many structures you have actually demonstrated, which is
                a different question from how many problems you have done. */}
            <div>
              <span className="text-2xl font-semibold tabular-nums text-status-done">
                {overall.verified}
              </span>
              <span className="text-xs text-text-faint ml-1.5">verified</span>
            </div>

            <div className="flex items-center gap-1.5 ml-auto flex-wrap">
              <Filter size={13} className="text-text-faint" aria-hidden />
              {DIFFICULTIES.map((d) => (
                <button
                  key={d}
                  type="button"
                  onClick={() => setDifficulty((cur) => (cur === d ? "" : d))}
                  className={cn(
                    "h-7 px-2.5 rounded-md text-[11px] font-medium border transition-colors",
                    difficulty === d
                      ? "border-accent bg-accent-soft text-accent-strong"
                      : "border-border text-text-muted hover:bg-surface-2"
                  )}
                >
                  {d}
                </button>
              ))}
              <button
                type="button"
                onClick={() => setHideSolved((v) => !v)}
                className={cn(
                  "h-7 px-2.5 rounded-md text-[11px] font-medium border transition-colors",
                  hideSolved
                    ? "border-accent bg-accent-soft text-accent-strong"
                    : "border-border text-text-muted hover:bg-surface-2"
                )}
              >
                Hide attempted
              </button>
            </div>
          </div>
        </Card>
      )}

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      )}

      {isError && (
        <QueryError error={error} onRetry={() => refetch()} fallback="Couldn't load problems." />
      )}

      {data && (
        <div className="space-y-3">
          {sections.map((section) => (
            <TopicSection
              key={section.topic}
              section={section}
              difficulty={difficulty}
              hideSolved={hideSolved}
              open={openTopic === section.topic}
              onToggle={() =>
                setOpenTopic((cur) => (cur === section.topic ? null : section.topic))
              }
              onVerify={() =>
                setVerifying({ topic: section.topic, displayName: section.display_name })
              }
            />
          ))}
        </div>
      )}

      {verifying && (
        <VerifyTopicDialog
          topic={verifying.topic}
          displayName={verifying.displayName}
          onClose={() => setVerifying(null)}
        />
      )}
    </PageContainer>
  );
}

function TopicSection({
  section,
  difficulty,
  hideSolved,
  open,
  onToggle,
  onVerify,
}: {
  section: TopicSectionOut;
  difficulty: string;
  hideSolved: boolean;
  open: boolean;
  onToggle: () => void;
  onVerify: () => void;
}) {
  const queryClient = useQueryClient();
  const [confirmOverride, setConfirmOverride] = useState(false);
  const override = useMutation({
    mutationFn: (reason: string) => overrideTopicGate(section.topic, reason),
    onSuccess: () => {
      setConfirmOverride(false);
      void queryClient.invalidateQueries({ queryKey: ["problems-by-topic"] });
    },
  });
  const gate = section.gate;
  const locked = gate != null && !gate.problems_visible;
  const shown = useMemo(() => {
    let list = section.problems;
    if (difficulty) list = list.filter((p) => p.difficulty === difficulty);
    if (hideSolved) list = list.filter((p) => p.attempt_count === 0);
    return list;
  }, [section.problems, difficulty, hideSolved]);

  const pct = section.total > 0 ? Math.round((section.solved / section.total) * 100) : 0;
  // A pure revision topic (OOP) has no problem list — it is a guide only,
  // so it should never render an empty "0 problems" shell.
  const isGuideOnly = section.total === 0;

  return (
    <Card className="p-0 overflow-hidden">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        className="w-full text-left px-4 py-3 flex items-center gap-3 hover:bg-surface-2/40 transition-colors"
      >
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h2 className="text-sm font-semibold text-text">{section.display_name}</h2>
            {gate && (
              <GateBadge
                state={gate.state}
                daysLeft={gate.days_until_expiry}
                overridden={gate.overridden}
              />
            )}
            {isGuideOnly ? (
              <Badge color="var(--status-partial)">Revision only</Badge>
            ) : (
              <>
                <span className="text-xs text-text-faint tabular-nums">
                  {section.total} problems
                </span>
                <span className="text-xs text-text-faint">·</span>
                <span className="text-xs tabular-nums text-status-partial">
                  {section.remaining} remaining
                </span>
                {section.solved > 0 && (
                  <span className="text-xs tabular-nums text-status-done">
                    {section.solved} attempted
                  </span>
                )}
              </>
            )}
          </div>

          {!isGuideOnly && (
            <div className="flex items-center gap-2 mt-1.5 flex-wrap">
              {DIFFICULTIES.map((d) =>
                section.by_difficulty[d] ? (
                  <Badge key={d} color={DIFFICULTY_COLOR[d]}>
                    {d} {section.by_difficulty[d]}
                  </Badge>
                ) : null
              )}
              {section.companies.length > 0 && (
                <span className="text-[11px] text-text-faint truncate">
                  asked by {section.companies.slice(0, 5).join(", ")}
                  {section.companies.length > 5 && ` +${section.companies.length - 5} more`}
                </span>
              )}
            </div>
          )}
        </div>

        {!isGuideOnly && (
          <div className="shrink-0 w-24 hidden sm:block">
            <div className="h-1.5 rounded-full bg-surface-2 overflow-hidden">
              <div
                className="h-full rounded-full bg-status-done"
                style={{ width: `${pct}%` }}
              />
            </div>
            <p className="text-[10px] text-text-faint tabular-nums mt-1 text-right">{pct}%</p>
          </div>
        )}

        <ChevronDown
          size={16}
          className={cn("shrink-0 text-text-faint transition-transform", open && "rotate-180")}
        />
      </button>

      {open && (
        <div className="px-4 pb-4 space-y-3 border-t border-border pt-3">
          {/* Always first: understand the structure, then the problems. */}
          {section.guide && (
            <TopicGuideCard guide={section.guide} defaultOpen={section.solved === 0} />
          )}

          <TopicLearningLog topic={section.topic} />

          {!isGuideOnly && locked && (
            <div className="rounded-xl border border-dashed border-border bg-surface-2/30 p-5 text-center">
              <div className="h-10 w-10 mx-auto rounded-xl bg-surface-2 border border-border flex items-center justify-center text-text-faint mb-3">
                <Lock size={18} />
              </div>
              <p className="text-sm font-medium text-text">
                {section.total} problems, locked
              </p>
              <p className="text-xs text-text-muted mt-1.5 max-w-md mx-auto leading-relaxed">
                {gate?.state === "expired"
                  ? "Your verification for this topic has expired — knowledge lapses, which is exactly what this catches. Defend it again to reopen the list."
                  : "Implement the structure above, then defend it closed-book. Reading the guide is not the gate; being able to write it and explain your own code is."}
              </p>
              <div className="flex items-center justify-center gap-2 mt-4 flex-wrap">
                <Button variant="primary" size="md" onClick={onVerify} className="gap-1.5">
                  <ShieldCheck size={15} />
                  {gate?.state === "expired" ? "Re-verify" : "Verify understanding"}
                </Button>
                {!confirmOverride ? (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setConfirmOverride(true)}
                    className="text-text-faint"
                  >
                    Unlock anyway
                  </Button>
                ) : (
                  <span className="flex items-center gap-2">
                    <Button
                      variant="danger"
                      size="sm"
                      disabled={override.isPending}
                      onClick={() => override.mutate("unlocked without verifying")}
                    >
                      {override.isPending ? "Unlocking…" : "Yes — mark as unverified"}
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => setConfirmOverride(false)}>
                      Cancel
                    </Button>
                  </span>
                )}
              </div>
              {confirmOverride && (
                <p className="text-[11px] text-text-faint mt-2.5">
                  This opens the problems now and marks the topic &quot;unlocked, never
                  verified&quot; permanently. Nothing stops you — it just stays on the record.
                </p>
              )}
            </div>
          )}

          {!isGuideOnly && !locked && (
            <>
              {gate?.state === "unverified_override" && (
                <p className="text-[11px] text-status-partial flex items-center gap-1.5">
                  <Lock size={11} className="shrink-0" />
                  Opened without verifying.{" "}
                  <button
                    type="button"
                    onClick={onVerify}
                    className="underline hover:text-text"
                  >
                    Verify it properly
                  </button>
                </p>
              )}
              {shown.length === 0 ? (
                <p className="text-xs text-text-faint py-4 text-center">
                  Nothing in this topic matches the current filter.
                </p>
              ) : (
                <ul className="space-y-2">
                  {shown.map((p) => (
                    <li key={p.problem_id}>
                      <ProblemRow problem={p} />
                    </li>
                  ))}
                </ul>
              )}
            </>
          )}
        </div>
      )}
    </Card>
  );
}
