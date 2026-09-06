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
