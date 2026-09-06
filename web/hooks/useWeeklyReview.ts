import { useQuery } from "@tanstack/react-query";
import { getWeeklyReview } from "@/lib/api";

export function useWeeklyReview() {
  return useQuery({
    queryKey: ["weekly-review"],
    queryFn: getWeeklyReview,
  });
}
