import { useQuery } from "@tanstack/react-query";
import { getToday } from "@/lib/api";

export const TODAY_QUERY_KEY = ["today"] as const;

export function useToday() {
  return useQuery({
    queryKey: TODAY_QUERY_KEY,
    queryFn: getToday,
    refetchInterval: 30_000,
  });
}
