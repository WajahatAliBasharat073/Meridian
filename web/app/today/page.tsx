"use client";

import { useToday } from "@/hooks/useToday";
import { CurrentBlockCard } from "@/components/today/CurrentBlockCard";
import { NextActionCard } from "@/components/today/NextActionCard";
import { Timeline } from "@/components/today/Timeline";
import { BandwidthControl } from "@/components/today/BandwidthControl";
import { Counters } from "@/components/today/Counters";
import { TodaySkeleton } from "@/components/today/TodaySkeleton";
import { Button } from "@/components/ui/button";

export default function TodayPage() {
  const { data, isLoading, isError, refetch, isFetching } = useToday();

  return (
    <main className="mx-auto max-w-lg px-4 py-6 pb-16">
      <header className="flex items-baseline justify-between mb-5">
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
        <div className="rounded-xl border border-danger/30 bg-danger/10 p-5 text-center">
          <p className="text-text text-sm mb-3">Couldn&apos;t reach the server.</p>
          <Button size="sm" onClick={() => refetch()}>
            Retry
          </Button>
        </div>
      )}

      {data && (
        <div className="space-y-4">
          <CurrentBlockCard block={data.current_block} />
          <Counters counters={data.counters} />
          <NextActionCard recommendation={data.next_action} />
          <BandwidthControl bandwidth={data.bandwidth} />

          <div>
            <h2 className="text-sm font-medium text-text-faint uppercase tracking-wide mb-2">
              Timeline
            </h2>
            <Timeline blocks={data.blocks} />
          </div>

          <p className="text-center text-[11px] text-text-faint pt-2">
            Prayer times ±{data.prayer_accuracy_minutes[0]}&ndash;{data.prayer_accuracy_minutes[1]} min
            {isFetching && " · syncing…"}
          </p>
        </div>
      )}
    </main>
  );
}
