import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getDailyTheoryQuestions,
  getInterviewModules,
  getQuestions,
  getQuestionsSummary,
  getTheoryPace,
  setQuestionMastery,
  setQuestionStatus,
  type QuestionFilters,
} from "@/lib/api";
import type { QuestionStatusInput } from "@/lib/types";

export function useQuestions(filters: QuestionFilters = {}) {
  return useQuery({
    // Every filter value is part of the cache key, so changing any one of
    // them — topic, phase, status, needs-review, attempted — refetches
    // rather than silently showing the previous filter's results.
    queryKey: ["questions", filters],
    queryFn: () => getQuestions(filters),
  });
}

/** OUTPUT 1 — the interview master map, with readiness per module. */
export function useInterviewModules() {
  return useQuery({
    queryKey: ["interview-modules"],
    queryFn: getInterviewModules,
  });
}

export function useQuestionsSummary() {
  return useQuery({
    queryKey: ["questions-summary"],
    queryFn: getQuestionsSummary,
  });
}

/** Sets a position on the 0-7 ladder. Replaced a coverage toggle: "seen"
 * and "can hold it under follow-ups" are different claims, and the module
 * readiness figure only counts the latter. */
export function useSetQuestionMastery() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      questionId,
      mastery,
      notes,
      minutes,
    }: {
      questionId: number;
      mastery: number;
      notes?: string;
      minutes?: number;
    }) => setQuestionMastery(questionId, mastery, notes, minutes),
    onSuccess: (_result, variables) => {
      queryClient.invalidateQueries({ queryKey: ["questions"] });
      queryClient.invalidateQueries({ queryKey: ["questions-summary"] });
      queryClient.invalidateQueries({ queryKey: ["interview-modules"] });
      queryClient.invalidateQueries({ queryKey: ["questions-daily"] });
      // Only a rating that actually logged time can move the pace
      // estimate — invalidating unconditionally would refetch it on
      // every single rating for no reason.
      if (variables.minutes != null) {
        queryClient.invalidateQueries({ queryKey: ["theory-pace"] });
      }
    },
  });
}

/** Sets the self-tag and/or revisit flag. Independent of mastery — a
 * status change never moves the mastery ladder or the readiness percentage,
 * only the personal filtering (`useQuestions({ learningStatus, ... })`). */
export function useSetQuestionStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      questionId,
      ...input
    }: { questionId: number } & QuestionStatusInput) => setQuestionStatus(questionId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["questions"] });
    },
  });
}

/** How long clearing the theory backlog takes at your actual recorded
 * pace, and the marginal cost/benefit of a different daily count. */
export function useTheoryPace() {
  return useQuery({
    queryKey: ["theory-pace"],
    queryFn: getTheoryPace,
  });
}

/** Today's 3 recommended theory questions — 1 case study plus 2 others by
 * default, for the Interview Prep — Theory block. Same day, same
 * progress state -> same picks; a rating change reshuffles what's due. */
export function useDailyTheoryQuestions() {
  return useQuery({
    queryKey: ["questions-daily"],
    queryFn: getDailyTheoryQuestions,
  });
}
