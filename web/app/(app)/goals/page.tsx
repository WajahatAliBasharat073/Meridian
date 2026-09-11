"use client";

import { useState } from "react";
import { Plus, Target } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { QueryError } from "@/components/ui/query-state";
import { useGoals, useCreateGoal, useUpdateGoal } from "@/hooks/useGoals";
import { useFinanceGoals } from "@/hooks/useFinance";
import { formatMoney } from "@/lib/money";
import { Select } from "@/components/ui/select";
import type { GoalOut } from "@/lib/types";

function GoalCard({ goal }: { goal: GoalOut }) {
  const update = useUpdateGoal();
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(goal.progress_pct);

  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3 mb-1">
        <h3 className="text-sm font-semibold text-text">{goal.title}</h3>
        {goal.status !== "active" && (
          <Badge color={goal.status === "completed" ? "var(--status-done)" : "var(--text-faint)"}>
            {goal.status}
          </Badge>
        )}
      </div>
      {goal.description && <p className="text-xs text-text-muted mb-3">{goal.description}</p>}

      <div className="flex items-center gap-3 mb-2">
        <div className="flex-1 h-2 rounded-full bg-surface-2 overflow-hidden">
          <div className="h-full rounded-full bg-accent transition-all" style={{ width: `${goal.progress_pct}%` }} />
        </div>
        <span className="text-xs text-text-muted tabular-nums shrink-0">{goal.progress_pct}%</span>
      </div>

      {goal.category && goal.minutes_logged != null && (
        <p className="text-[11px] text-text-faint mb-2">
          {goal.minutes_logged} min logged under &ldquo;{goal.category}&rdquo;
        </p>
      )}

      {/* Computed from real linked transactions -- shown alongside, never
          instead of, the manual self-report above, since they measure
          different things (money saved vs. how the user feels about it). */}
      {goal.linked_finance_goal && (
        <div className="mb-2 rounded-lg border border-border bg-surface-2/50 p-2.5">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] uppercase tracking-wide text-text-faint">
              Actual savings progress
            </span>
            <span className="text-[11px] font-mono tabular-nums text-text-muted">
              {formatMoney(goal.linked_finance_goal.current_amount, goal.linked_finance_goal.currency)} /{" "}
              {formatMoney(goal.linked_finance_goal.target_amount, goal.linked_finance_goal.currency)}
            </span>
          </div>
          <div className="h-1.5 rounded-full bg-surface overflow-hidden">
            <div
              className="h-full rounded-full bg-status-done"
              style={{ width: `${Math.min(goal.linked_finance_goal.progress_pct, 100)}%` }}
            />
          </div>
          {goal.linked_finance_goal.required_monthly_contribution != null && (
            <p className="text-[11px] text-text-faint mt-1">
              Save{" "}
              {formatMoney(
                goal.linked_finance_goal.required_monthly_contribution,
                goal.linked_finance_goal.currency
              )}
              /month to hit your target date
            </p>
          )}
        </div>
      )}

      {editing ? (
        <div className="flex items-center gap-2 mt-2">
          <input
            type="range"
            min={0}
            max={100}
            value={value}
            onChange={(e) => setValue(Number(e.target.value))}
            className="flex-1"
          />
          <span className="text-xs tabular-nums w-9 text-right">{value}%</span>
          <Button
            variant="primary"
            size="sm"
            onClick={() => {
              update.mutate({ goalId: goal.id, input: { progress_pct: value } });
              setEditing(false);
            }}
            disabled={update.isPending}
          >
            Save
          </Button>
        </div>
      ) : (
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={() => setEditing(true)} className="px-0">
            Update progress
          </Button>
          {goal.status === "active" && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => update.mutate({ goalId: goal.id, input: { status: "completed", progress_pct: 100 } })}
              disabled={update.isPending}
            >
              Mark complete
            </Button>
          )}
        </div>
      )}
    </Card>
  );
}

