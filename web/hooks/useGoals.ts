import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createGoal, getGoals, updateGoal } from "@/lib/api";
import type { GoalCreateInput, GoalUpdateInput } from "@/lib/types";

export const GOALS_QUERY_KEY = ["goals"] as const;

export function useGoals() {
  return useQuery({
    queryKey: GOALS_QUERY_KEY,
    queryFn: () => getGoals(),
  });
}

export function useCreateGoal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: GoalCreateInput) => createGoal(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: GOALS_QUERY_KEY }),
  });
}

export function useUpdateGoal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ goalId, input }: { goalId: number; input: GoalUpdateInput }) => updateGoal(goalId, input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: GOALS_QUERY_KEY }),
  });
}
