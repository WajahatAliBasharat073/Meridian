import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getConcepts, submitConceptAttempt } from "@/lib/api";
import type { ConceptAttemptInput } from "@/lib/types";

export function useConcepts(category?: string, phase?: string) {
  return useQuery({
    queryKey: ["concepts", category, phase],
    queryFn: () => getConcepts(category, phase),
  });
}

export function useSubmitConceptAttempt() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: ConceptAttemptInput) => submitConceptAttempt(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["concepts"] });
    },
  });
}
