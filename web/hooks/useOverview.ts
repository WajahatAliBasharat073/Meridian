import { useQuery } from "@tanstack/react-query";
import { getOverview } from "@/lib/api";

export function useOverview() {
  return useQuery({
    queryKey: ["overview"],
    queryFn: getOverview,
  });
}
