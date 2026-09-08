"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowRight, BrainCircuit, Calendar, Droplets, Sparkles } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  generateContextualRecommendations,
  type ContextualRecommendation,
} from "@/lib/recommendationEngine";
import type { RecommendationOut, TimeBlockOut } from "@/lib/types";

export function MeridianRecommends({
  blocks = [],
  dsaRec = null,
  currentBlock = null,
}: {
  blocks?: TimeBlockOut[];
  dsaRec?: RecommendationOut | null;
  currentBlock?: TimeBlockOut | null;
}) {
  const recommendations = generateContextualRecommendations(blocks, dsaRec, currentBlock);
  const [selectedIdx, setSelectedIdx] = useState(0);

  if (recommendations.length === 0) return null;
  const activeRec = recommendations[selectedIdx] || recommendations[0];

  const getIcon = (cat: ContextualRecommendation["category"]) => {
    switch (cat) {
      case "spaced_repetition":
        return <BrainCircuit size={15} className="text-accent-strong" />;
      case "focus_window":
        return <Sparkles size={15} className="text-warning" />;
      case "recovery":
        return <Droplets size={15} className="text-accent" />;
      case "schedule_gap":
      default:
        return <Calendar size={15} className="text-status-done" />;
    }
  };

  return (
    <Card className="p-5 border-border-strong bg-gradient-to-br from-surface to-surface-2/60">
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          <Sparkles size={16} className="text-accent-strong" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-text-muted">
            Meridian Recommends
          </h3>
        </div>
        <div className="flex items-center gap-1">
          {recommendations.map((_, i) => (
            <button
              key={i}
              onClick={() => setSelectedIdx(i)}
              className={`h-1.5 rounded-full transition-all ${
                selectedIdx === i ? "w-5 bg-accent-strong" : "w-1.5 bg-border hover:bg-border-strong"
              }`}
              aria-label={`View recommendation ${i + 1}`}
            />
          ))}
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 mb-1">
              {getIcon(activeRec.category)}
              <h4 className="text-sm font-semibold text-text truncate">{activeRec.title}</h4>
            </div>
            <p className="text-xs text-text-muted leading-relaxed">{activeRec.reason}</p>
          </div>
        </div>

        <div className="pt-2 border-t border-border flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-1.5">
            <Badge color="var(--accent-soft)">
              {activeRec.category.replace("_", " ").toUpperCase()}
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            {activeRec.actionType === "study" && activeRec.problemId ? (
              <Link href="/problems">
                <Button variant="primary" size="sm" className="gap-1">
                  Solve problem <ArrowRight size={13} />
                </Button>
              </Link>
            ) : (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setSelectedIdx((selectedIdx + 1) % recommendations.length)}
              >
                Next suggestion
              </Button>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}
