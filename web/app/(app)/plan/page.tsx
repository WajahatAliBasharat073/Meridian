"use client";

import { useState } from "react";
import { Clock, Plus, Trash2, ChevronDown, ChevronUp, Calendar, Target } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useTimeBudgets, useUpsertTimeBudget, useDeleteTimeBudget } from "@/hooks/useTimeBudgets";
import { formatCountdown } from "@/lib/time";
import { cn } from "@/lib/cn";

// ── Real Sep–Dec 2026 Daily Schedule (extracted from Wajahat_Productivity_OS_Sep-Dec_2026.xlsx) ──
// Grouped by phase. This is Monday's template — applies Mon/Tue/Wed/Thu.
const DAILY_SCHEDULE = [
  {
    phase: "🌅 Early Morning & Deep Work",
    phaseColor: "var(--status-partial)",
    blocks: [
      { start: "04:21", end: "04:41", activity: "🕌 Fajr + morning dua / reflection", tier: "T1", category: "Prayer", minutes: 20 },
      { start: "04:30", end: "04:40", activity: "Wake + water", tier: "T1", category: "Health", minutes: 10 },
      { start: "04:41", end: "06:45", activity: "Thesis — deep research / literature review", tier: "T2", category: "Research", minutes: 124, note: "Highest-energy window — protect it" },
      { start: "06:45", end: "07:30", activity: "Thesis — implementation / writing", tier: "T2", category: "Research", minutes: 45 },
      { start: "07:30", end: "08:05", activity: "🍳 Breakfast", tier: "T1", category: "Meal", minutes: 35 },
      { start: "08:05", end: "08:15", activity: "Hydration + light movement", tier: "T1", category: "Health", minutes: 10 },
      { start: "08:15", end: "09:00", activity: "Buffer / thesis admin catch-up", tier: "T2", category: "Research", minutes: 45 },
    ],
  },
  {
    phase: "💼 Remote Job Core Execution",
    phaseColor: "var(--accent)",
    blocks: [
      { start: "09:00", end: "11:00", activity: "💼 Remote job — focused work", tier: "T1", category: "Work", minutes: 120, note: "Job wins if urgent task appears" },
      { start: "11:00", end: "11:10", activity: "Short break — movement / hydration", tier: "T1", category: "Health", minutes: 10 },
      { start: "11:10", end: "12:08", activity: "💼 Remote job — work / meetings", tier: "T1", category: "Work", minutes: 58 },
      { start: "12:08", end: "12:23", activity: "🕌 Zuhr + short recovery", tier: "T1", category: "Prayer", minutes: 15, note: "No deep cognitive work across this transition" },
      { start: "12:23", end: "12:53", activity: "🍛 Lunch — a real meal", tier: "T1", category: "Meal", minutes: 30 },
      { start: "12:53", end: "16:36", activity: "💼 Remote job — afternoon work / meetings", tier: "T1", category: "Work", minutes: 223 },
      { start: "16:36", end: "16:51", activity: "🕌 Asr + movement / hydration reset", tier: "T1", category: "Prayer", minutes: 15 },
      { start: "16:51", end: "17:00", activity: "💼 Remote job — shutdown / admin buffer", tier: "T1", category: "Work", minutes: 9 },
    ],
  },
  {
    phase: "💻 Evening Interview Prep Mastery",
    phaseColor: "hsl(258,80%,65%)",
    blocks: [
      { start: "17:05", end: "19:25", activity: "💻 Interview Prep — Coding (DSA / LeetCode)", tier: "T2", category: "DSA", minutes: 140 },
      { start: "19:25", end: "20:40", activity: "💻 Interview Prep — Theory: ML System Design", tier: "T2", category: "Learning", minutes: 75 },
    ],
  },
  {
    phase: "🌙 Night Routine & Recovery",
    phaseColor: "var(--text-faint)",
    blocks: [
      { start: "20:40", end: "21:15", activity: "🍛 Dinner — moderate meal", tier: "T1", category: "Meal", minutes: 35, note: "Avoid heavy meal close to sleep" },
      { start: "21:15", end: "21:35", activity: "📚 English Vocabulary (spaced repetition)", tier: "T3", category: "Learning", minutes: 20 },
      { start: "21:35", end: "22:00", activity: "📖 Reading", tier: "T4", category: "Personal", minutes: 25 },
      { start: "22:00", end: "22:15", activity: "🔄 Night shutdown ritual", tier: "T1", category: "Health", minutes: 15 },
    ],
  },
];

