"""Adjudicated classifications: the cases where reading the question beats
any rule.

Every entry here is a judgement made by reading the question's full text
against the topic graph, and every one records why. They take precedence
over both the submodule label and the keyword rules, because each is a
case where the source metadata is wrong about its own content -- the bank
contains a tokenizer question filed under "Q/K/V & scaled dot-product" and
a quantization question filed under "Instruction tuning & SFT".

Matching is by distinctive title substring rather than question id. Ids
are assigned by ingestion order and would silently re-point at a different
question if the bank were reloaded; the title is the thing a human can
check.

Keep this list small and specific. It is for adjudicating genuine source
errors, not for tuning: a pattern that recurs belongs in KEYWORD_RULES, and
a topic that keeps needing overrides is usually a missing graph node -- as
"collaborative filtering" was, before recsys_fundamentals existed.
"""

from __future__ import annotations

#: (title substring, topic slug, reason). Lowercased comparison.
MANUAL_CLASSIFICATIONS: list[tuple[str, str, str]] = [
    # ---- source submodule contradicts the question's own subject -------
    (
        "what is kv cache",
        "llm_inference",
        "Filed under 'Q/K/V & scaled dot-product'. The KV cache is an inference-time "
        "memory optimisation, not part of the attention derivation; the question even "
        "says 'in LLM inference'.",
    ),
    (
        "mixture of experts",
        "llm_architecture",
        "Filed under attention. MoE is a model-architecture choice about routing and "
        "parameter efficiency, not a property of scaled dot-product attention.",
    ),
    (
        "explain quantization",
        "llm_inference",
        "Filed under 'Instruction tuning & SFT', which it has nothing to do with. "
        "Quantization trades model size and speed against accuracy at inference.",
    ),
    (
        "how can we use cnn for text classification",
        "nlp_tasks",
        "Filed under 'TF-IDF & sparse features', but the question is not about TF-IDF "
        "at all. It is applying a CNN to an NLP task, so it needs both and belongs "
        "with NLP tasks.",
    ),

    # ---- deep-learning optimisation misfiled as P0 mathematics ---------
    (
        "compare gradient descent, sgd, momentum",
        "dl_optimization",
        "In the Mathematics module, but comparing Adam and RMSprop is a deep-learning "
        "optimiser question. At P0 a learner has no network to optimise.",
    ),
    (
        "loss surface of a deep network",
        "dl_optimization",
        "In the Mathematics module, but explicitly about deep networks. Requires "
        "knowing what a deep network is.",
    ),

    # ---- activation functions swallowed by 'neural networks' -----------
    (
        "explain all standard activation functions",
        "activations",
        "A dedicated activations topic exists; this is its central question. Was "
        "landing on the broader neural_networks topic.",
    ),
    (
        "problems with sigmoid as an activation function",
        "activations",
        "Same: about activations, not about logistic regression, which is what "
        "'sigmoid' matched before the rules were split.",
    ),
    (
        "what is relu",
        "activations",
        "Same: an activation-function comparison.",
    ),

    # ---- RAG evaluation filed as generic LLM evaluation ----------------
    (
        "debug a rag chatbot giving confident but wrong",
        "rag_evaluation",
        "Diagnosing a RAG system requires knowing the retrieval pipeline, not just "
        "how to evaluate an LLM. Generic LLM evaluation is a weaker prerequisite.",
    ),
    (
        "how do you evaluate a rag pipeline",
        "rag_evaluation",
        "Explicitly RAG evaluation, which is its own topic with RAG architecture "
        "as a prerequisite.",
    ),

    # ---- system-design questions on a too-generic topic ----------------
    (
        "design: youtube recommendation",
        "recsys_design",
        "Was on the generic ml_system_design_process. It is a recommender design "
        "question and should sit with the others.",
    ),
    (
        "design: linkedin feed ranking",
        "recsys_design",
        "Feed ranking is a recommendation problem; was on the generic design topic.",
    ),
    (
        "design: estimate delivery time",
        "classic_ml_system_design",
        "A forecasting/regression system, which is what classic_ml_system_design "
        "covers; was on the generic design topic.",
    ),
    (
        "design: airbnb search ranking",
        "search_ranking_design",
        "A search-ranking design question; was on the generic design topic.",
    ),
    (
        "listing embeddings in search ranking",
        "search_ranking_design",
        "Filed as a recommender case study, but the paper is about search ranking.",
    ),
    (
        "unit test case generation with transformers",
        "genai_system_design",
        "Filed under 'RAG products'. It is code generation with a transformer and "
        "involves no retrieval-augmented generation.",
    ),

    # ---- fundamentals gated behind system design -----------------------
    (
        "what is collaborative filtering",
        "recsys_fundamentals",
        "An L1 definition that was reachable only after the entire P5 system-design "
        "chain. Prompted adding a recommendation-fundamentals topic at P1.",
    ),
    (
        "unsupervised baselines for text information retrieval",
        "information_retrieval",
        "An IR fundamentals question filed under learning-to-rank system design. "
        "BM25-style baselines precede ranking systems.",
    ),
    (
        "what is precision and recall at k",
        "information_retrieval",
        "Precision@k and recall@k are IR metrics, not the confusion-matrix metrics, "
        "and they are needed long before ranking-system design.",
    ),
    (
        "mean average precision at k",
        "information_retrieval",
        "Same: an IR ranking metric, previously gated behind P5.",
    ),

    # ---- module D questions with submodule="Regression" or "None" that -
    # ---- are not about regression at all. This module's default fallback
    # ---- (linear_regression) is a reasonable guess for the majority of its
    # ---- 119 questions, but these had a stronger, different signal once
    # ---- actually read; classified individually rather than in bulk.
    (
        "named entity recognition",
        "nlp_tasks",
        "Classic NLP task, not regression. Module D's default (linear_regression) "
        "was a pure fallback with no real signal.",
    ),
    (
        "latent dirichlet allocation",
        "nlp_tasks",
        "Topic modelling is a classic NLP technique.",
    ),
    (
        "out-of-vocabulary words",
        "text_preprocessing",
        "OOV handling is a tokenisation/preprocessing concern.",
    ),
    (
        "collinearity: how is it possible to have negative coefficient",
        "regression_assumptions",
        "Multicollinearity's effect on coefficient signs is a regression-diagnostics "
        "question, more specific than the bare 'linear_regression' fallback.",
    ),
    (
        "type of regularization, which one easier to use",
        "ridge_lasso",
        "Comparing Ridge/Lasso/Elastic Net by ease of use is that topic's own content.",
    ),
    (
        "what are the different metrics to classify the dataset",
        "classification_metrics",
        "Asking about classification metrics, not regression.",
    ),
    (
        "how to handle unbalanced data",
        "class_imbalance",
        "Its own dedicated topic exists; this is its central question.",
    ),
    (
        "how do you inspect missing data",
        "data_preprocessing",
        "Missing-data handling is a preprocessing question.",
    ),
    (
        "how to compare two regressions",
        "model_selection",
        "Choosing between two fitted models is model selection, not regression "
        "mechanics itself.",
    ),
    (
        "general ml questions like generative v.s",
        "what_is_ml",
        "Generative vs discriminative is a foundational ML-paradigm distinction.",
    ),
    (
        "type i vs type ii error",
        "statistics",
        "A hypothesis-testing concept, not regression.",
    ),
    (
        "what is selection bias",
        "statistics",
        "A statistical-inference concept, not regression.",
    ),
    (
        "what is the learning curve tool",
        "error_analysis",
        "Learning curves are how you diagnose bias/variance from data volume, which "
        "is error analysis, not the regression algorithm itself.",
    ),
    (
        "explain mle",
        "probability",
        "Maximum likelihood estimation is a probability-theory foundation, needed "
        "well before any specific regression model.",
    ),
    (
        "explain map",
        "probability",
        "Maximum a posteriori estimation, same reasoning as MLE.",
    ),
    (
        "explain how you select the best model",
        "model_selection",
        "Directly the subject of the model_selection topic.",
    ),
    (
        "how gmm works (em algorithm)",
        "clustering",
        "Gaussian Mixture Models are a soft-clustering method; grouped with "
        "clustering rather than inventing a separate EM topic for one pair "
        "of questions.",
    ),
    (
        "when using the gaussian mixture model, how do you know it is applicable",
        "clustering",
        "Same: GMM applicability is a clustering-method question.",
    ),
    (
        "describe some criteria for model selection",
        "model_selection",
        "Explicitly about model-selection criteria and dimensionality reduction.",
    ),
    (
        "what's the normal distribution",
        "probability",
        "A probability-distributions question, not regression.",
    ),
    (
        "how do we check if a variable follows the normal distribution",
        "statistics",
        "A goodness-of-fit / statistical-testing question.",
    ),
    (
        "what if we want to build a model for predicting prices",
        "data_preprocessing",
        "About whether and how to transform a skewed target before modelling, "
        "which is a preprocessing decision.",
    ),
    (
        "which metrics for evaluating regression models do you know",
        "regression_metrics",
        "Directly the subject of the regression_metrics topic; the module default "
        "(linear_regression) is one level too coarse.",
    ),
    (
        "what is classification? which models",
        "classification_fundamentals",
        "An overview question about classification itself, not regression.",
    ),
    (
        "how do we evaluate classification models",
        "classification_metrics",
        "Directly classification_metrics.",
    ),
    (
        "what is accuracy?",
        "classification_metrics",
        "A classification-metric definition.",
    ),
    (
        "is accuracy always a good metric",
        "classification_metrics",
        "About the limits of the accuracy metric specifically.",
    ),
    (
        "what is the confusion table",
        "classification_metrics",
        "The confusion matrix is a classification_metrics concept.",
    ),
    (
        "what do we do with categorical variables",
        "data_preprocessing",
        "Encoding categorical variables is a preprocessing step.",
    ),
    (
        "why do we need one-hot encoding",
        "data_preprocessing",
        "One-hot encoding is a preprocessing technique.",
    ),
    (
        "what is \"curse of dimensionality\"",
        "pca",
        "The curse of dimensionality is the motivating problem for dimensionality "
        "reduction, which is what the pca topic covers.",
    ),
    (
        "what is a time series?",
        "time_series",
        "New topic added: none of the existing 103 topics covered time series, and "
        "7 questions on it were falling through to a linear-regression default.",
    ),
    (
        "how is time series different from the usual regression problem",
        "time_series",
        "Same topic as the other time-series questions.",
    ),
    (
        "which models do you know for solving time series problems",
        "time_series",
        "Same.",
    ),
    (
        "if there's a trend in our series, how we can remove it",
        "time_series",
        "Same.",
    ),
    (
        "you have a series with only one variable",
        "time_series",
        "Same.",
    ),
    (
        "you have a series with a variable “y” and a set of features",
        "time_series",
        "Same.",
    ),
    (
        "what are the problems with using trees for solving time series",
        "time_series",
        "Same.",
    ),
]


def manual_topic(title: str) -> tuple[str, str] | None:
    """-> (topic_slug, reason), or None if this title was not adjudicated."""
    hay = " ".join((title or "").lower().split())
    for needle, slug, reason in MANUAL_CLASSIFICATIONS:
        if needle in hay:
            return slug, reason
    return None
