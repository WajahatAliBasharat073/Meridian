"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Hourglass } from "lucide-react";
import { useProfile } from "@/hooks/useProfile";

/** One-line version of the dashboard's LifeClock, sized for the top nav so
 * the countdown is present on every page. Reads the same profile
 * (birth_date + life_expectancy_years) — if that isn't set yet it links to
 * Insights to set it rather than inventing a number. */
export function LifeClockPill() {
  const { data: profile, isLoading } = useProfile();
  const [now, setNow] = useState<Date | null>(null);

  useEffect(() => {
    // Ticking wall clock — no non-effect way to subscribe to "now".
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setNow(new Date());
    const id = setInterval(() => setNow(new Date()), 60_000);
    return () => clearInterval(id);
  }, []);

  if (now === null) return null;

  const birth = profile?.birth_date;
  const expectancy = profile?.life_expectancy_years;

  // "Set countdown" is a claim that the profile is empty. While the fetch
  // is still in flight we don't know that, and showing it anyway made a
  // configured countdown flash as unconfigured on every page load.
  if (isLoading) return null;

  if (!birth || !expectancy) {
    return (
      <Link
        href="/dashboard"
        title="Set your birth date to see the countdown"
        className="hidden lg:inline-flex items-center gap-1.5 h-8 px-2.5 rounded-lg text-[11px] font-medium text-text-faint hover:text-text hover:bg-surface-2 transition-colors whitespace-nowrap"
      >
        <Hourglass size={13} className="shrink-0" />
        Set countdown
      </Link>
    );
  }

  const target = new Date(birth);
  target.setFullYear(target.getFullYear() + expectancy);

  const past = target.getTime() <= now.getTime();
  const from = past ? target : now;
  const to = past ? now : target;

  let years = to.getFullYear() - from.getFullYear();
  let months = to.getMonth() - from.getMonth();
  let days = to.getDate() - from.getDate();
  if (days < 0) {
    months -= 1;
    days += new Date(to.getFullYear(), to.getMonth(), 0).getDate();
  }
  if (months < 0) {
    years -= 1;
    months += 12;
  }

  return (
    <Link
      href="/dashboard"
      title={
        past
          ? "Past your estimated lifespan — every day now is bonus time"
          : "Estimated time remaining (an estimate, not a prediction)"
      }
      className="hidden lg:inline-flex items-center gap-1.5 h-8 px-2.5 rounded-lg text-[11px] font-medium text-text-muted hover:text-text hover:bg-surface-2 transition-colors whitespace-nowrap tabular-nums"
    >
      <Hourglass size={13} className="shrink-0 text-accent" />
      {past ? (
        <span>+{years}y {months}m over</span>
      ) : (
        <span>
          {years}y {months}m {days}d left
        </span>
      )}
    </Link>
  );
}
