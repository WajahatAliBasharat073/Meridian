"use client";

import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { useToday } from "@/hooks/useToday";
import { TodayGreeting } from "@/components/today/TodayGreeting";
import { ActivityController } from "@/components/today/ActivityController";
import { UpNextCard } from "@/components/today/UpNextCard";
import { TimeProgress } from "@/components/today/TimeProgress";
import { LifeVitalsBar } from "@/components/today/LifeVitalsBar";
import { DailyWisdom } from "@/components/today/DailyWisdom";
import { MeridianRecommends } from "@/components/recommendations/MeridianRecommends";
import { DailyTheoryCard } from "@/components/today/DailyTheoryCard";
import { TheoryPaceCard } from "@/components/today/TheoryPaceCard";
import { Timeline } from "@/components/today/Timeline";
import { isBlockLocked } from "@/lib/blockLock";
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
    <main className="w-full max-w-[1440px] mx-auto px-4 md:px-6 py-5 pb-24 md:pb-8">
      {isLoading && <TodaySkeleton />}

      {isError && (
        <QueryError
          error={error}
          onRetry={() => refetch()}
          fallback="Something went wrong loading today."
        />
      )}

      {data && data.blocks.length === 0 && (
        <WelcomeState date={data.date} nextAction={data.next_action} />
      )}

      {data && data.blocks.length > 0 && (
        <div>
          {/* ── Page header strip ── */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6 pb-4 border-b border-border/50">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-widest text-text-faint mb-0.5">
                Command Center
              </p>
              <h1 className="text-2xl font-bold tracking-tight text-text">Today</h1>
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <DailyWisdom />
              {dateLabel && (
                <time
                  className="text-xs text-text-muted tabular-nums font-mono shrink-0 hidden sm:block"
                  dateTime={data.date}
                >
                  {dateLabel}
                </time>
              )}
              {isFetching && (
                <span className="text-[11px] text-text-faint animate-pulse">syncing…</span>
              )}
            </div>
          </div>

          {/* ── Premium 2-column dashboard ── */}
          <div className="grid grid-cols-1 xl:grid-cols-[400px_1fr] gap-6 items-start">

            {/* ══ LEFT PANEL — Control + Vitals (sticky on xl+) ══ */}
            <div className="xl:sticky xl:top-4 space-y-4 xl:max-h-[calc(100vh-6rem)] xl:overflow-y-auto xl:pr-1">

              <TodayGreeting hour={Math.floor(nowMinutes / 60)} />

              <TimeProgress blocks={data.blocks} />

              <Counters counters={data.counters} />

              <ActivityController
                block={data.current_block}
                upcomingBlock={
                  data.current_block
                    ? null
                    : // Skip past a block whose window mostly elapsed with
                      // Focus never started on it — surfacing it here would
                      // invite exactly the dishonest "mark it done anyway"
                      // click the lock exists to prevent. Falls through to
                      // the plain first-unfinished-block if everything
                      // NOT DONE happens to be locked, then to the empty state.
                      data.blocks.find(
                        (b) => b.status === "NOT DONE" && !isBlockLocked(b, nowMinutes)
                      ) ||
                      data.blocks.find((b) => b.status === "NOT DONE") ||
                      data.blocks[0] ||
                      null
                }
              />

              <UpNextCard blocks={data.blocks} current={data.current_block} nowMinutes={nowMinutes} />

              <LifeVitalsBar />

              <DailyTheoryCard
                isLiveNow={
                  data.current_block?.category === "InterviewPrep" &&
                  data.current_block?.activity.toLowerCase().includes("theory")
                }
              />
              <TheoryPaceCard />

              <MeridianRecommends
                blocks={data.blocks}
                dsaRec={data.next_action}
                currentBlock={data.current_block}
              />

              {data.bandwidth && (
                <div className="border-t border-border pt-3">
                  <BandwidthControl bandwidth={data.bandwidth} />
                </div>
              )}

              <DailyReflection />

              <p className="text-center text-[10px] text-text-faint pb-2">
                Solar prayer times ±{data.prayer_accuracy_minutes[0]}–{data.prayer_accuracy_minutes[1]} min
              </p>
            </div>

            {/* ══ RIGHT PANEL — Full day timeline ══ */}
            <div className="space-y-3 min-w-0">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-sm font-semibold text-text">Execution Timeline</h2>
                  <p className="text-xs text-text-faint mt-0.5">
                    {data.blocks.length} blocks · full day schedule
                  </p>
                </div>
                <Button variant="ghost" size="sm" onClick={() => setAddingBlock((a) => !a)}>
                  <Plus size={14} /> {addingBlock ? "Cancel" : "Add block"}
                </Button>
              </div>

              {addingBlock && (
                <div className="mb-3">
                  <AddBlockForm date={data.date} onDone={() => setAddingBlock(false)} />
                </div>
              )}

              <Timeline blocks={data.blocks} nowMinutes={nowMinutes} />
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
