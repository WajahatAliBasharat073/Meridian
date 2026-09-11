import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createVocabWord,
  deleteVocabWord,
  getDailyVocabReview,
  getVocabSummary,
  getVocabWords,
  setVocabWordStatus,
  updateVocabWord,
} from "@/lib/api";
import type {
  VocabStatusUpdateInput,
  VocabWordCreateInput,
  VocabWordUpdateInput,
} from "@/lib/types";

const VOCAB_KEY = ["vocab"] as const;
const VOCAB_DAILY_KEY = ["vocab", "daily"] as const;
const VOCAB_SUMMARY_KEY = ["vocab", "summary"] as const;

export function useVocabWords(learningStatus?: string) {
  return useQuery({
    queryKey: [...VOCAB_KEY, learningStatus ?? "all"],
    queryFn: () => getVocabWords(learningStatus),
  });
}

export function useDailyVocabReview(count = 10) {
  return useQuery({
    queryKey: [...VOCAB_DAILY_KEY, count],
    queryFn: () => getDailyVocabReview(count),
  });
}

export function useCreateVocabWord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: VocabWordCreateInput) => createVocabWord(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: VOCAB_KEY });
    },
  });
}

export function useSetVocabWordStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ wordId, input }: { wordId: number; input: VocabStatusUpdateInput }) =>
      setVocabWordStatus(wordId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: VOCAB_KEY });
    },
  });
}

export function useDeleteVocabWord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (wordId: number) => deleteVocabWord(wordId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: VOCAB_KEY });
    },
  });
}

export function useUpdateVocabWord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ wordId, input }: { wordId: number; input: VocabWordUpdateInput }) =>
      updateVocabWord(wordId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: VOCAB_KEY });
    },
  });
}

export function useVocabSummary() {
  return useQuery({
    queryKey: VOCAB_SUMMARY_KEY,
    queryFn: getVocabSummary,
  });
}
