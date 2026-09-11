/** Mirrors api/app/schemas.py — keep in sync by hand until an OpenAPI
 * codegen step exists (out of scope for this phase). */

export type MasteryLevel = "L0" | "L1" | "L2" | "L3" | "L4" | "L5" | "L6";

export type BlockStatus = "DONE" | "NOT DONE" | "PARTIAL" | "RESCHEDULED";

export type RecommendQueue =
  | "FAILED_REVIEW"
  | "OVERDUE_REVIEW"
  | "DUE_REVIEW"
  | "SCHEDULED"
  | "PATTERN_GAP"
  | "INTERLEAVE";

export type BandwidthBand = "HIGH" | "MEDIUM" | "LOW" | "MINIMUM_VIABLE_DAY";

export interface TimeBlockOut {
  id: number;
  seq: number;
  start: string; // "HH:MM:SS"
  end: string;
  activity: string;
  tier: "T1" | "T2" | "T3" | "T4";
  category: string;
  planned_minutes: number;
  status: BlockStatus;
  actual_minutes: number | null;
  what_to_do: string | null;
  notes: string | null;
  is_current: boolean;
  /** Whether a focus session has ever been started on this block, in any
   * state — the signal the 70%-elapsed block-lock rule needs. Not
   * derivable from `status`: a block can be NOT DONE with an abandoned
   * session already on it. */
  has_focus_session: boolean;
}

export interface ProblemOut {
  problem_id: number;
  /** null for a classic algorithm with no LeetCode entry (Dijkstra, KMP). */
  lc_number: number | null;
  title: string;
  slug: string;
  url: string | null;
  pattern: string;
  topic: string | null;
  difficulty: string;
  source: string;
  /** Companies named by the source sheet, plus its own "+N" truncation as a
   * count — the unnamed ones are a number, not invented names. */
  companies: string[];
  company_extra_count: number;
  current_mastery: MasteryLevel | null;
  is_scheduled_today: boolean;
  last_solve_method: SolveMethod | null;
  attempt_count: number;
  last_attempted_at: string | null;
  last_minutes: number | null;
  last_key_insight: string | null;
  last_notes: string | null;
}

export interface TopicGuideTypeOut {
  name: string;
  note: string;
}

export interface TopicGuideOperationOut {
  op: string;
  complexity: string;
  note: string;
}

export interface TopicGuideOut {
  topic: string;
  display_name: string;
  seq: number;
  one_liner: string;
  learn_first: string;
  types: TopicGuideTypeOut[];
  operations: TopicGuideOperationOut[];
  must_know: string[];
  pitfalls: string[];
  needs_revision: boolean;
}

export interface TopicSectionOut {
  topic: string;
  display_name: string;
  seq: number;
  guide: TopicGuideOut | null;
  problems: ProblemOut[];
  total: number;
  solved: number;
  unaided: number;
  remaining: number;
  by_difficulty: Record<string, number>;
  companies: string[];
  /** Whether the structure has been demonstrated. `problems` comes back
   * empty while this is locked or expired — the server withholds it. */
  gate: TopicGateOut | null;
}

export type GateStateValue = "locked" | "unlocked" | "expired" | "unverified_override";

export interface TopicGateOut {
  topic: string;
  state: GateStateValue;
  problems_visible: boolean;
  passed_at: string | null;
  expires_at: string | null;
  days_until_expiry: number | null;
  attempt_count: number;
  overridden: boolean;
}

export type LearningEntryKind = "source" | "note" | "snippet" | "requirement";

export interface LearningEntryOut {
  id: number;
  topic: string;
  kind: LearningEntryKind;
  title: string;
  /** A bookmark only — nothing fetches it. `body` is the content that
   * actually reaches the question generator. */
  url: string | null;
  body: string | null;
  created_at: string;
}

export interface LearningEntryCreateInput {
  kind: LearningEntryKind;
  title: string;
  url?: string;
  body?: string;
}

export interface VerificationChecklistItemOut {
  text: string;
  self_added: boolean;
  entry_id: number | null;
}

export interface VerificationChecklistOut {
  topic: string;
  display_name: string;
  required: string[];
  items: VerificationChecklistItemOut[];
}

