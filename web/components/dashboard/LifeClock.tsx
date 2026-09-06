"use client";

import { useEffect, useState } from "react";
import { Hourglass, Pencil } from "lucide-react";
import { useProfile, useUpdateProfile } from "@/hooks/useProfile";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/cn";

interface Remaining {
  years: number;
  months: number;
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  lifePctUsed: number;
  past: boolean;
}

function calendarDiff(from: Date, to: Date) {
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
  return { years, months, days };
}

function computeRemaining(birthDate: Date, lifeExpectancyYears: number, now: Date): Remaining {
  const targetDate = new Date(birthDate);
  targetDate.setFullYear(targetDate.getFullYear() + lifeExpectancyYears);

  const past = targetDate.getTime() <= now.getTime();
  const from = past ? targetDate : now;
  const to = past ? now : targetDate;
  const { years, months, days } = calendarDiff(from, to);

  const totalMs = to.getTime() - from.getTime();
  const remainderMs = totalMs % (1000 * 60 * 60 * 24);
  const hours = Math.floor(remainderMs / (1000 * 60 * 60));
  const minutes = Math.floor((remainderMs / (1000 * 60)) % 60);
  const seconds = Math.floor((remainderMs / 1000) % 60);

  const lifeSpanMs = lifeExpectancyYears * 365.25 * 24 * 60 * 60 * 1000;
  const livedMs = now.getTime() - birthDate.getTime();
  const lifePctUsed = Math.min(100, Math.max(0, (livedMs / lifeSpanMs) * 100));

  return { years, months, days, hours, minutes, seconds, lifePctUsed, past };
}

function ProfileForm({
  onSaved,
  initialBirthDate,
  initialLifeExpectancy,
}: {
  onSaved: () => void;
  initialBirthDate?: string | null;
  initialLifeExpectancy?: number | null;
}) {
  const [birthDate, setBirthDate] = useState(initialBirthDate ?? "");
  const [lifeExpectancy, setLifeExpectancy] = useState(String(initialLifeExpectancy ?? 80));
  const updateProfile = useUpdateProfile();

  const canSave = birthDate.length > 0 && Number(lifeExpectancy) > 0;

  return (
    <form
      className="flex flex-col gap-2"
      onSubmit={(e) => {
        e.preventDefault();
        if (!canSave) return;
        updateProfile.mutate(
          { birth_date: birthDate, life_expectancy_years: Number(lifeExpectancy) },
          { onSuccess: onSaved }
        );
      }}
    >
      <label className="text-xs text-text-faint">
        Birth date
        <input
          type="date"
          value={birthDate}
          onChange={(e) => setBirthDate(e.target.value)}
          max={new Date().toISOString().slice(0, 10)}
          className="mt-1 h-9 w-full rounded-lg border border-border bg-surface-2 px-2 text-sm text-text"
        />
      </label>
      <label className="text-xs text-text-faint">
        Life expectancy (years)
        <input
          type="number"
          min={1}
          max={120}
          value={lifeExpectancy}
          onChange={(e) => setLifeExpectancy(e.target.value)}
          className="mt-1 h-9 w-full rounded-lg border border-border bg-surface-2 px-2 text-sm text-text tabular-nums"
        />
      </label>
      <Button type="submit" variant="primary" size="sm" disabled={!canSave || updateProfile.isPending}>
        {updateProfile.isPending ? "Saving…" : "Save"}
      </Button>
      {updateProfile.isError && (
        <p className="text-xs text-danger">Couldn&apos;t save — try again in a moment.</p>
      )}
    </form>
  );
}

function Unit({ value, label }: { value: number; label: string }) {
  return (
    <div className="flex flex-col items-center min-w-0">
      <span className="text-lg sm:text-xl font-semibold tabular-nums text-text tracking-tight">
        {value}
      </span>
      <span className="text-[10px] uppercase tracking-wide text-text-faint">{label}</span>
    </div>
  );
}

export function LifeClock() {
  const { data: profile, isLoading } = useProfile();
  const [editing, setEditing] = useState(false);
  const [now, setNow] = useState<Date | null>(null);

  useEffect(() => {
    // Ticking wall-clock display, not state derived from props — there is
    // no non-effect way to subscribe to "the current second."
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setNow(new Date());
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  if (isLoading || now === null) {
    return <Card className="p-4 w-full sm:w-72 h-[132px] animate-pulse" />;
  }

  const hasProfile = profile?.birth_date != null && profile?.life_expectancy_years != null;

  if (!hasProfile || editing) {
    return (
      <Card className="p-4 w-full sm:w-72">
        <div className="flex items-center gap-2 mb-2">
          <Hourglass size={14} className="text-accent" />
          <span className="text-xs font-medium text-text-faint uppercase tracking-wide">
            Time remaining
          </span>
        </div>
        {!hasProfile && !editing && (
          <p className="text-xs text-text-muted mb-3 leading-relaxed">
            Set your birth date to see a live countdown of your estimated remaining
            time — a reminder to spend it well, not a prediction.
          </p>
        )}
        <ProfileForm
          onSaved={() => setEditing(false)}
          initialBirthDate={profile?.birth_date}
          initialLifeExpectancy={profile?.life_expectancy_years}
        />
      </Card>
    );
  }

  const remaining = computeRemaining(
    new Date(profile!.birth_date as string),
    profile!.life_expectancy_years as number,
    now
  );

  return (
    <Card className="p-4 w-full sm:w-80 group relative">
      <button
        type="button"
        onClick={() => setEditing(true)}
        aria-label="Edit birth date and life expectancy"
        className="absolute top-3 right-3 h-8 w-8 flex items-center justify-center rounded-lg text-text-faint hover:text-text hover:bg-surface-2 opacity-0 group-hover:opacity-100 focus-visible:opacity-100 transition-opacity"
      >
        <Pencil size={13} />
      </button>

      <div className="flex items-center gap-2 mb-3">
        <Hourglass size={14} className="text-accent" />
        <span className="text-xs font-medium text-text-faint uppercase tracking-wide">
          {remaining.past ? "Time since your estimate" : "Time remaining (est.)"}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-y-2 mb-3">
        <Unit value={remaining.years} label="years" />
        <Unit value={remaining.months} label="months" />
        <Unit value={remaining.days} label="days" />
      </div>

      <div className="flex items-center justify-center gap-1 text-xs text-text-faint tabular-nums mb-3">
        <span>{String(remaining.hours).padStart(2, "0")}</span>:
        <span>{String(remaining.minutes).padStart(2, "0")}</span>:
        <span>{String(remaining.seconds).padStart(2, "0")}</span>
      </div>

      <div className="h-1.5 rounded-full bg-surface-2 overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all", remaining.past ? "bg-danger" : "bg-accent")}
          style={{ width: `${remaining.lifePctUsed}%` }}
        />
      </div>
      <p className="text-[11px] text-text-faint mt-1.5">
        {remaining.lifePctUsed.toFixed(1)}% of your estimated lifespan lived so far
      </p>
    </Card>
  );
}
