"use client";

import { Activity, Bed, Droplets, HeartPulse, Moon, Utensils } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { QueryError } from "@/components/ui/query-state";
import { FieldLabel } from "@/components/ui/field-label";
import { useAddWater, useTodayVitals, useUpdateNutrition, useUpdateRecovery } from "@/hooks/useVitals";
import { cn } from "@/lib/cn";
import type { VitalsOut } from "@/lib/types";

/** Plain-language names for the inputs the score is missing, so "not enough
 * logged" tells you what to actually go and fill in. */
const MISSING_LABEL: Record<string, string> = {
  sleep_hours: "hours slept",
  water_ml: "water",
  energy: "energy rating",
  stress: "stress rating",
};

export default function HealthPage() {
  const { data, isLoading, isError, error, refetch } = useTodayVitals();
  const updateRecovery = useUpdateRecovery();
  const updateNutrition = useUpdateNutrition();
  const water = useAddWater();

  return (
    <PageContainer>
      <PageHeader
        eyebrow="Physiological Foundation"
        title="Recovery, Sleep & Vitals"
        description="Physical recovery bounds your daily cognitive capacity. Everything here is what you logged — nothing is assumed on your behalf."
      />

      {isLoading && (
        <div className="space-y-3">
          <Skeleton className="h-28" />
          <Skeleton className="h-40" />
        </div>
      )}

      {isError && (
        <QueryError error={error} onRetry={() => refetch()} fallback="Couldn't load today's vitals." />
      )}

      {data && (
        <>
          <ScoreBanner vitals={data} />

          <div className="grid sm:grid-cols-2 gap-3 mb-3">
            <WaterCard
              vitals={data}
              onAdd={(ml) => water.mutate(ml)}
              pending={water.isPending}
            />
            <SleepCard
              vitals={data}
              onChange={(fields) => updateRecovery.mutate(fields)}
              pending={updateRecovery.isPending}
            />
          </div>

          <RatingsCard
            vitals={data}
            onChange={(fields) => updateRecovery.mutate(fields)}
            pending={updateRecovery.isPending}
          />

          <IntakeCard
            vitals={data}
            onChange={(fields) => updateNutrition.mutate(fields)}
            pending={updateNutrition.isPending}
          />
        </>
      )}
    </PageContainer>
  );
}

function ScoreBanner({ vitals }: { vitals: VitalsOut }) {
  const scored = vitals.recovery_score != null;
  const missing = vitals.missing.map((m) => MISSING_LABEL[m] ?? m);

  return (
    <Card className="p-6 mb-3 border-border-strong bg-gradient-to-r from-surface via-surface-2/70 to-surface">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="min-w-0">
          <span className="text-xs font-semibold uppercase tracking-wider text-accent-strong">
            Composite Recovery Score
          </span>
          <div className="flex items-baseline gap-3 mt-1">
            <span
              className={cn(
                "text-4xl font-bold tabular-nums font-mono",
                scored ? "text-text" : "text-text-faint"
              )}
            >
              {scored ? vitals.recovery_score : "—"}
            </span>
            {scored && <span className="text-sm text-text-faint">/ 100</span>}
          </div>

          {/* The honest bit: no score rather than a comfortable one, and a
              list of exactly what would make it computable. */}
          {scored ? (
            <p className="text-xs text-text-muted mt-2 leading-relaxed max-w-lg">
              From{" "}
              {Object.entries(vitals.score_components)
                .map(([k, v]) => `${k} ${Math.round(v)}`)
                .join(" · ")}
              {missing.length > 0 && (
                <span className="text-status-partial">
                  {" "}
                  — still unlogged: {missing.join(", ")}, so this is a floor, not a final
                  figure.
                </span>
              )}
            </p>
          ) : (
            <p className="text-xs text-text-muted mt-2 leading-relaxed max-w-lg">
              Not enough logged today to score honestly. Missing: {missing.join(", ")}.
              {!vitals.has_any_entry && " Nothing has been recorded for today yet."}
            </p>
          )}
        </div>

        <HeartPulse
          size={44}
          className={cn("shrink-0", scored ? "text-accent-strong" : "text-text-faint")}
          aria-hidden
        />
      </div>
    </Card>
  );
}

