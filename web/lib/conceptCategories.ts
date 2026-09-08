import {
  Bot,
  Brain,
  Bug,
  Code2,
  Cpu,
  Database,
  Eye,
  FileText,
  FlaskConical,
  Gauge,
  Layers,
  LineChart,
  MessageSquare,
  Mic,
  Network,
  Plug,
  Scale,
  Search,
  Server,
  ShieldCheck,
  Sigma,
  Sparkles,
  Target,
  Users,
  Workflow,
  type LucideIcon,
} from "lucide-react";

export interface CategoryMeta {
  key: string;
  label: string;
  description: string;
  icon: LucideIcon;
  /** Which band of the loop this belongs to — the page groups by this so
   * 32 tiles read as a curriculum rather than a wall. */
  group: CategoryGroup;
  /** Module letters in the master map that feed this category, so the tile
   * can point at the same material in the curriculum browser. */
  modules: string[];
}

export type CategoryGroup =
  | "Foundations"
  | "Modern AI"
  | "Systems & Design"
  | "Production"
  | "Coding rounds"
  | "Interview craft";

export const CATEGORY_GROUPS: { name: CategoryGroup; blurb: string }[] = [
  {
    name: "Foundations",
    blurb:
      "Still asked in 2026, and still where candidates who prepared only GenAI come apart.",
  },
  {
    name: "Modern AI",
    blurb: "Transformers through agents — the rounds that did not exist five years ago.",
  },
  {
    name: "Systems & Design",
    blurb: "The largest part of a senior loop: requirements to failure modes, every time.",
  },
  {
    name: "Production",
    blurb: "Training a model is not the end of the project, and interviewers know it.",
  },
  {
    name: "Coding rounds",
    blurb: "Two different rounds: general algorithms, and ML implemented from scratch.",
  },
  {
    name: "Interview craft",
    blurb: "Your own work, your judgement, and the stories — where levels are decided.",
  },
];

