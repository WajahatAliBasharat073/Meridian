"""The knowledge model: what depends on what.

This is the part of the curriculum rebuild that cannot be generated. It is
a judgement about which ideas genuinely require which other ideas, and it
is authored by hand, reviewed, and committed as data. Everything else --
the frontier engine, the daily picker, the validation tests -- is plumbing
that reads this file.

Two axes, kept apart on purpose (see CURRICULUM_AUDIT.md section 4):

  KNOWLEDGE  phase -> topic -> prerequisites.   Drives sequencing.
  FORMAT     how a question tests you.          Drives presentation.

Roughly 30% of the existing bank is format, not knowledge: case studies,
ML coding, behavioural, project deep dives. Today those compete for the
same daily slots as "What is linear regression?", which is why a learner
with no progress is served a Google case study on day one. Here they get a
knowledge topic of their own so they can be gated by the material they
actually exercise -- and the few that are genuinely topic-free
(behavioural, project deep dive) are marked ungated and never blocked.

Prerequisites are AND: a topic unlocks only when *all* of them are
mastered. Keep them minimal. Every extra edge is a wall the learner hits,
and an over-gated curriculum gets overridden, which teaches nothing.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Topic:
    slug: str
    name: str
    phase: int
    prereqs: tuple[str, ...] = ()
    # Ungated topics are always eligible: they test transferable skill
    # rather than curriculum knowledge, so blocking them teaches nothing.
    # Behavioural questions do not need linear regression.
    gated: bool = True
    note: str = ""


# --------------------------------------------------------------------------
# Phase names, for display and for the validation rule that a topic's phase
# is never lower than its prerequisites' (V4).
# --------------------------------------------------------------------------
PHASES: dict[int, str] = {
    0: "Foundations",
    1: "Classical Machine Learning",
    2: "Deep Learning",
    3: "NLP / LLM Foundations",
    4: "Modern LLM / Generative AI",
    5: "AI Systems / Agents / Advanced AI",
}

# Ordering *within* a phase comes from `order_index`, derived from position
# in TOPICS below. Six phases is the public model; the finer sequence lives
# in the prerequisite edges, which is where it belongs -- a phase is a
# coarse label for "roughly where am I", not the scheduling unit.


TOPICS: list[Topic] = [
    Topic("python_for_ml", "Python for ML", 0,
          note="Functions, classes, iterators, generators, exceptions, type hints."),
    Topic("numpy_vectorization", "NumPy & Vectorization", 0, ("python_for_ml",),
          note="Arrays, broadcasting, why loops lose to vectorised operations."),
    Topic("pandas_data", "Pandas & Data Manipulation", 0, ("python_for_ml",)),
    Topic("linear_algebra", "Linear Algebra", 0,
          note="Vectors, matrices, matrix operations, eigen-decomposition, SVD."),
    Topic("probability", "Probability", 0,
          note="Conditional probability, Bayes, distributions, expectation, variance."),
    Topic("statistics", "Statistics & Inference", 0, ("probability",),
          note="Sampling, confidence intervals, hypothesis testing, p-values."),
    Topic("calculus_optimization", "Calculus & Optimization Basics", 0,
          note="Derivatives, partial derivatives, chain rule, convexity, minima."),

    Topic("what_is_ml", "What is Machine Learning", 1,
          note="Supervised vs unsupervised, features, labels, the learning setup."),
    Topic("train_val_test", "Train / Validation / Test", 1, ("what_is_ml",)),
    Topic("loss_functions", "Loss & Objective Functions", 1,
          ("what_is_ml", "calculus_optimization")),
    Topic("gradient_descent", "Gradient Descent", 1,
          ("loss_functions", "calculus_optimization"),
          note="Learning rate, convergence, batch vs stochastic."),
    Topic("bias_variance", "Overfitting, Underfitting, Bias & Variance", 1,
          ("train_val_test",)),
    Topic("regularization_concepts", "Regularization (concept)", 1, ("bias_variance",)),
    Topic("data_preprocessing", "Data Preprocessing", 1, ("what_is_ml",)),
    Topic("feature_engineering", "Feature Engineering", 1, ("data_preprocessing",)),

    Topic("linear_regression", "Linear Regression", 1,
          ("gradient_descent", "loss_functions", "linear_algebra")),
    Topic("regression_metrics", "Regression Metrics", 1, ("linear_regression",),
          note="MSE, MAE, RMSE, R-squared, and when each misleads."),
    Topic("regression_assumptions", "Regression Assumptions & Diagnostics", 1,
          ("linear_regression",),
          note="Linearity, homoscedasticity, multicollinearity, residual analysis."),
    Topic("ridge_lasso", "Ridge, Lasso & Elastic Net", 1,
          ("linear_regression", "regularization_concepts")),

    Topic("classification_fundamentals", "Classification Fundamentals", 1, ("what_is_ml",)),
    Topic("logistic_regression", "Logistic Regression", 1,
          ("linear_regression", "classification_fundamentals"),
          note="Sigmoid, logits, decision boundaries, binary cross-entropy."),
    Topic("classification_metrics", "Classification Metrics", 1,
          ("classification_fundamentals",),
          note="Confusion matrix, accuracy, precision, recall, F1."),
    Topic("roc_thresholds", "ROC, PR Curves & Thresholds", 1, ("classification_metrics",)),
    Topic("calibration", "Probability Calibration", 1, ("roc_thresholds",)),
    Topic("knn", "k-Nearest Neighbours", 1, ("classification_fundamentals",)),
    Topic("naive_bayes", "Naive Bayes", 1, ("classification_fundamentals", "probability")),
    Topic("decision_trees", "Decision Trees", 1, ("classification_fundamentals",)),
    Topic("bagging_random_forest", "Bagging & Random Forests", 1, ("decision_trees",)),
    Topic("boosting", "Boosting (GBM, XGBoost, LightGBM)", 1,
          ("decision_trees", "gradient_descent")),
    Topic("svm", "SVM, Margins & Kernels", 1,
          ("classification_fundamentals", "linear_algebra")),

    Topic("recsys_fundamentals", "Recommendation Fundamentals", 1,
          ("what_is_ml", "linear_algebra"),
          note="Collaborative filtering, matrix factorisation, cold start. Split out because 'what is collaborative filtering?' was reachable only behind P5 system design."),
    Topic("clustering", "Clustering & k-Means", 1, ("what_is_ml", "linear_algebra"),
          note="Choosing k, initialisation, evaluating a clustering."),
    Topic("hierarchical_dbscan", "Hierarchical Clustering & DBSCAN", 1, ("clustering",)),
    Topic("pca", "PCA & Dimensionality Reduction", 1, ("linear_algebra", "clustering")),
    Topic("anomaly_detection", "Anomaly Detection", 1, ("clustering",)),

    Topic("cross_validation", "Cross-Validation", 1, ("train_val_test",)),
    Topic("data_leakage", "Data Leakage", 1, ("cross_validation",)),
    Topic("class_imbalance", "Class Imbalance", 1, ("classification_metrics",)),
    Topic("feature_selection", "Feature Selection", 1, ("feature_engineering", "ridge_lasso")),
    Topic("hyperparameter_optimization", "Hyperparameter Optimization", 1,
          ("cross_validation",)),
    Topic("model_selection", "Model Selection", 1, ("cross_validation", "bias_variance")),
    Topic("error_analysis", "Error Analysis & Model Debugging", 1,
          ("classification_metrics", "regression_metrics")),
    Topic("interpretability", "Interpretability", 1, ("model_selection",)),
    Topic("distribution_shift", "Distribution Shift & Robustness", 1, ("error_analysis",)),
    Topic("experimentation", "Experimentation & A/B Testing", 1, ("statistics",)),
    Topic("time_series", "Time Series", 1, ("regression_metrics", "statistics"),
          note="Trend, stationarity, classic forecasting models, and why trees "
          "struggle with extrapolation. Added because 7 questions on this had no "
          "topic to land on and were falling through to a linear-regression default."),

    Topic("neural_networks", "Perceptron, MLP & Neural Network Intuition", 2,
          ("logistic_regression", "gradient_descent")),
    Topic("activations", "Activation Functions", 2, ("neural_networks",)),
    Topic("backpropagation", "Backpropagation & Computational Graphs", 2,
          ("neural_networks", "calculus_optimization")),
    Topic("dl_optimization", "DL Optimizers, Schedules & Initialization", 2,
          ("backpropagation",)),
    Topic("dl_regularization", "Dropout, Batch & Layer Normalization", 2,
          ("backpropagation", "regularization_concepts")),
    Topic("training_stability", "Training Stability", 2, ("dl_optimization",),
          note="Vanishing and exploding gradients, and what actually fixes them."),

    Topic("cnn", "CNNs, Convolution & Pooling", 2, ("backpropagation", "dl_regularization")),
    Topic("rnn", "RNNs, LSTM & GRU", 2, ("backpropagation", "training_stability")),
    Topic("seq2seq", "Sequence-to-Sequence", 2, ("rnn",)),
    Topic("attention", "Attention & Self-Attention", 2, ("seq2seq",),
          note="The gate everything modern sits behind."),
    Topic("transformers", "Transformer Architecture", 2, ("attention",),
          note="Multi-head attention, positional encoding, encoder/decoder."),

    Topic("text_preprocessing", "Text Preprocessing & Tokenization", 3, ("what_is_ml",)),
    Topic("bow_tfidf", "Bag of Words & TF-IDF", 3, ("text_preprocessing",)),
    Topic("word_embeddings", "Word Embeddings", 3, ("bow_tfidf", "neural_networks")),
    Topic("nlp_tasks", "NLP Tasks & Evaluation", 3, ("word_embeddings", "transformers")),

    Topic("image_representation", "Image Representation", 2, ("cnn",)),
    Topic("image_classification", "Image Classification & Transfer Learning", 2,
          ("image_representation",)),
    Topic("detection_segmentation", "Object Detection & Segmentation", 2,
          ("image_classification",)),
    Topic("vision_transformers", "Vision Transformers", 2,
          ("image_classification", "transformers")),

    Topic("llm_architecture", "LLM Architecture", 3, ("transformers",),
          note="Decoder-only, next-token prediction, context windows."),
    Topic("pretraining_finetuning", "Pretraining & Fine-Tuning", 3, ("llm_architecture",)),
    Topic("instruction_tuning", "Instruction Tuning, RLHF & Preference Optimization", 3,
          ("pretraining_finetuning",)),
    Topic("llm_inference", "LLM Inference & Decoding", 3, ("llm_architecture",),
          note="Temperature, top-k, top-p, KV cache, serving cost."),
    Topic("llm_evaluation", "LLM Evaluation", 3, ("llm_inference",)),

    Topic("information_retrieval", "Information Retrieval & BM25", 4, ("bow_tfidf",)),
    Topic("embeddings", "Embeddings & Similarity", 4, ("word_embeddings",)),
    Topic("vector_search", "Vector Search & Indexes", 4, ("embeddings",),
          note="HNSW, IVF, the recall/latency trade-off."),
    Topic("chunking", "Chunking & Context Construction", 4, ("embeddings", "llm_architecture")),
    Topic("hybrid_retrieval", "Hybrid Retrieval & Reranking", 4,
          ("information_retrieval", "vector_search")),
    Topic("rag_architecture", "RAG Architecture", 4,
          ("chunking", "hybrid_retrieval", "llm_inference")),
    Topic("rag_evaluation", "RAG Evaluation & Failure Analysis", 4,
          ("rag_architecture", "llm_evaluation")),

    Topic("tool_calling", "Tool Calling & Structured Outputs", 5, ("llm_inference",)),
    Topic("agent_loop", "Agent Loop, State & Memory", 5, ("tool_calling",)),
    Topic("planning_reflection", "Planning & Reflection", 5, ("agent_loop",)),
    Topic("agent_evaluation", "Agent Evaluation & Reliability", 5,
          ("agent_loop", "llm_evaluation")),
    Topic("multi_agent", "Multi-Agent Systems", 5, ("planning_reflection",)),

    Topic("context_engineering", "Context Engineering", 5,
          ("chunking", "agent_loop"),
          note="Context selection, compression, long-context management."),
    Topic("ai_protocols", "MCP, A2A & Tool Interoperability", 5,
          ("context_engineering", "multi_agent")),
    Topic("prompt_security", "Prompt Injection & AI Security", 5, ("tool_calling",)),

    Topic("multimodal_models", "Vision-Language & Audio-Language Models", 4,
          ("transformers", "image_classification")),
    Topic("multimodal_rag", "Multimodal RAG & Agents", 4,
          ("multimodal_models", "rag_architecture")),

    Topic("data_pipelines", "Data & Feature Pipelines", 5, ("feature_engineering",)),
    Topic("training_pipelines", "Training Pipelines & Experiment Tracking", 5,
          ("data_pipelines", "model_selection")),
    Topic("model_serving", "Model Serving & Inference", 5, ("training_pipelines",),
          note="Batch vs online, latency, throughput."),
    Topic("monitoring_drift", "Monitoring, Drift & Retraining", 5,
          ("model_serving", "distribution_shift")),
    Topic("ml_infrastructure", "ML & GPU Infrastructure, Cost", 5, ("model_serving",)),
    Topic("responsible_ai", "Responsible AI & Security", 5, ("monitoring_drift",)),

    Topic("ml_system_design_process", "ML System Design: the Method", 5,
          ("monitoring_drift", "model_selection"),
          note="Requirements, data, architecture, evaluation, scaling, failure modes."),
    Topic("recsys_design", "Recommendation Systems", 5,
          ("ml_system_design_process", "embeddings", "recsys_fundamentals")),
    Topic("search_ranking_design", "Search & Ranking Systems", 5,
          ("ml_system_design_process", "information_retrieval")),
    Topic("classic_ml_system_design", "Fraud, Forecasting & Classification Systems", 5,
          ("ml_system_design_process", "class_imbalance")),
    Topic("genai_system_design", "GenAI System Design", 5,
          ("ml_system_design_process", "llm_inference")),
    Topic("rag_system_design", "RAG System Design", 5,
          ("genai_system_design", "rag_evaluation")),
    Topic("agent_system_design", "Agent System Design", 5,
          ("genai_system_design", "agent_evaluation")),

    # Ungated: transferable skill, not curriculum knowledge. Gating these
    # would mean refusing to let someone rehearse their own project story
    # until they had mastered PCA.
    Topic("dsa_coding", "Data Structures & Algorithms", 0, (), gated=False,
          note="Parallel track; see the DSA curriculum, which has its own gate."),
    Topic("behavioral", "Behavioral & Leadership", 0, (), gated=False),
    Topic("project_deep_dive", "Project Deep Dive", 0, (), gated=False),
    Topic("product_reasoning", "AI Product & Business Reasoning", 5,
          ("ml_system_design_process",)),
    Topic("research_reading", "Research & Paper Understanding", 3, ("transformers",)),
]


TOPIC_BY_SLUG: dict[str, Topic] = {t.slug: t for t in TOPICS}


# --------------------------------------------------------------------------
# Classification: existing question -> topic.
#
# Driven by the bank's own (module_code, submodule) labels wherever they are
# specific enough, then by title keywords for the coarse buckets -- module D
# alone has 62 questions labelled only "Regression" and 19 only
# "Classification". Anything that falls through lands on the module default
# and is flagged low-confidence for review rather than being guessed at.
# --------------------------------------------------------------------------

# (module, submodule) -> topic. Exact match, highest confidence.
SUBMODULE_MAP: dict[tuple[str, str], str] = {
    ("A", "Complexity analysis"): "dsa_coding",
    ("A", "SQL & data manipulation"): "pandas_data",
    ("C", "Statistics & inference"): "statistics",
    ("C", "Probability"): "probability",
    ("C", "Optimization"): "calculus_optimization",
    ("C", "Linear algebra"): "linear_algebra",
    ("C", "Calculus & gradients"): "calculus_optimization",
    ("D", "Ensembles (bagging/boosting)"): "bagging_random_forest",
    ("D", "Clustering"): "clustering",
    ("D", "Decision trees"): "decision_trees",
    ("D", "Dimensionality reduction"): "pca",
    ("E", "Overfitting & regularization"): "bias_variance",
    ("E", "Cross-validation"): "cross_validation",
    ("E", "Feature selection"): "feature_selection",
    ("F", "GenAI evaluation"): "llm_evaluation",
    ("F", "Agentic evaluation"): "agent_evaluation",
    ("H", "Neural network basics"): "neural_networks",
    ("H", "Optimizers & schedules"): "dl_optimization",
    ("I", "CNN architectures"): "cnn",
    ("J", "TF-IDF & sparse features"): "bow_tfidf",
    ("K", "Q/K/V & scaled dot-product"): "attention",
    ("K", "KV cache"): "llm_inference",
    ("K", "Attention complexity"): "attention",
    ("K", "Positional encoding & RoPE"): "transformers",
    ("K", "MHA / MQA / GQA"): "attention",
    ("K", "FlashAttention"): "attention",
    ("L", "Instruction tuning & SFT"): "instruction_tuning",
    ("L", "Inference & decoding"): "llm_inference",
    ("M", "Retrieval evaluation"): "rag_evaluation",
    ("M", "Parsing & chunking"): "chunking",
    ("M", "Vector indexes (HNSW/IVF)"): "vector_search",
    ("M", "Query rewriting & HyDE"): "hybrid_retrieval",
    ("M", "Dense vs BM25"): "hybrid_retrieval",
    ("M", "Hybrid search"): "hybrid_retrieval",
    ("M", "Reranking"): "hybrid_retrieval",
    ("N", "Tool & function calling"): "tool_calling",
    ("N", "Long-running agents"): "agent_loop",
    ("O", "Context selection"): "context_engineering",
    ("P", "MCP clients & servers"): "ai_protocols",
    ("P", "Prompt injection"): "prompt_security",
    ("Q", "Multimodal embeddings"): "multimodal_models",
    ("Q", "Vision-language models"): "multimodal_models",
    ("Q", "Multimodal RAG"): "multimodal_rag",
    ("Q", "OCR & document intelligence"): "multimodal_models",
    ("Q", "Audio-language models"): "multimodal_models",
    ("R", "Search & ranking"): "search_ranking_design",
    ("R", "Recommendation systems"): "recsys_design",
    ("R", "Fraud, spam & moderation"): "classic_ml_system_design",
    ("R", "Ads & newsfeed"): "recsys_design",
    ("R", "Architecture & MVP logic"): "ml_system_design_process",
    ("S", "Enterprise RAG assistant"): "rag_system_design",
    ("S", "LLM inference & serving platform"): "genai_system_design",
    ("T", "Agent harness & orchestrator"): "agent_system_design",
    ("V", "LLM observability"): "monitoring_drift",
    ("W", "Inference optimization"): "ml_infrastructure",
    ("X", "Ranking"): "recsys_design",
    ("Y", "Learning to rank"): "search_ranking_design",
    ("Z", "Train/serve skew"): "monitoring_drift",
    ("Z", "Training/validation divergence"): "error_analysis",
    ("Z", "Production accuracy drops"): "monitoring_drift",
    ("Z", "Offline-online metric mismatch"): "error_analysis",
    ("Z", "RAG retrieval failures"): "rag_evaluation",
    ("AA", "Recommendation"): "recsys_design",
    ("AA", "Document AI & OCR"): "multimodal_models",
    ("AA", "Search & ranking"): "search_ranking_design",
    ("AA", "Fraud detection"): "classic_ml_system_design",
    ("AA", "Forecasting"): "classic_ml_system_design",
    ("AA", "Anomaly detection"): "anomaly_detection",
    ("AA", "RAG products"): "rag_system_design",
    ("B", "Classic ML primitives"): "linear_regression",
    ("B", "Language-model mechanics"): "attention",
    ("B", "GenAI primitives"): "embeddings",
    ("B", "Agentic control-plane coding"): "agent_loop",
}

# Modules whose submodule labels are coarse buckets rather than topics, so
# a title keyword is the better signal. Module B ("ML coding") groups 43
# questions into four buckets -- "Language-model mechanics" alone covers
# TF-IDF, byte-pair encoding, attention masks, sampling and the KV cache --
# while every title states exactly what it implements. Trusting the
# submodule there filed TF-IDF under attention.
KEYWORD_FIRST_MODULES: frozenset[str] = frozenset({"B"})

# Markers so unambiguous that no submodule label should outrank them. The
# bank contains a tokenization question filed under "Q/K/V & scaled
# dot-product"; the label is simply wrong, and trusting it put tokenizers
# in Deep Learning. Keep this list short -- it exists for clear source
# errors, not for tuning.
OVERRIDE_KEYWORDS: list[tuple[str, str]] = [
    (r"\btokeniz|\btokenis|\bwordpiece\b|\bbyte.?pair\b|\bbpe\b", "text_preprocessing"),
    (r"\bbag of words\b|\btf.?idf\b", "bow_tfidf"),
]

# Rules specific enough to outrank a submodule label, checked before it.
#
# Every one of these was added after a real misclassification, and in each
# case the *submodule* was the thing that was wrong: "cold start" filed
# under ranking-system design, "collaborative filtering" under CNNs,
# "precision at k" under confusion-matrix metrics, "sigmoid" under
# logistic regression instead of activation functions. A rule this narrow
# is better evidence than a bucket name, so it wins.
SPECIFIC_RULES: list[tuple[str, str]] = [
    # Domain-disambiguating: a word that means different things in
    # different subfields, which the generic rules below would otherwise
    # claim for whichever field they happen to list first.
    #   "recall"/"precision" - IR@k vs the confusion-matrix metric
    #   "filter"             - collaborative filtering vs a conv filter
    #   "sigmoid"            - an activation function vs logistic regression
    #   "momentum"/"adam"    - a DL optimiser, not classical gradient descent
    (r"\bcollaborative filtering\b|\bmatrix factori[sz]|\bcold start\b|\bimplicit feedback\b",
     "recsys_fundamentals"),
    (r"\b(precision|recall|ndcg|map|mrr)\s*@\s*k\b|\bat k\b|\bmean average precision\b",
     "information_retrieval"),
    (r"\bhnsw\b|\bivf\b|\bfaiss\b|\bann index\b|\bvector (database|index)\b", "vector_search"),
    (r"\brelu\b|\bgelu\b|\bleaky.?relu\b|\bsoftplus\b|\btanh\b|\bsigmoid\b|\bactivation function",
     "activations"),
    (r"\badam\b|\brmsprop\b|\badagrad\b|\bmomentum\b|\blr schedul|\blearning.?rate schedul",
     "dl_optimization"),

    # ML-coding titles name their algorithm outright, so they are specific
    # in the same sense: "Implement: TF-IDF" is not an attention question
    # whatever coarse bucket its submodule label happens to file it in.
    (r"\bkv cache\b|\bpaged attention\b", "llm_inference"),
    (r"\btemperature\b.*\btop.?[kp]\b|\btop.?[kp]\b.*sampling|\bnucleus sampling\b",
     "llm_inference"),
    (r"\blora\b|\bqlora\b|\badapter\b", "pretraining_finetuning"),
    (r"\bdirect preference optimization\b|\bdpo\b|\bppo\b|\brlhf\b", "instruction_tuning"),
    (r"\bcontrastive loss\b|\bclip\b|\bsiamese\b", "embeddings"),
    (r"\bcosine top.?k\b|\btop.?k retrieval\b|\bvector recall\b", "vector_search"),
    (r"\bbyte.?pair\b|\bbpe\b|\bwordpiece\b|\bsentencepiece\b", "text_preprocessing"),
    (r"\bcausal (attention )?mask\b|\battention mask\b|\bscaled dot.?product\b", "attention"),
    (r"\bconversation memory\b|\bsliding.?window .*memory\b|\bscratchpad\b", "agent_loop"),
]

# Generic bucket rules, consulted only when SUBMODULE_MAP has nothing.
# Deliberately broad, and deliberately subordinate: "classification"
# appears in questions that are not about classification metrics, which is
# exactly why the disambiguating rules above must run first.
KEYWORD_RULES: list[tuple[str, str]] = [
    # regression, splitting module D's 62 "Regression" questions
    (r"\b(ridge|lasso|elastic ?net|l1|l2 regulari)", "ridge_lasso"),
    (r"\b(multicollinear|heteroscedastic|homoscedastic|residual|assumption)", "regression_assumptions"),
    (r"\b(r squared|r-squared|rmse|\bmae\b|\bmse\b|adjusted r)", "regression_metrics"),
    (r"\blogistic regression\b|\blog.?odds\b|\blogit\b", "logistic_regression"),
    (r"\blinear regression|ordinary least squares|\bols\b|normal equation", "linear_regression"),
    # classification
    (r"\b(precision|recall|f1|confusion matrix)", "classification_metrics"),
    (r"\b(roc|auc|pr curve|threshold)", "roc_thresholds"),
    (r"\bcalibrat", "calibration"),
    (r"\bimbalance|smote|class weight|resampl", "class_imbalance"),
    (r"\b(svm|support vector|kernel trick|margin)", "svm"),
    (r"\b(xgboost|lightgbm|gradient boost|adaboost|\bboost)", "boosting"),
    (r"\brandom forest|bagging|bootstrap aggreg", "bagging_random_forest"),
    (r"\bdecision tree|gini|information gain|entropy split", "decision_trees"),
    (r"\bnaive bayes", "naive_bayes"),
    (r"\bk-?nn|nearest neighbou?r", "knn"),
    # unsupervised
    (r"\bk-?means|silhouette|elbow method|cluster", "clustering"),
    (r"\bdbscan|hierarchical cluster", "hierarchical_dbscan"),
    (r"\bpca|principal component|dimensionality reduc|t-?sne|umap", "pca"),
    (r"\banomal|outlier detect", "anomaly_detection"),
    # foundations
    (r"\boverfit|underfit|bias.{0,10}variance", "bias_variance"),
    (r"\bcross.?validat|k-?fold", "cross_validation"),
    (r"\bleakage", "data_leakage"),
    (r"\bgradient descent\b|\blearning rate\b|\bsgd\b", "gradient_descent"),
    (r"\bloss function|cost function|cross.?entropy|objective function", "loss_functions"),
    (r"\bfeature engineer|feature scal|normali[sz]ation of features", "feature_engineering"),
    (r"\bfeature select", "feature_selection"),
    (r"\bhyperparameter|grid search|random search|bayesian opt", "hyperparameter_optimization"),
    (r"\btrain.{0,3}(valid|test)|holdout|data split", "train_val_test"),
    (r"\bsupervised|unsupervised|what is machine learning", "what_is_ml"),
    (r"\bpreprocess|missing value|imputation|encoding categor", "data_preprocessing"),
    (r"\bdrift|distribution shift|covariate shift", "distribution_shift"),
    (r"\binterpretab|shap|lime|feature importance", "interpretability"),
    (r"\bdebug|error analysis|why is my model", "error_analysis"),
    # deep learning
    (r"\bbackprop|computational graph|chain rule", "backpropagation"),
    (r"\bactivation|relu|gelu|tanh\b|softmax", "activations"),
    (r"\bdropout|batch ?norm|layer ?norm", "dl_regularization"),
    (r"\bvanishing|exploding gradient|gradient clip", "training_stability"),
    (r"\bcnn\b|\bconvolution|\bpooling\b|\bfeature map\b|\bkernel size\b", "cnn"),
    (r"\b(rnn|lstm|gru|recurrent)", "rnn"),
    (r"\bseq2seq|sequence.to.sequence|encoder.decoder", "seq2seq"),
    (r"\bself.?attention|attention mechanism|multi.?head", "attention"),
    (r"\btransformer", "transformers"),
    (r"\bperceptron|\bmlp\b|neural network|feed.?forward", "neural_networks"),
    # nlp / llm
    (r"\btoken(iz|is)|\bbpe\b|wordpiece|sentencepiece", "text_preprocessing"),
    (r"\btf.?idf|bag of words", "bow_tfidf"),
    (r"\bword2vec|glove|word embedding", "word_embeddings"),
    (r"\b(peft|lora|qlora|fine.?tun)", "pretraining_finetuning"),
    (r"\b(rlhf|dpo|instruction tun|preference optim|sft\b)", "instruction_tuning"),
    (r"\btemperature|top.?k|top.?p|beam search|decoding|kv cache|context window",
     "llm_inference"),
    (r"\bhallucinat|llm eval|benchmark.{0,10}llm", "llm_evaluation"),
    (r"\b(what is an? llm|foundation model|pretrain|scaling law|mixture of expert)",
     "llm_architecture"),
    # retrieval
    (r"\bbm25|inverted index|sparse retriev", "information_retrieval"),
    (r"\bembedding|cosine similarity|semantic search", "embeddings"),
    (r"\bvector (database|index|search)|hnsw|\bivf\b|faiss", "vector_search"),
    (r"\bchunk", "chunking"),
    (r"\brerank|hybrid (search|retriev)", "hybrid_retrieval"),
    (r"\brag\b|retrieval.augmented", "rag_architecture"),
    # agents
    (r"\b(tool call|function call|structured output|json mode)", "tool_calling"),
    (r"\bagent loop|react\b|scratchpad|agent memory|agent state", "agent_loop"),
    (r"\bplanning|reflection|self.?critique", "planning_reflection"),
    (r"\bmulti.?agent", "multi_agent"),
    (r"\bprompt injection|jailbreak", "prompt_security"),
    (r"\bmcp\b|a2a\b|model context protocol", "ai_protocols"),
    (r"\bcontext (engineering|compression|selection)|long.?context", "context_engineering"),
    # systems
    (r"\bfeature store|data pipeline|dataset version", "data_pipelines"),
    (r"\bexperiment track|model registry|training pipeline|mlflow", "training_pipelines"),
    (r"\bserv(e|ing)|latency|throughput|batch inference|quanti[sz]", "model_serving"),
    (r"\bmonitor|retrain|observability", "monitoring_drift"),
    (r"\bgpu|infrastructure|cost optim", "ml_infrastructure"),
    (r"\bfairness|bias audit|privacy|responsible", "responsible_ai"),
    (r"\ba/b test|hypothesis test|statistical significan|sample size", "experimentation"),
]

# Last resort: the module's own centre of gravity. Anything landing here is
# recorded as low confidence and listed for review.
MODULE_DEFAULT: dict[str, str] = {
    "A": "dsa_coding", "B": "linear_regression", "C": "statistics",
    "D": "linear_regression", "E": "what_is_ml", "F": "llm_evaluation",
    "G": "experimentation", "H": "neural_networks", "I": "cnn", "J": "nlp_tasks",
    "K": "transformers", "L": "llm_architecture", "M": "rag_architecture",
    "N": "agent_loop", "O": "context_engineering", "P": "ai_protocols",
    "Q": "multimodal_models", "R": "ml_system_design_process",
    "S": "genai_system_design", "T": "agent_system_design",
    "U": "model_serving", "V": "monitoring_drift", "W": "ml_infrastructure",
    "X": "recsys_design", "Y": "search_ranking_design", "Z": "error_analysis",
    "AA": "ml_system_design_process", "AB": "product_reasoning",
    "AC": "research_reading", "AD": "project_deep_dive",
    "AE": "responsible_ai", "AF": "behavioral",
}

# The format axis. A question's primary format decides how it is presented
# and which daily slot it can fill, never when it unlocks.
FORMAT_BY_QUESTION_TYPE: dict[str, str] = {
    "concept": "concept",
    "coding": "implementation",
    "system_design": "system_design",
    "case_study": "case_study",
    "behavioral": "behavioral",
    "project_deep_dive": "project_deep_dive",
    "debugging": "debugging",
}

# Cognitive level, L0..L5 (spec section 7):
#   L0 recognition   L1 recall      L2 understanding
#   L3 application   L4 analysis    L5 design / synthesis
#
# Seeded from difficulty, then overridden by an explicit verb in the title.
# The seed is deliberately conservative: an "advanced" tag means the
# *content* is hard, not that the question demands synthesis. Treating the
# two as the same pushed 77% of the bank into L4/L5 on the first pass,
# which would have left the picker nothing to progress *through*.
LEVEL_BY_DIFFICULTY: dict[str, int] = {"beginner": 1, "intermediate": 2, "advanced": 3}

# First match wins, so the most specific verb comes first. L5 is
# deliberately hard to reach by keyword alone: "in production" and "at
# scale" appear all over intermediate concept questions and are not, on
# their own, a request to design anything.
LEVEL_KEYWORD_RULES: list[tuple[str, int]] = [
    (r"^design\b|^how would you (build|design)\b|^build\b", 5),
    (r"\bdefend\b|\bconvince\b|\bpush ?back\b|\bjustify your\b", 5),
    (r"\bcompare\b|\bvs\.?\b|\bversus\b|\btrade.?off\b|\bwhen would you (use|choose|pick)", 4),
    (r"\bdebug\b|\bwhat (could |can )?go(es)? wrong\b|\bfailure mode\b|\bdiagnos|\bwhy is my\b", 4),
    (r"\bderive\b|\bproof\b|\bprove\b|\bgradient of\b", 4),
    (r"\bimplement\b|\bwrite (a|the) (function|code)\b|\bfrom scratch\b", 3),
    (r"^how does\b|^how do\b|\bexplain\b|\bwalk me through\b", 2),
    (r"^why (does|do|is|are)\b|\bintuition\b", 2),
    (r"^what is\b|^what are\b|^define\b|\bterminology\b", 1),
    (r"^name\b|^which of\b|\bstand for\b", 0),
]

# A floor by format: a system-design question is synthesis whatever its
# wording, and a coding question is at least application. Applied as a
# floor rather than an override, so an explicitly harder verb still wins.
LEVEL_FORMAT_FLOOR: dict[str, int] = {
    "system_design": 5,
    "case_study": 4,
    "implementation": 3,
    "debugging": 4,
}