function WaterCard({
  vitals,
  onAdd,
  pending,
}: {
  vitals: VitalsOut;
  onAdd: (ml: number) => void;
  pending: boolean;
}) {
  const ml = vitals.water_ml;
  const pct = vitals.hydration_pct ?? 0;

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-medium text-text flex items-center gap-1.5">
          <Droplets size={15} className="text-accent-strong" /> Water
        </p>
        {ml != null && (
          <Badge color={pct >= 100 ? "var(--status-done)" : "var(--status-partial)"}>
            {pct}%
          </Badge>
        )}
      </div>

      <p className="text-2xl font-bold tabular-nums font-mono mt-2 text-text">
        {ml != null ? `${ml} ml` : "—"}
        <span className="text-xs text-text-faint font-sans font-normal ml-1.5">
          of {vitals.water_target_ml} ml
        </span>
      </p>

      <div className="h-1.5 rounded-full bg-surface-2 overflow-hidden mt-2">
        <div className="h-full rounded-full bg-accent" style={{ width: `${Math.min(100, pct)}%` }} />
      </div>

      <div className="flex gap-2 mt-3">
        <Button
          variant="secondary"
          size="sm"
          disabled={pending}
          onClick={() => onAdd(250)}
          className="flex-1 text-xs"
        >
          + glass (250 ml)
        </Button>
        <Button
          variant="secondary"
          size="sm"
          disabled={pending}
          onClick={() => onAdd(500)}
          className="flex-1 text-xs"
        >
          + bottle (500 ml)
        </Button>
      </div>
      <p className="text-[10px] text-text-faint mt-2">
        Hydration reminders during a focus session log here too.
      </p>
    </Card>
  );
}

function SleepCard({
  vitals,
  onChange,
  pending,
}: {
  vitals: VitalsOut;
  onChange: (fields: { sleep_hours?: number; sleep_quality?: number }) => void;
  pending: boolean;
}) {
  return (
    <Card className="p-4">
      <p className="text-sm font-medium text-text flex items-center gap-1.5">
        <Bed size={15} className="text-accent-strong" /> Sleep
      </p>
      <p className="text-2xl font-bold tabular-nums font-mono mt-2 text-text">
        {vitals.sleep_hours != null ? `${vitals.sleep_hours} h` : "—"}
      </p>

      <div className="mt-3">
        <FieldLabel hint="drag to log">Hours slept</FieldLabel>
        <input
          type="range"
          min={0}
          max={12}
          step={0.5}
          value={vitals.sleep_hours ?? 7}
          disabled={pending}
          onChange={(e) => onChange({ sleep_hours: parseFloat(e.target.value) })}
          className="w-full accent-accent"
          aria-label="Hours slept"
        />
      </div>

      <div className="mt-2">
        <FieldLabel>Quality</FieldLabel>
        <RatingRow
          value={vitals.sleep_quality}
          disabled={pending}
          onPick={(n) => onChange({ sleep_quality: n })}
        />
      </div>
    </Card>
  );
}