export const CONCEPT_CATEGORIES: CategoryMeta[] = [
  // ---------------- Foundations ----------------
  {
    key: "math_stats",
    label: "Math & Statistics",
    description: "Linear algebra, calculus, probability — posed as scenarios with numbers.",
    icon: Sigma,
    group: "Foundations",
    modules: ["C"],
  },
  {
    key: "classical_ml",
    label: "Classical ML",
    description: "Bias-variance, trees, ensembles, SVMs, clustering, classic NLP.",
    icon: Brain,
    group: "Foundations",
    modules: ["D"],
  },
  {
    key: "ml_fundamentals",
    label: "ML Fundamentals",
    description: "Leakage, imbalance, drift, calibration, cross-validation — the breadth round.",
    icon: Layers,
    group: "Foundations",
    modules: ["E"],
  },
  {
    key: "evaluation",
    label: "Model Evaluation",
    description: "Not 'what is F1' but 'why this metric instead of that one, for this decision'.",
    icon: Gauge,
    group: "Foundations",
    modules: ["F"],
  },
  {
    key: "experimentation",
    label: "Experimentation & A/B",
    description: "Power, p-values, guardrails — and contradictions between metrics to resolve.",
    icon: FlaskConical,
    group: "Foundations",
    modules: ["G"],
  },
  {
    key: "deep_learning",
    label: "Deep Learning",
    description: "Backprop, initialisation, optimisers, normalisation, CNNs, RNNs.",
    icon: Cpu,
    group: "Foundations",
    modules: ["H"],
  },

  // ---------------- Modern AI ----------------
  {
    key: "transformers",
    label: "Transformers",
    description: "Q/K/V, RoPE, causal masking, KV cache, MQA/GQA, FlashAttention, MoE.",
    icon: Network,
    group: "Modern AI",
    modules: ["K"],
  },
  {
    key: "llm_genai",
    label: "LLMs & GenAI",
    description: "Pretraining, scaling laws, decoding, SFT, RLHF, DPO, LoRA, quantisation.",
    icon: Sparkles,
    group: "Modern AI",
    modules: ["L"],
  },
  {
    key: "rag",
    label: "RAG",
    description: "Chunking to reranking to citations — and whether a failure is retrieval or generation.",
    icon: Search,
    group: "Modern AI",
    modules: ["M"],
  },
  {
    key: "agentic_ai",
    label: "AI Agents",
    description: "Planning, tools, memory, permissions, budgets, recovery, long-running work.",
    icon: Bot,
    group: "Modern AI",
    modules: ["N", "T"],
  },
  {
    key: "context_engineering",
    label: "Context Engineering",
    description: "Selecting, ranking, compressing and proving what the model actually sees.",
    icon: Target,
    group: "Modern AI",
    modules: ["O"],
  },
  {
    key: "protocols",
    label: "MCP / A2A Protocols",
    description: "Tool and agent interoperability — where a protocol boundary is a trust boundary.",
    icon: Plug,
    group: "Modern AI",
    modules: ["P"],
  },
  {
    key: "nlp",
    label: "NLP",
    description: "Tokenization, TF-IDF, embeddings, encoders — what every RAG question rests on.",
    icon: MessageSquare,
    group: "Modern AI",
    modules: ["J"],
  },
  {
    key: "computer_vision",
    label: "Computer Vision",
    description: "CNNs, ViTs, detection, segmentation, OCR, IoU and mAP.",
    icon: Eye,
    group: "Modern AI",
    modules: ["I"],
  },
  {
    key: "multimodal",
    label: "Multimodal AI",
    description: "Vision-language, audio, document intelligence, multimodal RAG.",
    icon: Mic,
    group: "Modern AI",
    modules: ["Q"],
  },

  // ---------------- Systems & Design ----------------
  {
    key: "ml_system_design",
    label: "ML System Design",
    description: "Recommenders, search, ranking, feed and ads — the 9-step spine, driven not wandered.",
    icon: Workflow,
    group: "Systems & Design",
    modules: ["R"],
  },
  {
    key: "genai_system_design",
    label: "GenAI System Design",
    description: "Chat at scale, enterprise RAG, coding assistants, serving platforms, model routing.",
    icon: Sparkles,
    group: "Systems & Design",
    modules: ["S"],
  },
  {
    key: "recsys",
    label: "Recommendation Systems",
    description: "Two-tower retrieval, ranking, cold start, feedback loops, diversity.",
    icon: Users,
    group: "Systems & Design",
    modules: ["X"],
  },
  {
    key: "search_ir",
    label: "Search & Retrieval",
    description: "Inverted index, BM25, dense retrieval, ANN/HNSW, learning-to-rank.",
    icon: Search,
    group: "Systems & Design",
    modules: ["Y"],
  },

  // ---------------- Production ----------------
  {
    key: "mlops",
    label: "MLOps & Production",
    description: "Pipelines, registry, deployment, monitoring, drift, retraining, rollback.",
    icon: Server,
    group: "Production",
    modules: ["U"],
  },
  {
    key: "llmops",
    label: "LLMOps",
    description: "Prompt versioning, tracing, token cost, caching, routing, regression tests.",
    icon: LineChart,
    group: "Production",
    modules: ["V"],
  },
  {
    key: "ml_infrastructure",
    label: "ML Infrastructure",
    description: "Distributed training, GPU utilisation, quantisation, batching, p99 latency.",
    icon: Cpu,
    group: "Production",
    modules: ["W"],
  },
  {
    key: "ml_debugging",
    label: "ML Debugging",
    description: "A symptom, then an ordered investigation. Where the boundary of understanding shows.",
    icon: Bug,
    group: "Production",
    modules: ["Z"],
  },
  {
    key: "responsible_ai",
    label: "Responsible AI & Security",
    description: "Fairness, privacy, prompt injection, tool poisoning, exfiltration, access control.",
    icon: ShieldCheck,
    group: "Production",
    modules: ["AE"],
  },

  // ---------------- Coding rounds ----------------
  {
    key: "dsa",
    label: "DSA Patterns",
    description: "By pattern, not by problem count — recognising it from the statement is the skill.",
    icon: Code2,
    group: "Coding rounds",
    modules: ["A"],
  },
  {
    key: "ml_coding",
    label: "ML Coding",
    description: "Implement the primitives in NumPy: shapes, stability, edge cases, not library calls.",
    icon: Code2,
    group: "Coding rounds",
    modules: ["B"],
  },
  {
    key: "sql_data",
    label: "SQL & Data",
    description: "You cannot model the data before you can get it out.",
    icon: Database,
    group: "Coding rounds",
    modules: ["A"],
  },

  // ---------------- Interview craft ----------------
  {
    key: "project_deep_dive",
    label: "Project Deep Dive",
    description: "Your own work, interrogated until you stop having answers.",
    icon: FileText,
    group: "Interview craft",
    modules: ["AD"],
  },
  {
    key: "ml_case_study",
    label: "ML Case Studies",
    description: "Real production systems, published by the company. Read them, then argue with them.",
    icon: FileText,
    group: "Interview craft",
    modules: ["AA"],
  },
  {
    key: "product_reasoning",
    label: "Product & Business Reasoning",
    description: "Engineering judgement. 'Don't use ML here' is often the correct answer.",
    icon: Scale,
    group: "Interview craft",
    modules: ["AB"],
  },
  {
    key: "research_papers",
    label: "Research Papers",
    description: "Whether you read the paper, or read about the paper.",
    icon: FileText,
    group: "Interview craft",
    modules: ["AC"],
  },
  {
    key: "behavioral",
    label: "Behavioral & Leadership",
    description: "STAR, but the stories must carry technical depth. Often decides the level.",
    icon: Users,
    group: "Interview craft",
    modules: ["AF"],
  },
];

export function categoryMeta(key: string): CategoryMeta | undefined {
  return CONCEPT_CATEGORIES.find((c) => c.key === key);
}

export function categoriesInGroup(group: CategoryGroup): CategoryMeta[] {
  return CONCEPT_CATEGORIES.filter((c) => c.group === group);
}
