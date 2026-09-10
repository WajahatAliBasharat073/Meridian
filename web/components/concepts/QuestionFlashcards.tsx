"use client";

import { useMemo, useState } from "react";
import { Bookmark, ChevronLeft, ChevronRight, ExternalLink, Info } from "lucide-react";
import { useQuestions, useSetQuestionMastery, useSetQuestionStatus } from "@/hooks/useQuestions";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { ReferenceSolution } from "@/components/concepts/ReferenceSolution";
import { cn } from "@/lib/cn";
import {
  LEARNING_STATUS_LABELS,
  QUESTION_MASTERY,
  READY_MASTERY,
  type LearningStatus,
  type QuestionOut,
} from "@/lib/types";

/** Colour for each status, reusing the app's semantic tokens rather than
 * inventing a new palette — green/confident, amber/needs-help, red/gap. */
const STATUS_COLOR: Record<LearningStatus, string> = {
  already_know: "var(--status-done)",
  easy: "var(--status-done)",
  understood: "var(--accent-strong)",
  solved_with_help: "var(--status-partial)",
  struggled: "var(--danger)",
  no_idea: "var(--danger)",
};

const STATUS_FILTER_OPTIONS: { value: string; label: string }[] = [
  { value: "", label: "All" },
  { value: "not_attempted", label: "Not attempted" },
  ...(Object.keys(LEARNING_STATUS_LABELS) as LearningStatus[]).map((s) => ({
    value: s,
    label: LEARNING_STATUS_LABELS[s],
  })),
  { value: "needs_review", label: "Needs review" },
];

const EVIDENCE_LABEL: Record<string, string> = {
  reported: "Reported",
  common: "Commonly asked",
  fundamental: "Fundamental",
  derived: "Derived from a topic outline",
};

const EVIDENCE_HINT: Record<string, string> = {
  reported: "A named source ties this question to the companies listed.",
  common: "Appears across several independent preparation sources.",
  fundamental: "Core knowledge — no company claim is made or needed.",
  derived: "Generated from a topic outline, not a reported interview question.",
};

const DIFFICULTY_COLOR: Record<string, string> = {
  beginner: "var(--status-done)",
  intermediate: "var(--status-partial)",
  advanced: "var(--danger)",
  expert: "var(--danger)",
};