export interface BuildSubmissionInput {
  code: string;
  notes?: string;
}

export interface BuildResultOut {
  attempt_id: number;
  covered: string[];
  missing: string[];
  concerns: string[];
  notes: string;
  build_score: number;
  build_passed: boolean;
  questions: string[];
}

export interface DefendSubmissionInput {
  answers: string[];
  focus_losses: number;
  focus_lost_seconds: number;
  duration_seconds?: number;
}

export interface DefendGradeOut {
  question: string;
  answer: string;
  verdict: "correct" | "partial" | "wrong";
  feedback: string;
}

export interface DefendResultOut {
  attempt_id: number;
  grades: DefendGradeOut[];
  defend_score: number;
  passed: boolean;
  gate: TopicGateOut;
  focus_losses: number;
  focus_lost_seconds: number;
}


export interface RecommendationOut {
  problem_id: number;
  title: string;
  pattern: string;
  difficulty: string;
  reason: string;
  queue: RecommendQueue;
  is_review: boolean;
  prior_key_insight: string | null;
}

/** Mirrors `SolveMethod` in api/app/schemas.py. Deliberately separate from
 * MasteryLevel: mastery is "how well do I know this now", solve_method is
 * "how much help did this attempt take" — collapsing them makes "solved it,
 * but only after the video" invisible in the history. */
export type SolveMethod =
  | "independent"
  | "recalled_pattern"
  | "after_hint"
  | "after_editorial"
  | "after_video"
  | "brute_force_only"
  | "not_solved";

export interface AttemptCreate {
  problem_id: number;
  mastery_level: MasteryLevel;
  minutes?: number;
  hint_used?: boolean;
  key_insight?: string;
  solve_method?: SolveMethod;
  understood_approach_independently?: boolean;
  reached_optimal?: boolean;
  notes?: string;
}

export interface AttemptResult {
  next_review_due: string;
  interval_days: number;
  message: string;
}

export interface ReviewDueOut {
  subject_type: string;
  subject_id: number;
  due_date: string;
  overdue_days: number;
  interval_days: number;
  last_result: string | null;
}

export interface BandwidthOut {
  band: BandwidthBand;
  allow_new_hard: boolean;
  allow_new_medium: boolean;
  max_new_problems: number;
  include_reviews: boolean;
  include_mock: boolean;
  headline: string;
  spare_minutes_suggestion: string | null;
}

export interface TodayCounters {
  overdue_reviews: number;
  blocks_remaining: number;
  readiness_pct: number | null;
}

export interface TodayOut {
  date: string;
  blocks: TimeBlockOut[];
  current_block: TimeBlockOut | null;
  next_action: RecommendationOut | null;
  bandwidth: BandwidthOut | null;
  counters: TodayCounters;
  prayer_accuracy_minutes: [number, number];
}

export interface MasteryCountOut {
  level: MasteryLevel;
  count: number;
}

export interface PatternCoverageOut {
  pattern: string;
  scheduled_count: number;
  l5_plus_count: number;
  ratio: number;
}

export interface AttemptsByDayOut {
  day: string;
  count: number;
}

export interface DashboardSummaryOut {
  total_problems: number;
  attempted_count: number;
  mastery_distribution: MasteryCountOut[];
  pattern_coverage: PatternCoverageOut[];
  attempts_by_day: AttemptsByDayOut[];
  reviews_due_count: number;
  reviews_overdue_count: number;
  readiness_pct: number | null;
}

export interface ProfileOut {
  birth_date: string | null; // "YYYY-MM-DD"
  life_expectancy_years: number | null;
}

export interface ProfileUpdate {
  birth_date: string;
  life_expectancy_years: number;
}

export interface CategoryBreakdownOut {
  category: string;
  done: number;
  total: number;
}

export interface ConceptResourceOut {
  label: string;
  url: string | null;
}

export interface ConceptOut {
  concept_id: number;
  category: string;
  title: string;
  summary: string;
  resources: ConceptResourceOut[];
  phase: string;
  current_mastery: MasteryLevel | null;
}

export interface ConceptAttemptInput {
  concept_id: number;
  mastery_level: MasteryLevel;
  notes?: string;
}

