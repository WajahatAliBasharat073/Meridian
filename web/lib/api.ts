import type {
  FocusSessionOut,
  PunctualityOut,
  AISettingsOut,
  AISettingsUpdateInput,
  AttemptCreate,
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
  ProblemOut,
  ProfileOut,
  ProfileUpdate,
  DailyTheoryPickOut,
  TheoryPaceOut,
  InterviewModuleOut,
  QuestionOut,
  QuestionSummaryOut,
  RecommendationOut,
  ReviewDueOut,
  TimeBlockOut,
  TopicSectionOut,
  TopicGateOut,
  VerificationChecklistOut,
  LearningEntryOut,
  LearningEntryCreateInput,
  BuildSubmissionInput,
  BuildResultOut,
  DefendSubmissionInput,
  DefendResultOut,
  TimeBudgetOut,
  TimeBudgetUpsertInput,
  TodayOut,
  WeeklyReviewOut,
  ThesisLogOut,
  ThesisLogCreateInput,
  ReadingBookOut,
  ReadingBookCreateInput,
  ReadingBookUpdateInput,
  ReadingSessionOut,
  ReadingSessionCreateInput,
  VitalsOut,
  RecoveryUpdateInput,
  NutritionUpdateInput,
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
    // FastAPI's error body is `{"detail": "..."}` — surface that message
    // directly rather than the raw JSON when it parses, since callers
    // (e.g. the block-lock 423) show this string to the user as-is.
    let message = text || res.statusText;
    try {
      const parsed = JSON.parse(text) as { detail?: unknown };
      if (typeof parsed.detail === "string") message = parsed.detail;
    } catch {
      // Not JSON — keep the raw text.
    }
    throw new ApiError(res.status, message);
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

/** Kept as an alias so existing importers don't break. The full field set
 * (including solve_method and the two independence flags) lives in
 * lib/types.ts alongside the rest of the schema mirror. */
export type AttemptInput = AttemptCreate;

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

export function getProblemsByTopic(): Promise<TopicSectionOut[]> {
  return request<TopicSectionOut[]>("/api/problems/by-topic", { cache: "no-store" });
}

export function getTopicGates(): Promise<TopicGateOut[]> {
  return request<TopicGateOut[]>("/api/topics/gates", { cache: "no-store" });
}

export function getTopicChecklist(topic: string): Promise<VerificationChecklistOut> {
  return request<VerificationChecklistOut>(`/api/topics/${topic}/checklist`, { cache: "no-store" });
}

export function submitTopicBuild(
  topic: string,
  input: BuildSubmissionInput
): Promise<BuildResultOut> {
  return request<BuildResultOut>(`/api/topics/${topic}/verify/build`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function submitTopicDefend(
  topic: string,
  attemptId: number,
  input: DefendSubmissionInput
): Promise<DefendResultOut> {
  return request<DefendResultOut>(`/api/topics/${topic}/verify/${attemptId}/defend`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getTopicLearning(topic: string): Promise<LearningEntryOut[]> {
  return request<LearningEntryOut[]>(`/api/topics/${topic}/learning`, { cache: "no-store" });
}

export function addTopicLearning(
  topic: string,
  input: LearningEntryCreateInput
): Promise<LearningEntryOut> {
  return request<LearningEntryOut>(`/api/topics/${topic}/learning`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function deleteTopicLearning(topic: string, entryId: number): Promise<void> {
  const res = await fetch(`/api/topics/${topic}/learning/${entryId}`, { method: "DELETE" });
  if (!res.ok) throw new ApiError(res.status, "Couldn't delete that entry");
}

export function overrideTopicGate(topic: string, reason: string): Promise<TopicGateOut> {
  return request<TopicGateOut>(`/api/topics/${topic}/override`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
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

export function getQuestions(
  category?: string,
  module?: string,
  priority?: string,
  company?: string
): Promise<QuestionOut[]> {
  const params = new URLSearchParams();
  if (category) params.set("category", category);
  if (module) params.set("module", module);
  if (priority) params.set("priority", priority);
  if (company) params.set("company", company);
  const qs = params.toString();
  return request<QuestionOut[]>(`/api/questions${qs ? `?${qs}` : ""}`, { cache: "no-store" });
}

export function getInterviewModules(): Promise<InterviewModuleOut[]> {
  return request<InterviewModuleOut[]>("/api/questions/modules", { cache: "no-store" });
}

export function setQuestionMastery(
  questionId: number,
  mastery: number,
  notes?: string,
  minutes?: number
): Promise<{ mastery: number; label: string }> {
  return request<{ mastery: number; label: string }>(`/api/questions/${questionId}/mastery`, {
    method: "PUT",
    body: JSON.stringify({ mastery, notes, minutes }),
  });
}

export function getTheoryPace(): Promise<TheoryPaceOut> {
  return request<TheoryPaceOut>("/api/questions/pace", { cache: "no-store" });
}

export function getQuestionsSummary(): Promise<QuestionSummaryOut> {
  return request<QuestionSummaryOut>("/api/questions/summary", { cache: "no-store" });
}

export function getDailyTheoryQuestions(): Promise<DailyTheoryPickOut[]> {
  return request<DailyTheoryPickOut[]>("/api/questions/daily", { cache: "no-store" });
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

export function getThesisLogs(): Promise<ThesisLogOut[]> {
  return request<ThesisLogOut[]>("/api/thesis-log", { cache: "no-store" });
}

export function createThesisLog(input: ThesisLogCreateInput): Promise<ThesisLogOut> {
  return request<ThesisLogOut>("/api/thesis-log", { method: "POST", body: JSON.stringify(input) });
}

export function getReadingBooks(): Promise<ReadingBookOut[]> {
  return request<ReadingBookOut[]>("/api/reading/books", { cache: "no-store" });
}

export function createReadingBook(input: ReadingBookCreateInput): Promise<ReadingBookOut> {
  return request<ReadingBookOut>("/api/reading/books", { method: "POST", body: JSON.stringify(input) });
}

export function updateReadingBook(bookId: number, input: ReadingBookUpdateInput): Promise<ReadingBookOut> {
  return request<ReadingBookOut>(`/api/reading/books/${bookId}`, { method: "PATCH", body: JSON.stringify(input) });
}

export function getReadingSessions(bookId: number): Promise<ReadingSessionOut[]> {
  return request<ReadingSessionOut[]>(`/api/reading/books/${bookId}/sessions`, { cache: "no-store" });
}

export function logReadingSession(
  bookId: number,
  input: ReadingSessionCreateInput
): Promise<ReadingBookOut> {
  return request<ReadingBookOut>(`/api/reading/books/${bookId}/sessions`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export interface CoachChatRequest {
  message: string;
  history?: Array<{ role: string; content: string }>;
  model?: string;
}

export interface CoachChatResponse {
  reply: string;
  suggestions: string[];
  model_used: string;
}

export function sendCoachChat(input: CoachChatRequest): Promise<CoachChatResponse> {
  return request<CoachChatResponse>("/api/coach/chat", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function startFocusSession(blockId: number): Promise<FocusSessionOut> {
  return request<FocusSessionOut>("/api/focus-sessions", {
    method: "POST",
    body: JSON.stringify({ block_id: blockId }),
  });
}

export function updateFocusSession(
  sessionId: number,
  input: {
    state?: "in_progress" | "paused" | "completed" | "abandoned";
    elapsed_seconds?: number;
    focus_rating?: number;
    notes?: string;
  }
): Promise<FocusSessionOut> {
  return request<FocusSessionOut>(`/api/focus-sessions/${sessionId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function getPunctuality(days = 30): Promise<PunctualityOut> {
  return request<PunctualityOut>(`/api/focus-sessions/punctuality?days=${days}`, {
    cache: "no-store",
  });
}

export function getTodayVitals(): Promise<VitalsOut> {
  return request<VitalsOut>("/api/vitals/today", { cache: "no-store" });
}

export function updateRecovery(input: RecoveryUpdateInput): Promise<VitalsOut> {
  return request<VitalsOut>("/api/vitals/recovery", {
    method: "PUT",
    body: JSON.stringify(input),
  });
}

export function updateNutrition(input: NutritionUpdateInput): Promise<VitalsOut> {
  return request<VitalsOut>("/api/vitals/nutrition", {
    method: "PUT",
    body: JSON.stringify(input),
  });
}

/** Adds a glass. Additive server-side — each call is another glass, not a
 * new total. */
export function addWater(ml = 250): Promise<VitalsOut> {
  return request<VitalsOut>("/api/vitals/water", {
    method: "POST",
    body: JSON.stringify({ ml }),
  });
}
