import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getAISettings, updateAISettings } from "@/lib/api";
import type { AISettingsUpdateInput } from "@/lib/types";

export const AI_SETTINGS_QUERY_KEY = ["ai-settings"] as const;

export function useAISettings() {
  return useQuery({
    queryKey: AI_SETTINGS_QUERY_KEY,
    queryFn: getAISettings,
  });
}

export function useUpdateAISettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: AISettingsUpdateInput) => updateAISettings(input),
    onSuccess: (data) => {
      queryClient.setQueryData(AI_SETTINGS_QUERY_KEY, data);
    },
  });
}