/** The 0-7 interview mastery ladder (mirrors MASTERY_LADDER in
 * api/app/schemas.py). Seeing a question is not knowing it, which is why
 * this replaced a `covered` boolean. */
export const QUESTION_MASTERY: { level: number; label: string; short: string }[] = [
  { level: 0, label: "Never seen", short: "—" },
  { level: 1, label: "Recognize", short: "Recognize" },
  { level: 2, label: "Can explain", short: "Explain" },
  { level: 3, label: "Can solve", short: "Solve" },
  { level: 4, label: "Can reason about trade-offs", short: "Trade-offs" },
  { level: 5, label: "Can answer follow-ups", short: "Follow-ups" },
  { level: 6, label: "Can design a production system", short: "Production" },
  { level: 7, label: "Can teach it", short: "Teach" },
];

/** The bar at which a question counts toward readiness — matches
 * READY_MASTERY in api/app/repositories/questions.py. */
export const READY_MASTERY = 4;

export type QuestionEvidence = "reported" | "common" | "fundamental" | "derived";

export interface InterviewModuleOut {
  code: string;
  title: string;
  summary: string | null;
  priority: string;
  submodules: string[];
  target_seniority: string[];
  question_count: number;
  ready_count: number;
  pct: number;
}

export interface QuestionOut {
  question_id: number;
  category: string;
  title: string;
  source: string;
  mastery: number;

  module_code: string | null;
  submodule: string | null;
  question_type: string | null;
  difficulty: string | null;
  seniority: string | null;
  priority: string | null;
  frequency: string | null;
  /** A non-empty `companies` list is only ever present with
   * evidence === "reported" and a source_url — the API enforces it. */
  evidence: QuestionEvidence | null;
  source_url: string | null;
  tests_for: string | null;
  strong_signal: string | null;
  weak_signal: string | null;
  companies: string[];
  answer_dimensions: string[];
  follow_ups: string[];
  common_mistakes: string[];
  /** A real reference implementation, for coding questions backed by an
   * actual source file (Module B). Null for every other question type. */
  reference_solution: string | null;

  /** Curriculum position (migration 0019/0020) — null until classified. */
  topic: string | null;
  phase: number | null;
  cognitive_level: number | null;

  /** This user's self-tag and revisit flag (migration 0021). Independent
   * of `mastery` — never fed into curriculum mastery, purely a personal
   * filtering aid. */
  learning_status: LearningStatus | null;
  needs_review: boolean;
}

/** Mirrors api/app/schemas.py — "not_attempted" is deliberately not a
 * member: it is `learning_status === null`, not a stored value. */
export type LearningStatus =
  | "already_know"
  | "easy"
  | "understood"
  | "solved_with_help"
  | "struggled"
  | "no_idea";

export const LEARNING_STATUS_LABELS: Record<LearningStatus, string> = {
  already_know: "Already know",
  easy: "Easy",
  understood: "Understood",
  solved_with_help: "Solved with help",
  struggled: "Struggled",
  no_idea: "No idea",
};

export interface QuestionStatusInput {
  learning_status?: LearningStatus | null;
  needs_review?: boolean | null;
}

export interface QuestionStatusOut {
  learning_status: LearningStatus | null;
  needs_review: boolean;
}

/** One of today's recommended theory questions — the full QuestionOut
 * record plus why it was picked today. */
export interface DailyTheoryPickOut extends QuestionOut {
  is_case_study: boolean;
  pick_reason: string;
}

export interface TheoryPaceProjectionOut {
  daily_count: number;
  daily_minutes: number;
  days_to_clear_backlog: number | null;
  minutes_delta_vs_baseline: number;
  days_saved_vs_baseline: number | null;
}

/** How long clearing the theory backlog takes at your actual recorded
 * pace, and what changing the daily count buys — mirrors TheoryPaceOut in
 * api/app/schemas.py. `enough_data` gates everything else: below
 * min_questions_needed distinct rated-with-time questions, this refuses
 * to project rather than guess from too little signal. */
export interface TheoryPaceOut {
  enough_data: boolean;
  questions_with_data: number;
  min_questions_needed: number;
  avg_minutes_per_question: number | null;
  backlog_count: number;
  baseline_daily_count: number;
  projections: TheoryPaceProjectionOut[];
}

