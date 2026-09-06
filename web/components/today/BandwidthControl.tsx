"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getRecommend } from "@/lib/api";
import type { BandwidthOut, RecommendationOut } from "@/lib/types";

const MINUTE_PRESETS = [15, 30, 60, 90, 120];
const ENERGY_LABELS = ["Very low", "Low", "Okay", "Good", "High"];

const BAND_COLOR: Record<BandwidthOut["band"], string> = {
  HIGH: "var(--status-done)",
  MEDIUM: "var(--accent)",
  LOW: "var(--status-partial)",
  MINIMUM_VIABLE_DAY: "var(--danger)",
};

export function BandwidthControl({ bandwidth }: { bandwidth: BandwidthOut | null }) {
  const [adjusting, setAdjusting] = useState(false);
  const [minutes, setMinutes] = useState(30);
  const [energy, setEnergy] = useState(3);
  const [results, setResults] = useState<RecommendationOut[] | null>(null);
  const [loading, setLoading] = useState(false);

  if (!bandwidth) return null;

  const handleSubmit = async () => {
    setLoading(true);
    try {
      setResults(await getRecommend(minutes, energy));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span
              className="h-2 w-2 rounded-full shrink-0"
              style={{ background: BAND_COLOR[bandwidth.band] }}
              aria-hidden
            />
            <span className="text-xs font-medium uppercase tracking-wide text-text-muted">
              {bandwidth.band.replace(/_/g, " ")}
            </span>
          </div>
          <p className="text-sm text-text">{bandwidth.headline}</p>
          {bandwidth.spare_minutes_suggestion && (
            <p className="text-sm text-accent-strong mt-1">{bandwidth.spare_minutes_suggestion}</p>
          )}
        </div>
        <Button size="sm" variant="ghost" onClick={() => setAdjusting((a) => !a)} className="shrink-0">
          {adjusting ? "Close" : "Adjust"}
        </Button>
      </div>

      {adjusting && (
        <div className="mt-4 pt-4 border-t border-border space-y-4">
          <div>
            <p className="text-xs text-text-faint mb-2">Minutes available</p>
            <div className="flex flex-wrap gap-2">
              {MINUTE_PRESETS.map((m) => (
                <button
                  key={m}
                  onClick={() => setMinutes(m)}
                  className="h-9 px-3 rounded-md border text-sm transition-colors"
                  style={{
                    borderColor: minutes === m ? "var(--accent)" : "var(--border)",
                    color: minutes === m ? "var(--accent-strong)" : "var(--text-muted)",
                    background: minutes === m ? "var(--accent-soft)" : "transparent",
                  }}
                >
                  {m}m
                </button>
              ))}
            </div>
          </div>

          <div>
            <p className="text-xs text-text-faint mb-2">Energy</p>
            <div className="flex gap-2">
              {ENERGY_LABELS.map((label, i) => {
                const value = i + 1;
                return (
                  <button
                    key={value}
                    onClick={() => setEnergy(value)}
                    aria-label={label}
                    title={label}
                    className="h-9 flex-1 rounded-md border text-xs transition-colors"
                    style={{
                      borderColor: energy === value ? "var(--accent)" : "var(--border)",
                      color: energy === value ? "var(--accent-strong)" : "var(--text-muted)",
                      background: energy === value ? "var(--accent-soft)" : "transparent",
                    }}
                  >
                    {value}
                  </button>
                );
              })}
            </div>
          </div>

          <Button size="md" variant="primary" onClick={handleSubmit} disabled={loading} className="w-full">
            {loading ? "Fitting to your time…" : "Show what fits"}
          </Button>

          {results && (
            <ul className="space-y-1.5">
              {results.length === 0 && (
                <li className="text-sm text-text-faint text-center py-2">Nothing fits that window.</li>
              )}
              {results.map((r) => (
                <li
                  key={r.problem_id}
                  className="text-sm rounded-md bg-surface-2 px-3 py-2 flex items-center justify-between gap-2"
                >
                  <span className="text-text truncate">{r.title}</span>
                  <span className="text-text-faint text-xs shrink-0">{r.queue.replace(/_/g, " ")}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </Card>
  );
}
