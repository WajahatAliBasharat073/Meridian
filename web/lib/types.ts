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
}

export interface ProblemOut {
  problem_id: number;
  lc_number: number;
  title: string;
  slug: string;
  url: string;
  pattern: string;
  difficulty: string;
  is_neetcode150: boolean;
  is_blind75: boolean;
  current_mastery: MasteryLevel | null;
  is_scheduled_today: boolean;
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

export interface QuestionOut {
  question_id: number;
  category: string;
  title: string;
  source: string;
  covered: boolean;
}

export interface CategoryCoverageOut {
  category: string;
  covered_count: number;
  total_count: number;
  pct: number;
}

export interface QuestionSummaryOut {
  by_category: CategoryCoverageOut[];
  covered_count: number;
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
}

export interface GoalCreateInput {
  title: string;
  description?: string;
  category?: string;
  target_date?: string;
}

export interface GoalUpdateInput {
  progress_pct?: number;
  status?: GoalStatus;
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
