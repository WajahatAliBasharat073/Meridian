import type {
  AISettingsOut,
  AISettingsUpdateInput,
  AttemptResult,
  BlockStatus,
  ConceptAttemptInput,
  ConceptOut,
  DailyReflectionOut,
  DailyReflectionUpsertInput,
  DailyRecapOut,
  DashboardSummaryOut,
  GoalCreateInput,
  GoalOut,
  GoalUpdateInput,
  MasteryLevel,
  ProblemOut,
  ProfileOut,
  ProfileUpdate,
  QuestionOut,
  QuestionSummaryOut,
  RecommendationOut,
  ReviewDueOut,
  TimeBlockOut,
  TimeBudgetOut,
  TimeBudgetUpsertInput,
  TodayOut,
  WeeklyReviewOut,
} from "./types";

/** Carries the HTTP status (0 = the request never reached a server at
 * all) so callers can tell "you're logged out" apart from "the network
 * is down" apart from "the server errored" — one generic message for
 * all three is a real diagnosis dead-end, not just unpolished copy. */
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(path, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new ApiError(0, "Network request failed");
  }

  if (!res.ok) {
    const text = await res.text();
    throw new ApiError(res.status, text || res.statusText);
  }

  return res.json() as Promise<T>;
}

export function getToday(): Promise<TodayOut> {
  return request<TodayOut>("/api/today", { cache: "no-store" });
}

export function setBlockStatus(
  blockId: number,
  status: BlockStatus,
  actualMinutes?: number
): Promise<unknown> {
  return request(`/api/blocks/${blockId}/status`, {
    method: "POST",
    body: JSON.stringify({ status, actual_minutes: actualMinutes ?? null }),
  });
}

export interface BlockCreateInput {
  date: string; // "YYYY-MM-DD"
  start_spec: string;
  end_spec: string;
  activity: string;
  tier: "T1" | "T2" | "T3" | "T4";
  category: string;
  planned_minutes: number;
  what_to_do?: string;
  notes?: string;
}

export function createBlock(input: BlockCreateInput): Promise<TimeBlockOut> {
  return request<TimeBlockOut>("/api/blocks", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export interface AttemptInput {
  problem_id: number;
  mastery_level: MasteryLevel;
  minutes?: number;
  hint_used?: boolean;
  key_insight?: string;
}

export function submitAttempt(input: AttemptInput): Promise<AttemptResult> {
  return request<AttemptResult>("/api/attempts", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getRecommend(minutes?: number, energy?: number): Promise<RecommendationOut[]> {
  const params = new URLSearchParams();
  if (minutes != null) params.set("minutes", String(minutes));
  if (energy != null) params.set("energy", String(energy));
  const qs = params.toString();
  return request<RecommendationOut[]>(`/api/recommend${qs ? `?${qs}` : ""}`);
}

export function getReviewsDue(): Promise<ReviewDueOut[]> {
  return request<ReviewDueOut[]>("/api/reviews/due");
}

export function getDashboardSummary(): Promise<DashboardSummaryOut> {
  return request<DashboardSummaryOut>("/api/dashboard/summary", { cache: "no-store" });
}

export function getProblems(pattern?: string, difficulty?: string): Promise<ProblemOut[]> {
  const params = new URLSearchParams();
  if (pattern) params.set("pattern", pattern);
  if (difficulty) params.set("difficulty", difficulty);
  const qs = params.toString();
  return request<ProblemOut[]>(`/api/problems${qs ? `?${qs}` : ""}`);
}

export function getProfile(): Promise<ProfileOut> {
  return request<ProfileOut>("/api/profile", { cache: "no-store" });
}

export function updateProfile(input: ProfileUpdate): Promise<ProfileOut> {
  return request<ProfileOut>("/api/profile", {
    method: "PUT",
    body: JSON.stringify(input),
  });
}

export function getDailyRecap(): Promise<DailyRecapOut> {
  return request<DailyRecapOut>("/api/daily-recap", { cache: "no-store" });
}

export function getQuestions(category?: string): Promise<QuestionOut[]> {
  const qs = category ? `?category=${encodeURIComponent(category)}` : "";
  return request<QuestionOut[]>(`/api/questions${qs}`, { cache: "no-store" });
}

export function toggleQuestionCoverage(questionId: number): Promise<{ covered: boolean }> {
  return request<{ covered: boolean }>(`/api/questions/${questionId}/toggle`, { method: "POST" });
}

export function getQuestionsSummary(): Promise<QuestionSummaryOut> {
  return request<QuestionSummaryOut>("/api/questions/summary", { cache: "no-store" });
}

export function getConcepts(category?: string, phase?: string): Promise<ConceptOut[]> {
  const params = new URLSearchParams();
  if (category) params.set("category", category);
  if (phase) params.set("phase", phase);
  const qs = params.toString();
  return request<ConceptOut[]>(`/api/concepts${qs ? `?${qs}` : ""}`, { cache: "no-store" });
}

export function submitConceptAttempt(input: ConceptAttemptInput): Promise<AttemptResult> {
  return request<AttemptResult>("/api/concepts/attempts", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getGoals(statusFilter?: string): Promise<GoalOut[]> {
  const qs = statusFilter ? `?status_filter=${encodeURIComponent(statusFilter)}` : "";
  return request<GoalOut[]>(`/api/goals${qs}`, { cache: "no-store" });
}

export function createGoal(input: GoalCreateInput): Promise<GoalOut> {
  return request<GoalOut>("/api/goals", { method: "POST", body: JSON.stringify(input) });
}

export function updateGoal(goalId: number, input: GoalUpdateInput): Promise<GoalOut> {
  return request<GoalOut>(`/api/goals/${goalId}`, { method: "PATCH", body: JSON.stringify(input) });
}

export function getTimeBudgets(): Promise<TimeBudgetOut[]> {
  return request<TimeBudgetOut[]>("/api/time-budgets", { cache: "no-store" });
}

export function upsertTimeBudget(input: TimeBudgetUpsertInput): Promise<TimeBudgetOut> {
  return request<TimeBudgetOut>("/api/time-budgets", { method: "PUT", body: JSON.stringify(input) });
}

export function deleteTimeBudget(budgetId: number): Promise<void> {
  return request<void>(`/api/time-budgets/${budgetId}`, { method: "DELETE" });
}

export function getTodayReflection(): Promise<DailyReflectionOut | null> {
  return request<DailyReflectionOut | null>("/api/reflections/today", { cache: "no-store" });
}

export function upsertTodayReflection(input: DailyReflectionUpsertInput): Promise<DailyReflectionOut> {
  return request<DailyReflectionOut>("/api/reflections/today", {
    method: "PUT",
    body: JSON.stringify(input),
  });
}

export function getWeeklyReview(): Promise<WeeklyReviewOut> {
  return request<WeeklyReviewOut>("/api/weekly-review", { cache: "no-store" });
}

export function getAISettings(): Promise<AISettingsOut> {
  return request<AISettingsOut>("/api/settings/ai", { cache: "no-store" });
}

export function updateAISettings(input: AISettingsUpdateInput): Promise<AISettingsOut> {
  return request<AISettingsOut>("/api/settings/ai", { method: "PUT", body: JSON.stringify(input) });
}
