"""ML / GenAI / system-design interview-prep roadmap — real, curated
content in the same spirit as scripts/seed_data.py's PROBLEMS: every
summary is a plain, accurate restatement of well-established material
(not sourced from a single external document, so no citation is owed —
same footing as PATTERNS' cues), and every resource link is included only
where the URL is one this assistant is confident is real and correct.
Where that confidence doesn't exist, the resource is named with no URL
rather than guessing one (build prompt: never fabricate a URL).

Columns: (category, title, summary, resources, phase, order_index)
resources: list of (label, url | None)
"""

CONCEPTS: list[tuple[str, str, str, list[tuple[str, str | None]], str, int]] = [
    # math_stats
    (
        "math_stats",
        "Linear Algebra Essentials",
        "Vectors, matrices, eigenvalues/eigenvectors and the SVD — the "
        "language every ML model is written in, from a single logistic "
        "regression to attention weights in a transformer.",
        [("3Blue1Brown — Essence of Linear Algebra", "https://www.3blue1brown.com/topics/linear-algebra")],
        "foundation",
        1,
    ),
    (
        "math_stats",
        "Calculus for ML",
        "Gradients, partial derivatives and the chain rule — the mechanics "
        "behind backpropagation and every gradient-descent variant.",
        [("3Blue1Brown — Essence of Calculus", "https://www.3blue1brown.com/topics/calculus")],
        "foundation",
        2,
    ),
    (
        "math_stats",
        "Probability & Statistics Fundamentals",
        "Distributions, Bayes' theorem, expectation/variance, and hypothesis "
        "testing — the toolkit behind every metric, confidence interval and "
        "naive Bayes classifier you'll be asked about.",
        [("StatQuest with Josh Starmer (YouTube)", "https://www.youtube.com/@statquest")],
        "foundation",
        3,
    ),
    (
        "math_stats",
        "Information Theory Basics",
        "Entropy, cross-entropy and KL divergence — why cross-entropy loss "
        "is the default classification loss, and how KL divergence shows up "
        "in VAEs and distillation.",
        [],
        "foundation",
        4,
    ),
    (
        "math_stats",
        "Optimization for ML",
        "Convexity, gradient descent, SGD, momentum and Adam — what each "
        "optimizer actually changes about the descent path, and when plain "
        "SGD still beats Adam.",
        [("Stanford CS229 (Andrew Ng) — lecture notes", "https://cs229.stanford.edu/")],
        "foundation",
        5,
    ),
    (
        "math_stats",
        "A/B Testing & Experiment Design",
        "Randomization, power analysis, and common pitfalls (peeking, "
        "novelty effects, network interference) — the statistics questions "
        "that show up constantly in Meta/Amazon-style product-sense rounds.",
        [],
        "core",
        6,
    ),
    # classical_ml
    (
        "classical_ml",
        "Bias–Variance Tradeoff",
        "Why a model can fail by being too simple (bias) or too flexible "
        "(variance), and how that framing explains overfitting, "
        "regularization and ensembling in one picture.",
        [("An Introduction to Statistical Learning (free PDF)", "https://www.statlearning.com/")],
        "foundation",
        1,
    ),
    (
        "classical_ml",
        "Regularization",
        "L1 vs. L2 penalties, why L1 induces sparsity, and how early "
        "stopping and dropout generalize the same idea to deep nets.",
        [],
        "foundation",
        2,
    ),
    (
        "classical_ml",
        "Decision Trees & Ensembles",
        "Splitting criteria, bagging vs. boosting, and why gradient-boosted "
        "trees (XGBoost/LightGBM) still win most tabular-data competitions.",
        [("scikit-learn — Ensemble methods user guide", "https://scikit-learn.org/stable/modules/ensemble.html")],
        "core",
        3,
    ),
    (
        "classical_ml",
        "Support Vector Machines",
        "Maximum-margin classifiers, the kernel trick, and when an SVM is "
        "still a better choice than a neural net (small, high-dimensional "
        "datasets).",
        [],
        "core",
        4,
    ),
    (
        "classical_ml",
        "Clustering",
        "k-means, hierarchical clustering and DBSCAN — how each defines a "
        "cluster differently, and what that implies about the shapes of "
        "clusters each one can find.",
        [("scikit-learn — Clustering user guide", "https://scikit-learn.org/stable/modules/clustering.html")],
        "core",
        5,
    ),
    (
        "classical_ml",
        "Dimensionality Reduction",
        "PCA, t-SNE and UMAP — variance-preserving linear projection vs. "
        "neighbor-preserving nonlinear embeddings, and why you'd reach for "
        "each.",
        [],
        "core",
        6,
    ),
    (
        "classical_ml",
        "Model Evaluation Metrics",
        "Precision/recall/F1, ROC-AUC vs. PR-AUC, and why accuracy is the "
        "wrong metric on an imbalanced dataset — the single most-asked "
        "conceptual question in ML interviews.",
        [],
        "foundation",
        7,
    ),
    (
        "classical_ml",
        "Feature Engineering & Selection",
        "Encoding categoricals, handling missing data, and selecting "
        "features by mutual information or model-based importance — still "
        "the highest-leverage lever on most real tabular problems.",
        [],
        "core",
        8,
    ),
    # deep_learning
    (
        "deep_learning",
        "Neural Network Fundamentals",
        "Forward pass, backpropagation and the vanishing/exploding gradient "
        "problem, built up from a single neuron rather than taken as a "
        "black box.",
        [("Andrej Karpathy — Neural Networks: Zero to Hero", "https://karpathy.ai/zero-to-hero.html")],
        "foundation",
        1,
    ),
    (
        "deep_learning",
        "CNNs for Computer Vision",
        "Convolution, pooling and receptive fields — why weight-sharing "
        "makes CNNs the right inductive bias for images.",
        [("Stanford CS231n", "http://cs231n.stanford.edu/")],
        "core",
        2,
    ),
    (
        "deep_learning",
        "RNNs, LSTMs & Sequence Modeling",
        "Why vanilla RNNs struggle with long sequences, and how gating in "
        "LSTMs/GRUs addresses it — the architecture attention was built to "
        "replace.",
        [],
        "core",
        3,
    ),
    (
        "deep_learning",
        "The Transformer & Self-Attention",
        "Query/key/value attention, multi-head attention and positional "
        "encoding — the single architecture behind almost every modern "
        "LLM.",
        [
            ("Attention Is All You Need (Vaswani et al., 2017)", "https://arxiv.org/abs/1706.03762"),
            ("The Illustrated Transformer — Jay Alammar", "https://jalammar.github.io/illustrated-transformer/"),
        ],
        "core",
        4,
    ),
    (
        "deep_learning",
        "Optimization & Regularization in Deep Nets",
        "Batch norm, dropout, weight decay and learning-rate schedules — "
        "the practical levers that make a deep net actually converge.",
        [],
        "core",
        5,
    ),
    (
        "deep_learning",
        "Transfer Learning & Fine-Tuning",
        "Why pretraining on a large corpus and fine-tuning on a small one "
        "usually beats training from scratch, and how that same idea scales "
        "up to LLM fine-tuning.",
        [],
        "core",
        6,
    ),
    (
        "deep_learning",
        "Generative Models",
        "GANs, VAEs and diffusion models — three different ways to learn a "
        "data distribution well enough to sample new, realistic examples "
        "from it.",
        [],
        "advanced",
        7,
    ),
    (
        "deep_learning",
        "NLP with Deep Learning",
        "Word embeddings, seq2seq and how the field's architecture choices "
        "evolved from RNNs to transformers.",
        [("Stanford CS224n", "https://web.stanford.edu/class/cs224n/")],
        "core",
        8,
    ),
    # llm_genai
    (
        "llm_genai",
        "Tokenization & Embeddings",
        "Byte-pair encoding and subword tokenization, and why a model's "
        "context window is measured in tokens, not words or characters.",
        [("Hugging Face NLP Course", "https://huggingface.co/learn/nlp-course")],
        "foundation",
        1,
    ),
    (
        "llm_genai",
        "LLM Pretraining, Fine-Tuning & RLHF",
        "Next-token pretraining, supervised fine-tuning (instruction "
        "tuning), and reinforcement learning from human feedback — the "
        "three stages behind a model like ChatGPT, and what each one is "
        "actually optimizing.",
        [],
        "core",
        2,
    ),
    (
        "llm_genai",
        "Prompt Engineering",
        "Few-shot prompting, chain-of-thought, and ReAct-style "
        "reasoning-then-acting — techniques that change model behavior "
        "without touching a single weight.",
        [("DeepLearning.AI short courses", "https://www.deeplearning.ai/short-courses/")],
        "core",
        3,
    ),
    (
        "llm_genai",
        "Retrieval-Augmented Generation (RAG)",
        "Grounding a model's answers in a retrieved external knowledge base "
        "at inference time — cheaper to keep current and easier to audit "
        "than re-fine-tuning every time the underlying knowledge changes.",
        [("Lewis et al., 2020 — Retrieval-Augmented Generation", "https://arxiv.org/abs/2005.11401")],
        "core",
        4,
    ),
    (
        "llm_genai",
        "Vector Databases & Embedding Search",
        "Approximate nearest-neighbor search (HNSW, IVF) over embeddings — "
        "the retrieval half of every RAG system.",
        [],
        "core",
        5,
    ),
    (
        "llm_genai",
        "Agentic Systems & Tool Use",
        "Function calling, ReAct-style planning loops, and multi-agent "
        "orchestration — how an LLM goes from answering questions to "
        "taking actions.",
        [("LangChain documentation", "https://python.langchain.com/")],
        "advanced",
        6,
    ),
    (
        "llm_genai",
        "LLM Evaluation & Hallucination Mitigation",
        "Why no single technique is sufficient alone: grounding via RAG, "
        "output guardrails, and confidence scoring to flag uncertain "
        "answers for review are usually combined, not chosen between.",
        [],
        "advanced",
        7,
    ),
    # mlops
    (
        "mlops",
        "The ML System Lifecycle",
        "Data collection, training, deployment and monitoring as one loop, "
        "not four separate projects — most production ML failures happen "
        "at the seams between these stages, not inside the model.",
        [("Made With ML", "https://madewithml.com/")],
        "foundation",
        1,
    ),
    (
        "mlops",
        "Feature Stores & Data Pipelines",
        "Why training/serving skew (a feature computed differently offline "
        "vs. online) is one of the most common causes of a model that "
        "works in notebooks but fails in production.",
        [],
        "core",
        2,
    ),
    (
        "mlops",
        "Model Serving & Deployment Patterns",
        "Batch vs. online inference, canary releases and shadow "
        "deployments — how a new model actually reaches production "
        "traffic safely.",
        [],
        "core",
        3,
    ),
    (
        "mlops",
        "Model Monitoring & Drift Detection",
        "Data drift vs. concept drift, and why a model's accuracy can "
        "degrade in production with no code change at all — the "
        "underlying data distribution simply moved.",
        [],
        "core",
        4,
    ),
    (
        "mlops",
        "Reproducibility & Experiment Tracking",
        "Versioning data, code and model artifacts together so a result "
        "from three months ago can still be reproduced exactly.",
        [],
        "core",
        5,
    ),
    (
        "mlops",
        "Scaling Training",
        "Data vs. model parallelism, mixed-precision training, and why "
        "large-model training is often bottlenecked on communication "
        "between GPUs, not compute.",
        [("Full Stack Deep Learning", "https://fullstackdeeplearning.com/")],
        "advanced",
        6,
    ),
    (
        "mlops",
        "Responsible AI",
        "Fairness metrics, bias sources in training data, and "
        "explainability techniques (SHAP, LIME) — increasingly a real "
        "interview topic at companies deploying ML at consumer scale.",
        [],
        "advanced",
        7,
    ),
    # ml_system_design
    (
        "ml_system_design",
        "Framing an ML System Design Interview",
        "Clarifying the objective, constraints and success metric before "
        "any architecture — the single biggest differentiator between "
        "strong and weak answers in this round.",
        [],
        "foundation",
        1,
    ),
    (
        "ml_system_design",
        "Recommendation Systems Design",
        "The two-stage pattern (candidate generation, then ranking) behind "
        "most large-scale recommenders — why you never rank the entire "
        "catalog directly.",
        [],
        "core",
        2,
    ),
    (
        "ml_system_design",
        "Search & Ranking Systems",
        "Query understanding, retrieval, and learning-to-rank — the same "
        "two-stage shape as recommendations, applied to a query instead of "
        "a user profile.",
        [],
        "core",
        3,
    ),
    (
        "ml_system_design",
        "Feed & Ads Ranking",
        "Multi-objective ranking (engagement vs. revenue vs. quality) and "
        "why these systems optimize a blended score, not one metric — the "
        "shape of a Meta-style feed-ranking interview.",
        [],
        "core",
        4,
    ),
    (
        "ml_system_design",
        "Fraud & Anomaly Detection Systems",
        "Extreme class imbalance, adversarial adaptation (fraud patterns "
        "shift to evade the model), and why precision/recall tradeoffs "
        "dominate this design space.",
        [],
        "core",
        5,
    ),
    (
        "ml_system_design",
        "Designing a RAG-Based GenAI Product",
        "Chunking strategy, retrieval quality, and evaluation for a "
        "chatbot answering questions over private/proprietary documents — "
        "the GenAI-era version of this interview round.",
        [],
        "advanced",
        6,
    ),
    (
        "ml_system_design",
        "Online vs. Offline Evaluation",
        "Why an offline metric improvement doesn't guarantee an online win "
        "— and how A/B testing, interleaving, and holdout groups close "
        "that gap.",
        [],
        "core",
        7,
    ),
    (
        "ml_system_design",
        "System Design Fundamentals for ML Interviews",
        "Load balancing, caching, sharding and consistency — the "
        "non-ML systems vocabulary an ML system design round still "
        "assumes you have.",
        [("The System Design Primer (GitHub)", "https://github.com/donnemartin/system-design-primer")],
        "foundation",
        8,
    ),
]
