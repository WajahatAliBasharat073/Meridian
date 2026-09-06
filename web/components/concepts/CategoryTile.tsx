"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import type { CategoryMeta } from "@/lib/conceptCategories";

export function CategoryTile({
  meta,
  topicsRated,
  topicsTotal,
  questionsCovered,
  questionsTotal,
}: {
  meta: CategoryMeta;
  topicsRated: number;
  topicsTotal: number;
  questionsCovered: number;
  questionsTotal: number;
}) {
  const Icon = meta.icon;
  const questionsPct = questionsTotal > 0 ? Math.round((questionsCovered / questionsTotal) * 100) : 0;

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

        <h3 className="text-sm font-semibold text-text mb-1">{meta.label}</h3>
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
                <span className="text-text-faint">Questions covered</span>
                <span className="text-text-muted tabular-nums">
                  {questionsCovered}/{questionsTotal}
                </span>
              </div>
              <div className="h-1.5 rounded-full bg-surface-2 overflow-hidden">
                <div className="h-full rounded-full bg-accent" style={{ width: `${questionsPct}%` }} />
              </div>
            </div>
          )}
          {topicsTotal === 0 && questionsTotal === 0 && (
            <p className="text-[11px] text-text-faint">Nothing here yet</p>
          )}
        </div>
      </Card>
    </Link>
  );
}
