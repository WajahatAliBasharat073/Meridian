"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Brain, Check, Loader2, RotateCcw, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert } from "@/components/ui/alert";
import { getConceptDrill, gradeConceptDrill } from "@/lib/api";
import { cn } from "@/lib/cn";
import type { ConceptDrillKind, ConceptDrillResultOut } from "@/lib/types";

const KIND_LABEL: Record<ConceptDrillKind, string> = {
  complexity: "Complexity",
  variant: "Variant",
  pitfall: "Pitfall",
  technique: "Technique",
};

const KIND_COLOR: Record<ConceptDrillKind, string> = {
  complexity: "var(--accent)",
  variant: "var(--mastery-l4)",
  pitfall: "var(--status-partial)",
  technique: "var(--mastery-l5)",
};

/** The topic gate: twelve multiple-choice questions, 80% opens the
 * problems.
 *
 * This replaced a build-then-defend flow (implement the structure, then
 * answer LLM-generated closed-book questions about your own code). That
 * proved authorship, which multiple choice cannot — but it was a wall on
 * day one of a topic, it cost an LLM call per attempt so it couldn't be
 * repeated, and it refused to pass a topic at all when the LLM was
 * unreachable.
 *
 * Every question and distractor here is a curated string from the topic
 * guide — complexities, which variant to reach for, what breaks, which
 * technique fits — graded in-process from the same data. So it's
 * instant, free, offline-safe, and repeatable. The trade is honest:
 * recognising that insertion is O(n) is not the same as writing Kadane's
 * from memory. */