export interface CategoryCoverageOut {
  category: string;
  /** Ready: mastery >= READY_MASTERY. Field name kept for compatibility. */
  covered_count: number;
  /** Attempted: rated at all (mastery >= 1). */
  started_count: number;
  total_count: number;
  pct: number;
}

export interface QuestionSummaryOut {
  by_category: CategoryCoverageOut[];
  covered_count: number;
  started_count: number;
  total_count: number;
  pct: number | null;
}

export interface DailyRecapOut {
  recap_date: string;
  total_blocks: number;
  done_count: number;
  partial_count: number;
  not_done_count: number;
  rescheduled_count: number;
  completion_pct: number | null;
  category_breakdown: CategoryBreakdownOut[];
  problems_attempted: number;
  deep_work_planned_minutes: number;
  deep_work_actual_minutes: number;
  headline: string;
  suggestions: string[];
}

export type GoalStatus = "active" | "completed" | "abandoned";

export interface GoalOut {
  id: number;
  title: string;
  description: string | null;
  category: string | null;
  target_date: string | null;
  progress_pct: number;
  status: GoalStatus;
  minutes_logged: number | null;
  //: Set only when linked to a money goal -- its progress is always
  //: computed from real transactions, never the manual slider above.
  finance_goal_id: number | null;
  linked_finance_goal: FinanceGoalOut | null;
}

export interface GoalCreateInput {
  title: string;
  description?: string;
  category?: string;
  target_date?: string;
  finance_goal_id?: number;
}

export interface GoalUpdateInput {
  progress_pct?: number;
  status?: GoalStatus;
  //: 0 clears an existing link; omit for "no change"; any other id links it.
  finance_goal_id?: number;
}

export interface TimeBudgetOut {
  id: number;
  category: string;
  minutes_per_week: number;
  actual_minutes_this_week: number;
}

export interface TimeBudgetUpsertInput {
  category: string;
  minutes_per_week: number;
}

export type Mood = "difficult" | "normal" | "good" | "excellent";

export interface DailyReflectionOut {
  date: string;
  mood: Mood;
  what_got_in_the_way: string | null;
  what_went_well: string | null;
}

export interface DailyReflectionUpsertInput {
  mood: Mood;
  what_got_in_the_way?: string;
  what_went_well?: string;
}

export interface WeeklyCategoryMinutesOut {
  category: string;
  minutes: number;
}

export interface MoodCountOut {
  mood: string;
  count: number;
}

export interface WeeklyReviewOut {
  window_start: string;
  window_end: string;
  total_minutes_logged: number;
  days_active: number;
  days_in_window: number;
  completion_pct: number | null;
  category_minutes: WeeklyCategoryMinutesOut[];
  avg_focus_session_minutes: number | null;
  rescheduled_count: number;
  mood_distribution: MoodCountOut[];
  what_went_well: string[];
  what_to_improve: string[];
}

export interface ThesisLogOut {
  id: number;
  milestone: string | null;
  work_summary: string;
  minutes: number | null;
  output_type: string | null;
  deadline: string | null;
  status: string | null;
  date: string;
}

export interface ThesisLogCreateInput {
  date: string;
  work_summary: string;
  milestone?: string;
  minutes?: number;
  output_type?: string;
  deadline?: string;
  status?: string;
}

export type ReadingFormat = "book" | "paper" | "article" | "docs";
export type ReadingStatus = "to_read" | "reading" | "completed" | "paused" | "dropped";
export type ReadingCategory =
  | "fiction"
  | "non_fiction"
  | "self_help"
  | "business"
  | "technical"
  | "biography_memoir"
  | "philosophy"
  | "science"
  | "history"
  | "other";

export const READING_CATEGORY_LABELS: Record<ReadingCategory, string> = {
  fiction: "Fiction",
  non_fiction: "Non-Fiction",
  self_help: "Self-Help / Personal Development",
  business: "Business & Career",
  technical: "Technical",
  biography_memoir: "Biography & Memoir",
  philosophy: "Philosophy",
  science: "Science",
  history: "History",
  other: "Other",
};

export const READING_FORMAT_LABELS: Record<ReadingFormat, string> = {
  book: "Book",
  paper: "Paper",
  article: "Article",
  docs: "Docs",
};

