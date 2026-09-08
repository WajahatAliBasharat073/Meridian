"use client";

import { useState } from "react";
import { FlaskConical, Plus } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { QueryError } from "@/components/ui/query-state";
import { useCreateThesisLog, useThesisLogs } from "@/hooks/useThesis";
import { formatCountdown } from "@/lib/time";

export default function ResearchPage() {
  const { data, isLoading, isError, error, refetch } = useThesisLogs();
  const createLog = useCreateThesisLog();
  const [adding, setAdding] = useState(false);

  // Form state
  const [workSummary, setWorkSummary] = useState("");
  const [milestone, setMilestone] = useState("");
  const [minutes, setMinutes] = useState(60);
  const [outputType, setOutputType] = useState("experiment");

  const logs = data ?? [];
  const loading = isLoading;
  const saving = createLog.isPending;

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!workSummary.trim()) return;
    createLog.mutate(
      {
        date: new Date().toISOString().slice(0, 10),
        work_summary: workSummary.trim(),
        milestone: milestone.trim() || undefined,
        minutes: Number(minutes) || undefined,
        output_type: outputType,
        status: "completed",
      },
      {
        onSuccess: () => {
          setWorkSummary("");
          setMilestone("");
          setAdding(false);
        },
      }
    );
  };

  // Every figure below is computed from the logs that exist. The previous
  // version fell back to invented numbers (490 minutes, 8 sessions, "+18%
  // this month", "3 research milestones", "GenAI Architectures / On
  // schedule") whenever the real data was empty, which made an untouched
  // tracker look like a month of work.
  const timed = logs.filter((l) => l.minutes != null && l.minutes > 0);
  const totalMinutes = timed.reduce((acc, l) => acc + (l.minutes ?? 0), 0);
  const milestones = Array.from(
    new Set(logs.map((l) => l.milestone).filter((m): m is string => Boolean(m)))
  );
  const workTypes = Array.from(
    new Set(logs.map((l) => l.output_type).filter((t): t is string => Boolean(t)))
  );
  const nextDeadline = logs
    .map((l) => l.deadline)
    .filter((d): d is string => Boolean(d))
    .sort()[0];

  return (
    <PageContainer>
      <PageHeader
        eyebrow="Academic & R&D"
        title="Research & Thesis Hub"
        description="Track research papers, architectural experiments, thesis milestones, and deep engineering writing."
        action={
          !adding && (
            <Button variant="primary" size="md" onClick={() => setAdding(true)} className="gap-1.5">
              <Plus size={15} /> Log Research
            </Button>
          )
        }
      />

      {isError && (
        <QueryError
          error={error}
          onRetry={() => refetch()}
          fallback="Couldn't load your thesis log."
        />
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
        <Card className="p-4">
          <p className="text-xs text-text-faint">Time logged</p>
          <p className="text-2xl font-bold text-text tabular-nums font-mono mt-1">
            {totalMinutes > 0 ? formatCountdown(totalMinutes) : "—"}
          </p>
          <p className="text-[10px] text-text-faint mt-1">
            {totalMinutes > 0
              ? `across ${timed.length} timed ${timed.length === 1 ? "entry" : "entries"}`
              : "no entry has hours recorded yet"}
          </p>
        </Card>

        <Card className="p-4">
          <p className="text-xs text-text-faint">Entries</p>
          <p className="text-2xl font-bold text-text tabular-nums font-mono mt-1">
            {logs.length}
          </p>
          <p className="text-[10px] text-text-faint mt-1">
            {milestones.length > 0
              ? `${milestones.length} ${milestones.length === 1 ? "milestone" : "milestones"}`
              : "no milestone recorded"}
          </p>
        </Card>

        <Card className="p-4">
          <p className="text-xs text-text-faint">Work type</p>
          <p className="text-base font-semibold text-text mt-1 truncate">
            {workTypes.length > 0 ? workTypes.join(", ") : "—"}
          </p>
          <p className="text-[10px] text-text-faint mt-1">
            {nextDeadline ? `next deadline ${nextDeadline}` : "no deadline recorded"}
          </p>
        </Card>
      </div>

      {/* New Log Form */}
      {adding && (
        <Card className="p-5 mb-4 border-accent/40 bg-gradient-to-b from-surface to-surface-2">
          <form onSubmit={handleCreate} className="space-y-3">
            <h3 className="text-sm font-semibold text-text">Log Research Output</h3>
            <div>
              <label className="text-xs text-text-muted block mb-1">Work Summary</label>
              <textarea
                value={workSummary}
                onChange={(e) => setWorkSummary(e.target.value)}
                placeholder="Key findings, derivations, implementation notes..."
                rows={2}
                className="w-full rounded-lg border border-border bg-surface-2 p-2.5 text-xs text-text resize-none"
                required
              />
            </div>

            <div className="grid sm:grid-cols-3 gap-2">
              <div>
                <label className="text-xs text-text-muted block mb-1">Milestone (optional)</label>
                <input
                  type="text"
                  value={milestone}
                  onChange={(e) => setMilestone(e.target.value)}
                  placeholder="e.g. Attention benchmark"
                  className="w-full h-9 rounded-lg border border-border bg-surface-2 px-2.5 text-xs text-text"
                />
              </div>

              <div>
                <label className="text-xs text-text-muted block mb-1">Duration (min)</label>
                <input
                  type="number"
                  value={minutes}
                  onChange={(e) => setMinutes(Number(e.target.value))}
                  className="w-full h-9 rounded-lg border border-border bg-surface-2 px-2.5 text-xs text-text font-mono"
                />
              </div>

              <div>
                <label className="text-xs text-text-muted block mb-1">Output Type</label>
                <select
                  value={outputType}
                  onChange={(e) => setOutputType(e.target.value)}
                  className="w-full h-9 rounded-lg border border-border bg-surface-2 px-2.5 text-xs text-text"
                >
                  <option value="experiment">Experiment</option>
                  <option value="paper_reading">Paper Reading</option>
                  <option value="thesis_writing">Thesis Writing</option>
                  <option value="code_implementation">Code Implementation</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="ghost" size="sm" onClick={() => setAdding(false)}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" size="sm" disabled={saving || !workSummary.trim()}>
                {saving ? "Saving…" : "Save Entry"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Logs List */}
      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-20" />
          ))}
        </div>
      ) : logs.length === 0 ? (
        <Card className="p-8 text-center border-dashed border-border bg-surface/40">
          <FlaskConical size={28} className="mx-auto text-text-faint mb-2" />
          <p className="text-sm text-text font-medium">No research logs recorded yet</p>
          <p className="text-xs text-text-faint mt-1 mb-4">
            Log your paper readings, thesis milestones, and experimental findings.
          </p>
          <Button variant="primary" size="sm" onClick={() => setAdding(true)}>
            Start First Research Log
          </Button>
        </Card>
      ) : (
        <ul className="space-y-2">
          {logs.map((log) => (
            <li key={log.id}>
              <Card className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <Badge color="var(--accent)">{log.output_type || "Research"}</Badge>
                    {log.milestone && (
                      <span className="text-xs text-text-faint font-medium">· {log.milestone}</span>
                    )}
                    <span className="text-[11px] text-text-faint tabular-nums ml-auto sm:ml-0">
                      {log.date}
                    </span>
                  </div>
                  <p className="text-xs text-text leading-relaxed">{log.work_summary}</p>
                </div>
                {log.minutes && (
                  <div className="text-right shrink-0">
                    <span className="text-xs font-mono tabular-nums text-text-muted">
                      {formatCountdown(log.minutes)}
                    </span>
                  </div>
                )}
              </Card>
            </li>
          ))}
        </ul>
      )}
    </PageContainer>
  );
}