const TIER_META: Record<string, { label: string; cls: string }> = {
  T1: { label: "Fixed Anchor", cls: "bg-amber-500/10 text-amber-500 border-amber-500/30" },
  T2: { label: "High Leverage", cls: "bg-indigo-500/10 text-indigo-400 border-indigo-500/30" },
  T3: { label: "Growth", cls: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" },
  T4: { label: "Buffer", cls: "bg-surface-3 text-text-faint border-border" },
};

export default function PlanPage() {
  const { data: budgets, isLoading } = useTimeBudgets();
  const upsertBudget = useUpsertTimeBudget();
  const deleteBudget = useDeleteTimeBudget();

  const [addingBudget, setAddingBudget] = useState(false);
  const [category, setCategory] = useState("Work");
  const [hoursPerWeek, setHoursPerWeek] = useState(35);
  const [expandedPhase, setExpandedPhase] = useState<string | null>(null);

  const hasBudgets = budgets && budgets.length > 0;
  const totalBudgetMinutes = hasBudgets ? budgets.reduce((a, b) => a + b.minutes_per_week, 0) : 0;
  const totalActualMinutes = hasBudgets ? budgets.reduce((a, b) => a + b.actual_minutes_this_week, 0) : 0;
  const adherencePct = totalBudgetMinutes > 0 ? Math.min(100, Math.round((totalActualMinutes / totalBudgetMinutes) * 100)) : 0;

  const totalDailyMinutes = DAILY_SCHEDULE.flatMap(p => p.blocks).reduce((s, b) => s + b.minutes, 0);

  const handleSaveBudget = (e: React.FormEvent) => {
    e.preventDefault();
    upsertBudget.mutate({ category, minutes_per_week: hoursPerWeek * 60 });
    setAddingBudget(false);
  };

  return (
    <PageContainer width="wide">
      <PageHeader
        eyebrow="Architecture of Time"
        title="Planning, Budgets & Routines"
        description="Structured weekly time budgets and your real Sep–Dec 2026 daily operating schedule."
      />

      {/* ── Stats Row ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
        <Card className="p-4">
          <p className="text-xs text-text-faint">Weekly Budget</p>
          <p className="text-2xl font-bold text-text tabular-nums font-mono mt-1">
            {hasBudgets ? formatCountdown(totalBudgetMinutes) : "—"}
          </p>
          <p className="text-[10px] text-text-muted mt-1">{hasBudgets ? "Allocated" : "Not set yet"}</p>
        </Card>

        <Card className="p-4">
          <p className="text-xs text-text-faint">Logged This Week</p>
          <p className="text-2xl font-bold text-accent-strong tabular-nums font-mono mt-1">
            {hasBudgets ? formatCountdown(totalActualMinutes) : "—"}
          </p>
          <p className="text-[10px] mt-1" style={{ color: hasBudgets ? "var(--status-done)" : "var(--text-faint)" }}>
            {hasBudgets ? `${adherencePct}% adherence` : "No data yet"}
          </p>
        </Card>

        <Card className="p-4">
          <p className="text-xs text-text-faint">Daily Blocks</p>
          <p className="text-2xl font-bold text-text tabular-nums font-mono mt-1">21</p>
          <p className="text-[10px] text-text-muted mt-1">Sep–Dec schedule</p>
        </Card>

        <Card className="p-4">
          <p className="text-xs text-text-faint">Daily Focus Time</p>
          <p className="text-2xl font-bold text-text tabular-nums font-mono mt-1">{formatCountdown(totalDailyMinutes)}</p>
          <p className="text-[10px] text-text-muted mt-1">Planned per day</p>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-6 items-start">

        {/* ══ LEFT — Real daily schedule ══ */}
        <div className="space-y-4">
          <div>
            <h2 className="text-sm font-semibold text-text">Sep–Dec 2026 Daily Operating Schedule</h2>
            <p className="text-xs text-text-muted mt-1">
              Monday template (your real schedule from the productivity workbook). Anchored to solar prayer times and biological energy cycles.
            </p>
          </div>

          {DAILY_SCHEDULE.map((phase) => {
            const isOpen = expandedPhase === phase.phase || expandedPhase === null;
            const phaseMinutes = phase.blocks.reduce((s, b) => s + b.minutes, 0);
            return (
              <div key={phase.phase} className="rounded-xl border border-border bg-surface overflow-hidden shadow-sm">
                {/* Phase header */}
                <button
                  type="button"
                  onClick={() => setExpandedPhase(isOpen && expandedPhase === phase.phase ? null : phase.phase)}
                  className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-surface-2/40 transition-colors"
                >
                  <div>
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-text flex items-center gap-2">
                      <span
                        className="h-2 w-2 rounded-full shrink-0"
                        style={{ backgroundColor: phase.phaseColor }}
                      />
                      {phase.phase}
                    </h3>
                    <p className="text-[11px] text-text-faint mt-0.5">
                      {phase.blocks[0].start} – {phase.blocks[phase.blocks.length - 1].end}
                      {" · "}
                      {phase.blocks.length} blocks · {formatCountdown(phaseMinutes)}
                    </p>
                  </div>
                  {expandedPhase === phase.phase ? (
                    <ChevronUp size={15} className="text-text-faint shrink-0" />
                  ) : (
                    <ChevronDown size={15} className="text-text-faint shrink-0" />
                  )}
                </button>

                {/* Block rows */}
                {(expandedPhase === phase.phase || expandedPhase === null) && (
                  <ul className="divide-y divide-border/60">
                    {phase.blocks.map((block, i) => {
                      const tierMeta = TIER_META[block.tier] ?? TIER_META.T2;
                      return (
                        <li key={i} className="flex items-start gap-3 px-4 py-2.5 hover:bg-surface-2/30 transition-colors">
                          <div className="shrink-0 w-20 text-[11px] font-mono tabular-nums text-text-faint pt-0.5">
                            {block.start}
                            <br />
                            <span className="text-[10px]">→ {block.end}</span>
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-2 flex-wrap">
                              <p className="text-xs font-medium text-text">{block.activity}</p>
                              <span
                                className={cn("text-[9px] px-1.5 py-0.5 rounded border font-medium shrink-0", tierMeta.cls)}
                              >
                                {block.tier}
                              </span>
                            </div>
                            {block.note && (
                              <p className="text-[10px] text-text-faint italic mt-0.5">{block.note}</p>
                            )}
                          </div>
                          <span className="shrink-0 text-[11px] font-mono tabular-nums text-text-muted pt-0.5">
                            {block.minutes}m
                          </span>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            );
          })}
        </div>

        {/* ══ RIGHT — Weekly time budgets ══ */}
        <div className="lg:sticky lg:top-4 space-y-4">
          <Card className="p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-text">Weekly Budgets</h3>
                <p className="text-xs text-text-muted mt-0.5">
                  Category time allocation targets
                </p>
              </div>
              {!addingBudget && (
                <Button variant="secondary" size="sm" onClick={() => setAddingBudget(true)} className="gap-1 text-xs">
                  <Plus size={13} /> Add
                </Button>
              )}
            </div>

            {addingBudget && (
              <form onSubmit={handleSaveBudget} className="mb-4 p-3 rounded-xl bg-surface-2 border border-border space-y-3 text-xs">
                <div>
                  <label className="text-text-muted block mb-1">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full h-9 rounded-lg border border-border bg-surface px-2.5 text-xs text-text"
                  >
                    <option value="Work">Work</option>
                    <option value="Research">Research</option>
                    <option value="Learning">Learning & ML</option>
                    <option value="DSA">DSA</option>
                    <option value="Health">Health & Exercise</option>
                    <option value="Personal">Personal & Reading</option>
                  </select>
                </div>
                <div>
                  <label className="text-text-muted block mb-1">Hours / week</label>
                  <input
                    type="number" min="1" max="80" value={hoursPerWeek}
                    onChange={(e) => setHoursPerWeek(Number(e.target.value))}
                    className="w-full h-9 rounded-lg border border-border bg-surface px-2.5 text-xs text-text font-mono"
                  />
                </div>
                <div className="flex gap-2">
                  <Button type="button" variant="ghost" size="sm" onClick={() => setAddingBudget(false)}>Cancel</Button>
                  <Button type="submit" variant="primary" size="sm">Save</Button>
                </div>
              </form>
            )}

            <div className="space-y-4">
              {isLoading ? (
                <p className="text-xs text-text-faint text-center py-4">Loading…</p>
              ) : hasBudgets ? (
                budgets.map((b) => {
                  const pct = Math.min(100, Math.round((b.actual_minutes_this_week / Math.max(1, b.minutes_per_week)) * 100));
                  const barColor = pct >= 100 ? "var(--danger)" : pct >= 80 ? "var(--status-done)" : "var(--accent)";
                  return (
                    <div key={b.category} className="space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-text">{b.category}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-text-muted font-mono tabular-nums text-[11px]">
                            {formatCountdown(b.actual_minutes_this_week)} / {formatCountdown(b.minutes_per_week)}
                          </span>
                          <span className="text-text-faint font-semibold text-[11px]">{pct}%</span>
                          <button
                            type="button"
                            onClick={() => deleteBudget.mutate(b.id)}
                            className="text-text-faint hover:text-danger transition-colors"
                          >
                            <Trash2 size={11} />
                          </button>
                        </div>
                      </div>
                      <div className="h-2 rounded-full bg-surface-2 overflow-hidden">
                        <div className="h-full transition-all duration-300" style={{ width: `${pct}%`, backgroundColor: barColor }} />
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-center py-8 space-y-3">
                  <div className="h-10 w-10 mx-auto rounded-xl bg-surface-2 flex items-center justify-center text-text-faint">
                    <Clock size={20} />
                  </div>
                  <p className="text-xs text-text-muted">No time budgets yet.</p>
                  <Button variant="secondary" size="sm" onClick={() => setAddingBudget(true)} className="gap-1">
                    <Plus size={13} /> Set up first budget
                  </Button>
                </div>
              )}
            </div>
          </Card>

          {/* Schedule legend */}
          <Card className="p-4">
            <h3 className="text-xs font-semibold text-text mb-3">Tier Legend</h3>
            <div className="space-y-2">
              {Object.entries(TIER_META).map(([tier, meta]) => (
                <div key={tier} className="flex items-center gap-2 text-xs">
                  <span className={cn("px-1.5 py-0.5 rounded border text-[10px] font-semibold", meta.cls)}>{tier}</span>
                  <span className="text-text-muted">{meta.label}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </PageContainer>
  );
}