function NewGoalForm({ onDone }: { onDone: () => void }) {
  const create = useCreateGoal();
  const { data: financeGoals } = useFinanceGoals();
  const unlinkedFinanceGoals = (financeGoals ?? []).filter((g) => g.status === "active");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [targetDate, setTargetDate] = useState("");
  const [financeGoalId, setFinanceGoalId] = useState<number | "">("");

  return (
    <Card className="p-4">
      <form
        className="flex flex-col gap-2.5"
        onSubmit={(e) => {
          e.preventDefault();
          if (!title.trim()) return;
          create.mutate(
            {
              title: title.trim(),
              description: description.trim() || undefined,
              category: category.trim() || undefined,
              target_date: targetDate || undefined,
              finance_goal_id: financeGoalId === "" ? undefined : financeGoalId,
            },
            { onSuccess: onDone }
          );
        }}
      >
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Goal title — e.g. Become interview-ready for ML roles"
          className="h-10 rounded-lg border border-border bg-surface-2 px-3 text-sm text-text"
          autoFocus
        />
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Description (optional)"
          rows={2}
          className="rounded-lg border border-border bg-surface-2 px-3 py-2 text-sm text-text resize-none"
        />
        <div className="flex gap-2">
          <input
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="Linked category (optional, e.g. InterviewPrep)"
            className="h-10 flex-1 rounded-lg border border-border bg-surface-2 px-3 text-sm text-text"
          />
          <input
            type="date"
            value={targetDate}
            onChange={(e) => setTargetDate(e.target.value)}
            className="h-10 rounded-lg border border-border bg-surface-2 px-3 text-sm text-text"
          />
        </div>
        {unlinkedFinanceGoals.length > 0 && (
          <Select
            value={financeGoalId}
            onChange={(e) => setFinanceGoalId(e.target.value ? Number(e.target.value) : "")}
            className="h-10 text-sm"
          >
            <option value="">Not linked to a savings goal</option>
            {unlinkedFinanceGoals.map((fg) => (
              <option key={fg.id} value={fg.id}>
                Track real progress against: {fg.title}
              </option>
            ))}
          </Select>
        )}
        <div className="flex gap-2">
          <Button type="submit" variant="primary" size="sm" disabled={!title.trim() || create.isPending}>
            {create.isPending ? "Adding…" : "Add goal"}
          </Button>
          <Button type="button" variant="ghost" size="sm" onClick={onDone}>
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  );
}

export default function GoalsPage() {
  const { data, isLoading, isError, error } = useGoals();
  const [adding, setAdding] = useState(false);

  const active = data?.filter((g) => g.status === "active") ?? [];
  const other = data?.filter((g) => g.status !== "active") ?? [];

  return (
    <PageContainer>
      <PageHeader
        eyebrow="Insights"
        title="Goals"
        description="What you're actually working toward — progress is your own self-reported check-in; the minutes-logged figure is real, pulled from your linked category."
        action={
          !adding && (
            <Button variant="primary" size="md" onClick={() => setAdding(true)}>
              <Plus size={16} /> New goal
            </Button>
          )
        }
      />

      {adding && (
        <div className="mb-4">
          <NewGoalForm onDone={() => setAdding(false)} />
        </div>
      )}

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      )}

      {isError && <QueryError error={error} fallback="Couldn't load goals." />}

      {data && data.length === 0 && !adding && (
        <Card className="p-8 text-center">
          <Target size={28} className="mx-auto text-text-faint mb-3" />
          <p className="text-sm text-text-muted">No goals yet — add one to start tracking progress.</p>
        </Card>
      )}

      {active.length > 0 && (
        <div className="space-y-2 mb-6">
          {active.map((g) => (
            <GoalCard key={g.id} goal={g} />
          ))}
        </div>
      )}

      {other.length > 0 && (
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-text-faint mb-2">Completed / abandoned</p>
          <div className="space-y-2">
            {other.map((g) => (
              <GoalCard key={g.id} goal={g} />
            ))}
          </div>
        </div>
      )}
    </PageContainer>
  );
}
