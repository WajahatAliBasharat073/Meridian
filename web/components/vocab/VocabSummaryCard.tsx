"use client";

import { Card } from "@/components/ui/card";
import { useVocabSummary } from "@/hooks/useVocab";
import { VOCAB_STATUS_LABELS, type VocabLearningStatus } from "@/lib/types";

const STATUS_COLOR: Record<VocabLearningStatus, string> = {
  known: "var(--status-done)",
  learning: "var(--accent-strong)",
  difficult: "var(--status-partial)",
  need_to_revisit: "var(--danger)",
};

export function VocabSummaryCard() {
  const { data, isLoading } = useVocabSummary();

  if (isLoading || !data) {
    return <Card className="p-4 h-[150px] animate-pulse" />;
  }

  const attemptedPct = data.total_words > 0 ? Math.round((data.attempted_count / data.total_words) * 100) : null;
  const statusCounts: { status: VocabLearningStatus; count: number }[] = [
    { status: "known", count: data.known_count },
    { status: "learning", count: data.learning_count },
    { status: "difficult", count: data.difficult_count },
    { status: "need_to_revisit", count: data.need_to_revisit_count },
  ];
  const maxLevelCount = Math.max(1, ...data.by_level.map(([, count]) => count));

  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3 mb-3 flex-wrap">
        <div>
          <p className="text-xs font-medium text-text-faint uppercase tracking-wide">Vocabulary progress</p>
          <p className="text-2xl font-semibold tracking-tight tabular-nums text-text mt-1">
            {attemptedPct != null ? `${attemptedPct}%` : "—"}
            <span className="text-text-faint text-base font-normal ml-1.5">
              ({data.attempted_count}/{data.total_words} attempted)
            </span>
          </p>
          <p className="text-xs text-text-faint mt-0.5">{data.not_attempted_count} not attempted yet</p>
        </div>

        <div className="flex gap-4">
          {statusCounts.map(({ status, count }) => (
            <div key={status} className="text-center">
              <div className="text-lg font-semibold tabular-nums" style={{ color: STATUS_COLOR[status] }}>
                {count}
              </div>
              <div className="text-[10px] text-text-faint uppercase tracking-wide whitespace-nowrap">
                {VOCAB_STATUS_LABELS[status]}
              </div>
            </div>
          ))}
        </div>
      </div>

      {data.by_level.length > 0 && (
        <div className="space-y-1.5 mt-3">
          {data.by_level.map(([level, count]) => (
            <div key={level} className="flex items-center gap-2">
              <span className="text-xs text-text-muted w-6 shrink-0">{level}</span>
              <div className="h-1.5 rounded-full bg-surface-2 overflow-hidden flex-1">
                <div
                  className="h-full rounded-full bg-accent"
                  style={{ width: `${(count / maxLevelCount) * 100}%` }}
                />
              </div>
              <span className="text-xs text-text-faint tabular-nums w-8 text-right shrink-0">{count}</span>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
