import { Sigma, Brain, Cpu, Sparkles, Server, Workflow, Bot, type LucideIcon } from "lucide-react";

export interface CategoryMeta {
  key: string;
  label: string;
  description: string;
  icon: LucideIcon;
}

export const CONCEPT_CATEGORIES: CategoryMeta[] = [
  {
    key: "math_stats",
    label: "Math & Statistics",
    description: "Linear algebra, calculus, probability — the language every model is written in.",
    icon: Sigma,
  },
  {
    key: "classical_ml",
    label: "Classical ML",
    description: "Bias-variance, trees, SVMs, clustering, classic NLP.",
    icon: Brain,
  },
  {
    key: "deep_learning",
    label: "Deep Learning",
    description: "Backprop, CNNs, RNNs, transformers, generative models.",
    icon: Cpu,
  },
  {
    key: "llm_genai",
    label: "LLMs & GenAI",
    description: "Attention, RAG, fine-tuning, embeddings, evaluation.",
    icon: Sparkles,
  },
  {
    key: "mlops",
    label: "MLOps & Production",
    description: "Serving, monitoring, drift, CI/CD for ML systems.",
    icon: Server,
  },
  {
    key: "ml_system_design",
    label: "ML System Design",
    description: "Recommenders, search/ranking, feed and ads systems.",
    icon: Workflow,
  },
  {
    key: "agentic_ai",
    label: "Agentic AI Systems",
    description: "Agent workflows, tool use, guardrails, multi-agent design.",
    icon: Bot,
  },
];

export const CATEGORY_LABEL: Record<string, string> = Object.fromEntries(
  CONCEPT_CATEGORIES.map((c) => [c.key, c.label])
);

export function categoryMeta(key: string): CategoryMeta | undefined {
  return CONCEPT_CATEGORIES.find((c) => c.key === key);
}
