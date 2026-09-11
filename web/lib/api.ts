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
  LearningStatus,
  QuestionStatusInput,
  QuestionStatusOut,
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
  ReadingBookFilters,
  ReadingStatsOut,
  ReadingQuoteCreateInput,
  ReadingSessionOut,
  ReadingSessionCreateInput,
  VitalsOut,
  RecoveryUpdateInput,
  NutritionUpdateInput,
  FinanceAccountOut,
  FinanceAccountCreateInput,
  FinanceAccountUpdateInput,
  FinanceCategoryOut,
  FinanceCategoryCreateInput,
  FinanceTransactionOut,
  FinanceTransactionCreateInput,
  FinanceRecurringOut,
  FinanceRecurringCreateInput,
  FinanceBudgetOut,
  FinanceBudgetUpsertInput,
  FinanceGoalOut,
  FinanceGoalCreateInput,
  FinanceGoalUpdateInput,
  FinanceNetWorthPointOut,
  FinanceDashboardOut,
  TransactionType,
  TransactionStatus,
  VocabWordOut,
  VocabWordCreateInput,
  VocabWordUpdateInput,
  VocabStatusUpdateInput,
  VocabSummaryOut,
  OverviewOut,
  ResearchAtAGlanceOut,
  ResearchTopicOut,
  ResearchTopicCreateInput,
  ResearchTopicUpdateInput,
  ResearchPaperOut,
  ResearchPaperCreateInput,
  ResearchPaperUpdateInput,
  ResearchNoteOut,
  ResearchNoteCreateInput,
  ResearchExperimentOut,
  ResearchExperimentCreateInput,
  ResearchExperimentUpdateInput,
  ResearchMilestoneOut,
  ResearchMilestoneCreateInput,
  ResearchMilestoneUpdateInput,
  ResearchOpportunityOut,
  ResearchOpportunityCreateInput,
  ResearchOpportunityUpdateInput,
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

export interface QuestionFilters {
  category?: string;
  module?: string;
  priority?: string;
  company?: string;
  /** Curriculum position filters (migration 0019/0020). */
  topic?: string;
  phase?: number;
  difficulty?: string;
  /** This user's self-tag / revisit flag / attempted state. Combine
   * freely with the curriculum filters above — e.g. topic + phase +
   * learningStatus together returns only questions matching all three. */
  learningStatus?: LearningStatus;
  needsReview?: boolean;
  attempted?: boolean;
}

