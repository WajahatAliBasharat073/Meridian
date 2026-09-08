"use client";

import { useState } from "react";
import {
  CheckCircle2,
  Circle,
  CircleDashed,
  CircleSlash,
  ExternalLink,
  Pencil,
  StickyNote,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LogAttemptForm } from "@/components/problems/LogAttemptForm";
import { useSubmitAttempt } from "@/hooks/useMutations";
import { masteryMeta } from "@/lib/mastery";
import { SOLVE_METHOD_LABELS, isAssisted } from "@/lib/solveMethod";
import type { ProblemOut } from "@/lib/types";

export const DIFFICULTY_COLOR: Record<string, string> = {
  Easy: "var(--status-done)",
  Medium: "var(--status-partial)",
  Hard: "var(--danger)",
};

/** The row's completion state, at a glance.
 *
 * Four states rather than a checkbox, because "done" isn't binary here:
 * solved alone and solved after watching the editorial are both attempts,
 * and flattening them into one tick is what makes progress look better
 * than it is. */
function attemptStatus(p: ProblemOut): {
  Icon: typeof Circle;
  color: string;
  label: string;
  done: boolean;
} {
  if (p.attempt_count === 0) {
    return { Icon: Circle, color: "var(--text-faint)", label: "Not attempted", done: false };
  }
  if (p.last_solve_method === "not_solved") {
    return {
      Icon: CircleSlash,
      color: "var(--danger)",
      label: "Attempted, not solved",
      done: false,
    };
  }
  if (p.last_solve_method && isAssisted(p.last_solve_method)) {
    return {
      Icon: CircleDashed,
      color: "var(--status-partial)",
      label: `Solved with help — ${SOLVE_METHOD_LABELS[p.last_solve_method]}`,
      done: true,
    };
  }
  return { Icon: CheckCircle2, color: "var(--status-done)", label: "Solved unaided", done: true };
}

/** "today" / "yesterday" / "3 Sep" — a date is more useful than a
 * timestamp for something logged once a day. */
function formatWhen(iso: string): string {
  const then = new Date(iso);
  if (Number.isNaN(then.getTime())) return "—";
  const startOfDay = (d: Date) => new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
  const days = Math.round((startOfDay(new Date()) - startOfDay(then)) / 86_400_000);
  if (days === 0) return "today";
  if (days === 1) return "yesterday";
  if (days > 1 && days < 7) return `${days} days ago`;
  return then.toLocaleDateString(undefined, { day: "numeric", month: "short" });
}

