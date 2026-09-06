"use client";

import { useState } from "react";
import { Check } from "lucide-react";
import { useTodayReflection, useUpsertReflection } from "@/hooks/useReflection";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";
import type { Mood } from "@/lib/types";

const MOODS: { value: Mood; label: string }[] = [
  { value: "difficult", label: "Difficult" },
  { value: "normal", label: "Normal" },
  { value: "good", label: "Good" },
  { value: "excellent", label: "Excellent" },
];

/** Optional, never forced — a plain end-of-day check-in. */
export function DailyReflection() {
  const { data, isLoading } = useTodayReflection();
  const upsert = useUpsertReflection();
  const [mood, setMood] = useState<Mood | null>(null);
  const [gotInWay, setGotInWay] = useState("");
  const [wentWell, setWentWell] = useState("");
  const [expanded, setExpanded] = useState(false);

  if (isLoading) return null;

  if (data && !expanded) {
    const label = MOODS.find((m) => m.value === data.mood)?.label ?? data.mood;
    return (
      <Card className="p-4 flex items-center justify-between">
        <p className="text-sm text-text-muted">
          Today logged as <span className="text-text font-medium">{label}</span>
        </p>
        <Button variant="ghost" size="sm" onClick={() => setExpanded(true)}>
          Edit
        </Button>
      </Card>
    );
  }

  return (
    <Card className="p-4">
      <p className="text-sm font-medium text-text mb-3">How did today feel? (optional)</p>
      <div className="flex flex-wrap gap-2 mb-3">
        {MOODS.map((m) => (
          <button
            key={m.value}
            type="button"
            onClick={() => setMood(m.value)}
            className={cn(
              "h-9 px-3 rounded-lg text-sm border transition-colors",
              (mood ?? data?.mood) === m.value
                ? "border-accent bg-accent-soft text-accent-strong"
                : "border-border text-text-muted hover:bg-surface-2"
            )}
          >
            {m.label}
          </button>
        ))}
      </div>

      {(mood ?? data?.mood) && (
        <div className="space-y-2 mb-3">
          <textarea
            value={gotInWay || data?.what_got_in_the_way || ""}
            onChange={(e) => setGotInWay(e.target.value)}
            placeholder="What got in your way? (optional)"
            rows={2}
            className="w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-sm text-text resize-none"
          />
          <textarea
            value={wentWell || data?.what_went_well || ""}
            onChange={(e) => setWentWell(e.target.value)}
            placeholder="What went well? (optional)"
            rows={2}
            className="w-full rounded-lg border border-border bg-surface-2 px-3 py-2 text-sm text-text resize-none"
          />
        </div>
      )}

      <Button
        variant="primary"
        size="sm"
        disabled={!(mood ?? data?.mood) || upsert.isPending}
        onClick={() => {
          const finalMood = mood ?? data?.mood;
          if (!finalMood) return;
          upsert.mutate(
            {
              mood: finalMood,
              what_got_in_the_way: gotInWay || data?.what_got_in_the_way || undefined,
              what_went_well: wentWell || data?.what_went_well || undefined,
            },
            { onSuccess: () => setExpanded(false) }
          );
        }}
      >
        <Check size={14} /> Save
      </Button>
    </Card>
  );
}
