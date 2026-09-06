import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getQuestions, getQuestionsSummary, toggleQuestionCoverage } from "@/lib/api";

export function useQuestions(category?: string) {
  return useQuery({
    queryKey: ["questions", category],
    queryFn: () => getQuestions(category),
  });
}

export function useQuestionsSummary() {
  return useQuery({
    queryKey: ["questions-summary"],
    queryFn: getQuestionsSummary,
  });
}

export function useToggleQuestionCoverage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (questionId: number) => toggleQuestionCoverage(questionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["questions"] });
      queryClient.invalidateQueries({ queryKey: ["questions-summary"] });
    },
  });
}
