"use client";

import { useState } from "react";

// Grounded, rotating messages — no unverifiable claims ("ahead of 99% of
// people"), just plain encouragement tied to the day in front of you.
const MESSAGES = [
  "One focused hour today can move a long-term goal forward.",
  "Consistency matters more than having a perfect day.",
  "Start with the next important thing.",
  "You don't need a perfect day — you need one that moves you forward.",
  "Small, repeated effort compounds more than the occasional big push.",
];

function greetingWord(hour: number): string {
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

export function TodayGreeting({ hour }: { hour: number }) {
  // Lazy initializer: reads the clock once at mount, not on every
  // render, so the pick is stable for the page's lifetime but still
  // varies day to day.
  const [message] = useState(() => {
    const dayIndex = Math.floor(Date.now() / 86_400_000);
    return MESSAGES[dayIndex % MESSAGES.length];
  });

  return (
    <div className="mb-1">
      <p className="text-xs font-medium uppercase tracking-wide text-text-faint mb-1">
        {greetingWord(hour)}
      </p>
      <p className="text-sm text-text-muted italic">&ldquo;{message}&rdquo;</p>
    </div>
  );
}
