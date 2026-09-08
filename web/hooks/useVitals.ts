import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { addWater, getTodayVitals, updateNutrition, updateRecovery } from "@/lib/api";
import type { NutritionUpdateInput, RecoveryUpdateInput } from "@/lib/types";

export const VITALS_QUERY_KEY = ["vitals-today"] as const;

export function useTodayVitals() {
  return useQuery({
    queryKey: VITALS_QUERY_KEY,
    queryFn: () => getTodayVitals(),
  });
}

export function useUpdateRecovery() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: RecoveryUpdateInput) => updateRecovery(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: VITALS_QUERY_KEY }),
  });
}

export function useUpdateNutrition() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: NutritionUpdateInput) => updateNutrition(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: VITALS_QUERY_KEY }),
  });
}

export function useAddWater() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (ml: number) => addWater(ml),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: VITALS_QUERY_KEY }),
  });
}