export function QuestionFlashcards({ category, module }: { category?: string; module?: string }) {
  const [statusFilter, setStatusFilter] = useState("");
  const { data: allData, isLoading } = useQuestions({ category, module });

  // "not_attempted" and "needs_review" aren't `learning_status` values —
  // they read `mastery`/`needs_review` instead — so they're applied
  // client-side over the already-fetched set rather than as a server
  // query param the API wouldn't recognise.
  const data = useMemo(() => {
    if (!allData) return allData;
    if (statusFilter === "") return allData;
    if (statusFilter === "not_attempted") return allData.filter((q) => q.mastery === 0);
    if (statusFilter === "needs_review") return allData.filter((q) => q.needs_review);
    return allData.filter((q) => q.learning_status === statusFilter);
  }, [allData, statusFilter]);

  return (
    <div>
      <div className="flex items-center justify-end mb-3">
        <Select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          aria-label="Filter by learning status"
          className="h-8 text-xs w-auto"
        >
          {STATUS_FILTER_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </Select>
      </div>

      {isLoading && <Skeleton className="h-48" />}
      {!isLoading && (!data || data.length === 0) && (
        <p className="text-xs text-text-faint py-6 text-center">
          {statusFilter
            ? "No questions match this filter."
            : "No interview questions in this section yet."}
        </p>
      )}
      {data && data.length > 0 && (
        // Keying remounts (and re-picks a starting question) on navigation
        // or when the filter changes the underlying set.
        <QuestionFlashcardsLoaded
          key={`${category ?? ""}:${module ?? ""}:${statusFilter}`}
          data={data}
        />
      )}
    </div>
  );
}

function QuestionFlashcardsLoaded({ data }: { data: QuestionOut[] }) {
  const setMastery = useSetQuestionMastery();
  const setStatus = useSetQuestionStatus();
  // Lazy initializer reads `data` once, at mount — lands on the first
  // question not yet at the readiness bar rather than always at #1.
  const [index, setIndex] = useState(() => {
    const firstUnready = data.findIndex((q) => q.mastery < READY_MASTERY);
    return firstUnready === -1 ? 0 : firstUnready;
  });

  const ready = data.filter((q) => q.mastery >= READY_MASTERY).length;
  const current = data[Math.min(index, data.length - 1)];
  const evidence = current.evidence ?? "derived";

  return (
    <div>
      <div className="flex items-center justify-between mb-3 gap-2">
        <h3 className="text-xs font-medium text-text-faint uppercase tracking-wide">
          Interview questions
        </h3>
        {/* "Ready" is mastery >= 4, not "seen" — a count of questions you
            have merely looked at would not mean anything. */}
        <span className="text-xs text-text-faint tabular-nums">
          {ready}/{data.length} at trade-off level or above
        </span>
      </div>

      <div className="flex flex-wrap gap-1.5 mb-4">
        {data.map((q, i) => (
          <button
            key={q.question_id}
            type="button"
            onClick={() => setIndex(i)}
            aria-label={`Question ${i + 1} — ${QUESTION_MASTERY[q.mastery]?.label ?? "Never seen"}`}
            aria-current={i === index ? "true" : undefined}
            className={cn(
              "h-2.5 w-2.5 rounded-full transition-all",
              i === index ? "ring-2 ring-accent ring-offset-1 ring-offset-surface" : "",
              q.mastery >= READY_MASTERY
                ? "bg-status-done"
                : q.mastery > 0
                  ? "bg-status-partial"
                  : "bg-border-strong"
            )}
          />
        ))}
      </div>

      <Card className="p-5">
        <div className="flex items-start justify-between gap-3 mb-3 flex-wrap">
          <span className="text-xs text-text-faint tabular-nums shrink-0">
            {index + 1} / {data.length}
          </span>
          <div className="flex items-center gap-1.5 flex-wrap justify-end">
            {current.priority && <Badge color="var(--accent)">{current.priority}</Badge>}
            {current.difficulty && (
              <Badge color={DIFFICULTY_COLOR[current.difficulty] ?? "var(--text-faint)"}>
                {current.difficulty}
              </Badge>
            )}
            {current.module_code && (
              <Badge color="var(--text-faint)">Module {current.module_code}</Badge>
            )}
          </div>
        </div>

        <p className="text-base text-text leading-relaxed mb-4">{current.title}</p>

        {current.tests_for && (
          <div className="mb-4 rounded-lg border border-border bg-surface-2/50 p-3">
            <p className="text-[10px] uppercase tracking-wide text-text-faint mb-1">
              What the interviewer is testing
            </p>
            <p className="text-xs text-text-muted leading-relaxed">{current.tests_for}</p>
          </div>
        )}

        {current.follow_ups.length > 0 && (
          <details className="mb-4">
            <summary className="text-xs text-accent-strong cursor-pointer">
              Follow-ups they will push on ({current.follow_ups.length})
            </summary>
            <ul className="mt-2 space-y-1.5 pl-4 list-disc marker:text-text-faint">
              {current.follow_ups.map((f) => (
                <li key={f} className="text-xs text-text-muted leading-relaxed">
                  {f}
                </li>
              ))}
            </ul>
          </details>
        )}

        {current.reference_solution && (
          <ReferenceSolution code={current.reference_solution} />
        )}

        {(current.strong_signal || current.weak_signal) && (
          <div className="mb-4 grid sm:grid-cols-2 gap-2">
            {current.strong_signal && (
              <div className="rounded-lg border border-status-done/25 bg-status-done/5 p-2.5 min-w-0">
                <p className="text-[10px] uppercase tracking-wide text-status-done mb-1">
                  Strong signal
                </p>
                <p className="text-xs text-text-muted leading-relaxed">{current.strong_signal}</p>
              </div>
            )}
            {current.weak_signal && (
              <div className="rounded-lg border border-danger/25 bg-danger/5 p-2.5 min-w-0">
                <p className="text-[10px] uppercase tracking-wide text-danger mb-1">Weak signal</p>
                <p className="text-xs text-text-muted leading-relaxed">{current.weak_signal}</p>
              </div>
            )}
          </div>
        )}

        {/* Provenance sits beside the question, not in a footnote: a
            company name is only meaningful next to how it was sourced. */}
        <div className="mb-4 flex items-center gap-2 flex-wrap text-[11px]">
          <span className="inline-flex items-center gap-1 text-text-faint" title={EVIDENCE_HINT[evidence]}>
            <Info size={11} />
            {EVIDENCE_LABEL[evidence]}
          </span>
          {current.companies.map((c) => (
            <Badge key={c} color="var(--accent-strong)">
              {c}
            </Badge>
          ))}
          {current.source_url && (
            <a
              href={current.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-text-faint hover:text-text"
            >
              {current.source} <ExternalLink size={10} />
            </a>
          )}
          {!current.source_url && <span className="text-text-faint">{current.source}</span>}
        </div>

        <div className="border-t border-border pt-3">
          <p className="text-[10px] uppercase tracking-wide text-text-faint mb-2">
            Where are you on this? (0–7)
          </p>
          <div className="flex flex-wrap gap-1.5">
            {QUESTION_MASTERY.map((m) => (
              <button
                key={m.level}
                type="button"
                disabled={setMastery.isPending}
                onClick={() =>
                  setMastery.mutate({ questionId: current.question_id, mastery: m.level })
                }
                title={`${m.level} — ${m.label}`}
                className={cn(
                  "h-8 px-2.5 rounded-md text-[11px] font-medium border transition-colors",
                  current.mastery === m.level
                    ? m.level >= READY_MASTERY
                      ? "border-status-done bg-status-done/10 text-status-done"
                      : "border-accent bg-accent-soft text-accent-strong"
                    : "border-border text-text-muted hover:bg-surface-2 hover:text-text"
                )}
              >
                {m.level}
                <span className="hidden sm:inline"> · {m.short}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="border-t border-border pt-3 mt-3">
          <div className="flex items-center justify-between mb-2">
            <p className="text-[10px] uppercase tracking-wide text-text-faint">
              How did it go?
            </p>
            {current.needs_review && (
              <span className="inline-flex items-center gap-1 text-[11px] text-status-partial">
                <Bookmark size={11} fill="currentColor" /> Flagged for revisit
              </span>
            )}
          </div>
          <div className="flex flex-wrap gap-1.5">
            {(Object.keys(LEARNING_STATUS_LABELS) as LearningStatus[]).map((s) => (
              <button
                key={s}
                type="button"
                disabled={setStatus.isPending}
                onClick={() =>
                  setStatus.mutate({
                    questionId: current.question_id,
                    // Clicking the already-selected status clears it —
                    // "how did it go" is meant to be correctable, not a
                    // one-way ratchet.
                    learning_status: current.learning_status === s ? null : s,
                  })
                }
                className={cn(
                  "h-8 px-2.5 rounded-md text-[11px] font-medium border transition-colors",
                  current.learning_status === s
                    ? "text-bg"
                    : "border-border text-text-muted hover:bg-surface-2 hover:text-text"
                )}
                style={
                  current.learning_status === s
                    ? { borderColor: STATUS_COLOR[s], backgroundColor: STATUS_COLOR[s] }
                    : undefined
                }
              >
                {LEARNING_STATUS_LABELS[s]}
              </button>
            ))}
            <button
              type="button"
              disabled={setStatus.isPending}
              onClick={() =>
                setStatus.mutate({
                  questionId: current.question_id,
                  needs_review: !current.needs_review,
                })
              }
              title={
                current.needs_review ? "Remove from revisit list" : "Flag for revisit later"
              }
              aria-pressed={current.needs_review}
              className={cn(
                "h-8 px-2.5 rounded-md text-[11px] font-medium border transition-colors inline-flex items-center gap-1",
                current.needs_review
                  ? "border-status-partial bg-status-partial/10 text-status-partial"
                  : "border-border text-text-muted hover:bg-surface-2 hover:text-text"
              )}
            >
              <Bookmark size={11} fill={current.needs_review ? "currentColor" : "none"} />
              Revisit
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between gap-2 mt-4">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setIndex((i) => Math.max(0, i - 1))}
            disabled={index === 0}
          >
            <ChevronLeft size={15} />
            Prev
          </Button>
          <span className="text-[11px] text-text-faint truncate">
            {QUESTION_MASTERY[current.mastery]?.label ?? "Never seen"}
          </span>
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
