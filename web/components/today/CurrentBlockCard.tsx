"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { categoryMeta } from "@/lib/category";
import { formatCountdown, formatTime12h, minutesUntil, nowMinutesInKarachi } from "@/lib/time";
import type { TimeBlockOut } from "@/lib/types";

export function CurrentBlockCard({ block }: { block: TimeBlockOut | null }) {
  // Safe as a lazy initializer, not a hydration hazard: this component
  // only mounts once `data` has already loaded client-side (see
  // app/today/page.tsx), so it never appears in the server-rendered HTML.
  const [nowMinutes, setNowMinutes] = useState<number>(() => nowMinutesInKarachi());

  useEffect(() => {
    const id = setInterval(() => setNowMinutes(nowMinutesInKarachi()), 1000);
    return () => clearInterval(id);
  }, []);

  if (!block) {
    return (
      <Card className="p-6 text-center">
        <p className="text-text-muted text-sm">No block scheduled right now.</p>
        <p className="text-text-faint text-xs mt-1">Check the timeline below for what&apos;s next.</p>
      </Card>
    );
  }

  const { icon: Icon, colorVar } = categoryMeta(block.category);
  const isPrayer = block.category === "Prayer";
  const remaining = minutesUntil(block.end, nowMinutes);

  return (
    <Card
      className="p-6 relative overflow-hidden"
      style={isPrayer ? { borderColor: "var(--prayer)", background: "var(--prayer-soft)" } : undefined}
    >
      <div className="flex items-center gap-2 mb-3">
        <Icon size={18} style={{ color: colorVar }} aria-hidden />
        <span className="text-xs font-medium uppercase tracking-wide" style={{ color: colorVar }}>
          {block.category}
        </span>
        {isPrayer && (
          <span className="text-xs text-text-faint ml-auto">Not skippable</span>
        )}
      </div>

      <h2 className="text-3xl font-semibold text-text text-balance leading-tight">{block.activity}</h2>

      <div className="mt-4 flex items-baseline gap-3">
        <span className="text-sm text-text-muted tabular-nums">
          {formatTime12h(block.start)}&ndash;{formatTime12h(block.end)}
        </span>
        <span className="text-lg font-medium tabular-nums" style={{ color: colorVar }}>
          {remaining > 0 ? `ends in ${formatCountdown(remaining)}` : "wrapping up"}
        </span>
      </div>

      {block.what_to_do && <p className="mt-3 text-sm text-text-muted">{block.what_to_do}</p>}
    </Card>
  );
}
