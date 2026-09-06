"use client";

import { Card } from "@/components/ui/card";
import { categoryMeta } from "@/lib/category";
import { formatCountdown, formatTime12h, minutesUntil, timeStringToMinutes } from "@/lib/time";
import type { TimeBlockOut } from "@/lib/types";

/** The next not-yet-started block after `current` (or after now, if
 * nothing is current) — distinct from the interview-prep recommendation,
 * which answers "what should I study," not "what's on my schedule." */
export function UpNextCard({
  blocks,
  current,
  nowMinutes,
}: {
  blocks: TimeBlockOut[];
  current: TimeBlockOut | null;
  nowMinutes: number;
}) {
  const upcoming = blocks
    .filter((b) => b.status === "NOT DONE" && b.id !== current?.id)
    .filter((b) => timeStringToMinutes(b.start) >= (current ? timeStringToMinutes(current.end) : nowMinutes))
    .sort((a, b) => timeStringToMinutes(a.start) - timeStringToMinutes(b.start));

  const next = upcoming[0];
  if (!next) return null;

  const { icon: Icon, colorVar } = categoryMeta(next.category);
  const startsIn = minutesUntil(next.start, nowMinutes);

  return (
    <Card className="p-4 flex items-center gap-3">
      <span
        className="h-10 w-10 rounded-full flex items-center justify-center shrink-0"
        style={{ backgroundColor: `color-mix(in srgb, ${colorVar} 15%, transparent)`, color: colorVar }}
      >
        <Icon size={17} />
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-[10px] font-medium uppercase tracking-wide text-text-faint">Up next</p>
        <p className="text-sm font-medium text-text truncate">{next.activity}</p>
      </div>
      <div className="text-right shrink-0">
        <p className="text-xs text-text-muted tabular-nums">{formatTime12h(next.start)}</p>
        <p className="text-xs tabular-nums" style={{ color: colorVar }}>
          {startsIn > 0 ? `in ${formatCountdown(startsIn)}` : "starting now"}
        </p>
      </div>
    </Card>
  );
}
