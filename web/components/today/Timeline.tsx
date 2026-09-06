"use client";

import { useState } from "react";
import { Check, ChevronDown, RotateCcw } from "lucide-react";
import { cn } from "@/lib/cn";
import { Button } from "@/components/ui/button";
import { categoryMeta } from "@/lib/category";
import { formatTime12h } from "@/lib/time";
import { useMarkBlockStatus } from "@/hooks/useMutations";
import type { BlockStatus, TimeBlockOut } from "@/lib/types";

const STATUS_STYLE: Record<BlockStatus, { bg: string; fg: string; label: string }> = {
  DONE: { bg: "var(--status-done)", fg: "var(--status-done)", label: "Done" },
  PARTIAL: { bg: "var(--status-partial)", fg: "var(--status-partial)", label: "Partial" },
  "NOT DONE": { bg: "transparent", fg: "var(--text-faint)", label: "Mark done" },
  RESCHEDULED: { bg: "var(--status-rescheduled)", fg: "var(--status-rescheduled)", label: "Rescheduled" },
};

function Row({ block }: { block: TimeBlockOut }) {
  const [expanded, setExpanded] = useState(false);
  const mark = useMarkBlockStatus();
  const { icon: Icon, colorVar } = categoryMeta(block.category);
  const isPrayer = block.category === "Prayer";
  const style = STATUS_STYLE[block.status];

  const setStatus = (status: BlockStatus, actualMinutes?: number) => {
    mark.mutate({ blockId: block.id, status, actualMinutes });
    setExpanded(false);
  };

  const primaryTap = () => setStatus(block.status === "DONE" ? "NOT DONE" : "DONE");

  return (
    <li className={cn(block.is_current && "bg-accent-soft/40")}>
      <div className="flex items-center gap-3 py-2.5 px-1">
        <Icon size={16} style={{ color: colorVar }} aria-hidden className="shrink-0" />

        <div className="min-w-0 flex-1">
          <div className="flex items-baseline gap-2">
            <span className="text-xs text-text-faint tabular-nums shrink-0">
              {formatTime12h(block.start)}
            </span>
            <span
              className={cn(
                "text-sm truncate",
                block.status === "DONE" ? "text-text-muted line-through decoration-text-faint" : "text-text"
              )}
            >
              {block.activity}
            </span>
            {isPrayer && <span className="text-[10px] text-prayer shrink-0">●</span>}
          </div>
        </div>

        <button
          onClick={primaryTap}
          disabled={mark.isPending}
          aria-label={`Mark "${block.activity}" as ${block.status === "DONE" ? "not done" : "done"}`}
          className="h-11 min-w-11 shrink-0 rounded-full border flex items-center justify-center gap-1 px-3 text-xs font-medium transition-colors disabled:opacity-50"
          style={{
            borderColor: style.fg,
            color: block.status === "NOT DONE" ? style.fg : "var(--bg)",
            backgroundColor: block.status === "NOT DONE" ? "transparent" : style.bg,
          }}
        >
          {block.status === "DONE" ? <Check size={14} /> : null}
          {style.label}
        </button>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => setExpanded((e) => !e)}
          aria-label="More status options"
          className="shrink-0"
        >
          <ChevronDown size={16} className={cn("transition-transform", expanded && "rotate-180")} />
        </Button>
      </div>

      {expanded && (
        <div className="flex gap-2 pb-3 px-1 pl-8">
          <Button variant="secondary" size="sm" onClick={() => setStatus("PARTIAL")}>
            Partial
          </Button>
          <Button variant="secondary" size="sm" onClick={() => setStatus("RESCHEDULED")}>
            Reschedule
          </Button>
          {block.status !== "NOT DONE" && (
            <Button variant="secondary" size="sm" onClick={() => setStatus("NOT DONE")}>
              <RotateCcw size={12} /> Undo
            </Button>
          )}
        </div>
      )}
    </li>
  );
}

export function Timeline({ blocks }: { blocks: TimeBlockOut[] }) {
  return (
    <ul className="rounded-xl border border-border bg-surface divide-y divide-border overflow-hidden">
      {blocks.map((b) => (
        <Row key={b.id} block={b} />
      ))}
    </ul>
  );
}
