import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createBlock,
  setBlockStatus,
  submitAttempt,
  type AttemptInput,
  type BlockCreateInput,
} from "@/lib/api";
import type { BlockStatus, TodayOut } from "@/lib/types";
import { TODAY_QUERY_KEY } from "./useToday";

/** One tap, optimistic, undoable (build prompt 7) — the block flips
 * immediately in the cache; a failed request rolls it back. */
export function useMarkBlockStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ blockId, status, actualMinutes }: { blockId: number; status: BlockStatus; actualMinutes?: number }) =>
      setBlockStatus(blockId, status, actualMinutes),

    onMutate: async ({ blockId, status }) => {
      await queryClient.cancelQueries({ queryKey: TODAY_QUERY_KEY });
      const previous = queryClient.getQueryData<TodayOut>(TODAY_QUERY_KEY);

      if (previous) {
        const wasCounted = (s: BlockStatus) => s === "NOT DONE";
        queryClient.setQueryData<TodayOut>(TODAY_QUERY_KEY, {
          ...previous,
          blocks: previous.blocks.map((b) => (b.id === blockId ? { ...b, status } : b)),
          current_block:
            previous.current_block?.id === blockId
              ? { ...previous.current_block, status }
              : previous.current_block,
          counters: {
            ...previous.counters,
            blocks_remaining:
              previous.counters.blocks_remaining +
              (wasCounted(status) ? 1 : 0) -
              (previous.blocks.find((b) => b.id === blockId)?.status === "NOT DONE" ? 1 : 0),
          },
        });
      }
      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) queryClient.setQueryData(TODAY_QUERY_KEY, context.previous);
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: TODAY_QUERY_KEY });
    },
  });
}

/** New blocks always land after the day's schedule is refetched (their
 * server-assigned seq isn't knowable client-side), so no optimistic
 * insert — just invalidate once the write lands. */
export function useCreateBlock() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: BlockCreateInput) => createBlock(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TODAY_QUERY_KEY });
    },
  });
}

/** Writes the attempt and advances the review ladder server-side. The
 * next recommendation isn't predictable client-side, so this refetches
 * Today afterward rather than guessing at an optimistic next_action. */
export function useSubmitAttempt() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: AttemptInput) => submitAttempt(input),
    onSuccess: () => {
      // An attempt changes the problem's mastery and the solved counts, so
      // every view that reads them has to refetch. Invalidating only Today
      // is why a logged attempt left the Problems list still showing "Not
      // attempted".
      queryClient.invalidateQueries({ queryKey: TODAY_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ["problems"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });
}
