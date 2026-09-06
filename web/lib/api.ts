import type {
  AttemptResult,
  BlockStatus,
  MasteryLevel,
  RecommendationOut,
  ReviewDueOut,
  TodayOut,
} from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${path}: ${text}`);
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