export const READING_STATUS_LABELS: Record<ReadingStatus, string> = {
  to_read: "To Read",
  reading: "Reading",
  completed: "Completed",
  paused: "Paused",
  dropped: "Dropped",
};

export interface ReadingSessionOut {
  id: number;
  book_id: number;
  date: string;
  page_reached: number | null;
  minutes: number | null;
  note: string | null;
}

export interface ReadingSessionCreateInput {
  date: string;
  page_reached?: number;
  minutes?: number;
  note?: string;
}

export type ReadingPriority = "high" | "medium" | "low";

export const READING_PRIORITY_LABELS: Record<ReadingPriority, string> = {
  high: "High priority",
  medium: "Medium priority",
  low: "Low priority",
};

export interface ReadingQuoteOut {
  text: string;
  page: number | null;
}

export interface ReadingQuoteCreateInput {
  text: string;
  page?: number;
}

export interface ReadingBookOut {
  id: number;
  title: string;
  author: string | null;
  cover_url: string | null;
  total_pages: number | null;
  format: ReadingFormat;
  category: ReadingCategory | null;
  status: ReadingStatus;
  rating: number | null;
  started_date: string | null;
  finished_date: string | null;
  notes: string | null;
  priority: ReadingPriority | null;
  tags: string[];
  quotes: ReadingQuoteOut[];
  why_reading: string | null;
  revisit_date: string | null;
  current_page: number | null;
  progress_pct: number | null;
  session_count: number;
  total_minutes_logged: number;
  last_session_date: string | null;
  last_session_note: string | null;
}

export interface ReadingBookCreateInput {
  title: string;
  author?: string;
  cover_url?: string;
  total_pages?: number;
  format?: ReadingFormat;
  category?: ReadingCategory;
  status?: ReadingStatus;
  started_date?: string;
  priority?: ReadingPriority;
  tags?: string[];
  why_reading?: string;
}

export interface ReadingBookUpdateInput {
  title?: string;
  author?: string;
  cover_url?: string;
  total_pages?: number;
  format?: ReadingFormat;
  category?: ReadingCategory;
  status?: ReadingStatus;
  rating?: number;
  started_date?: string;
  finished_date?: string;
  //: null explicitly clears priority/revisit_date; omit either for "no change".
  priority?: ReadingPriority | null;
  tags?: string[];
  why_reading?: string;
  revisit_date?: string | null;
}

export interface ReadingBookFilters {
  statusFilter?: ReadingStatus;
  category?: ReadingCategory;
  tag?: string;
  search?: string;
  needsRevisit?: boolean;
}

export interface ReadingStatsOut {
  completed_count: number;
  reading_count: number;
  to_read_count: number;
  completed_this_month: number;
  completed_this_year: number;
  pages_read_this_month: number;
  streak_days: number;
  top_categories: [string, number][];
}

export interface GroqModelOut {
  id: string;
  label: string;
  description: string;
  enabled: boolean;
}

export interface AISettingsOut {
  api_key_set: boolean;
  active_model: string;
  models: GroqModelOut[];
}

export interface AISettingsUpdateInput {
  api_key?: string;
  active_model?: string;
  enabled_model_ids?: string[];
}

export interface FocusSessionOut {
  id: number;
  block_id: number;
  scheduled_start: string | null;
  planned_minutes: number;
  started_at: string;
  ended_at: string | null;
  elapsed_seconds: number;
  start_delay_minutes: number | null;
  state: "in_progress" | "paused" | "completed" | "abandoned";
  focus_rating: number | null;
}

export interface CategoryPunctualityOut {
  category: string;
  sessions: number;
  avg_delay_minutes: number;
  on_time_pct: number;
}

export interface PunctualityOut {
  enough_data: boolean;
  session_count: number;
  min_sessions_needed: number;
  on_time_pct: number | null;
  avg_delay_minutes: number | null;
  median_delay_minutes: number | null;
  started_early_or_on_time: number;
  started_late: number;
  worst_category: CategoryPunctualityOut | null;
  best_category: CategoryPunctualityOut | null;
  by_category: CategoryPunctualityOut[];
  observations: string[];
}

