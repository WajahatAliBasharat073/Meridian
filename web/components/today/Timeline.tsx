"use client";

import { useMemo, useState } from "react";
import { Check, ChevronDown, Lock, Play, RotateCcw, Sparkles } from "lucide-react";
import { cn } from "@/lib/cn";
import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api";
import { categoryMeta } from "@/lib/category";
import { EARLY_COMPLETION_MESSAGE, isBlockLocked, isTooEarlyToComplete, LOCK_MESSAGE } from "@/lib/blockLock";
import { formatTime12h, timeStringToMinutes } from "@/lib/time";
import { useMarkBlockStatus } from "@/hooks/useMutations";
import { startActivitySession } from "@/lib/activityStore";
import type { BlockStatus, TimeBlockOut } from "@/lib/types";

const STATUS_STYLE: Record<BlockStatus, { bg: string; fg: string; label: string }> = {
  DONE: { bg: "var(--status-done)", fg: "var(--status-done)", label: "Done" },
  PARTIAL: { bg: "var(--status-partial)", fg: "var(--status-partial)", label: "Partial" },
  "NOT DONE": { bg: "transparent", fg: "var(--text-faint)", label: "Mark done" },
  RESCHEDULED: { bg: "var(--status-rescheduled)", fg: "var(--status-rescheduled)", label: "Rescheduled" },
};