export function getQuestions(filters: QuestionFilters = {}): Promise<QuestionOut[]> {
  const params = new URLSearchParams();
  if (filters.category) params.set("category", filters.category);
  if (filters.module) params.set("module", filters.module);
  if (filters.priority) params.set("priority", filters.priority);
  if (filters.company) params.set("company", filters.company);
  if (filters.topic) params.set("topic", filters.topic);
  if (filters.phase != null) params.set("phase", String(filters.phase));
  if (filters.difficulty) params.set("difficulty", filters.difficulty);
  if (filters.learningStatus) params.set("learning_status", filters.learningStatus);
  if (filters.needsReview != null) params.set("needs_review", String(filters.needsReview));
  if (filters.attempted != null) params.set("attempted", String(filters.attempted));
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

/** Sets the self-tag and/or revisit flag. Independent of mastery — never
 * touches the 0-7 ladder. Pass `needsReview` to override the auto-derived
 * flag (e.g. "solved with help" but you don't actually need to revisit
 * this one); omit it to let the server derive it from the status. */
export function setQuestionStatus(
  questionId: number,
  input: QuestionStatusInput
): Promise<QuestionStatusOut> {
  return request<QuestionStatusOut>(`/api/questions/${questionId}/status`, {
    method: "PUT",
    body: JSON.stringify({
      learning_status: input.learning_status ?? null,
      needs_review: input.needs_review ?? null,
    }),
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

export function getReadingBooks(filters: ReadingBookFilters = {}): Promise<ReadingBookOut[]> {
  const params = new URLSearchParams();
  if (filters.statusFilter) params.set("status_filter", filters.statusFilter);
  if (filters.category) params.set("category", filters.category);
  if (filters.tag) params.set("tag", filters.tag);
  if (filters.search) params.set("search", filters.search);
  if (filters.needsRevisit) params.set("needs_revisit", "true");
  const qs = params.toString();
  return request<ReadingBookOut[]>(`/api/reading/books${qs ? `?${qs}` : ""}`, { cache: "no-store" });
}

export function getReadingStats(): Promise<ReadingStatsOut> {
  return request<ReadingStatsOut>("/api/reading/stats", { cache: "no-store" });
}

export function createReadingBook(input: ReadingBookCreateInput): Promise<ReadingBookOut> {
  return request<ReadingBookOut>("/api/reading/books", { method: "POST", body: JSON.stringify(input) });
}

export function updateReadingBook(bookId: number, input: ReadingBookUpdateInput): Promise<ReadingBookOut> {
  return request<ReadingBookOut>(`/api/reading/books/${bookId}`, { method: "PATCH", body: JSON.stringify(input) });
}

export function deleteReadingBook(bookId: number): Promise<void> {
  return request<void>(`/api/reading/books/${bookId}`, { method: "DELETE" });
}

export function addReadingQuote(bookId: number, input: ReadingQuoteCreateInput): Promise<ReadingBookOut> {
  return request<ReadingBookOut>(`/api/reading/books/${bookId}/quotes`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function deleteReadingQuote(bookId: number, quoteIndex: number): Promise<ReadingBookOut> {
  return request<ReadingBookOut>(`/api/reading/books/${bookId}/quotes/${quoteIndex}`, {
    method: "DELETE",
  });
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

// ------------------------------------------------------------- Finance

export function getFinanceAccounts(): Promise<FinanceAccountOut[]> {
  return request<FinanceAccountOut[]>("/api/finance/accounts", { cache: "no-store" });
}

export function createFinanceAccount(input: FinanceAccountCreateInput): Promise<FinanceAccountOut> {
  return request<FinanceAccountOut>("/api/finance/accounts", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateFinanceAccount(
  accountId: number,
  input: FinanceAccountUpdateInput
): Promise<FinanceAccountOut> {
  return request<FinanceAccountOut>(`/api/finance/accounts/${accountId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteFinanceAccount(accountId: number): Promise<void> {
  return request<void>(`/api/finance/accounts/${accountId}`, { method: "DELETE" });
}

export function getFinanceCategories(): Promise<FinanceCategoryOut[]> {
  return request<FinanceCategoryOut[]>("/api/finance/categories", { cache: "no-store" });
}

export function createFinanceCategory(input: FinanceCategoryCreateInput): Promise<FinanceCategoryOut> {
  return request<FinanceCategoryOut>("/api/finance/categories", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export interface FinanceTransactionFilters {
  accountId?: number;
  categoryId?: number;
  type?: TransactionType;
  status?: TransactionStatus;
  dateFrom?: string;
  dateTo?: string;
}

export function getFinanceTransactions(
  filters: FinanceTransactionFilters = {}
): Promise<FinanceTransactionOut[]> {
  const params = new URLSearchParams();
  if (filters.accountId != null) params.set("account_id", String(filters.accountId));
  if (filters.categoryId != null) params.set("category_id", String(filters.categoryId));
  if (filters.type) params.set("type", filters.type);
  if (filters.status) params.set("status_", filters.status);
  if (filters.dateFrom) params.set("date_from", filters.dateFrom);
  if (filters.dateTo) params.set("date_to", filters.dateTo);
  const qs = params.toString();
  return request<FinanceTransactionOut[]>(`/api/finance/transactions${qs ? `?${qs}` : ""}`, {
    cache: "no-store",
  });
}

export function createFinanceTransaction(
  input: FinanceTransactionCreateInput
): Promise<FinanceTransactionOut> {
  return request<FinanceTransactionOut>("/api/finance/transactions", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function deleteFinanceTransaction(transactionId: number): Promise<void> {
  return request<void>(`/api/finance/transactions/${transactionId}`, { method: "DELETE" });
}

export function getFinanceRecurring(): Promise<FinanceRecurringOut[]> {
  return request<FinanceRecurringOut[]>("/api/finance/recurring", { cache: "no-store" });
}

export function createFinanceRecurring(input: FinanceRecurringCreateInput): Promise<FinanceRecurringOut> {
  return request<FinanceRecurringOut>("/api/finance/recurring", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function deleteFinanceRecurring(recurringId: number): Promise<void> {
  return request<void>(`/api/finance/recurring/${recurringId}`, { method: "DELETE" });
}

export function getFinanceBudgets(): Promise<FinanceBudgetOut[]> {
  return request<FinanceBudgetOut[]>("/api/finance/budgets", { cache: "no-store" });
}

export function upsertFinanceBudget(input: FinanceBudgetUpsertInput): Promise<FinanceBudgetOut> {
  return request<FinanceBudgetOut>("/api/finance/budgets", { method: "PUT", body: JSON.stringify(input) });
}

export function deleteFinanceBudget(budgetId: number): Promise<void> {
  return request<void>(`/api/finance/budgets/${budgetId}`, { method: "DELETE" });
}

export function getFinanceGoals(): Promise<FinanceGoalOut[]> {
  return request<FinanceGoalOut[]>("/api/finance/goals", { cache: "no-store" });
}

export function createFinanceGoal(input: FinanceGoalCreateInput): Promise<FinanceGoalOut> {
  return request<FinanceGoalOut>("/api/finance/goals", { method: "POST", body: JSON.stringify(input) });
}

export function updateFinanceGoal(goalId: number, input: FinanceGoalUpdateInput): Promise<FinanceGoalOut> {
  return request<FinanceGoalOut>(`/api/finance/goals/${goalId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteFinanceGoal(goalId: number): Promise<void> {
  return request<void>(`/api/finance/goals/${goalId}`, { method: "DELETE" });
}

export function getFinanceDashboard(): Promise<FinanceDashboardOut> {
  return request<FinanceDashboardOut>("/api/finance/dashboard", { cache: "no-store" });
}

export function takeFinanceNetWorthSnapshot(): Promise<FinanceNetWorthPointOut> {
  return request<FinanceNetWorthPointOut>("/api/finance/dashboard/snapshot", { method: "POST" });
}

// ------------------------------------------------------------- Vocabulary

export function getVocabWords(learningStatus?: string): Promise<VocabWordOut[]> {
  const qs = learningStatus ? `?learning_status=${encodeURIComponent(learningStatus)}` : "";
  return request<VocabWordOut[]>(`/api/vocab${qs}`, { cache: "no-store" });
}

export function getDailyVocabReview(count = 10): Promise<VocabWordOut[]> {
  return request<VocabWordOut[]>(`/api/vocab/daily?count=${count}`, { cache: "no-store" });
}

export function createVocabWord(input: VocabWordCreateInput): Promise<VocabWordOut> {
  return request<VocabWordOut>("/api/vocab", { method: "POST", body: JSON.stringify(input) });
}

export function setVocabWordStatus(
  wordId: number,
  input: VocabStatusUpdateInput
): Promise<VocabWordOut> {
  return request<VocabWordOut>(`/api/vocab/${wordId}/status`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteVocabWord(wordId: number): Promise<void> {
  return request<void>(`/api/vocab/${wordId}`, { method: "DELETE" });
}

export function updateVocabWord(wordId: number, input: VocabWordUpdateInput): Promise<VocabWordOut> {
  return request<VocabWordOut>(`/api/vocab/${wordId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function getVocabSummary(): Promise<VocabSummaryOut> {
  return request<VocabSummaryOut>("/api/vocab/summary", { cache: "no-store" });
}

// --------------------------------------------------- Personal OS overview

export function getOverview(): Promise<OverviewOut> {
  return request<OverviewOut>("/api/overview", { cache: "no-store" });
}

// --------------------------------------------- Research command center

export function getResearchAtAGlance(): Promise<ResearchAtAGlanceOut> {
  return request<ResearchAtAGlanceOut>("/api/research/at-a-glance", { cache: "no-store" });
}

export function getResearchTopics(): Promise<ResearchTopicOut[]> {
  return request<ResearchTopicOut[]>("/api/research/topics", { cache: "no-store" });
}

export function createResearchTopic(input: ResearchTopicCreateInput): Promise<ResearchTopicOut> {
  return request<ResearchTopicOut>("/api/research/topics", { method: "POST", body: JSON.stringify(input) });
}

export function updateResearchTopic(
  topicId: number,
  input: ResearchTopicUpdateInput
): Promise<ResearchTopicOut> {
  return request<ResearchTopicOut>(`/api/research/topics/${topicId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteResearchTopic(topicId: number): Promise<void> {
  return request<void>(`/api/research/topics/${topicId}`, { method: "DELETE" });
}

export function getResearchPapers(topicId?: number): Promise<ResearchPaperOut[]> {
  const qs = topicId != null ? `?topic_id=${topicId}` : "";
  return request<ResearchPaperOut[]>(`/api/research/papers${qs}`, { cache: "no-store" });
}

export function createResearchPaper(input: ResearchPaperCreateInput): Promise<ResearchPaperOut> {
  return request<ResearchPaperOut>("/api/research/papers", { method: "POST", body: JSON.stringify(input) });
}

export function updateResearchPaper(
  paperId: number,
  input: ResearchPaperUpdateInput
): Promise<ResearchPaperOut> {
  return request<ResearchPaperOut>(`/api/research/papers/${paperId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteResearchPaper(paperId: number): Promise<void> {
  return request<void>(`/api/research/papers/${paperId}`, { method: "DELETE" });
}

export function getResearchNotes(topicId?: number): Promise<ResearchNoteOut[]> {
  const qs = topicId != null ? `?topic_id=${topicId}` : "";
  return request<ResearchNoteOut[]>(`/api/research/notes${qs}`, { cache: "no-store" });
}

export function createResearchNote(input: ResearchNoteCreateInput): Promise<ResearchNoteOut> {
  return request<ResearchNoteOut>("/api/research/notes", { method: "POST", body: JSON.stringify(input) });
}

export function deleteResearchNote(noteId: number): Promise<void> {
  return request<void>(`/api/research/notes/${noteId}`, { method: "DELETE" });
}

export function getResearchExperiments(topicId?: number): Promise<ResearchExperimentOut[]> {
  const qs = topicId != null ? `?topic_id=${topicId}` : "";
  return request<ResearchExperimentOut[]>(`/api/research/experiments${qs}`, { cache: "no-store" });
}

export function createResearchExperiment(
  input: ResearchExperimentCreateInput
): Promise<ResearchExperimentOut> {
  return request<ResearchExperimentOut>("/api/research/experiments", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateResearchExperiment(
  experimentId: number,
  input: ResearchExperimentUpdateInput
): Promise<ResearchExperimentOut> {
  return request<ResearchExperimentOut>(`/api/research/experiments/${experimentId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteResearchExperiment(experimentId: number): Promise<void> {
  return request<void>(`/api/research/experiments/${experimentId}`, { method: "DELETE" });
}

export function getResearchMilestones(topicId?: number): Promise<ResearchMilestoneOut[]> {
  const qs = topicId != null ? `?topic_id=${topicId}` : "";
  return request<ResearchMilestoneOut[]>(`/api/research/milestones${qs}`, { cache: "no-store" });
}

export function createResearchMilestone(
  input: ResearchMilestoneCreateInput
): Promise<ResearchMilestoneOut> {
  return request<ResearchMilestoneOut>("/api/research/milestones", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateResearchMilestone(
  milestoneId: number,
  input: ResearchMilestoneUpdateInput
): Promise<ResearchMilestoneOut> {
  return request<ResearchMilestoneOut>(`/api/research/milestones/${milestoneId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteResearchMilestone(milestoneId: number): Promise<void> {
  return request<void>(`/api/research/milestones/${milestoneId}`, { method: "DELETE" });
}

export function getResearchOpportunities(statusFilter?: string): Promise<ResearchOpportunityOut[]> {
  const qs = statusFilter ? `?status_filter=${encodeURIComponent(statusFilter)}` : "";
  return request<ResearchOpportunityOut[]>(`/api/research/opportunities${qs}`, { cache: "no-store" });
}

export function createResearchOpportunity(
  input: ResearchOpportunityCreateInput
): Promise<ResearchOpportunityOut> {
  return request<ResearchOpportunityOut>("/api/research/opportunities", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateResearchOpportunity(
  opportunityId: number,
  input: ResearchOpportunityUpdateInput
): Promise<ResearchOpportunityOut> {
  return request<ResearchOpportunityOut>(`/api/research/opportunities/${opportunityId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteResearchOpportunity(opportunityId: number): Promise<void> {
  return request<void>(`/api/research/opportunities/${opportunityId}`, { method: "DELETE" });
}

export function addResearchOpportunityToGoals(opportunityId: number): Promise<GoalOut> {
  return request<GoalOut>(`/api/research/opportunities/${opportunityId}/add-to-goals`, { method: "POST" });
}