export function ConceptDrill({ topic, displayName }: { topic: string; displayName: string }) {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  // Bumped to start a fresh drill; also the react-query cache key, so a
  // retry re-fetches rather than replaying the same twelve questions.
  const [round, setRound] = useState(0);
  const [answers, setAnswers] = useState<(number | null)[]>([]);
  const [result, setResult] = useState<ConceptDrillResultOut | null>(null);

  const drill = useQuery({
    queryKey: ["concept-drill", topic, round],
    queryFn: () => getConceptDrill(topic),
    enabled: open,
    // Each round is a fresh sample by design, so nothing here is worth
    // serving from cache on remount.
    gcTime: 0,
    staleTime: 0,
  });

  const grade = useMutation({
    mutationFn: () => gradeConceptDrill(topic, { seed: drill.data!.seed, answers }),
    onSuccess: (graded) => {
      setResult(graded);
      // A pass unlocks the problems, so the topic list has to re-read its
      // gate state rather than keep showing the padlock.
      if (graded.passed) {
        void queryClient.invalidateQueries({ queryKey: ["problems-by-topic"] });
      }
    },
  });

  const start = () => {
    setOpen(true);
    setResult(null);
    setAnswers([]);
  };

  const restart = () => {
    setResult(null);
    setAnswers([]);
    setRound((r) => r + 1);
  };

  if (!open) {
    return (
      <div className="rounded-xl border border-border bg-surface-2/30 p-3.5 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h4 className="text-xs font-semibold text-text flex items-center gap-1.5">
            <Brain size={13} className="text-accent-strong shrink-0" />
            Concept check
          </h4>
          <p className="text-[11px] text-text-muted mt-1 leading-relaxed">
            Twelve questions on {displayName} — complexities, which variant to reach for,
            what breaks, which technique fits. Score 80% and the problems unlock. Graded
            instantly, and you can retake it as often as you like.
          </p>
        </div>
        <Button variant="secondary" size="sm" onClick={start} className="gap-1.5 shrink-0">
          Start
        </Button>
      </div>
    );
  }

  const questions = drill.data?.questions ?? [];
  const answered = answers.filter((a) => a != null).length;

  return (
    <div className="rounded-xl border border-border bg-surface-2/30 p-3.5 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h4 className="text-xs font-semibold text-text flex items-center gap-1.5">
            <Brain size={13} className="text-accent-strong shrink-0" />
            Concept check — {displayName}
          </h4>
          {drill.data && !result && (
            <p className="text-[11px] text-text-faint mt-0.5 tabular-nums">
              {answered}/{questions.length} answered · sampled from {drill.data.bank_size}{" "}
              questions
            </p>
          )}
        </div>
        <button
          onClick={() => setOpen(false)}
          className="text-text-faint hover:text-text shrink-0"
          aria-label="Close concept check"
        >
          <X size={15} />
        </button>
      </div>

      {drill.isLoading && (
        <p className="text-[11px] text-text-faint flex items-center gap-1.5">
          <Loader2 size={12} className="animate-spin" /> Building a drill…
        </p>
      )}

      {drill.isError && (
        <Alert variant="error">Couldn&apos;t load a drill for this topic.</Alert>
      )}

      {/* ---------------- Result ---------------- */}
      {result && (
        <>
          <Alert variant={result.passed ? "success" : "info"}>
            {result.correct_count}/{result.total} — {Math.round(result.score * 100)}%.{" "}
            {result.passed ? (
              <>
                Passed. {displayName} is unlocked
                {result.gate?.days_until_expiry != null &&
                  ` for ${result.gate.days_until_expiry} days`}
                .
              </>
            ) : (
              <>
                {Math.round(result.pass_threshold * 100)}% unlocks the problems — re-read
                the guide above and take it again. Every wrong answer is explained below.
              </>
            )}
          </Alert>

          <ol className="space-y-2">
            {result.grades.map((g, i) => (
              <li
                key={g.id}
                className={cn(
                  "rounded-lg border p-2.5",
                  g.correct
                    ? "border-status-done/30 bg-status-done/5"
                    : "border-danger/30 bg-danger/5"
                )}
              >
                <p className="text-[11px] font-medium text-text flex items-start gap-1.5">
                  {g.correct ? (
                    <Check size={12} className="text-status-done shrink-0 mt-0.5" />
                  ) : (
                    <X size={12} className="text-danger shrink-0 mt-0.5" />
                  )}
                  <span>
                    {i + 1}. {g.prompt}
                  </span>
                </p>
                {!g.correct && (
                  <p className="text-[11px] text-text-muted mt-1.5 ml-4">
                    {g.chosen_index == null ? (
                      <span className="text-text-faint">Left blank. </span>
                    ) : (
                      <>
                        You said{" "}
                        <span className="text-danger">{g.options[g.chosen_index]}</span>.{" "}
                      </>
                    )}
                    Answer:{" "}
                    <span className="text-status-done">{g.options[g.answer_index]}</span>
                  </p>
                )}
                {g.explanation && (
                  <p className="text-[11px] text-text-faint mt-1 ml-4 leading-relaxed">
                    {g.explanation}
                  </p>
                )}
              </li>
            ))}
          </ol>

          <div className="flex justify-end">
            <Button variant="secondary" size="sm" onClick={restart} className="gap-1.5">
              <RotateCcw size={13} /> New set of 12
            </Button>
          </div>
        </>
      )}

      {/* ---------------- Questions ---------------- */}
      {!result && questions.length > 0 && (
        <>
          <ol className="space-y-3">
            {questions.map((q, i) => (
              <li key={q.id}>
                <div className="flex items-start gap-2">
                  <Badge color={KIND_COLOR[q.kind]}>{KIND_LABEL[q.kind]}</Badge>
                  <p className="text-[11px] font-medium text-text leading-relaxed">
                    {i + 1}. {q.prompt}
                  </p>
                </div>
                <div className="mt-1.5 ml-1 grid gap-1">
                  {q.options.map((option, oi) => {
                    const picked = answers[i] === oi;
                    return (
                      <label
                        key={oi}
                        className={cn(
                          "flex items-start gap-2 rounded-md border px-2 py-1.5 cursor-pointer text-[11px] transition-colors",
                          picked
                            ? "border-accent bg-accent-soft text-text"
                            : "border-border bg-surface-2/40 text-text-muted hover:text-text hover:bg-surface-2"
                        )}
                      >
                        <input
                          type="radio"
                          name={q.id}
                          checked={picked}
                          onChange={() =>
                            setAnswers((prev) => {
                              const next = [...prev];
                              // Sparse until answered, so unanswered
                              // questions stay null rather than 0.
                              while (next.length < questions.length) next.push(null);
                              next[i] = oi;
                              return next;
                            })
                          }
                          className="mt-0.5 shrink-0 accent-accent"
                        />
                        <span>{option}</span>
                      </label>
                    );
                  })}
                </div>
              </li>
            ))}
          </ol>

          <div className="flex items-center justify-between gap-2">
            <p className="text-[11px] text-text-faint">
              Unanswered counts as wrong.
            </p>
            <Button
              variant="primary"
              size="sm"
              disabled={grade.isPending}
              onClick={() => grade.mutate()}
              className="gap-1.5"
            >
              {grade.isPending ? (
                <>
                  <Loader2 size={13} className="animate-spin" /> Grading…
                </>
              ) : (
                <>Submit</>
              )}
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
