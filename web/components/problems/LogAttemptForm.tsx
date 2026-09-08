"use client";

import { useState } from "react";
import { Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { MASTERY_LEVELS } from "@/lib/mastery";
import { SOLVE_METHODS } from "@/lib/solveMethod";
import { cn } from "@/lib/cn";
import type { MasteryLevel, SolveMethod } from "@/lib/types";

/** Two independent questions, asked separately on purpose:
 *  - mastery level: how well do you know this *now*
 *  - solve method:  how much help did this attempt actually take
 *  Collapsing them into one scale is what makes "solved it, but only after
 *  the video" impossible to see later. */

export function LogAttemptForm({
  problemTitle,
  onSubmit,
  onCancel,
  isPending,
  previousNotes,
  previousKeyInsight,
}: {
  problemTitle: string;
  onSubmit: (input: {
    mastery_level: MasteryLevel;
    solve_method: SolveMethod;
    minutes?: number;
    understood_approach_independently?: boolean;
    reached_optimal?: boolean;
    key_insight?: string;
    notes?: string;
  }) => void;
  onCancel: () => void;
  isPending: boolean;
  /** Carried over from the last attempt so a re-log starts from what you
   * already wrote instead of a blank box. */
  previousNotes?: string | null;
  previousKeyInsight?: string | null;
}) {
  const [mastery, setMastery] = useState<MasteryLevel | null>(null);
  const [method, setMethod] = useState<SolveMethod | null>(null);
  const [minutes, setMinutes] = useState("");
  const [understood, setUnderstood] = useState<boolean | null>(null);
  const [optimal, setOptimal] = useState<boolean | null>(null);
  const [insight, setInsight] = useState(previousKeyInsight ?? "");
  const [notes, setNotes] = useState(previousNotes ?? "");

  const canSave = mastery !== null && method !== null;

  return (
    <div className="border-t border-border pt-3 mt-3 space-y-3">
      <p className="text-xs text-text-faint">
        Logging an attempt for <span className="text-text-muted">{problemTitle}</span>
      </p>

      <div>
        <p className="text-[11px] uppercase tracking-wide text-text-faint mb-1.5">
          How well do you know it now?
        </p>
        <div className="flex flex-wrap gap-1.5">
          {MASTERY_LEVELS.map((m) => (
            <button
              key={m.level}
              type="button"
              onClick={() => setMastery(m.level)}
              className={cn(
                "h-8 px-2.5 rounded-md text-xs font-medium border transition-colors",
                mastery === m.level ? "bg-surface-2" : "hover:bg-surface-2"
              )}
              style={{
                borderColor: mastery === m.level ? m.colorVar : "var(--border)",
                color: m.colorVar,
              }}
              title={m.label}
            >
              {m.shortLabel} · {m.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <p className="text-[11px] uppercase tracking-wide text-text-faint mb-1.5">
          How did you get there?
        </p>
        <div className="flex flex-wrap gap-1.5">
          {SOLVE_METHODS.map((s) => (
            <button
              key={s.value}
              type="button"
              onClick={() => setMethod(s.value)}
              title={s.hint}
              className={cn(
                "h-8 px-2.5 rounded-md text-xs font-medium border transition-colors",
                method === s.value
                  ? "border-accent bg-accent-soft text-accent-strong"
                  : "border-border text-text-muted hover:bg-surface-2 hover:text-text"
              )}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap gap-x-5 gap-y-2 items-center">
        <label className="text-xs text-text-faint flex items-center gap-2">
          Minutes
          <input
            type="number"
            min={1}
            value={minutes}
            onChange={(e) => setMinutes(e.target.value)}
            placeholder="—"
            className="h-8 w-20 rounded-md border border-border bg-surface-2 px-2 text-sm text-text tabular-nums"
          />
        </label>

        <Tri label="Worked out the approach yourself" value={understood} onChange={setUnderstood} />
        <Tri label="Reached optimal complexity" value={optimal} onChange={setOptimal} />
      </div>

      {/* Two writing fields with different jobs: the one-liner comes back
          at review time as a recall prompt, the notes stay with the
          problem for when you actually revisit it. */}
      <div>
        <label
          htmlFor="key-insight"
          className="block text-[11px] uppercase tracking-wide text-text-faint mb-1.5"
        >
          Key insight — shown when this comes back for review
        </label>
        <input
          id="key-insight"
          type="text"
          value={insight}
          onChange={(e) => setInsight(e.target.value)}
          placeholder="One line you'd want to see before trying this again"
          className="h-9 w-full rounded-md border border-border bg-surface-2 px-2.5 text-sm text-text"
        />
      </div>

      <div>
        <label
          htmlFor="attempt-notes"
          className="block text-[11px] uppercase tracking-wide text-text-faint mb-1.5"
        >
          Notes
        </label>
        <textarea
          id="attempt-notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={4}
          placeholder="The approach, the edge case that caught you, complexity, what you'd do differently…"
          className="w-full rounded-md border border-border bg-surface-2 px-2.5 py-2 text-sm text-text leading-relaxed resize-y"
        />
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="primary"
          size="sm"
          disabled={!canSave || isPending}
          onClick={() =>
            onSubmit({
              mastery_level: mastery!,
              solve_method: method!,
              minutes: minutes ? Number(minutes) : undefined,
              understood_approach_independently: understood ?? undefined,
              reached_optimal: optimal ?? undefined,
              key_insight: insight.trim() || undefined,
              notes: notes.trim() || undefined,
            })
          }
        >
          <Check size={14} /> {isPending ? "Saving…" : "Log attempt"}
        </Button>
        <Button variant="ghost" size="sm" onClick={onCancel}>
          <X size={14} /> Cancel
        </Button>
        {!canSave && (
          <span className="text-[11px] text-text-faint">
            Pick a level and how you got there.
          </span>
        )}
      </div>
    </div>
  );
}

/** Yes / no / unanswered — unanswered stays unanswered rather than
 * defaulting to "no", which would be a claim we didn't make. */
function Tri({
  label,
  value,
  onChange,
}: {
  label: string;
  value: boolean | null;
  onChange: (v: boolean | null) => void;
}) {
  return (
    <div className="flex items-center gap-1.5">
      <span className="text-xs text-text-faint">{label}</span>
      {[
        { v: true, t: "Yes" },
        { v: false, t: "No" },
      ].map(({ v, t }) => (
        <button
          key={t}
          type="button"
          onClick={() => onChange(value === v ? null : v)}
          className={cn(
            "h-7 px-2 rounded-md text-[11px] font-medium border transition-colors",
            value === v
              ? v
                ? "border-status-done text-status-done bg-status-done/10"
                : "border-border-strong text-text-muted bg-surface-2"
              : "border-border text-text-faint hover:bg-surface-2"
          )}
        >
          {t}
        </button>
      ))}
    </div>
  );
}
