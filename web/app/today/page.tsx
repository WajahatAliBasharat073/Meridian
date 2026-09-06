"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { useToday } from "@/hooks/useToday";
import { ApiError } from "@/lib/api";
import { AppShell } from "@/components/AppShell";
import { CurrentBlockCard } from "@/components/today/CurrentBlockCard";
import { NextActionCard } from "@/components/today/NextActionCard";
import { Timeline } from "@/components/today/Timeline";
import { BandwidthControl } from "@/components/today/BandwidthControl";
import { Counters } from "@/components/today/Counters";
import { TodaySkeleton } from "@/components/today/TodaySkeleton";
import { WelcomeState } from "@/components/today/WelcomeState";
import { AddBlockForm } from "@/components/today/AddBlockForm";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";

export default function TodayPage() {
  const { data, isLoading, isError, error, refetch, isFetching } = useToday();
  const [addingBlock, setAddingBlock] = useState(false);

  const isAuthError = error instanceof ApiError && error.status === 401;
  const errorMessage = isAuthError
    ? "Your session expired."
    : error instanceof ApiError && error.status === 0
      ? "Couldn't reach the server — check your connection."
      : "Something went wrong loading today.";

  return (
    <AppShell>
      <main className="mx-auto max-w-lg px-4 py-6 pb-16">
        <header className="flex items-center justify-between mb-5">
          <h1 className="text-sm font-medium text-text-faint uppercase tracking-wide">Today</h1>
          {data && (
            <time className="text-sm text-text-muted tabular-nums" dateTime={data.date}>
              {new Date(data.date + "T00:00:00").toLocaleDateString("en-US", {
                weekday: "long",
                month: "short",
                day: "numeric",
              })}
            </time>
          )}
        </header>

        {isLoading && <TodaySkeleton />}

        {isError && (
          <div className="space-y-3">
            <Alert variant="error">{errorMessage}</Alert>
            {isAuthError ? (
              <a href="/login">
                <Button size="md" variant="primary" className="w-full">
                  Sign in again
                </Button>
              </a>
            ) : (
              <Button size="md" variant="secondary" onClick={() => refetch()} className="w-full">
                Retry
              </Button>
            )}
          </div>
        )}

        {data && data.blocks.length === 0 && (
          <WelcomeState date={data.date} nextAction={data.next_action} />
        )}

        {data && data.blocks.length > 0 && (
          <div className="space-y-4">
            <CurrentBlockCard block={data.current_block} />
            <Counters counters={data.counters} />
            <NextActionCard recommendation={data.next_action} />
            <BandwidthControl bandwidth={data.bandwidth} />

            <div>
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-sm font-medium text-text-faint uppercase tracking-wide">
                  Timeline
                </h2>
                <Button variant="ghost" size="sm" onClick={() => setAddingBlock((a) => !a)}>
                  <Plus size={14} /> Add block
                </Button>
              </div>
              {addingBlock && (
                <div className="mb-3">
                  <AddBlockForm date={data.date} onDone={() => setAddingBlock(false)} />
                </div>
              )}
              <Timeline blocks={data.blocks} />
            </div>

            <p className="text-center text-[11px] text-text-faint pt-2">
              Prayer times ±{data.prayer_accuracy_minutes[0]}&ndash;{data.prayer_accuracy_minutes[1]} min
              {isFetching && " · syncing…"}
            </p>
          </div>
        )}
      </main>
    </AppShell>
  );
}
