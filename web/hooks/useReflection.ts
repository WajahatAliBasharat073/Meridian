import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getTodayReflection, upsertTodayReflection } from "@/lib/api";
import type { DailyReflectionUpsertInput } from "@/lib/types";

export const REFLECTION_QUERY_KEY = ["reflection-today"] as const;

export function useTodayReflection() {
  return useQuery({
    queryKey: REFLECTION_QUERY_KEY,
    queryFn: getTodayReflection,
  });
}

export function useUpsertReflection() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: DailyReflectionUpsertInput) => upsertTodayReflection(input),
    onSuccess: (data) => queryClient.setQueryData(REFLECTION_QUERY_KEY, data),
  });
}
