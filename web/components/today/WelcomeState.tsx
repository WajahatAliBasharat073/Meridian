"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { NextActionCard } from "@/components/today/NextActionCard";
import { AddBlockForm } from "@/components/today/AddBlockForm";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import type { RecommendationOut } from "@/lib/types";

/** Shown instead of the full Today layout when a real account has no
 * time_blocks for today yet — a brand-new signup, before any schedule
 * exists. Never fabricates data to fill the space; explains what's
 * missing, offers the actual fix (add a block), and shows the one thing
 * that's already genuinely available (a recommendation drawn from the
 * shared problem set, independent of any personal schedule) — "empty
 * states teach the system rather than showing a shrug" (build prompt 7). */
export function WelcomeState({
  date,
  nextAction,
}: {
  date: string;
  nextAction: RecommendationOut | null;
}) {
  const { email } = useCurrentUser();
  const name = email ? email.split("@")[0] : null;
  const [adding, setAdding] = useState(false);

  return (
    <div className="space-y-4">
      <Card className="p-6">
        <p className="text-xs font-medium uppercase tracking-wide text-accent mb-2">
          Welcome{name ? `, ${name}` : ""}
        </p>
        <h2 className="text-2xl font-semibold text-text text-balance leading-tight">
          There&apos;s no schedule for today yet.
        </h2>
        <p className="text-sm text-text-muted mt-2 leading-relaxed">
          Once your daily time-blocks exist, this is where you&apos;ll see the current
          one with a live countdown, and a running tally of what&apos;s left.
        </p>
        {!adding && (
          <Button variant="primary" size="lg" className="w-full mt-4" onClick={() => setAdding(true)}>
            Add your first block
          </Button>
        )}
      </Card>

      {adding && <AddBlockForm date={date} onDone={() => setAdding(false)} />}

      {nextAction && (
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-text-faint mb-2">
            What already works — your next recommended problem
          </p>
          <NextActionCard recommendation={nextAction} />
        </div>
      )}
    </div>
  );
}
