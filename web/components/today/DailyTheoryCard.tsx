"use client";

import { useState } from "react";
import Link from "next/link";
import { BookOpen, Brain, ChevronDown, ChevronUp, Sparkles } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ReferenceSolution } from "@/components/concepts/ReferenceSolution";
import { useDailyTheoryQuestions, useSetQuestionMastery } from "@/hooks/useQuestions";
import { QUESTION_MASTERY, READY_MASTERY, type DailyTheoryPickOut } from "@/lib/types";
import { cn } from "@/lib/cn";

const DIFFICULTY_COLOR: Record<string, string> = {
  beginner: "var(--status-done)",
  intermediate: "var(--status-partial)",
  advanced: "var(--danger)",
  expert: "var(--danger)",
};

/** Today's 3 theory picks for the Interview Prep — Theory block: 1 case
 * study plus 2 others, chosen by the daily-theory engine from what's due
 * for reinforcement, then what's never been seen, spread across modules
 * so the same one doesn't dominate every day. See
 * api/app/engines/daily_theory.py for the ranking itself — this component
 * only renders what it decided and lets you rate it on the spot.
 *
 * Shown always (morning planning needs it before the block starts), with
 * `isLiveNow` as a quiet accent rather than a gate — hiding it outside the
 * scheduled window would block exactly the "look at this ahead of time"
 * use case that makes it useful. */
export function DailyTheoryCard({ isLiveNow = false }: { isLiveNow?: boolean }) {
  const { data, isLoading, isError } = useDailyTheoryQuestions();

  if (isLoading) return <Skeleton className="h-64" />;
  if (isError || !data || data.length === 0) return null;

  return (
    <Card className={cn("p-5", isLiveNow && "border-accent/50 ring-1 ring-accent/20")}>
      <div className="flex items-center justify-between gap-2 mb-1">
        <h3 className="text-sm font-semibold text-text inline-flex items-center gap-2">
          <Sparkles size={15} className="text-accent-strong" />
          Today&apos;s Theory Focus
          {isLiveNow && (
            <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-accent text-accent-contrast">
              NOW
            </span>
          )}
        </h3>
        <span className="text-xs text-text-faint tabular-nums">{data.length} picks</span>
      </div>
      <p className="text-xs text-text-muted mb-4">
        Chosen for today from the full bank — due reinforcement first, then what you haven&apos;t
        seen yet, spread across modules.
      </p>

      <div className="space-y-3">
        {data.map((q) => (
          <TheoryPickRow key={q.question_id} pick={q} />
        ))}
      </div>
    </Card>
  );
}

function TheoryPickRow({ pick }: { pick: DailyTheoryPickOut }) {
  const [expanded, setExpanded] = useState(false);
  const [minutes, setMinutes] = useState("");
  const setMastery = useSetQuestionMastery();

  return (
    <div className="rounded-xl border border-border p-3.5">
      <div className="flex items-start gap-3">
        <span
          className={cn(
            "h-8 w-8 shrink-0 rounded-lg flex items-center justify-center",
            pick.is_case_study
              ? "bg-accent-soft text-accent-strong"
              : "bg-surface-2 text-text-muted"
          )}
        >
          {pick.is_case_study ? <BookOpen size={15} /> : <Brain size={15} />}
        </span>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5 flex-wrap mb-1">
            {pick.is_case_study && <Badge color="var(--accent-strong)">Case study</Badge>}
            {pick.priority && <Badge color="var(--danger)">{pick.priority}</Badge>}
            {pick.difficulty && (
              <Badge color={DIFFICULTY_COLOR[pick.difficulty] ?? "var(--text-faint)"}>
                {pick.difficulty}
              </Badge>
            )}
            {pick.module_code && (
              <Badge color="var(--text-faint)">Module {pick.module_code}</Badge>
            )}
          </div>

          <p className="text-sm text-text leading-relaxed">{pick.title}</p>
          <p className="text-xs text-text-faint mt-1 italic">{pick.pick_reason}</p>

          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="text-xs text-accent-strong hover:underline mt-2 inline-flex items-center gap-1"
          >
            {expanded ? "Hide details" : "What’s being tested / follow-ups"}
            {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </button>

          {expanded && (
            <div className="mt-3 space-y-2">
              {pick.tests_for && (
                <div className="rounded-lg border border-border bg-surface-2/50 p-2.5">
                  <p className="text-[10px] uppercase tracking-wide text-text-faint mb-1">
                    What the interviewer is testing
                  </p>
                  <p className="text-xs text-text-muted leading-relaxed">{pick.tests_for}</p>
                </div>
              )}
              {pick.follow_ups.length > 0 && (
                <ul className="space-y-1 pl-4 list-disc marker:text-text-faint">
                  {pick.follow_ups.map((f) => (
                    <li key={f} className="text-xs text-text-muted leading-relaxed">
                      {f}
                    </li>
                  ))}
                </ul>
              )}
              {pick.reference_solution && (
                <ReferenceSolution code={pick.reference_solution} />
              )}
              {pick.category && (
                <Link
                  href={`/concepts/${pick.category}`}
                  className="text-xs text-accent-strong hover:underline inline-block"
                >
                  Open full section →
                </Link>
              )}
            </div>
          )}

          <div className="flex flex-wrap items-center gap-1 mt-3">
            {QUESTION_MASTERY.map((m) => (
              <button
                key={m.level}
                type="button"
                disabled={setMastery.isPending}
                onClick={() =>
                  setMastery.mutate({
                    questionId: pick.question_id,
                    mastery: m.level,
                    minutes: minutes ? Number(minutes) : undefined,
                  })
                }
                title={`${m.level} — ${m.label}`}
                className={cn(
                  "h-6 w-6 rounded text-[10px] font-medium border transition-colors",
                  pick.mastery === m.level
                    ? m.level >= READY_MASTERY
                      ? "border-status-done bg-status-done/10 text-status-done"
                      : "border-accent bg-accent-soft text-accent-strong"
                    : "border-border text-text-faint hover:bg-surface-2 hover:text-text"
                )}
              >
                {m.level}
              </button>
            ))}

            {/* Optional — only questions rated with real minutes feed the
                pace projection (see TheoryPaceCard). Untimed ratings are
                still recorded, just not counted toward that average. */}
            <label className="flex items-center gap-1 ml-1.5">
              <input
                type="number"
                min={1}
                value={minutes}
                onChange={(e) => setMinutes(e.target.value)}
                placeholder="min"
                aria-label="Minutes spent on this question (optional)"
                className="h-6 w-12 rounded border border-border bg-surface-2 px-1.5 text-[10px] text-text tabular-nums"
              />
              <span className="text-[10px] text-text-faint">min spent</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}
