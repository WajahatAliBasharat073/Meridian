"""OUTPUT 1 — the Interview Master Map.

The 32 modules of the AI/ML interview curriculum, as reference data.

Priority is the point of this file. If every module were P0 the map would
carry no information and preparation order would be guesswork. The split
reflects what an ML/AI engineering loop at Meta/Amazon/Netflix/Google/
OpenAI actually spends its rounds on, not what a syllabus would weight:

  P0 — appears in nearly every loop for these roles
  P1 — appears often, or is the differentiator at senior+
  P2 — appears when the role or the candidate's background invites it
  P3 — specialised; prepare only if the role explicitly calls for it

Structure is adapted from alirezadir/AIMLInterviews' six chapters (coding,
ML coding, ML breadth, ML/GenAI system design, agentic systems, behavioral)
and expanded for a 2026 loop: the modern additions are context engineering,
protocols (MCP/A2A), agentic system design, LLMOps, and post-training —
none of which existed as interview rounds when the classical structure was
written. Classical ML, statistics and DSA are deliberately retained at P0:
2026 loops added GenAI rounds on top of the fundamentals, they did not
replace them.

Columns: (code, title, priority, target_seniority, summary, submodules)
"""

MODULES: list[tuple[str, str, str, list[str], str, list[str]]] = [
    (
        "A",
        "General Coding & DSA",
        "P0",
        ["junior", "mid", "senior", "staff"],
        "One or two rounds in nearly every loop, in the same format as a SWE coding round. "
        "Prepared by pattern, not by problem count — recognising the pattern from the "
        "statement is the skill being tested.",
        [
            "Arrays, strings & hashing", "Two pointers & sliding window", "Stack & monotonic stack",
            "Binary search", "Linked lists", "Intervals", "Trees (BFS/DFS/BST)",
            "Tries, heaps & priority queues", "Backtracking", "Graphs",
            "Advanced graphs & greedy", "1-D dynamic programming", "2-D dynamic programming",
            "Math, geometry & bit manipulation", "Complexity analysis",
        ],
    ),
    (
        "B",
        "ML Coding",
        "P0",
        ["junior", "mid", "senior", "staff"],
        "A separate round from DSA: implement ML primitives from scratch in NumPy/PyTorch. "
        "Tests whether the maths is understood at implementation depth — shapes, numerical "
        "stability, and edge cases, not library calls.",
        [
            "Classic ML primitives", "Metrics & evaluation functions", "Data preparation & sampling",
            "Neural network & backprop", "Language-model mechanics", "GenAI primitives",
            "Agentic control-plane coding",
        ],
    ),
    (
        "C",
        "Mathematics & Statistics",
        "P0",
        ["junior", "mid", "senior", "staff"],
        "Applied, not recited. Questions are posed as scenarios with numbers "
        "(base rates, power, estimator choice) rather than definitions.",
        [
            "Linear algebra", "Calculus & gradients", "Probability", "Statistics & inference",
            "Optimization", "Experimental statistics",
        ],
    ),
    (
        "D",
        "Classical Machine Learning",
        "P0",
        ["junior", "mid", "senior", "staff"],
        "Still asked in 2026 loops and still where candidates who prepared only GenAI fail. "
        "Every algorithm carries the same 15-question interrogation: objective, assumptions, "
        "hyperparameters, failure modes, alternatives, production behaviour.",
        [
            "Regression", "Classification", "Decision trees", "Ensembles (bagging/boosting)",
            "SVM & kernels", "Naive Bayes", "Nearest neighbours", "Clustering",
            "Dimensionality reduction", "Anomaly detection", "Feature engineering",
        ],
    ),
    (
        "E",
        "ML Fundamentals & Breadth",
        "P0",
        ["junior", "mid", "senior", "staff"],
        "The breadth round. Follows a consistent structure across interviewers, which makes "
        "it the highest-ROI module to over-prepare.",
        [
            "Bias & variance", "Overfitting & regularization", "Feature selection",
            "Missing data & outliers", "Imbalanced data", "Data leakage", "Sampling",
            "Cross-validation", "Distribution & concept drift", "Label noise & data quality",
            "Calibration & threshold selection",
        ],
    ),
    (
        "F",
        "Model Evaluation",
        "P0",
        ["junior", "mid", "senior", "staff"],
        "Kept separate from algorithms on purpose. The recurring question is never "
        "'what is F1' but 'why this metric instead of that one, for this decision'.",
        [
            "Classification metrics", "Regression metrics", "Ranking metrics",
            "GenAI evaluation", "Agentic evaluation", "Metric selection & trade-offs",
            "Offline vs online metrics",
        ],
    ),
    (
        "G",
        "Experimentation & A/B Testing",
        "P1",
        ["mid", "senior", "staff"],
        "Heavier for product-facing ML and Applied Scientist roles. The good questions are "
        "contradictions to resolve, not formulas to state.",
        [
            "Hypothesis testing", "p-values & confidence intervals", "Power & sample size",
            "Type I/II errors", "Multiple comparisons", "Selection bias & contamination",
            "Novelty effects", "Guardrail metrics", "Sequential testing",
        ],
    ),
    (
        "H",
        "Deep Learning",
        "P0",
        ["junior", "mid", "senior", "staff"],
        "Separate from classical ML. Every concept is asked as WHAT / HOW / WHY / MATH / "
        "FAILURE / TRADE-OFF / PRODUCTION.",
        [
            "Neural network basics", "Activations & losses", "Backpropagation",
            "Initialization", "Optimizers & schedules", "Regularization & dropout",
            "Normalization (Batch/Layer)", "Residual networks", "CNNs", "RNN/LSTM/GRU",
            "Seq2seq & attention",
        ],
    ),
    (
        "I",
        "Computer Vision",
        "P2",
        ["mid", "senior", "staff"],
        "Role-dependent. P0 for a CV-titled role, P2 otherwise — but multimodal work has "
        "pulled the embedding and detection parts back into general relevance.",
        [
            "CNN architectures", "Vision transformers", "Classification", "Object detection",
            "Segmentation", "OCR & document AI", "Image embeddings", "Transfer learning",
            "Augmentation", "CV metrics (IoU, mAP)",
        ],
    ),
    (
        "J",
        "NLP",
        "P1",
        ["junior", "mid", "senior", "staff"],
        "The classical half still matters: tokenization, TF-IDF and retrieval fundamentals "
        "underpin every RAG question in Module M.",
        [
            "Tokenization", "TF-IDF & sparse features", "Word embeddings", "Sequence models",
            "BERT & encoder models", "Decoder models", "NER & classification",
            "Semantic similarity", "Information retrieval",
        ],
    ),
    (
        "K",
        "Transformers",
        "P0",
        ["junior", "mid", "senior", "staff"],
        "A dedicated high-priority module. Architecture-level understanding is expected — "
        "why each design choice exists, not what the diagram looks like.",
        [
            "Q/K/V & scaled dot-product", "Multi-head attention", "Positional encoding & RoPE",
            "Causal masking", "Encoder vs decoder", "Attention complexity", "KV cache",
            "MHA / MQA / GQA", "FlashAttention", "Mixture of Experts",
        ],
    ),
    (
        "L",
        "Foundation Models & LLMs",
        "P0",
        ["junior", "mid", "senior", "staff"],
        "Pretraining through post-training. The distinguishing questions are 'why' — why "
        "next-token prediction produces general capability, why DPO removes the reward model.",
        [
            "Pretraining & next-token prediction", "Tokenization at scale", "Scaling laws",
            "Context windows", "Inference & decoding", "Sampling (temperature/top-k/top-p)",
            "Instruction tuning & SFT", "RLHF", "DPO & preference optimization", "Alignment",
            "LoRA / QLoRA / PEFT", "Quantization", "Distillation & pruning",
        ],
    ),
    (
        "M",
        "RAG",
        "P0",
        ["junior", "mid", "senior", "staff"],
        "The most consistently asked GenAI system topic. The load-bearing question is "
        "diagnostic: is this failure retrieval or generation, and how do you know?",
        [
            "Parsing & chunking", "Embeddings", "Vector indexes (HNSW/IVF)", "Dense vs BM25",
            "Hybrid search", "Reranking", "Query rewriting & HyDE", "Metadata filtering",
            "Context construction & compression", "Citations & grounding", "Freshness",
            "Multi-tenancy & access control", "Retrieval evaluation", "Generation evaluation",
        ],
    ),
    (
        "N",
        "AI Agents",
        "P1",
        ["mid", "senior", "staff"],
        "New as a distinct round. The senior signal is keeping permissions, budgets, retries "
        "and termination in deterministic code rather than in prompt text.",
        [
            "Agent vs workflow", "Planning", "Tool & function calling", "Memory & state",
            "Reflection", "Routing & orchestration", "Multi-agent systems",
            "Human-in-the-loop & approval", "Guardrails & permissions", "Long-running agents",
            "Scheduling & checkpointing", "Recovery & idempotency", "Retries & cancellation",
            "Budgets & cost control",
        ],
    ),
    (
        "O",
        "Context Engineering",
        "P1",
        ["mid", "senior", "staff"],
        "A 2026 module with no classical equivalent: what enters the context window is now a "
        "systems-design decision with cost, latency and correctness consequences.",
        [
            "Context selection", "Context ranking", "Context compression", "Context isolation",
            "Provenance", "Memory", "Tool-output handling", "Prompt budgeting",
            "Context pollution",
        ],
    ),
    (
        "P",
        "MCP / A2A / AI Protocols",
        "P2",
        ["mid", "senior", "staff"],
        "Emerging and role-dependent, but the security half is asked well beyond agent roles.",
        [
            "MCP clients & servers", "Tools, resources & prompts", "Authorization",
            "Remote MCP", "A2A & interoperability", "Prompt injection",
            "Tool poisoning", "Confused deputy", "Privilege escalation", "Data exfiltration",
        ],
    ),
    (
        "Q",
        "Multimodal AI",
        "P2",
        ["mid", "senior", "staff"],
        "Rising. Strongly relevant for document-AI, search and assistant products.",
        [
            "Vision-language models", "Audio-language models", "Video understanding",
            "Speech", "OCR & document intelligence", "Multimodal embeddings",
            "Multimodal RAG",
        ],
    ),
    (
        "R",
        "ML System Design",
        "P0",
        ["mid", "senior", "staff", "principal"],
        "One of the two largest modules. Every answer follows the same 20-point spine from "
        "requirements through failure modes; the spine is what separates a senior answer "
        "from a list of components.",
        [
            "Requirements & problem formulation", "Metrics (offline & online)",
            "Architecture & MVP logic", "Data collection & labels", "Feature engineering",
            "Model development", "Offline evaluation", "Serving & prediction service",
            "Online testing & deployment", "Monitoring & drift", "Retraining & rollback",
            "Scale, cost & failure modes", "Recommendation systems", "Search & ranking",
            "Ads & newsfeed", "Fraud, spam & moderation", "Forecasting & anomaly detection",
        ],
    ),
    (
        "S",
        "GenAI System Design",
        "P0",
        ["mid", "senior", "staff", "principal"],
        "Now frequently a separate round. The same design spine with a GenAI lens: models, "
        "prompting, context, RAG, caching, streaming, latency, cost, safety, evals, fallbacks.",
        [
            "LLM chatbot at scale", "Enterprise RAG assistant", "LLM inference & serving platform",
            "AI coding assistant", "Customer-support AI", "Document intelligence platform",
            "AI / semantic search", "Multimodal assistant", "LLM evaluation platform",
            "LLM gateway & model routing", "Cost & latency optimization",
        ],
    ),
    (
        "T",
        "Agentic System Design",
        "P1",
        ["senior", "staff", "principal"],
        "The 2026 addition to the design round. Must explicitly cover harness, orchestrator, "
        "permissions, checkpoints, recovery, approval, budgets and observability.",
        [
            "Research agent", "Coding agent", "Browser agent", "Enterprise workflow agent",
            "Long-running background agent", "Multi-agent support system",
            "Autonomous monitoring agent", "Agent harness & orchestrator",
            "Permissions & security", "Evaluation & observability",
        ],
    ),
    (
        "U",
        "Production ML & MLOps",
        "P1",
        ["mid", "senior", "staff", "principal"],
        "Training a model is not the end of the project. This module is where senior "
        "candidates separate from strong juniors.",
        [
            "Problem formulation & business impact", "Data & feature pipelines",
            "Training pipelines", "Experiment tracking", "Model registry & versioning",
            "Deployment & serving", "Monitoring", "Drift detection", "Retraining",
            "CI/CD", "Canary & shadow deployment", "Rollback", "Batch vs online vs streaming",
            "Cost & technical debt",
        ],
    ),
    (
        "V",
        "LLMOps & AI Operations",
        "P1",
        ["mid", "senior", "staff"],
        "The operational layer specific to LLM products: what you version, trace, cache, "
        "route and regression-test when the model is not yours.",
        [
            "Prompt versioning", "Model versioning", "Evaluation datasets", "LLM observability",
            "Tracing", "Token usage & cost", "Latency", "Caching", "Model routing",
            "Fallback models", "Prompt regression testing", "Human feedback loops",
        ],
    ),
    (
        "W",
        "ML Infrastructure",
        "P2",
        ["senior", "staff", "principal"],
        "P0 for infra-titled roles, P2 otherwise — but inference optimization has become "
        "general knowledge for anyone shipping LLM products.",
        [
            "Distributed training", "Data parallelism", "Tensor parallelism",
            "Pipeline parallelism", "GPU utilization", "Inference optimization",
            "Quantization", "Batching & continuous batching", "KV cache management",
            "Autoscaling", "P99 latency & throughput", "Fault tolerance",
        ],
    ),
    (
        "X",
        "Recommendation Systems",
        "P1",
        ["mid", "senior", "staff"],
        "P0 at Meta/Netflix/Amazon-style product companies. The two-tower / retrieval-then-"
        "rank structure is the single most reused system-design pattern in these loops.",
        [
            "Candidate generation & retrieval", "Two-tower models", "Embeddings", "Ranking",
            "Re-ranking", "Cold start", "Exploration vs exploitation", "Feedback loops",
            "Popularity bias", "Diversity",
        ],
    ),
    (
        "Y",
        "Search & Information Retrieval",
        "P1",
        ["mid", "senior", "staff"],
        "Underpins both classical search design and every RAG question in Module M.",
        [
            "Inverted index", "BM25", "Dense retrieval", "ANN & HNSW", "Hybrid retrieval",
            "Learning to rank", "Reranking", "Query understanding", "Autocomplete",
            "Semantic search",
        ],
    ),
    (
        "Z",
        "ML Debugging",
        "P1",
        ["mid", "senior", "staff", "principal"],
        "Scenario-driven. Each item is a symptom; the answer is an ordered investigation, "
        "not a guess. This is the module that most reliably finds the boundary of "
        "someone's understanding.",
        [
            "Training/validation divergence", "Production accuracy drops",
            "Offline-online metric mismatch", "RAG retrieval failures",
            "Hallucination spikes", "Agent tool-call loops", "Latency regressions",
            "GPU under-utilization", "Train/serve skew", "Segment-level failures",
        ],
    ),
    (
        "AA",
        "ML Case Studies",
        "P1",
        ["mid", "senior", "staff", "principal"],
        "Realistic constraints only: millions of users, latency budgets, missing labels, "
        "privacy limits, drift. Toy cases teach nothing that survives an interview follow-up.",
        [
            "Fraud detection", "Recommendation", "Search & ranking", "Ads", "Moderation & spam",
            "Churn prediction", "Forecasting", "Anomaly detection", "Document AI & OCR",
            "Voice AI", "RAG products", "Agent products", "AI coding assistant",
            "Education / healthcare / financial AI",
        ],
    ),
    (
        "AB",
        "AI Product & Business Reasoning",
        "P1",
        ["senior", "staff", "principal"],
        "Tests engineering judgement rather than knowledge. The correct answer is often "
        "'don't use ML for this', and saying so is the signal.",
        [
            "Should this use ML at all?", "Should this use an LLM?", "Build vs buy",
            "RAG vs fine-tuning", "Small vs large model", "Accuracy vs latency",
            "Quality vs cost", "Automation vs human review",
        ],
    ),
    (
        "AC",
        "Research & Paper Understanding",
        "P2",
        ["senior", "staff", "principal"],
        "P0 for Applied Scientist and research-adjacent roles. Each paper is interrogated "
        "as problem → prior limitation → contribution → results → limitations.",
        [
            "Attention Is All You Need", "BERT", "GPT series", "ResNet", "Word2Vec", "CLIP",
            "LoRA & QLoRA", "RLHF (InstructGPT)", "DPO", "FlashAttention",
            "Mixture of Experts", "Reading a paper critically",
        ],
    ),
    (
        "AD",
        "Project Deep Dive",
        "P0",
        ["junior", "mid", "senior", "staff", "principal"],
        "The ML-depth round, and the easiest to under-prepare because it is your own work. "
        "Structured as an interviewer attack tree that keeps descending until you stop "
        "having answers.",
        [
            "Why this problem & why ML", "Baseline & alternatives", "Data & labelling",
            "Leakage", "Metric choice", "What failed & how you debugged it", "Deployment",
            "Latency & cost", "Monitoring & drift", "Rollback", "What you'd change",
            "Your hardest personal decision",
        ],
    ),
    (
        "AE",
        "Responsible AI & Security",
        "P2",
        ["mid", "senior", "staff", "principal"],
        "The security half (prompt injection, exfiltration, access control) has moved from "
        "P3 to genuinely expected for anyone building agents or RAG over private data.",
        [
            "Fairness & bias", "Privacy & PII", "Explainability", "Adversarial attacks",
            "Data poisoning", "Model extraction", "Membership inference", "Prompt injection",
            "Tool poisoning", "Access control", "AI governance", "Human oversight",
        ],
    ),
    (
        "AF",
        "Behavioral & Leadership",
        "P0",
        ["junior", "mid", "senior", "staff", "principal"],
        "Every loop has one, and at staff+ it is often the round that decides the level. "
        "STAR format, but the stories must carry technical depth, not just narrative.",
        [
            "Failed models & post-mortems", "Disagreement & influence",
            "Production incidents", "Technical trade-offs", "Insufficient data",
            "Cost reduction", "Cross-team influence", "Mentoring & enablement",
            "Ambiguity & prioritization",
        ],
    ),
]