export interface VitalsOut {
  date: string;
  sleep_hours: number | null;
  sleep_quality: number | null;
  energy: number | null;
  mood: number | null;
  stress: number | null;
  exercise_minutes: number | null;
  water_ml: number | null;
  calories: number | null;
  protein_g: number | null;
  /** null when too little was logged today to compute one honestly. */
  recovery_score: number | null;
  score_components: Record<string, number>;
  missing: string[];
  water_target_ml: number;
  hydration_pct: number | null;
  has_any_entry: boolean;
}

export interface RecoveryUpdateInput {
  date?: string;
  sleep_hours?: number;
  sleep_quality?: number;
  energy?: number;
  mood?: number;
  stress?: number;
  exercise_minutes?: number;
}

export interface NutritionUpdateInput {
  date?: string;
  water_ml?: number;
  calories?: number;
  protein_g?: number;
}

// ------------------------------------------------------------- Finance

export type AccountType =
  | "cash"
  | "bank"
  | "savings"
  | "investment"
  | "receivable"
  | "credit"
  | "loan"
  | "other";
export type TransactionType = "income" | "expense";
export type TransactionStatus = "actual" | "planned";
export type RecurringInterval = "weekly" | "monthly" | "yearly";
export type FinanceGoalCategory = "emergency_fund" | "short_term" | "long_term" | "custom";
export type FinanceGoalStatus = "active" | "completed" | "abandoned";

export interface FinanceAccountOut {
  id: number;
  name: string;
  account_type: AccountType;
  currency: string;
  opening_balance: number;
  current_balance: number;
  is_liability: boolean;
  is_active: boolean;
}

export interface FinanceAccountCreateInput {
  name: string;
  account_type: AccountType;
  currency?: string;
  opening_balance?: number;
}

export interface FinanceAccountUpdateInput {
  name?: string;
  is_active?: boolean;
}

export interface FinanceCategoryOut {
  id: number;
  name: string;
  kind: TransactionType;
  parent_id: number | null;
  is_system: boolean;
}

export interface FinanceCategoryCreateInput {
  name: string;
  kind: TransactionType;
  parent_id?: number;
}

export interface FinanceTransactionOut {
  id: number;
  account_id: number;
  category_id: number;
  type: TransactionType;
  amount: number;
  currency: string;
  occurred_on: string;
  status: TransactionStatus;
  description: string | null;
  notes: string | null;
  goal_id: number | null;
}

export interface FinanceTransactionCreateInput {
  account_id: number;
  category_id: number;
  type: TransactionType;
  amount: number;
  currency?: string;
  occurred_on: string;
  status?: TransactionStatus;
  description?: string;
  notes?: string;
  goal_id?: number;
}

export interface FinanceRecurringOut {
  id: number;
  description: string;
  account_id: number;
  category_id: number;
  type: TransactionType;
  amount: number;
  currency: string;
  interval: RecurringInterval;
  anchor_day: number;
  next_due_date: string;
  active: boolean;
}

export interface FinanceRecurringCreateInput {
  description: string;
  account_id: number;
  category_id: number;
  type: TransactionType;
  amount: number;
  currency?: string;
  interval: RecurringInterval;
  anchor_day: number;
  next_due_date: string;
}

export interface FinanceBudgetOut {
  id: number;
  category_id: number;
  category_name: string;
  planned: number;
  actual: number;
  remaining: number;
  utilization_pct: number;
  over_budget: boolean;
}

export interface FinanceBudgetUpsertInput {
  category_id: number;
  monthly_amount: number;
}

export interface FinanceGoalOut {
  id: number;
  title: string;
  target_amount: number;
  current_amount: number;
  remaining: number;
  progress_pct: number;
  required_monthly_contribution: number | null;
  currency: string;
  target_date: string | null;
  category: FinanceGoalCategory;
  status: FinanceGoalStatus;
  notes: string | null;
}

export interface FinanceGoalCreateInput {
  title: string;
  target_amount: number;
  currency?: string;
  target_date?: string;
  category?: FinanceGoalCategory;
  notes?: string;
}

export interface FinanceGoalUpdateInput {
  status?: FinanceGoalStatus;
}

