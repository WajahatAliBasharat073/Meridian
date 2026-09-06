import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deleteTimeBudget, getTimeBudgets, upsertTimeBudget } from "@/lib/api";
import type { TimeBudgetUpsertInput } from "@/lib/types";

export const TIME_BUDGETS_QUERY_KEY = ["time-budgets"] as const;

export function useTimeBudgets() {
  return useQuery({
    queryKey: TIME_BUDGETS_QUERY_KEY,
    queryFn: getTimeBudgets,
  });
}

export function useUpsertTimeBudget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: TimeBudgetUpsertInput) => upsertTimeBudget(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: TIME_BUDGETS_QUERY_KEY }),
  });
}

export function useDeleteTimeBudget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (budgetId: number) => deleteTimeBudget(budgetId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: TIME_BUDGETS_QUERY_KEY }),
  });
}
