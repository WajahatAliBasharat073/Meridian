import { useQuery } from "@tanstack/react-query";
import { getProblemsByTopic } from "@/lib/api";

/** The whole bank grouped by data structure, each section carrying its
 * "learn this first" guide. One request: the page renders every section. */
export function useProblemsByTopic() {
  return useQuery({
    queryKey: ["problems-by-topic"],
    queryFn: () => getProblemsByTopic(),
  });
}