export interface FinanceNetWorthPointOut {
  snapshot_date: string;
  total_assets: number;
  total_liabilities: number;
  net_worth: number;
}

export interface FinanceCategorySpend {
  category_name: string;
  amount: number;
}

export interface FinanceCategoryOutlier {
  category_name: string;
  this_month: number;
  trailing_avg: number;
  pct_diff: number;
}

export interface FinanceDashboardOut {
  month: string;
  income: number;
  expenses: number;
  savings: number;
  savings_rate_pct: number | null;
  income_change_pct: number | null;
  category_breakdown: FinanceCategorySpend[];
  outliers: FinanceCategoryOutlier[];
  budgets: FinanceBudgetOut[];
  goals: FinanceGoalOut[];
  upcoming_commitments: FinanceRecurringOut[];
  upcoming_total: number;
  net_worth: FinanceNetWorthPointOut | null;
  net_worth_trend: FinanceNetWorthPointOut[];
  insights: string[];
}

// ------------------------------------------------------------- Vocabulary

export type VocabLearningStatus = "known" | "learning" | "difficult" | "need_to_revisit";

export const VOCAB_STATUS_LABELS: Record<VocabLearningStatus, string> = {
  known: "Known",
  learning: "Learning",
  difficult: "Difficult",
  need_to_revisit: "Need to revisit",
};

export type VocabCefrLevel = "A1" | "A2" | "B1" | "B2" | "C1" | "C2";

export interface VocabWordOut {
  id: number;
  word: string;
  definition: string | null;
  example_sentence: string | null;
  pronunciation: string | null;
  part_of_speech: string | null;
  category: string | null;
  cefr_level: VocabCefrLevel | null;
  synonyms: string | null;
  antonyms: string | null;
  word_patterns: string | null;
  paraphrase: string | null;
  dictionary_link: string | null;
  notes: string | null;
  date_introduced: string;
  learning_status: VocabLearningStatus | null;
  source: string;
}

export interface VocabWordCreateInput {
  word: string;
  definition?: string;
  example_sentence?: string;
  pronunciation?: string;
  part_of_speech?: string;
  category?: string;
  cefr_level?: VocabCefrLevel;
  synonyms?: string;
  antonyms?: string;
  word_patterns?: string;
  paraphrase?: string;
  dictionary_link?: string;
  notes?: string;
}

export interface VocabWordUpdateInput {
  definition?: string | null;
  example_sentence?: string | null;
  pronunciation?: string | null;
  part_of_speech?: string | null;
  category?: string | null;
  cefr_level?: VocabCefrLevel | null;
  synonyms?: string | null;
  antonyms?: string | null;
  word_patterns?: string | null;
  paraphrase?: string | null;
  dictionary_link?: string | null;
  notes?: string | null;
}

export interface VocabStatusUpdateInput {
  learning_status: VocabLearningStatus | null;
}

export interface VocabSummaryOut {
  total_words: number;
  attempted_count: number;
  not_attempted_count: number;
  known_count: number;
  learning_count: number;
  difficult_count: number;
  need_to_revisit_count: number;
  by_level: [string, number][];
}

// ------------------------------------------------------- Personal OS overview

export interface OverviewOut {
  readiness_pct: number | null;
  reviews_due_today: number;
  reviews_overdue: number;
  active_goal_count: number;
  finance_income_this_month: number | null;
  finance_expenses_this_month: number | null;
  finance_savings_this_month: number | null;
  research_minutes_this_week: number;
  highlights: string[];
}

// --------------------------------------------------- Research command center

export type ResearchTopicStatus = "active" | "paused" | "completed" | "abandoned";
export type ResearchPaperStatus = "to_read" | "reading" | "read";
export type ResearchNoteKind = "idea" | "question" | "hypothesis" | "methodology" | "note";
export type ResearchExperimentStatus = "planned" | "running" | "completed" | "abandoned";
export type ResearchMilestoneStatus = "pending" | "in_progress" | "completed" | "missed";
export type ResearchVenueType = "conference" | "journal" | "workshop";
export type ResearchRelevance = "high" | "medium" | "low";
export type ResearchOpportunityStatus =
  | "interested"
  | "shortlisted"
  | "preparing"
  | "submitted"
  | "accepted"
  | "rejected"
  | "not_relevant";

