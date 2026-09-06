import { useQuery } from "@tanstack/react-query";
import { getDailyRecap } from "@/lib/api";

export function useDailyRecap() {
  return useQuery({
    queryKey: ["daily-recap"],
    queryFn: getDailyRecap,
  });
}
