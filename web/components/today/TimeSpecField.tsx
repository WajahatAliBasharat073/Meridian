"use client";

import { useState } from "react";
import { FieldLabel } from "@/components/ui/field-label";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";

const PRAYERS = ["fajr", "sunrise", "zuhr", "asr", "maghrib", "isha"] as const;

/** Produces the same spec grammar app/engines/scheduling.py resolves:
 * an absolute "HH:MM" or a prayer-relative "prayer±Nm". Two input modes
 * so the user never has to type that grammar by hand. */
export function TimeSpecField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (spec: string) => void;
}) {
  const [mode, setMode] = useState<"clock" | "prayer">("clock");
  const [prayer, setPrayer] = useState<(typeof PRAYERS)[number]>("fajr");
  const [offset, setOffset] = useState(0);

  const emitPrayerSpec = (p: typeof prayer, off: number) => {
    onChange(off === 0 ? p : `${p}${off > 0 ? "+" : ""}${off}m`);
  };

  return (
    <div>
      <div className="flex items-baseline justify-between mb-1.5">
        <FieldLabel className="mb-0">{label}</FieldLabel>
        <div className="flex gap-1 text-[11px]">
          <button
            type="button"
            onClick={() => {
              setMode("clock");
              onChange("");
            }}
            className={mode === "clock" ? "text-accent-strong" : "text-text-faint hover:text-text-muted"}
          >
            Clock time
          </button>
          <span className="text-text-faint">·</span>
          <button
            type="button"
            onClick={() => {
              setMode("prayer");
              emitPrayerSpec(prayer, offset);
            }}
            className={mode === "prayer" ? "text-accent-strong" : "text-text-faint hover:text-text-muted"}
          >
            Prayer-relative
          </button>
        </div>
      </div>

      {mode === "clock" ? (
        <Input
          type="time"
          required
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      ) : (
        <div className="flex gap-2">
          <Select
            value={prayer}
            onChange={(e) => {
              const p = e.target.value as typeof prayer;
              setPrayer(p);
              emitPrayerSpec(p, offset);
            }}
            className="capitalize flex-1"
          >
            {PRAYERS.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </Select>
          <div className="w-20 shrink-0">
            <Input
              type="number"
              value={offset}
              onChange={(e) => {
                const n = Number(e.target.value) || 0;
                setOffset(n);
                emitPrayerSpec(prayer, n);
              }}
              aria-label="Minutes offset"
            />
          </div>
          <span className="flex items-center text-xs text-text-faint">min offset</span>
        </div>
      )}
    </div>
  );
}
