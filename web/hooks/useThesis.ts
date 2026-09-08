import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createThesisLog, getThesisLogs } from "@/lib/api";
import type { ThesisLogCreateInput } from "@/lib/types";

export const THESIS_LOGS_QUERY_KEY = ["thesis-logs"] as const;

export function useThesisLogs() {
  return useQuery({
    queryKey: THESIS_LOGS_QUERY_KEY,
    queryFn: () => getThesisLogs(),
  });
}

export function useCreateThesisLog() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: ThesisLogCreateInput) => createThesisLog(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: THESIS_LOGS_QUERY_KEY }),
  });
}
