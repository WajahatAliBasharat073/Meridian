import type {
  AttemptResult,
  BlockStatus,
  DashboardSummaryOut,
  MasteryLevel,
  RecommendationOut,
  ReviewDueOut,
  TimeBlockOut,
  TodayOut,
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
