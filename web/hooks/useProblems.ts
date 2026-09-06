import { useQuery } from "@tanstack/react-query";
import { getProblems } from "@/lib/api";

export function useProblems(pattern?: string, difficulty?: string) {
  return useQuery({
    queryKey: ["problems", pattern, difficulty],
    queryFn: () => getProblems(pattern, difficulty),
  });
}
