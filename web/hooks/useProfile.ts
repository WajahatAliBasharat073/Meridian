import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getProfile, updateProfile } from "@/lib/api";
import type { ProfileUpdate } from "@/lib/types";

export const PROFILE_QUERY_KEY = ["profile"] as const;

export function useProfile() {
  return useQuery({
    queryKey: PROFILE_QUERY_KEY,
    queryFn: getProfile,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: ProfileUpdate) => updateProfile(input),
    onSuccess: (data) => {
      queryClient.setQueryData(PROFILE_QUERY_KEY, data);
    },
  });
}
