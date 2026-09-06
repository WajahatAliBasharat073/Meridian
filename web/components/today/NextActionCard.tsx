"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MASTERY_LEVELS } from "@/lib/mastery";
import { useSubmitAttempt } from "@/hooks/useMutations";
import type { RecommendationOut, RecommendQueue } from "@/lib/types";

const QUEUE_LABEL: Record<RecommendQueue, string> = {
  FAILED_REVIEW: "Failed review",
  OVERDUE_REVIEW: "Overdue review",
  DUE_REVIEW: "Due today",
  SCHEDULED: "Today's curriculum",
  PATTERN_GAP: "Weakest pattern",
  INTERLEAVE: "Interleaved practice",
};

const DIFFICULTY_COLOR: Record<string, string> = {
  Easy: "var(--status-done)",
  Medium: "var(--status-partial)",
  Hard: "var(--danger)",
};

export function NextActionCard({ recommendation }: { recommendation: RecommendationOut | null }) {
  const [revealed, setRevealed] = useState(false);
  const [confirmation, setConfirmation] = useState<string | null>(null);
  const submitAttempt = useSubmitAttempt();

  if (!recommendation) {
    return (
      <Card className="p-6 text-center">
        <p className="text-text font-medium">Nothing due right now.</p>
        <p className="text-text-faint text-sm mt-1">Reviews and curriculum are both clear — nice.</p>
      </Card>
    );
  }

  const handleRate = (level: (typeof MASTERY_LEVELS)[number]) => {
    setConfirmation(null);
    submitAttempt.mutate(
      { problem_id: recommendation.problem_id, mastery_level: level.level },
      { onSuccess: (result) => setConfirmation(result.message) }
    );
  };

  return (
    <Card className="p-0 overflow-hidden">
      <CardHeader className="pb-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap mb-1.5">
            <Badge color="var(--accent)">{QUEUE_LABEL[recommendation.queue]}</Badge>
            <Badge color="var(--text-faint)">{recommendation.pattern.replace(/_/g, " ")}</Badge>
            <Badge color={DIFFICULTY_COLOR[recommendation.difficulty] ?? "var(--text-faint)"}>
              {recommendation.difficulty}
            </Badge>
          </div>
          <h3 className="text-lg font-semibold text-text">{recommendation.title}</h3>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <p className="text-sm text-text-muted">{recommendation.reason}</p>

        {recommendation.prior_key_insight && (
          <div className="mt-3">
            {revealed ? (
              <p className="text-sm rounded-lg bg-surface-2 p-3 text-text">
                {recommendation.prior_key_insight}
              </p>
            ) : (
              <button
                onClick={() => setRevealed(true)}
                className="text-sm text-accent underline underline-offset-2 hover:text-accent-strong"
              >
                Recall first, then reveal your last insight
              </button>
            )}
          </div>
        )}

        {confirmation ? (
          <div className="mt-4 rounded-lg border border-status-done/30 bg-status-done/10 p-3 text-sm text-text">
            {confirmation}
          </div>
        ) : (
          <fieldset className="mt-4" disabled={submitAttempt.isPending}>
            <legend className="text-xs uppercase tracking-wide text-text-faint mb-2">
              How did it go?
            </legend>
            <div className="flex flex-wrap gap-2">
              {MASTERY_LEVELS.map((m) => (
                <Button
                  key={m.level}
                  size="sm"
                  variant="secondary"
                  onClick={() => handleRate(m)}
                  className="flex-col h-auto py-2 px-3 gap-0.5"
                  style={{ borderColor: m.colorVar }}
                >
                  <span className="text-xs font-semibold" style={{ color: m.colorVar }}>
                    {m.shortLabel}
                  </span>
                  <span className="text-[11px] text-text-muted">{m.label}</span>
                </Button>
              ))}
            </div>
          </fieldset>
        )}
      </CardContent>
    </Card>
  );
}
