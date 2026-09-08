"use client";

import { useMemo } from "react";
import { Compass } from "lucide-react";

const GROUNDED_MESSAGES = [
  "One focused hour today is enough to move something important forward.",
  "Consistency beats waiting for the perfect day.",
  "Start with the next important thing — clarity follows action.",
  "Protect your primary focus window before the day fractures.",
  "A good day is not zero friction; it is intentional recovery after deep work.",
  "Progress is compounding: small honest iterations outlast sporadic intensity.",
  "Execute the block in front of you. The rest of the day can wait.",
];

export function DailyWisdom() {
  const message = useMemo(() => {
    const dayOfYear = Math.floor(
      (Date.now() - new Date(new Date().getFullYear(), 0, 0).getTime()) / (1000 * 60 * 60 * 24)
    );
    return GROUNDED_MESSAGES[dayOfYear % GROUNDED_MESSAGES.length];
  }, []);

  return (
    <div className="flex items-center gap-2.5 px-4 py-2.5 rounded-xl border border-border bg-surface-2/40 text-xs text-text-muted">
      <Compass size={15} className="text-accent-strong shrink-0" />
      <p className="italic leading-relaxed font-normal">
        &ldquo;{message}&rdquo;
      </p>
    </div>
  );
}