export const RESEARCH_NOTE_KIND_LABELS: Record<ResearchNoteKind, string> = {
  idea: "Idea",
  question: "Question",
  hypothesis: "Hypothesis",
  methodology: "Methodology",
  note: "Note",
};

export const RESEARCH_OPPORTUNITY_STATUS_LABELS: Record<ResearchOpportunityStatus, string> = {
  interested: "Interested",
  shortlisted: "Shortlisted",
  preparing: "Preparing",
  submitted: "Submitted",
  accepted: "Accepted",
  rejected: "Rejected",
  not_relevant: "Not relevant",
};

export interface ResearchTopicOut {
  id: number;
  title: string;
  description: string | null;
  status: ResearchTopicStatus;
  current_blocker: string | null;
}

export interface ResearchTopicCreateInput {
  title: string;
  description?: string;
}

export interface ResearchTopicUpdateInput {
  title?: string;
  description?: string;
  status?: ResearchTopicStatus;
  current_blocker?: string | null;
}

export interface ResearchPaperOut {
  id: number;
  topic_id: number | null;
  title: string;
  authors: string | null;
  year: number | null;
  venue: string | null;
  url: string | null;
  status: ResearchPaperStatus;
  summary: string | null;
  relevance_note: string | null;
}

export interface ResearchPaperCreateInput {
  topic_id?: number;
  title: string;
  authors?: string;
  year?: number;
  venue?: string;
  url?: string;
  status?: ResearchPaperStatus;
  summary?: string;
  relevance_note?: string;
}

export interface ResearchPaperUpdateInput {
  status?: ResearchPaperStatus;
  summary?: string;
  relevance_note?: string;
}

export interface ResearchNoteOut {
  id: number;
  topic_id: number | null;
  paper_id: number | null;
  kind: ResearchNoteKind;
  content: string;
}

export interface ResearchNoteCreateInput {
  topic_id?: number;
  paper_id?: number;
  kind?: ResearchNoteKind;
  content: string;
}

export interface ResearchExperimentOut {
  id: number;
  topic_id: number | null;
  title: string;
  description: string | null;
  dataset: string | null;
  methodology_note: string | null;
  status: ResearchExperimentStatus;
  result_summary: string | null;
  started_date: string | null;
  completed_date: string | null;
}

export interface ResearchExperimentCreateInput {
  topic_id?: number;
  title: string;
  description?: string;
  dataset?: string;
  status?: ResearchExperimentStatus;
}

export interface ResearchExperimentUpdateInput {
  status?: ResearchExperimentStatus;
  result_summary?: string;
  completed_date?: string;
}

export interface ResearchMilestoneOut {
  id: number;
  topic_id: number | null;
  title: string;
  description: string | null;
  target_date: string | null;
  status: ResearchMilestoneStatus;
}

export interface ResearchMilestoneCreateInput {
  topic_id?: number;
  title: string;
  target_date?: string;
}

export interface ResearchMilestoneUpdateInput {
  status?: ResearchMilestoneStatus;
}

export interface ResearchOpportunityOut {
  id: number;
  venue_name: string;
  venue_type: ResearchVenueType;
  research_area: string | null;
  submission_deadline: string | null;
  notification_date: string | null;
  event_date: string | null;
  location: string | null;
  links: string[];
  submission_type: string | null;
  relevance: ResearchRelevance | null;
  priority: ResearchRelevance | null;
  status: ResearchOpportunityStatus;
  notes: string | null;
}

export interface ResearchOpportunityCreateInput {
  venue_name: string;
  venue_type: ResearchVenueType;
  research_area?: string;
  submission_deadline?: string;
  relevance?: ResearchRelevance;
  priority?: ResearchRelevance;
  notes?: string;
}

export interface ResearchOpportunityUpdateInput {
  status?: ResearchOpportunityStatus;
  priority?: ResearchRelevance;
  notes?: string;
}

export interface ResearchAtAGlanceOut {
  active_topic: ResearchTopicOut | null;
  papers_to_read_count: number;
  next_milestone: ResearchMilestoneOut | null;
  next_opportunity: ResearchOpportunityOut | null;
  highlights: string[];
}
