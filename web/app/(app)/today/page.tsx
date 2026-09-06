"use client";

import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { useToday } from "@/hooks/useToday";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";
import { TodayGreeting } from "@/components/today/TodayGreeting";
import { CurrentBlockCard } from "@/components/today/CurrentBlockCard";
import { UpNextCard } from "@/components/today/UpNextCard";
import { TimeProgress } from "@/components/today/TimeProgress";
import { NextActionCard } from "@/components/today/NextActionCard";
import { Timeline } from "@/components/today/Timeline";
import { BandwidthControl } from "@/components/today/BandwidthControl";
import { Counters } from "@/components/today/Counters";
import { TodaySkeleton } from "@/components/today/TodaySkeleton";
import { WelcomeState } from "@/components/today/WelcomeState";
import { AddBlockForm } from "@/components/today/AddBlockForm";
import { DailyReflection } from "@/components/today/DailyReflection";
import { Button } from "@/components/ui/button";
import { QueryError } from "@/components/ui/query-state";
import { nowMinutesInKarachi } from "@/lib/time";

export default function TodayPage() {
  const { data, isLoading, isError, error, refetch, isFetching } = useToday();
  const [addingBlock, setAddingBlock] = useState(false);

  // Client-only clock, safe as a lazy initializer since this whole tree
  // only mounts once `data` has loaded (see below) — never part of the
  // server-rendered HTML.
  const [nowMinutes, setNowMinutes] = useState<number>(() => nowMinutesInKarachi());
  useEffect(() => {
    const id = setInterval(() => setNowMinutes(nowMinutesInKarachi()), 1000);
    return () => clearInterval(id);
  }, []);

  const dateLabel = data
    ? new Date(data.date + "T00:00:00").toLocaleDateString("en-US", {
        weekday: "long",
        month: "short",
        day: "numeric",
      })
    : undefined;

  return (
    <PageContainer width="narrow">
      <PageHeader
        eyebrow="Today"
        title="Today"
        description="What to do right now, what's next, and how the day is going."
        action={
          data ? (
            <time className="text-sm text-text-muted tabular-nums" dateTime={data.date}>
              {dateLabel}
            </time>
          ) : undefined
        }
      />

      {isLoading && <TodaySkeleton />}

      {isError && (
        <QueryError error={error} onRetry={() => refetch()} fallback="Something went wrong loading today." />
      )}

      {data && data.blocks.length === 0 && (
        <WelcomeState date={data.date} nextAction={data.next_action} />
      )}

      {data && data.blocks.length > 0 && (
        <div className="space-y-4">
          <TodayGreeting hour={Math.floor(nowMinutes / 60)} />

          <CurrentBlockCard block={data.current_block} />

          <UpNextCard blocks={data.blocks} current={data.current_block} nowMinutes={nowMinutes} />

          <TimeProgress blocks={data.blocks} />

          <Counters counters={data.counters} />

          <div>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-xs font-medium uppercase tracking-wide text-text-faint">
                Timeline
              </h2>
              <Button variant="ghost" size="sm" onClick={() => setAddingBlock((a) => !a)}>
                <Plus size={14} /> {addingBlock ? "Cancel" : "Add block"}
              </Button>
            </div>
            {addingBlock && (
              <div className="mb-3">
                <AddBlockForm date={data.date} onDone={() => setAddingBlock(false)} />
              </div>
            )}
            <Timeline blocks={data.blocks} />
          </div>

          <div className="pt-2 border-t border-border">
            <p className="text-xs font-medium uppercase tracking-wide text-text-faint mb-2 mt-4">
              Interview prep — what to study next
            </p>
            <NextActionCard recommendation={data.next_action} />
            <div className="mt-3">
              <BandwidthControl bandwidth={data.bandwidth} />
            </div>
          </div>

          <DailyReflection />

          <p className="text-center text-[11px] text-text-faint pt-2">
            Prayer times ±{data.prayer_accuracy_minutes[0]}–{data.prayer_accuracy_minutes[1]} min
            {isFetching && " · syncing…"}
          </p>
        </div>
      )}
    </PageContainer>
  );
}