const TIER_META: Record<string, { label: string; badgeClass: string }> = {
  T1: { label: "Fixed Anchor", badgeClass: "bg-amber-500/10 text-amber-500 border-amber-500/30" },
  T2: { label: "High Leverage", badgeClass: "bg-indigo-500/10 text-indigo-400 border-indigo-500/30" },
  T3: { label: "Growth", badgeClass: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" },
  T4: { label: "Buffer", badgeClass: "bg-surface-3 text-text-faint border-border" },
};

function formatDuration(minutes: number): string {
  if (minutes < 60) return `${minutes}m`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m === 0 ? `${h}h` : `${h}h ${m}m`;
}

function getPhase(startStr: string): "morning" | "job" | "prep" | "night" {
  const min = timeStringToMinutes(startStr);
  if (min < 9 * 60) return "morning";
  if (min < 17 * 60 + 5) return "job";
  if (min < 20 * 60 + 40) return "prep";
  return "night";
}

const PHASE_LABELS: Record<string, { title: string; subtitle: string; icon: string }> = {
  morning: { title: "Early Morning & Deep Work", subtitle: "04:21 – 09:00 · Fajr, Thesis Research & Morning Anchors", icon: "🌅" },
  job: { title: "Remote Job Core Execution", subtitle: "09:00 – 17:00 · Focused Work, Zuhr, Lunch & Meetings", icon: "💼" },
  prep: { title: "Evening Interview Prep Mastery", subtitle: "17:05 – 20:40 · Coding (140m) & ML System Design (75m)", icon: "💻" },
  night: { title: "Night Routine & Recovery", subtitle: "20:40 – 22:15 · Dinner, English Vocab, Reading & Sleep Shutdown", icon: "🌙" },
};

function Row({ block, nowMinutes }: { block: TimeBlockOut; nowMinutes: number }) {
  const [expanded, setExpanded] = useState(false);
  const mark = useMarkBlockStatus();
  const { icon: Icon, colorVar } = categoryMeta(block.category);
  const isPrayer = block.category === "Prayer";
  const style = STATUS_STYLE[block.status];
  const tierInfo = TIER_META[block.tier] ?? TIER_META.T2;
  // Only a NOT DONE block can be locked — one already DONE/PARTIAL/
  // RESCHEDULED already carries a real record, there's nothing left to
  // guard against.
  const locked = block.status === "NOT DONE" && isBlockLocked(block, nowMinutes);
  const tooEarly = block.status === "NOT DONE" && !locked && isTooEarlyToComplete(block, nowMinutes);
  const wasRejectedByGuard =
    mark.isError && mark.error instanceof ApiError && mark.error.status === 423;

  const setStatus = (status: BlockStatus, actualMinutes?: number) => {
    mark.mutate({ blockId: block.id, status, actualMinutes });
    setExpanded(false);
  };

  const primaryTap = () => setStatus(block.status === "DONE" ? "NOT DONE" : "DONE");

  const handleStartFocus = () => {
    startActivitySession(
      block.id,
      block.activity,
      block.category,
      block.planned_minutes,
      timeStringToMinutes(block.end)
    );
  };

  return (
    <li
      className={cn(
        "transition-colors",
        block.is_current ? "bg-accent-soft/50 border-l-2 border-l-accent" : "hover:bg-surface-2/40"
      )}
    >
      <div className="flex items-center gap-3 py-2.5 px-3">
        {/* Category Icon */}
        <span
          className="h-8 w-8 rounded-lg flex items-center justify-center shrink-0"
          style={{
            backgroundColor: `color-mix(in srgb, ${colorVar} 12%, transparent)`,
            color: colorVar,
          }}
          aria-hidden
        >
          <Icon size={15} />
        </span>

        {/* Core Block Info */}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-mono font-medium text-text-faint tabular-nums shrink-0">
              {formatTime12h(block.start)} – {formatTime12h(block.end)}
            </span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-surface-2 text-text-muted border border-border shrink-0">
              {formatDuration(block.planned_minutes)}
            </span>
            <span
              className={cn("text-[10px] px-1.5 py-0.2 rounded border font-medium shrink-0", tierInfo.badgeClass)}
              title={tierInfo.label}
            >
              {block.tier}
            </span>
            {block.is_current && (
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-accent text-accent-contrast animate-pulse shrink-0">
                ACTIVE NOW
              </span>
            )}
            {isPrayer && <span className="text-[10px] text-prayer shrink-0">🕌 Anchor</span>}
          </div>

          <div className="mt-0.5 flex items-baseline gap-2">
            <p
              className={cn(
                "text-sm font-medium leading-tight truncate",
                block.status === "DONE" ? "text-text-muted line-through decoration-text-faint" : "text-text"
              )}
            >
              {block.activity}
            </p>
          </div>

          {block.notes && (
            <p className="text-[11px] text-text-faint italic truncate mt-0.5 max-w-xl">
              {block.notes}
            </p>
          )}
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-1.5 shrink-0">
          {block.status === "NOT DONE" && !locked && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleStartFocus}
              className="h-8 px-2.5 text-xs gap-1 text-accent-strong hover:bg-accent-soft"
              title="Start live focus session"
            >
              <Play size={12} fill="currentColor" />
              <span className="hidden sm:inline">Focus</span>
            </Button>
          )}

          {locked && (
            <span
              className="h-8 px-2 rounded-lg border border-border flex items-center gap-1 text-[11px] text-text-faint shrink-0"
              title={LOCK_MESSAGE}
            >
              <Lock size={11} />
              <span className="hidden sm:inline">Locked</span>
            </span>
          )}

          <button
            onClick={primaryTap}
            disabled={mark.isPending || (block.status === "NOT DONE" && (locked || tooEarly))}
            aria-label={`Mark "${block.activity}" as ${block.status === "DONE" ? "not done" : "done"}`}
            title={
              block.status === "NOT DONE"
                ? locked
                  ? LOCK_MESSAGE
                  : tooEarly
                    ? EARLY_COMPLETION_MESSAGE
                    : undefined
                : undefined
            }
            className="h-8 min-w-[76px] rounded-lg border flex items-center justify-center gap-1 px-2.5 text-xs font-medium transition-all disabled:opacity-50"
            style={{
              borderColor: block.status === "NOT DONE" ? "var(--border)" : style.fg,
              color: block.status === "NOT DONE" ? "var(--text-muted)" : "var(--bg)",
              backgroundColor: block.status === "NOT DONE" ? "var(--surface-2)" : style.bg,
            }}
          >
            {block.status === "DONE" ? <Check size={13} /> : null}
            {style.label}
          </button>

          <Button
            variant="ghost"
            size="icon"
            onClick={() => setExpanded((e) => !e)}
            aria-label="More status options"
            className="h-8 w-8 shrink-0 text-text-faint hover:text-text"
          >
            <ChevronDown size={14} className={cn("transition-transform", expanded && "rotate-180")} />
          </Button>
        </div>
      </div>

      {wasRejectedByGuard && (
        <p className="px-4 pb-2 text-[11px] text-status-partial flex items-center gap-1.5">
          <Lock size={11} className="shrink-0" />
          {mark.error instanceof ApiError ? mark.error.message : LOCK_MESSAGE}
        </p>
      )}

      {expanded && (
        <div className="flex items-center justify-between gap-2 py-2 px-4 bg-surface-2/60 border-t border-border/50 text-xs">
          <div className="text-text-muted">
            <span className="font-semibold text-text">{block.category}</span> · Planned: {block.planned_minutes} min
            {block.actual_minutes != null && ` · Logged: ${block.actual_minutes} min`}
          </div>
          <div className="flex gap-1.5">
            <Button variant="secondary" size="sm" className="h-7 text-xs" onClick={() => setStatus("PARTIAL")}>
              Partial
            </Button>
            <Button variant="secondary" size="sm" className="h-7 text-xs" onClick={() => setStatus("RESCHEDULED")}>
              Reschedule
            </Button>
            {block.status !== "NOT DONE" && (
              <Button variant="secondary" size="sm" className="h-7 text-xs" onClick={() => setStatus("NOT DONE")}>
                <RotateCcw size={11} /> Undo
              </Button>
            )}
          </div>
        </div>
      )}
    </li>
  );
}

