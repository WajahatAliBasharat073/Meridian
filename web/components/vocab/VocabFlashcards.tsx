"use client";

import { useMemo, useState } from "react";
import { ChevronLeft, ChevronRight, Volume2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/cn";
import { useDailyVocabReview, useSetVocabWordStatus, useVocabWords } from "@/hooks/useVocab";
import {
  VOCAB_STATUS_LABELS,
  type VocabCefrLevel,
  type VocabLearningStatus,
  type VocabWordOut,
} from "@/lib/types";
import { VocabWordDetailsPanel } from "@/components/vocab/VocabWordDetailsPanel";

/** Reuses the app's existing semantic tokens rather than a new palette --
 * revisit is the urgent one (danger), difficult is a caution (partial),
 * learning is neutral progress (accent), known is settled (done). */
const STATUS_COLOR: Record<VocabLearningStatus, string> = {
  known: "var(--status-done)",
  learning: "var(--accent-strong)",
  difficult: "var(--status-partial)",
  need_to_revisit: "var(--danger)",
};

const STATUS_FILTER_OPTIONS: { value: string; label: string }[] = [
  { value: "", label: "All words" },
  { value: "not_reviewed", label: "Not yet reviewed" },
  ...(Object.keys(VOCAB_STATUS_LABELS) as VocabLearningStatus[]).map((s) => ({
    value: s,
    label: VOCAB_STATUS_LABELS[s],
  })),
];

const CEFR_LEVELS: VocabCefrLevel[] = ["A1", "A2", "B1", "B2", "C1", "C2"];
const LEVEL_FILTER_OPTIONS: { value: string; label: string }[] = [
  { value: "", label: "All levels" },
  ...CEFR_LEVELS.map((l) => ({ value: l, label: l })),
];

type Mode = "daily" | "browse";

export function VocabFlashcards() {
  const [mode, setMode] = useState<Mode>("daily");
  const [statusFilter, setStatusFilter] = useState("");
  const [levelFilter, setLevelFilter] = useState("");

  const daily = useDailyVocabReview(5);
  const all = useVocabWords();

  // Today's 5 picks are frozen the moment they first load, and stay put --
  // otherwise rating word #1 changes its learning_status, which changes
  // its priority in build_daily_review, which reshuffles words #2-5 out
  // from under the user mid-session. Only once every word in the current
  // batch has been rated (ratedInBatch, updated from handleRate below)
  // does the batch unfreeze and pick up whatever the server now ranks
  // highest.
  const [frozenDailyIds, setFrozenDailyIds] = useState<number[] | null>(null);
  const [ratedInBatch, setRatedInBatch] = useState<Set<number>>(new Set());
  const [batchGen, setBatchGen] = useState(0);

  // Render-time state adjustment (React's documented alternative to an
  // Effect for "derive state once from a value that just became
  // available"): as soon as daily.data has words and nothing is frozen
  // yet, freeze it. The `=== null` guard makes this a one-shot per batch
  // -- freezing triggers an immediate re-render with frozenDailyIds set,
  // so this body never runs twice for the same batch.
  if (frozenDailyIds === null && daily.data && daily.data.length > 0) {
    setFrozenDailyIds(daily.data.map((w) => w.id));
    setBatchGen((g) => g + 1);
  }

  function handleRate(wordId: number, isRated: boolean) {
    const next = new Set(ratedInBatch);
    if (isRated) next.add(wordId);
    else next.delete(wordId);
    if (frozenDailyIds && next.size >= frozenDailyIds.length) {
      // Whole batch rated -- unfreeze so the next render picks up a
      // fresh top-5 now that these words' priorities have changed.
      setFrozenDailyIds(null);
      setRatedInBatch(new Set());
    } else {
      setRatedInBatch(next);
    }
  }

  // Membership and order come from frozenDailyIds; the word *content*
  // (learning_status badge, etc.) is always the freshest copy available,
  // so rating a word still updates its own card immediately.
  const dailyById = useMemo(() => {
    const map = new Map<number, VocabWordOut>();
    daily.data?.forEach((w) => map.set(w.id, w));
    all.data?.forEach((w) => map.set(w.id, w));
    return map;
  }, [daily.data, all.data]);

  const frozenDailyData = useMemo(() => {
    if (!frozenDailyIds) return undefined;
    return frozenDailyIds.map((id) => dailyById.get(id)).filter((w): w is VocabWordOut => !!w);
  }, [frozenDailyIds, dailyById]);

  const browseData = useMemo(() => {
    if (!all.data) return all.data;
    let words = all.data;
    if (statusFilter === "not_reviewed") words = words.filter((w) => w.learning_status == null);
    else if (statusFilter !== "") words = words.filter((w) => w.learning_status === statusFilter);
    if (levelFilter !== "") words = words.filter((w) => w.cefr_level === levelFilter);
    return words;
  }, [all.data, statusFilter, levelFilter]);

  // Falls back to the live (unfrozen) daily.data only when there's no
  // batch to freeze yet -- still loading, or genuinely no words due --
  // so the loading/empty states below behave exactly as before.
  const data = mode === "daily" ? frozenDailyData ?? daily.data : browseData;
  const isLoading = mode === "daily" ? daily.isLoading : all.isLoading;

  return (
    <div>
      <div className="flex items-center justify-between mb-4 gap-2 flex-wrap">
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-surface-2 border border-border">
          <button
            onClick={() => setMode("daily")}
            className={cn(
              "px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors",
              mode === "daily"
                ? "bg-surface text-text shadow-xs border border-border"
                : "text-text-muted hover:text-text"
            )}
          >
            Today&apos;s Review
          </button>
          <button
            onClick={() => setMode("browse")}
            className={cn(
              "px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors",
              mode === "browse"
                ? "bg-surface text-text shadow-xs border border-border"
                : "text-text-muted hover:text-text"
            )}
          >
            Browse All
          </button>
        </div>

        {mode === "browse" && (
          <div className="flex items-center gap-2">
            <Select
              value={levelFilter}
              onChange={(e) => setLevelFilter(e.target.value)}
              aria-label="Filter by CEFR level"
              className="h-8 text-xs w-auto"
            >
              {LEVEL_FILTER_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </Select>
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              aria-label="Filter by learning status"
              className="h-8 text-xs w-auto"
            >
              {STATUS_FILTER_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </Select>
          </div>
        )}
      </div>

      {isLoading && <Skeleton className="h-64" />}

      {!isLoading && (!data || data.length === 0) && (
        <EmptyState
          icon={Volume2}
          title={mode === "daily" ? "No words due for review" : "No words match this filter"}
          description={
            mode === "daily"
              ? "Add vocabulary or import from your Notion export -- once you have words, today's review appears here."
              : "Try a different status filter, or add your first word from the form above."
          }
        />
      )}

      {data && data.length > 0 && (
        <VocabFlashcardsLoaded
          key={mode === "daily" ? `daily:${batchGen}` : `browse:${statusFilter}:${levelFilter}`}
          data={data}
          onRate={mode === "daily" ? handleRate : undefined}
        />
      )}
    </div>
  );
}

function VocabFlashcardsLoaded({
  data,
  onRate,
}: {
  data: VocabWordOut[];
  onRate?: (wordId: number, isRated: boolean) => void;
}) {
  const setStatus = useSetVocabWordStatus();
  const [index, setIndex] = useState(0);
  const current = data[Math.min(index, data.length - 1)];

  return (
    <div>
      <div className="flex flex-wrap gap-1.5 mb-4">
        {data.map((w, i) => (
          <button
            key={w.id}
            type="button"
            onClick={() => setIndex(i)}
            aria-label={`${w.word} — ${w.learning_status ? VOCAB_STATUS_LABELS[w.learning_status] : "Not yet reviewed"}`}
            aria-current={i === index ? "true" : undefined}
            className={cn(
              "h-2.5 w-2.5 rounded-full transition-all",
              i === index ? "ring-2 ring-accent ring-offset-1 ring-offset-surface" : ""
            )}
            style={{
              backgroundColor: w.learning_status ? STATUS_COLOR[w.learning_status] : "var(--border-strong)",
            }}
          />
        ))}
      </div>

      <Card className="p-8 text-center">
        <span className="text-xs text-text-faint tabular-nums">
          {index + 1} / {data.length}
        </span>

        <div className="my-6">
          <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight text-text text-balance">
            {current.word}
          </h2>
          <div className="flex items-center justify-center gap-2 mt-2 flex-wrap">
            {current.pronunciation && (
              <span className="text-sm text-text-faint font-mono">/{current.pronunciation}/</span>
            )}
            {current.part_of_speech && <Badge color="var(--text-faint)">{current.part_of_speech}</Badge>}
            {current.cefr_level && <Badge color="var(--accent-strong)">{current.cefr_level}</Badge>}
            {current.category && <Badge color="var(--accent)">{current.category}</Badge>}
          </div>
        </div>

        <VocabWordDetailsPanel key={current.id} word={current} />

        {(current.word_family || current.collocations?.length) && (
          <div className="mt-4 space-y-2 text-left max-w-xl mx-auto text-sm">
            {current.word_family && Object.keys(current.word_family).length > 0 && (
              <p>
                <span className="text-text-faint">Word family: </span>
                <span className="text-text-muted">
                  {Object.entries(current.word_family)
                    .map(([pos, form]) => `${form} (${pos})`)
                    .join(" · ")}
                </span>
              </p>
            )}
            {current.collocations && current.collocations.length > 0 && (
              <div>
                <span className="text-text-faint">Collocations: </span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {current.collocations.map((phrase) => (
                    <Badge key={phrase} color="var(--mastery-l4)">
                      {phrase}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {current.common_mistake && (
          <p className="mt-3 text-left max-w-xl mx-auto text-sm rounded-lg border border-danger/30 bg-danger/10 px-3 py-2">
            <span className="text-danger font-medium">Common mistake: </span>
            <span className="text-text-muted">{current.common_mistake}</span>
          </p>
        )}

        {(current.word_patterns || current.paraphrase) && (
          <div className="mt-4 space-y-1.5 text-left max-w-xl mx-auto text-sm">
            {current.word_patterns && (
              <p>
                <span className="text-text-faint">Patterns &amp; collocations: </span>
                <span className="text-text-muted">{current.word_patterns}</span>
              </p>
            )}
            {current.paraphrase && (
              <p>
                <span className="text-text-faint">Paraphrase: </span>
                <span className="text-text-muted">{current.paraphrase}</span>
              </p>
            )}
          </div>
        )}

        {current.dictionary_link && (
          <a
            href={current.dictionary_link}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block mt-3 text-xs text-accent-strong hover:underline"
          >
            Dictionary / video link
          </a>
        )}

        <div className="border-t border-border mt-6 pt-4">
          <p className="text-[10px] uppercase tracking-wide text-text-faint mb-2">How well do you know it?</p>
          <div className="flex flex-wrap justify-center gap-1.5">
            {(Object.keys(VOCAB_STATUS_LABELS) as VocabLearningStatus[]).map((s) => (
              <button
                key={s}
                type="button"
                disabled={setStatus.isPending}
                onClick={() => {
                  // Clicking the already-selected status clears it back
                  // to unreviewed, matching the question bank's status
                  // toggle -- a self-rating should be correctable.
                  const nextStatus = current.learning_status === s ? null : s;
                  setStatus.mutate({ wordId: current.id, input: { learning_status: nextStatus } });
                  onRate?.(current.id, nextStatus !== null);
                }}
                className={cn(
                  "h-9 px-3 rounded-md text-[12px] font-medium border transition-colors",
                  current.learning_status === s
                    ? "text-bg"
                    : "border-border text-text-muted hover:bg-surface-2 hover:text-text"
                )}
                style={
                  current.learning_status === s
                    ? { borderColor: STATUS_COLOR[s], backgroundColor: STATUS_COLOR[s] }
                    : undefined
                }
              >
                {VOCAB_STATUS_LABELS[s]}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-between gap-2 mt-6">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setIndex((i) => Math.max(0, i - 1))}
            disabled={index === 0}
          >
            <ChevronLeft size={15} />
            Prev
          </Button>
          <span className="text-[11px] text-text-faint truncate">
            {current.learning_status ? VOCAB_STATUS_LABELS[current.learning_status] : "Not yet reviewed"}
          </span>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setIndex((i) => Math.min(data.length - 1, i + 1))}
            disabled={index === data.length - 1}
          >
            Next
            <ChevronRight size={15} />
          </Button>
        </div>
      </Card>
    </div>
  );
}