export function ProblemRow({ problem: p }: { problem: ProblemOut }) {
  const [isOpen, setIsOpen] = useState(false);
  const submitAttempt = useSubmitAttempt();
  const mastery = p.current_mastery ? masteryMeta(p.current_mastery) : null;
  const status = attemptStatus(p);
  const hasWriting = Boolean(p.last_key_insight || p.last_notes);
  const toggle = () => setIsOpen((v) => !v);

  return (
    <Card className="p-3.5">
      <div className="flex items-start gap-3">
        {/* The status control *is* the way to mark it done — one visible
            affordance rather than a hidden one. */}
        <button
          type="button"
          onClick={toggle}
          aria-expanded={isOpen}
          aria-label={`${status.label} — log an attempt for ${p.title}`}
          title={status.label}
          className="h-9 w-9 mt-0.5 shrink-0 flex items-center justify-center rounded-lg hover:bg-surface-2 transition-colors"
          style={{ color: status.color }}
        >
          <status.Icon size={20} strokeWidth={status.done ? 2.25 : 1.75} />
        </button>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            {/* A classic algorithm has no LeetCode number — say so rather
                than printing "#null". */}
            {p.lc_number != null ? (
              <span className="text-xs text-text-faint tabular-nums">#{p.lc_number}</span>
            ) : (
              <span className="text-xs text-text-faint">classic</span>
            )}
            <span className="text-sm font-medium text-text">{p.title}</span>
            {p.is_scheduled_today && <Badge color="var(--accent)">Today</Badge>}
          </div>

          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
            <Badge color={DIFFICULTY_COLOR[p.difficulty] ?? "var(--text-faint)"}>
              {p.difficulty}
            </Badge>
            <Badge color="var(--text-faint)">{p.pattern.replace(/_/g, " ")}</Badge>
            {mastery ? (
              <Badge color={mastery.colorVar}>
                {mastery.shortLabel} · {mastery.label}
              </Badge>
            ) : (
              <span className="text-xs text-text-faint">Not attempted</span>
            )}
            {p.last_solve_method && (
              <Badge
                color={
                  isAssisted(p.last_solve_method)
                    ? "var(--status-partial)"
                    : "var(--status-done)"
                }
              >
                {SOLVE_METHOD_LABELS[p.last_solve_method]}
              </Badge>
            )}
          </div>

          {/* Who asks it. The "+N" is the source sheet's own truncation,
              shown as a count because the names were never listed. */}
          {(p.companies.length > 0 || p.company_extra_count > 0) && (
            <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
              {p.companies.map((c) => (
                <span
                  key={c}
                  className="text-[11px] px-1.5 py-0.5 rounded-md bg-surface-2 border border-border text-text-muted"
                >
                  {c}
                </span>
              ))}
              {p.company_extra_count > 0 && (
                <span
                  className="text-[11px] text-text-faint"
                  title={`The source sheet lists ${p.company_extra_count} more companies without naming them`}
                >
                  +{p.company_extra_count} more
                </span>
              )}
            </div>
          )}

          {/* What was actually recorded, in plain words. */}
          {p.attempt_count > 0 && (
            <p className="text-xs text-text-faint mt-1.5">
              {p.attempt_count} attempt{p.attempt_count === 1 ? "" : "s"}
              {p.last_minutes != null && <> · {p.last_minutes}m</>}
              {p.last_attempted_at && <> · last {formatWhen(p.last_attempted_at)}</>}
            </p>
          )}

          {hasWriting && (
            <details className="mt-2 group">
              <summary className="text-xs text-accent-strong cursor-pointer inline-flex items-center gap-1 list-none">
                <StickyNote size={12} />
                My notes
              </summary>
              <div className="mt-2 rounded-lg border border-border bg-surface-2/50 p-2.5 space-y-2">
                {p.last_key_insight && (
                  <p className="text-xs text-text-muted">
                    <span className="text-text-faint">Key insight: </span>
                    {p.last_key_insight}
                  </p>
                )}
                {p.last_notes && (
                  <p className="text-xs text-text-muted whitespace-pre-wrap leading-relaxed">
                    {p.last_notes}
                  </p>
                )}
              </div>
            </details>
          )}
        </div>

        <button
          type="button"
          onClick={toggle}
          aria-expanded={isOpen}
          className="h-9 px-2.5 shrink-0 flex items-center gap-1.5 text-xs font-medium text-text-muted hover:text-text rounded-lg border border-border hover:bg-surface-2"
        >
          {isOpen ? (
            "Close"
          ) : (
            <>
              <Pencil size={13} />
              <span className="hidden sm:inline">
                {p.attempt_count > 0 ? "Log again" : "Mark done"}
              </span>
            </>
          )}
        </button>

        {/* No link for a classic with no canonical page — an empty href
            that goes nowhere is worse than no button. */}
        {p.url ? (
          <a
            href={p.url}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`Open ${p.title} on LeetCode`}
            className="h-9 w-9 shrink-0 flex items-center justify-center text-text-faint hover:text-text rounded-lg hover:bg-surface-2"
          >
            <ExternalLink size={16} />
          </a>
        ) : (
          <span className="h-9 w-9 shrink-0" aria-hidden />
        )}
      </div>

      {isOpen && (
        <LogAttemptForm
          problemTitle={p.title}
          isPending={submitAttempt.isPending}
          previousNotes={p.last_notes}
          previousKeyInsight={p.last_key_insight}
          onCancel={() => setIsOpen(false)}
          onSubmit={(input) =>
            submitAttempt.mutate(
              {
                problem_id: p.problem_id,
                ...input,
                // hint_used predates solve_method; keep it consistent so
                // older reads stay truthful.
                hint_used: input.solve_method === "after_hint",
              },
              { onSuccess: () => setIsOpen(false) }
            )
          }
        />
      )}
      {isOpen && submitAttempt.isError && (
        <p className="text-xs text-danger mt-2">
          Couldn&apos;t save that attempt. Nothing was recorded — try again.
        </p>
      )}
    </Card>
  );
}
