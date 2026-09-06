import { useMutation, useQueryClient } from "@tanstack/react-query";
import { setBlockStatus, submitAttempt, type AttemptInput } from "@/lib/api";
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

/** Writes the attempt and advances the review ladder server-side. The
 * next recommendation isn't predictable client-side, so this refetches
 * Today afterward rather than guessing at an optimistic next_action. */
export function useSubmitAttempt() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: AttemptInput) => submitAttempt(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TODAY_QUERY_KEY });
    },
  });
}