export function Timeline({ blocks, nowMinutes }: { blocks: TimeBlockOut[]; nowMinutes: number }) {
  const [filter, setFilter] = useState<"all" | "morning" | "job" | "prep" | "night">("all");

  const phases = useMemo(() => {
    const map = {
      morning: [] as TimeBlockOut[],
      job: [] as TimeBlockOut[],
      prep: [] as TimeBlockOut[],
      night: [] as TimeBlockOut[],
    };
    for (const b of blocks) {
      const phase = getPhase(b.start);
      map[phase].push(b);
    }
    return map;
  }, [blocks]);

  const displayedBlocks = filter === "all" ? blocks : phases[filter];

  return (
    <div className="space-y-3">
      {/* Filter Tabs */}
      <div className="flex items-center justify-between gap-2 overflow-x-auto pb-1">
        <div className="flex items-center gap-1 p-0.5 rounded-lg bg-surface-2 border border-border text-xs">
          <button
            type="button"
            onClick={() => setFilter("all")}
            className={cn(
              "px-2.5 py-1 rounded-md font-medium transition-colors",
              filter === "all" ? "bg-surface text-text shadow-sm" : "text-text-muted hover:text-text"
            )}
          >
            All Day ({blocks.length})
          </button>
          <button
            type="button"
            onClick={() => setFilter("morning")}
            className={cn(
              "px-2.5 py-1 rounded-md font-medium transition-colors",
              filter === "morning" ? "bg-surface text-text shadow-sm" : "text-text-muted hover:text-text"
            )}
          >
            🌅 Morning ({phases.morning.length})
          </button>
          <button
            type="button"
            onClick={() => setFilter("job")}
            className={cn(
              "px-2.5 py-1 rounded-md font-medium transition-colors",
              filter === "job" ? "bg-surface text-text shadow-sm" : "text-text-muted hover:text-text"
            )}
          >
            💼 Remote Job ({phases.job.length})
          </button>
          <button
            type="button"
            onClick={() => setFilter("prep")}
            className={cn(
              "px-2.5 py-1 rounded-md font-medium transition-colors",
              filter === "prep" ? "bg-surface text-text shadow-sm" : "text-text-muted hover:text-text"
            )}
          >
            💻 Prep ({phases.prep.length})
          </button>
          <button
            type="button"
            onClick={() => setFilter("night")}
            className={cn(
              "px-2.5 py-1 rounded-md font-medium transition-colors",
              filter === "night" ? "bg-surface text-text shadow-sm" : "text-text-muted hover:text-text"
            )}
          >
            🌙 Night ({phases.night.length})
          </button>
        </div>
      </div>

      {/* Schedule Content */}
      {filter === "all" ? (
        <div className="space-y-4">
          {(["morning", "job", "prep", "night"] as const).map((phaseKey) => {
            const phaseBlocks = phases[phaseKey];
            if (phaseBlocks.length === 0) return null;
            const meta = PHASE_LABELS[phaseKey];
            return (
              <div key={phaseKey} className="rounded-xl border border-border bg-surface overflow-hidden shadow-sm">
                <div className="px-3.5 py-2 bg-surface-2/60 border-b border-border flex items-center justify-between">
                  <div>
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-text flex items-center gap-1.5">
                      <span>{meta.icon}</span>
                      <span>{meta.title}</span>
                    </h3>
                    <p className="text-[11px] text-text-faint mt-0.5">{meta.subtitle}</p>
                  </div>
                  <span className="text-[11px] font-mono font-medium text-text-muted bg-surface px-2 py-0.5 rounded border border-border">
                    {phaseBlocks.length} blocks
                  </span>
                </div>
                <ul className="divide-y divide-border">
                  {phaseBlocks.map((b) => (
                    <Row key={b.id} block={b} nowMinutes={nowMinutes} />
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="rounded-xl border border-border bg-surface overflow-hidden shadow-sm">
          <div className="px-3.5 py-2 bg-surface-2/60 border-b border-border">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-text flex items-center gap-1.5">
              <span>{PHASE_LABELS[filter].icon}</span>
              <span>{PHASE_LABELS[filter].title}</span>
            </h3>
            <p className="text-[11px] text-text-faint mt-0.5">{PHASE_LABELS[filter].subtitle}</p>
          </div>
          <ul className="divide-y divide-border">
            {displayedBlocks.map((b) => (
              <Row key={b.id} block={b} nowMinutes={nowMinutes} />
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
