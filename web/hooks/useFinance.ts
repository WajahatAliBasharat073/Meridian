import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createFinanceAccount,
  createFinanceCategory,
  createFinanceGoal,
  createFinanceRecurring,
  createFinanceTransaction,
  deleteFinanceAccount,
  deleteFinanceBudget,
  deleteFinanceGoal,
  deleteFinanceRecurring,
  deleteFinanceTransaction,
  getFinanceAccounts,
  getFinanceBudgets,
  getFinanceCategories,
  getFinanceDashboard,
  getFinanceGoals,
  getFinanceRecurring,
  getFinanceTransactions,
  takeFinanceNetWorthSnapshot,
  updateFinanceAccount,
  updateFinanceGoal,
  upsertFinanceBudget,
  type FinanceTransactionFilters,
} from "@/lib/api";
import type {
  FinanceAccountCreateInput,
  FinanceAccountUpdateInput,
  FinanceBudgetUpsertInput,
  FinanceCategoryCreateInput,
  FinanceGoalCreateInput,
  FinanceGoalUpdateInput,
  FinanceRecurringCreateInput,
  FinanceTransactionCreateInput,
} from "@/lib/types";

const ACCOUNTS_KEY = ["finance", "accounts"] as const;
const CATEGORIES_KEY = ["finance", "categories"] as const;
const BUDGETS_KEY = ["finance", "budgets"] as const;
const GOALS_KEY = ["finance", "goals"] as const;
const RECURRING_KEY = ["finance", "recurring"] as const;
const DASHBOARD_KEY = ["finance", "dashboard"] as const;

/** Every mutation below invalidates the dashboard too -- it's a rollup of
 * all the others, and a stale dashboard after adding a transaction is
 * exactly the kind of "looks confident but is wrong" bug this app has
 * been deliberately cleaned of elsewhere (research/thesis log, coach
 * fallback). */
function useInvalidateFinance() {
  const queryClient = useQueryClient();
  return (keys: readonly (readonly unknown[])[]) => {
    for (const key of keys) queryClient.invalidateQueries({ queryKey: key });
    queryClient.invalidateQueries({ queryKey: DASHBOARD_KEY });
  };
}

export function useFinanceAccounts() {
  return useQuery({ queryKey: ACCOUNTS_KEY, queryFn: getFinanceAccounts });
}

export function useCreateFinanceAccount() {
  const invalidate = useInvalidateFinance();
  return useMutation({
    mutationFn: (input: FinanceAccountCreateInput) => createFinanceAccount(input),
    onSuccess: () => invalidate([ACCOUNTS_KEY]),
  });
}

export function useUpdateFinanceAccount() {
  const invalidate = useInvalidateFinance();
  return useMutation({
    mutationFn: ({ accountId, input }: { accountId: number; input: FinanceAccountUpdateInput }) =>
      updateFinanceAccount(accountId, input),
    onSuccess: () => invalidate([ACCOUNTS_KEY]),
  });
}

export function useDeleteFinanceAccount() {
  const invalidate = useInvalidateFinance();
  return useMutation({
    mutationFn: (accountId: number) => deleteFinanceAccount(accountId),
    onSuccess: () => invalidate([ACCOUNTS_KEY]),
  });
}

export function useFinanceCategories() {
  return useQuery({ queryKey: CATEGORIES_KEY, queryFn: getFinanceCategories });
}

export function useCreateFinanceCategory() {
  const invalidate = useInvalidateFinance();
  return useMutation({
    mutationFn: (input: FinanceCategoryCreateInput) => createFinanceCategory(input),
    onSuccess: () => invalidate([CATEGORIES_KEY]),
  });
}

export function useFinanceTransactions(filters: FinanceTransactionFilters = {}) {
  return useQuery({
    queryKey: ["finance", "transactions", filters],
    queryFn: () => getFinanceTransactions(filters),
  });
}

export function useCreateFinanceTransaction() {
  const invalidate = useInvalidateFinance();
  return useMutation({
    mutationFn: (input: FinanceTransactionCreateInput) => createFinanceTransaction(input),
    // Account balances and budget utilization both move when a
    // transaction is created -- not just the transaction list itself.
    onSuccess: () => invalidate([["finance", "transactions"], ACCOUNTS_KEY, BUDGETS_KEY, GOALS_KEY]),
  });
}

export function useDeleteFinanceTransaction() {
  const invalidate = useInvalidateFinance();
  return useMutation({
    mutationFn: (transactionId: number) => deleteFinanceTransaction(transactionId),
    onSuccess: () => invalidate([["finance", "transactions"], ACCOUNTS_KEY, BUDGETS_KEY, GOALS_KEY]),
  });
}

export function useFinanceRecurring() {
  return useQuery({ queryKey: RECURRING_KEY, queryFn: getFinanceRecurring });
}

export function useCreateFinanceRecurring() {
  const invalidate = useInvalidateFinance();
  return useMutation({
    mutationFn: (input: FinanceRecurringCreateInput) => createFinanceRecurring(input),
    onSuccess: () => invalidate([RECURRING_KEY]),
  });
}

export function useDeleteFinanceRecurring() {
  const invalidate = useInvalidateFinance();
  return useMutation({
    mutationFn: (recurringId: number) => deleteFinanceRecurring(recurringId),
    onSuccess: () => invalidate([RECURRING_KEY]),
  });
}

export function useFinanceBudgets() {
  return useQuery({ queryKey: BUDGETS_KEY, queryFn: getFinanceBudgets });
}

export function useUpsertFinanceBudget() {
  const invalidate = useInvalidateFinance();
  return useMutation({
    mutationFn: (input: FinanceBudgetUpsertInput) => upsertFinanceBudget(input),
    onSuccess: () => invalidate([BUDGETS_KEY]),
  });
}

export function useDeleteFinanceBudget() {
  const invalidate = useInvalidateFinance();
  return useMutation({
    mutationFn: (budgetId: number) => deleteFinanceBudget(budgetId),
    onSuccess: () => invalidate([BUDGETS_KEY]),
  });
}

export function useFinanceGoals() {
  return useQuery({ queryKey: GOALS_KEY, queryFn: getFinanceGoals });
}

export function useCreateFinanceGoal() {
  const invalidate = useInvalidateFinance();
  return useMutation({
    mutationFn: (input: FinanceGoalCreateInput) => createFinanceGoal(input),
    onSuccess: () => invalidate([GOALS_KEY]),
  });
}

export function useUpdateFinanceGoal() {
  const invalidate = useInvalidateFinance();
  return useMutation({
    mutationFn: ({ goalId, input }: { goalId: number; input: FinanceGoalUpdateInput }) =>
      updateFinanceGoal(goalId, input),
    onSuccess: () => invalidate([GOALS_KEY]),
  });
}

export function useDeleteFinanceGoal() {
  const invalidate = useInvalidateFinance();
  return useMutation({
    mutationFn: (goalId: number) => deleteFinanceGoal(goalId),
    onSuccess: () => invalidate([GOALS_KEY]),
  });
}

export function useFinanceDashboard() {
  return useQuery({ queryKey: DASHBOARD_KEY, queryFn: getFinanceDashboard });
}

export function useTakeNetWorthSnapshot() {
  const invalidate = useInvalidateFinance();
  return useMutation({
    mutationFn: () => takeFinanceNetWorthSnapshot(),
    onSuccess: () => invalidate([]),
  });
}
