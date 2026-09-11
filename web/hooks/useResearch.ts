import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  addResearchOpportunityToGoals,
  createResearchExperiment,
  createResearchMilestone,
  createResearchNote,
  createResearchOpportunity,
  createResearchPaper,
  createResearchTopic,
  deleteResearchExperiment,
  deleteResearchMilestone,
  deleteResearchNote,
  deleteResearchOpportunity,
  deleteResearchPaper,
  deleteResearchTopic,
  getResearchAtAGlance,
  getResearchExperiments,
  getResearchMilestones,
  getResearchNotes,
  getResearchOpportunities,
  getResearchPapers,
  getResearchTopics,
  updateResearchExperiment,
  updateResearchMilestone,
  updateResearchOpportunity,
  updateResearchPaper,
  updateResearchTopic,
} from "@/lib/api";
import type {
  ResearchExperimentCreateInput,
  ResearchExperimentUpdateInput,
  ResearchMilestoneCreateInput,
  ResearchMilestoneUpdateInput,
  ResearchNoteCreateInput,
  ResearchOpportunityCreateInput,
  ResearchOpportunityUpdateInput,
  ResearchPaperCreateInput,
  ResearchPaperUpdateInput,
  ResearchTopicCreateInput,
  ResearchTopicUpdateInput,
} from "@/lib/types";

const KEYS = {
  glance: ["research", "at-a-glance"] as const,
  topics: ["research", "topics"] as const,
  papers: (topicId?: number) => ["research", "papers", topicId ?? "all"] as const,
  notes: (topicId?: number) => ["research", "notes", topicId ?? "all"] as const,
  experiments: (topicId?: number) => ["research", "experiments", topicId ?? "all"] as const,
  milestones: (topicId?: number) => ["research", "milestones", topicId ?? "all"] as const,
  opportunities: (status?: string) => ["research", "opportunities", status ?? "all"] as const,
};

function useInvalidateResearch() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: ["research"] });
}

export function useResearchAtAGlance() {
  return useQuery({ queryKey: KEYS.glance, queryFn: getResearchAtAGlance });
}

export function useResearchTopics() {
  return useQuery({ queryKey: KEYS.topics, queryFn: getResearchTopics });
}

export function useCreateResearchTopic() {
  const invalidate = useInvalidateResearch();
  return useMutation({
    mutationFn: (input: ResearchTopicCreateInput) => createResearchTopic(input),
    onSuccess: invalidate,
  });
}

export function useUpdateResearchTopic() {
  const invalidate = useInvalidateResearch();
  return useMutation({
    mutationFn: ({ topicId, input }: { topicId: number; input: ResearchTopicUpdateInput }) =>
      updateResearchTopic(topicId, input),
    onSuccess: invalidate,
  });
}

export function useDeleteResearchTopic() {
  const invalidate = useInvalidateResearch();
  return useMutation({ mutationFn: (topicId: number) => deleteResearchTopic(topicId), onSuccess: invalidate });
}

export function useResearchPapers(topicId?: number) {
  return useQuery({ queryKey: KEYS.papers(topicId), queryFn: () => getResearchPapers(topicId) });
}

export function useCreateResearchPaper() {
  const invalidate = useInvalidateResearch();
  return useMutation({
    mutationFn: (input: ResearchPaperCreateInput) => createResearchPaper(input),
    onSuccess: invalidate,
  });
}

export function useUpdateResearchPaper() {
  const invalidate = useInvalidateResearch();
  return useMutation({
    mutationFn: ({ paperId, input }: { paperId: number; input: ResearchPaperUpdateInput }) =>
      updateResearchPaper(paperId, input),
    onSuccess: invalidate,
  });
}

export function useDeleteResearchPaper() {
  const invalidate = useInvalidateResearch();
  return useMutation({ mutationFn: (paperId: number) => deleteResearchPaper(paperId), onSuccess: invalidate });
}

export function useResearchNotes(topicId?: number) {
  return useQuery({ queryKey: KEYS.notes(topicId), queryFn: () => getResearchNotes(topicId) });
}

export function useCreateResearchNote() {
  const invalidate = useInvalidateResearch();
  return useMutation({
    mutationFn: (input: ResearchNoteCreateInput) => createResearchNote(input),
    onSuccess: invalidate,
  });
}

export function useDeleteResearchNote() {
  const invalidate = useInvalidateResearch();
  return useMutation({ mutationFn: (noteId: number) => deleteResearchNote(noteId), onSuccess: invalidate });
}

export function useResearchExperiments(topicId?: number) {
  return useQuery({ queryKey: KEYS.experiments(topicId), queryFn: () => getResearchExperiments(topicId) });
}

export function useCreateResearchExperiment() {
  const invalidate = useInvalidateResearch();
  return useMutation({
    mutationFn: (input: ResearchExperimentCreateInput) => createResearchExperiment(input),
    onSuccess: invalidate,
  });
}

export function useUpdateResearchExperiment() {
  const invalidate = useInvalidateResearch();
  return useMutation({
    mutationFn: ({ experimentId, input }: { experimentId: number; input: ResearchExperimentUpdateInput }) =>
      updateResearchExperiment(experimentId, input),
    onSuccess: invalidate,
  });
}

export function useDeleteResearchExperiment() {
  const invalidate = useInvalidateResearch();
  return useMutation({
    mutationFn: (experimentId: number) => deleteResearchExperiment(experimentId),
    onSuccess: invalidate,
  });
}

export function useResearchMilestones(topicId?: number) {
  return useQuery({ queryKey: KEYS.milestones(topicId), queryFn: () => getResearchMilestones(topicId) });
}

export function useCreateResearchMilestone() {
  const invalidate = useInvalidateResearch();
  return useMutation({
    mutationFn: (input: ResearchMilestoneCreateInput) => createResearchMilestone(input),
    onSuccess: invalidate,
  });
}

export function useUpdateResearchMilestone() {
  const invalidate = useInvalidateResearch();
  return useMutation({
    mutationFn: ({ milestoneId, input }: { milestoneId: number; input: ResearchMilestoneUpdateInput }) =>
      updateResearchMilestone(milestoneId, input),
    onSuccess: invalidate,
  });
}

export function useDeleteResearchMilestone() {
  const invalidate = useInvalidateResearch();
  return useMutation({
    mutationFn: (milestoneId: number) => deleteResearchMilestone(milestoneId),
    onSuccess: invalidate,
  });
}

export function useResearchOpportunities(statusFilter?: string) {
  return useQuery({
    queryKey: KEYS.opportunities(statusFilter),
    queryFn: () => getResearchOpportunities(statusFilter),
  });
}

export function useCreateResearchOpportunity() {
  const invalidate = useInvalidateResearch();
  return useMutation({
    mutationFn: (input: ResearchOpportunityCreateInput) => createResearchOpportunity(input),
    onSuccess: invalidate,
  });
}

export function useUpdateResearchOpportunity() {
  const invalidate = useInvalidateResearch();
  return useMutation({
    mutationFn: ({
      opportunityId,
      input,
    }: {
      opportunityId: number;
      input: ResearchOpportunityUpdateInput;
    }) => updateResearchOpportunity(opportunityId, input),
    onSuccess: invalidate,
  });
}

export function useDeleteResearchOpportunity() {
  const invalidate = useInvalidateResearch();
  return useMutation({
    mutationFn: (opportunityId: number) => deleteResearchOpportunity(opportunityId),
    onSuccess: invalidate,
  });
}

export function useAddResearchOpportunityToGoals() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (opportunityId: number) => addResearchOpportunityToGoals(opportunityId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
    },
  });
}
