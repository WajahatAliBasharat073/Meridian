"use client";

import { useState } from "react";
import { ExternalLink } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MASTERY_LEVELS, masteryMeta } from "@/lib/mastery";
import { useSubmitConceptAttempt } from "@/hooks/useConcepts";
import type { ConceptOut } from "@/lib/types";

const PHASE_COLOR: Record<string, string> = {
  foundation: "var(--accent)",
  core: "var(--status-partial)",
  advanced: "var(--danger)",
};

export function ConceptCard({ concept }: { concept: ConceptOut }) {
  const [rating, setRating] = useState(false);
  const [confirmation, setConfirmation] = useState<string | null>(null);
  const submitAttempt = useSubmitConceptAttempt();
  const mastery = concept.current_mastery ? masteryMeta(concept.current_mastery) : null;

  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3 mb-1.5">
        <h3 className="text-sm font-semibold text-text">{concept.title}</h3>
        {mastery ? (
          <Badge color={mastery.colorVar} className="shrink-0">
            {mastery.shortLabel} · {mastery.label}
          </Badge>
        ) : (
          <span className="shrink-0 text-xs text-text-faint">Not rated</span>
        )}
      </div>

      <div className="flex items-center gap-2 mb-2">
        <Badge color={PHASE_COLOR[concept.phase] ?? "var(--text-faint)"}>{concept.phase}</Badge>
      </div>

      <p className="text-sm text-text-muted leading-relaxed mb-3">{concept.summary}</p>

      {concept.resources.length > 0 && (
        <ul className="flex flex-wrap gap-2 mb-3">
          {concept.resources.map((r, i) =>
            r.url ? (
              <li key={i}>
                <a
                  href={r.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-accent-strong hover:underline"
                >
                  {r.label}
                  <ExternalLink size={11} />
                </a>
              </li>
            ) : (
              <li key={i} className="text-xs text-text-faint">
                {r.label}
              </li>
            )
          )}
        </ul>
      )}

      {confirmation ? (
        <p className="text-xs text-status-done">{confirmation}</p>
      ) : rating ? (
        <fieldset disabled={submitAttempt.isPending} className="flex flex-wrap gap-1.5">
          {MASTERY_LEVELS.map((m) => (
            <button
              key={m.level}
              type="button"
              onClick={() => {
                setConfirmation(null);
                submitAttempt.mutate(
                  { concept_id: concept.concept_id, mastery_level: m.level },
                  {
                    onSuccess: (result) => {
                      setConfirmation(result.message);
                      setRating(false);
                    },
                  }
                );
              }}
              className="h-8 px-2 rounded-md text-xs font-medium border"
              style={{ borderColor: m.colorVar, color: m.colorVar }}
            >
              {m.shortLabel}
            </button>
          ))}
        </fieldset>
      ) : (
        <Button variant="ghost" size="sm" onClick={() => setRating(true)} className="px-0">
          Rate my understanding
        </Button>
      )}
    </Card>
  );
}