function RatingsCard({
  vitals,
  onChange,
  pending,
}: {
  vitals: VitalsOut;
  onChange: (fields: {
    energy?: number;
    mood?: number;
    stress?: number;
    exercise_minutes?: number;
  }) => void;
  pending: boolean;
}) {
  return (
    <Card className="p-4 mb-3">
      <p className="text-sm font-medium text-text flex items-center gap-1.5 mb-3">
        <Activity size={15} className="text-accent-strong" /> How today felt
      </p>

      <div className="grid sm:grid-cols-3 gap-4">
        <div>
          <FieldLabel hint={vitals.energy == null ? "unlogged" : undefined}>Energy</FieldLabel>
          <RatingRow
            value={vitals.energy}
            disabled={pending}
            onPick={(n) => onChange({ energy: n })}
          />
        </div>
        <div>
          <FieldLabel hint={vitals.mood == null ? "unlogged" : undefined}>Mood</FieldLabel>
          <RatingRow
            value={vitals.mood}
            disabled={pending}
            onPick={(n) => onChange({ mood: n })}
          />
        </div>
        <div>
          <FieldLabel hint={vitals.stress == null ? "unlogged" : "1 calm · 5 maxed"}>
            Stress
          </FieldLabel>
          <RatingRow
            value={vitals.stress}
            disabled={pending}
            onPick={(n) => onChange({ stress: n })}
            inverted
          />
        </div>
      </div>

      <div className="mt-4 max-w-xs">
        <FieldLabel hint="minutes">
          <span className="inline-flex items-center gap-1.5">
            <Moon size={11} /> Exercise
          </span>
        </FieldLabel>
        <input
          type="number"
          min={0}
          value={vitals.exercise_minutes ?? ""}
          disabled={pending}
          placeholder="not logged"
          onChange={(e) =>
            onChange({ exercise_minutes: e.target.value === "" ? 0 : Number(e.target.value) })
          }
          className="w-full h-9 rounded-lg border border-border bg-surface-2 px-2.5 text-xs text-text"
        />
      </div>
    </Card>
  );
}

function IntakeCard({
  vitals,
  onChange,
  pending,
}: {
  vitals: VitalsOut;
  onChange: (fields: { calories?: number; protein_g?: number }) => void;
  pending: boolean;
}) {
  return (
    <Card className="p-4">
      <p className="text-sm font-medium text-text flex items-center gap-1.5 mb-3">
        <Utensils size={15} className="text-accent-strong" /> Intake
      </p>
      <div className="grid sm:grid-cols-2 gap-3 max-w-md">
        <div>
          <FieldLabel hint="kcal">Calories</FieldLabel>
          <input
            type="number"
            min={0}
            value={vitals.calories ?? ""}
            disabled={pending}
            placeholder="not logged"
            onChange={(e) => onChange({ calories: e.target.value === "" ? 0 : Number(e.target.value) })}
            className="w-full h-9 rounded-lg border border-border bg-surface-2 px-2.5 text-xs text-text"
          />
        </div>
        <div>
          <FieldLabel hint="grams">Protein</FieldLabel>
          <input
            type="number"
            min={0}
            value={vitals.protein_g ?? ""}
            disabled={pending}
            placeholder="not logged"
            onChange={(e) => onChange({ protein_g: e.target.value === "" ? 0 : Number(e.target.value) })}
            className="w-full h-9 rounded-lg border border-border bg-surface-2 px-2.5 text-xs text-text"
          />
        </div>
      </div>
    </Card>
  );
}

/** 1-5 picker. Empty until you actually pick — an unlogged rating shows as
 * nothing rather than silently defaulting to the middle. */
function RatingRow({
  value,
  onPick,
  disabled,
  inverted = false,
}: {
  value: number | null;
  onPick: (n: number) => void;
  disabled: boolean;
  inverted?: boolean;
}) {
  return (
    <div className="flex items-center gap-1.5">
      {[1, 2, 3, 4, 5].map((n) => {
        const active = value != null && n <= value;
        const good = inverted ? n <= 2 : n >= 4;
        return (
          <button
            key={n}
            type="button"
            disabled={disabled}
            onClick={() => onPick(n)}
            aria-label={`Rate ${n} of 5`}
            aria-pressed={value === n}
            className={cn(
              "h-8 flex-1 rounded-md border text-xs font-semibold transition-colors disabled:opacity-40",
              active
                ? good
                  ? "border-status-done bg-status-done/15 text-status-done"
                  : "border-status-partial bg-status-partial/15 text-status-partial"
                : "border-border bg-surface-2 text-text-faint hover:text-text"
            )}
          >
            {n}
          </button>
        );
      })}
    </div>
  );
}
