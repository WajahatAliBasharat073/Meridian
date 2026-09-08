"use client";

import Link from "next/link";
import { ArrowRight, BookOpen } from "lucide-react";
import { Card } from "@/components/ui/card";
import type { CategoryMeta } from "@/lib/conceptCategories";

export function CategoryTile({
  meta,
  topicsRated,
  topicsTotal,
  questionsCovered,
  questionsStarted = 0,
  questionsTotal,
  resourceCount = 0,
}: {
  meta: CategoryMeta;
  topicsRated: number;
  topicsTotal: number;
  /** Ready: mastery >= 4. */
  questionsCovered: number;
  /** Attempted: rated at all (mastery >= 1). */
  questionsStarted?: number;
  questionsTotal: number;
  resourceCount?: number;
}) {
  const Icon = meta.icon;
  const questionsPct = questionsTotal > 0 ? (questionsCovered / questionsTotal) * 100 : 0;
  const startedPct = questionsTotal > 0 ? (questionsStarted / questionsTotal) * 100 : 0;

  return (
    <Link href={`/concepts/${meta.key}`}>
      <Card className="p-4 h-full flex flex-col hover:border-border-strong hover:bg-surface-2 transition-colors group">
        <div className="flex items-start justify-between mb-3">
          <span className="h-9 w-9 rounded-lg bg-accent-soft text-accent-strong flex items-center justify-center shrink-0">
            <Icon size={17} />
          </span>
          <ArrowRight
            size={16}
            className="text-text-faint group-hover:text-text-muted group-hover:translate-x-0.5 transition-all mt-1.5"
          />
        </div>

        <div className="flex items-center gap-2 mb-1 flex-wrap">
          <h3 className="text-sm font-semibold text-text">{meta.label}</h3>
          {meta.modules.map((m) => (
            <span
              key={m}
              title={`Module ${m} in the curriculum`}
              className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-2 border border-border text-text-faint"
            >
              {m}
            </span>
          ))}
        </div>
        <p className="text-xs text-text-muted leading-relaxed mb-4 flex-1">{meta.description}</p>

        <div className="space-y-2">
          {topicsTotal > 0 && (
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-text-faint">Topics rated</span>
              <span className="text-text-muted tabular-nums">
                {topicsRated}/{topicsTotal}
              </span>
            </div>
          )}
          {questionsTotal > 0 && (
            <div>
              <div className="flex items-center justify-between text-[11px] mb-1">
                {/* "Ready" is mastery >= 4, not "seen" — see READY_MASTERY. */}
                <span className="text-text-faint">
                  {questionsStarted > 0 ? `${questionsStarted} attempted` : "Questions"}
                </span>
                <span className="text-text-muted tabular-nums">
                  {questionsCovered}/{questionsTotal} ready
                </span>
              </div>
              {/* Two segments: attempted behind, ready in front — the gap
                  between them is the work still to do. */}
              <div className="h-1.5 rounded-full bg-surface-2 overflow-hidden relative">
                <div
                  className="absolute inset-y-0 left-0 bg-accent/35"
                  style={{ width: `${startedPct}%` }}
                />
                <div
                  className="absolute inset-y-0 left-0 bg-status-done"
                  style={{ width: `${questionsPct}%` }}
                />
              </div>
            </div>
          )}
          {resourceCount > 0 && (
            <div className="flex items-center gap-1.5 text-[11px] text-text-faint pt-0.5">
              <BookOpen size={11} className="shrink-0" />
              {resourceCount} resource{resourceCount === 1 ? "" : "s"}
            </div>
          )}
          {topicsTotal === 0 && questionsTotal === 0 && resourceCount === 0 && (
            <p className="text-[11px] text-text-faint">Nothing here yet</p>
          )}
        </div>
      </Card>
    </Link>
  );
}
