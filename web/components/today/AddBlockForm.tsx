"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FieldLabel } from "@/components/ui/field-label";
import { Alert } from "@/components/ui/alert";
import { TimeSpecField } from "@/components/today/TimeSpecField";
import { useCreateBlock } from "@/hooks/useMutations";
import { ApiError } from "@/lib/api";

const TIERS = [
  { value: "T1", label: "T1 · deep work" },
  { value: "T2", label: "T2 · focused" },
  { value: "T3", label: "T3 · maintenance" },
  { value: "T4", label: "T4 · buffer" },
] as const;

const KNOWN_CATEGORIES = [
  "Prayer",
  "InterviewPrep",
  "Job",
  "Thesis",
  "English",
  "Nutrition",
  "Recovery",
  "Reading",
  "Buffer",
];

export function AddBlockForm({ date, onDone }: { date: string; onDone?: () => void }) {
  const [activity, setActivity] = useState("");
  const [category, setCategory] = useState("");
  const [tier, setTier] = useState<(typeof TIERS)[number]["value"]>("T2");
  const [startSpec, setStartSpec] = useState("");
  const [endSpec, setEndSpec] = useState("");
  const [plannedMinutes, setPlannedMinutes] = useState(30);
  const [whatToDo, setWhatToDo] = useState("");

  const createBlock = useCreateBlock();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createBlock.mutate(
      {
        date,
        start_spec: startSpec,
        end_spec: endSpec,
        activity,
        tier,
        category: category || "Other",
        planned_minutes: plannedMinutes,
        what_to_do: whatToDo || undefined,
      },
      {
        onSuccess: () => {
          setActivity("");
          setStartSpec("");
          setEndSpec("");
          setWhatToDo("");
          onDone?.();
        },
      }
    );
  };

  const errorMessage =
    createBlock.error instanceof ApiError
      ? createBlock.error.status === 422
        ? "That start or end time isn't valid — use HH:MM or a prayer name."
        : "Couldn't create that block."
      : null;

  return (
    <Card className="p-4">
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <div>
          <FieldLabel htmlFor="activity">Activity</FieldLabel>
          <input
            id="activity"
            required
            value={activity}
            onChange={(e) => setActivity(e.target.value)}
            placeholder="e.g. DSA — new problem"
            className="w-full h-11 rounded-lg border border-border bg-surface-2 px-3 text-sm text-text placeholder:text-text-faint focus:outline-none focus:ring-2 focus:ring-accent"
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <TimeSpecField label="Start" value={startSpec} onChange={setStartSpec} />
          <TimeSpecField label="End" value={endSpec} onChange={setEndSpec} />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <FieldLabel htmlFor="category">Category</FieldLabel>
            <input
              id="category"
              list="category-suggestions"
              required
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="e.g. InterviewPrep"
              className="w-full h-11 rounded-lg border border-border bg-surface-2 px-3 text-sm text-text placeholder:text-text-faint focus:outline-none focus:ring-2 focus:ring-accent"
            />
            <datalist id="category-suggestions">
              {KNOWN_CATEGORIES.map((c) => (
                <option key={c} value={c} />
              ))}
            </datalist>
          </div>
          <div>
            <FieldLabel htmlFor="planned-minutes">Planned minutes</FieldLabel>
            <input
              id="planned-minutes"
              type="number"
              min={1}
              required
              value={plannedMinutes}
              onChange={(e) => setPlannedMinutes(Number(e.target.value) || 0)}
              className="w-full h-11 rounded-lg border border-border bg-surface-2 px-3 text-sm text-text focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
        </div>

        <div>
          <FieldLabel>Tier</FieldLabel>
          <div className="flex flex-wrap gap-2">
            {TIERS.map((t) => (
              <button
                key={t.value}
                type="button"
                onClick={() => setTier(t.value)}
                className="h-9 px-3 rounded-md border text-xs transition-colors"
                style={{
                  borderColor: tier === t.value ? "var(--accent)" : "var(--border)",
                  color: tier === t.value ? "var(--accent-strong)" : "var(--text-muted)",
                  background: tier === t.value ? "var(--accent-soft)" : "transparent",
                }}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <FieldLabel htmlFor="what-to-do">What to do (optional)</FieldLabel>
          <input
            id="what-to-do"
            value={whatToDo}
            onChange={(e) => setWhatToDo(e.target.value)}
            className="w-full h-11 rounded-lg border border-border bg-surface-2 px-3 text-sm text-text focus:outline-none focus:ring-2 focus:ring-accent"
          />
        </div>

        {errorMessage && <Alert variant="error">{errorMessage}</Alert>}

        <Button
          type="submit"
          variant="primary"
          size="lg"
          disabled={createBlock.isPending || !startSpec || !endSpec}
          className="w-full"
        >
          {createBlock.isPending ? "Adding…" : "Add block"}
        </Button>
      </form>
    </Card>
  );
}
