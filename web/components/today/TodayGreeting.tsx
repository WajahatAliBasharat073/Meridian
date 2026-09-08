"use client";

import { useState } from "react";

// Grounded, rotating messages tied to the day in front of you.
const MESSAGES = [
  "One focused hour today can move a long-term goal forward.",
  "Consistency matters more than having a perfect day.",
  "Start with the next important thing.",
  "You don't need a perfect day — you need one that moves you forward.",
  "Small, repeated effort compounds more than the occasional big push.",
  "Every block completed is a vote for the person you want to become.",
  "Show up with intent. Results follow consistency.",
];

function greetingWord(hour: number): string {
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

/** Sep 7, 2026 = Day 1 of the program (Monday) */
const PROGRAM_START_MS = new Date("2026-09-07T00:00:00+05:00").getTime();

function getDayLabel(): string {
  const msPerDay = 86_400_000;
  const daysSinceStart = Math.floor((Date.now() - PROGRAM_START_MS) / msPerDay);
  if (daysSinceStart < 0) return "Day 1 Incoming";
  const day   = daysSinceStart + 1;
  const week  = Math.ceil(day / 7);
  const dayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const dayOfWeek = dayNames[daysSinceStart % 7] ?? "Day";
  return `Week ${week} · Day ${day} (${dayOfWeek})`;
}

export function TodayGreeting({ hour }: { hour: number }) {
  const [message] = useState(() => {
    const dayIndex = Math.floor(Date.now() / 86_400_000);
    return MESSAGES[dayIndex % MESSAGES.length];
  });

  const dayLabel = getDayLabel();

  return (
    // Always stacked: this sits in a ~400px sticky column, so the `sm:`
    // viewport breakpoint fired while the *container* was still far too
    // narrow for a side-by-side row — the name and the day chip both
    // spilled past the edge.
    <div className="mb-3 flex flex-col gap-2 border-b border-border/50 pb-3 min-w-0">
      <div className="min-w-0">
        <h2 className="text-base sm:text-lg font-semibold tracking-tight text-text flex flex-wrap items-center gap-x-2">
          <span>{greetingWord(hour)},</span>
          <span className="text-accent-strong">Wajahat Ali Basharat</span>
        </h2>
        <p className="text-xs text-text-muted italic mt-0.5">&ldquo;{message}&rdquo;</p>
      </div>
      <div className="flex items-center gap-2 min-w-0">
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-accent-soft text-accent-strong border border-accent/20 shrink-0 whitespace-nowrap">
          <span className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse" />
          {dayLabel}
        </span>
      </div>
    </div>
  );
}

