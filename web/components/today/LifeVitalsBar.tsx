"use client";

import { useEffect, useState } from "react";
import { Coffee, Droplets, Moon, Utensils } from "lucide-react";
import { Card } from "@/components/ui/card";
import { logBehavioralEvent, pushNotification } from "@/lib/notifications";
import { playSound } from "@/lib/soundEngine";

const WATER_STORAGE_KEY = "meridian_water_today";

export function LifeVitalsBar() {
  const [waterMl, setWaterMl] = useState<number>(1000);
  const targetWaterMl = 2500;

  useEffect(() => {
    try {
      const stored = localStorage.getItem(WATER_STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        const todayStr = new Date().toISOString().slice(0, 10);
        if (parsed.date === todayStr) {
          setWaterMl(parsed.ml);
        }
      }
    } catch {}
  }, []);

  const addWater = (amount = 250) => {
    const updated = waterMl + amount;
    setWaterMl(updated);
    try {
      const todayStr = new Date().toISOString().slice(0, 10);
      localStorage.setItem(WATER_STORAGE_KEY, JSON.stringify({ date: todayStr, ml: updated }));
    } catch {}
    playSound("gentle");
    logBehavioralEvent("hydration_logged", undefined, { added: amount, total: updated });

    if (updated >= targetWaterMl && waterMl < targetWaterMl) {
      pushNotification({
        kind: "hydration",
        title: "Daily Hydration Met",
        body: `💧 Target of ${targetWaterMl}ml reached. Outstanding job maintaining your vitals!`,
        soundType: "completion",
      });
    }
  };

  const waterPct = Math.min(100, Math.round((waterMl / targetWaterMl) * 100));

  return (
    <Card className="p-4 bg-surface/90 border-border">
      <div className="flex items-center justify-between gap-3 mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-text-faint">
          Daily Vitals & Balance
        </span>
        <span className="text-[11px] text-text-faint">Auto-syncs with recovery log</span>
      </div>

      {/* Two columns, not four: in the ~400px sticky panel four tracks left
          ~85px each, which collided each card's label with its status text. */}
      <div className="grid grid-cols-2 gap-3">
        {/* Hydration */}
        <div className="p-3 rounded-xl bg-surface-2/60 border border-border flex flex-col justify-between min-w-0">
          <div className="flex items-center justify-between gap-1.5 min-w-0 text-xs text-text-muted mb-1.5">
            <span className="flex items-center gap-1 min-w-0 text-accent-strong font-medium">
              <Droplets size={14} className="shrink-0" />
              <span className="truncate">Water</span>
            </span>
            <span className="tabular-nums text-text-faint shrink-0">{waterPct}%</span>
          </div>
          <div className="flex items-baseline justify-between mb-2">
            <span className="text-base font-semibold text-text tabular-nums">{waterMl}</span>
            <span className="text-[11px] text-text-faint">/ {targetWaterMl} ml</span>
          </div>
          <button
            onClick={() => addWater(250)}
            className="w-full py-1.5 text-xs font-medium rounded-lg bg-accent-soft text-accent-strong hover:bg-accent-soft/80 border border-accent/20 transition-colors"
          >
            +250 ml
          </button>
        </div>

        {/* Nutrition / Meal */}
        <div className="p-3 rounded-xl bg-surface-2/60 border border-border flex flex-col justify-between min-w-0">
          <div className="flex items-center justify-between gap-1.5 min-w-0 text-xs text-text-muted mb-1.5">
            <span className="flex items-center gap-1 min-w-0 text-warning font-medium">
              <Utensils size={14} className="shrink-0" />
              <span className="truncate">Nutrition</span>
            </span>
            <span className="text-[10px] text-text-faint shrink-0">Scheduled</span>
          </div>
          <div>
            <p className="text-xs font-semibold text-text">Dinner Window</p>
            <p className="text-[11px] text-text-faint mt-0.5">20:00 &ndash; 21:00</p>
          </div>
          <span className="text-[10px] text-text-faint mt-2 block">Protects cognitive energy</span>
        </div>

        {/* Focus Recovery Break */}
        <div className="p-3 rounded-xl bg-surface-2/60 border border-border flex flex-col justify-between min-w-0">
          <div className="flex items-center justify-between gap-1.5 min-w-0 text-xs text-text-muted mb-1.5">
            <span className="flex items-center gap-1 min-w-0 text-text-muted font-medium">
              <Coffee size={14} className="shrink-0" />
              <span className="truncate">Breaks</span>
            </span>
            <span className="text-[10px] text-status-done font-medium shrink-0">On track</span>
          </div>
          <div>
            <p className="text-xs font-semibold text-text">Micro-Rest</p>
            <p className="text-[11px] text-text-faint mt-0.5">Every 90 min deep work</p>
          </div>
          <span className="text-[10px] text-text-faint mt-2 block">Prevents afternoon crash</span>
        </div>

        {/* Sleep & Wind Down */}
        <div className="p-3 rounded-xl bg-surface-2/60 border border-border flex flex-col justify-between min-w-0">
          <div className="flex items-center justify-between gap-1.5 min-w-0 text-xs text-text-muted mb-1.5">
            <span className="flex items-center gap-1 min-w-0 text-text-muted font-medium">
              <Moon size={14} className="shrink-0" />
              <span className="truncate">Wind Down</span>
            </span>
            <span className="text-[10px] text-text-faint shrink-0">23:00</span>
          </div>
          <div>
            <p className="text-xs font-semibold text-text">Rest Target</p>
            <p className="text-[11px] text-text-faint mt-0.5">7.5 hours optimal</p>
          </div>
          <span className="text-[10px] text-text-faint mt-2 block">&lt; 5.5h reduces focus by 40%</span>
        </div>
      </div>
    </Card>
  );
}
