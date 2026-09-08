import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getDailyTheoryQuestions,
  getInterviewModules,
  getQuestions,
  getQuestionsSummary,
  getTheoryPace,
  setQuestionMastery,
} from "@/lib/api";

export function useQuestions(category?: string, module?: string) {
  return useQuery({
    queryKey: ["questions", category, module],
    queryFn: () => getQuestions(category, module),
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
