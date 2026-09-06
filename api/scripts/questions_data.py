"""ML/GenAI/Agentic/Production interview question bank.

Sources, by `source` value:
- "AIMLInterviews" / "Agentic-AI-Systems" / "Production-Level-Deep-Learning":
  this assistant's own phrasing of standard ML/AI interview topics,
  informed by those three MIT-licensed public repos' subject-matter scope
  — not copied text from them.
- "aakriti1318/interview_questions": likewise this assistant's own
  phrasing, informed only by that repo's file/topic names (no license
  file, so no body text was read or reused).
- "personal repo": the user's own questions from their own GitHub repo
  wajahatalibasharat073/ai-llm-interview-questions-answers, reused at
  their explicit request — deduplicated against everything above rather
  than imported wholesale (that repo has 335 entries; many are
  near-duplicates of each other or of the questions already here).

Columns: (category, title, source, order_index)
"""

CATEGORY_LABELS: dict[str, str] = {
    "classical_ml": "Classical ML",
    "deep_learning": "Deep Learning",
    "llm_genai": "GenAI & LLMs",
    "ml_system_design": "ML System Design",
    "agentic_ai": "Agentic AI Systems",
    "mlops": "Production ML & MLOps",
}

QUESTIONS: list[tuple[str, str, str, int]] = [
    # classical_ml — AIMLInterviews
    ("classical_ml", "What is the bias-variance tradeoff, and how does it show up in model selection?", "AIMLInterviews", 1),
    ("classical_ml", "How do you detect and prevent overfitting?", "AIMLInterviews", 2),
    ("classical_ml", "Why do you split data into train/validation/test sets, and what can go wrong with the split?", "AIMLInterviews", 3),
    ("classical_ml", "What is k-fold cross-validation and when is it worth the extra compute?", "AIMLInterviews", 4),
    ("classical_ml", "Compare L1 and L2 regularization — what does each actually do to the weights?", "AIMLInterviews", 5),
    ("classical_ml", "How would you handle missing or corrupted data in a real dataset?", "AIMLInterviews", 6),
    ("classical_ml", "Walk through how a decision tree picks its splits.", "AIMLInterviews", 7),
    ("classical_ml", "Compare bagging and boosting — why does one reduce variance and the other reduce bias?", "AIMLInterviews", 8),
    ("classical_ml", "How does gradient boosting (e.g. XGBoost) differ from a random forest?", "AIMLInterviews", 9),
    ("classical_ml", "Explain logistic regression and why it uses the log-loss rather than squared error.", "AIMLInterviews", 10),
    ("classical_ml", "What is the kernel trick in an SVM, and why does it matter?", "AIMLInterviews", 11),
    ("classical_ml", "Compare k-means clustering with k-nearest neighbors — these get confused constantly.", "AIMLInterviews", 12),
    ("classical_ml", "When is precision more important than recall, and vice versa?", "AIMLInterviews", 13),
    ("classical_ml", "Why is accuracy a misleading metric on an imbalanced dataset, and what would you use instead?", "AIMLInterviews", 14),
    # classical NLP — personal repo
    ("classical_ml", "What is tokenization, and what's the difference between lemmatization and stemming?", "personal repo", 15),
    ("classical_ml", "Explain the Bag of Words (BoW) model and its limitations.", "personal repo", 16),
    ("classical_ml", "How does TF-IDF work, and how is it different from raw word frequency?", "personal repo", 17),
    ("classical_ml", "What is Named Entity Recognition, and where is it applied?", "personal repo", 18),
    ("classical_ml", "How does Latent Dirichlet Allocation (LDA) work for topic modeling?", "personal repo", 19),
    ("classical_ml", "How do you handle out-of-vocabulary words in a classic (non-LLM) NLP pipeline?", "personal repo", 20),
    # deep_learning — AIMLInterviews
    ("deep_learning", "Walk through forward and backward propagation in a small neural network.", "AIMLInterviews", 1),
    ("deep_learning", "What causes vanishing/exploding gradients, and how do modern architectures mitigate it?", "AIMLInterviews", 2),
    ("deep_learning", "Why does a CNN use convolution and pooling instead of a fully-connected layer on raw pixels?", "AIMLInterviews", 3),
    ("deep_learning", "What problem do LSTMs/GRUs solve that a vanilla RNN can't?", "AIMLInterviews", 4),
    ("deep_learning", "What does batch normalization actually do, and why does it speed up training?", "AIMLInterviews", 5),
    ("deep_learning", "Compare dropout and weight decay as regularizers for a deep net.", "AIMLInterviews", 6),
    ("deep_learning", "How does the Adam optimizer differ from plain SGD, and when might SGD still win?", "AIMLInterviews", 7),
    ("deep_learning", "What is transfer learning, and when does fine-tuning beat training from scratch?", "AIMLInterviews", 8),
    ("deep_learning", "How does a GAN's generator/discriminator setup differ from a VAE's approach to generation?", "AIMLInterviews", 9),
    ("deep_learning", "At a high level, how does a diffusion model generate an image from noise?", "AIMLInterviews", 10),
    ("deep_learning", "What is the vanishing-gradient intuition behind why residual (skip) connections help very deep networks?", "AIMLInterviews", 11),
    ("deep_learning", "How would you choose a learning-rate schedule for a large training run?", "AIMLInterviews", 12),
    ("deep_learning", "What are activation functions for, and how do the common choices (ReLU, sigmoid, tanh, GELU) differ?", "personal repo", 13),
    ("deep_learning", "How do you choose the number of layers and neurons when sizing a neural network for a new problem?", "personal repo", 14),
    ("deep_learning", "How do you choose a loss function for a given model and task?", "personal repo", 15),
    ("deep_learning", "Compare stochastic and mini-batch gradient descent — what does the batch size actually trade off?", "personal repo", 16),
    ("deep_learning", "Beyond CNNs and RNNs, what other neural architectures exist, and when would you reach for each?", "personal repo", 17),
    ("deep_learning", "What does a vanilla RNN struggle with, independent of the vanishing-gradient problem specifically?", "personal repo", 18),
    ("deep_learning", "Distinguish discriminative and generative models — what does each actually learn to model?", "personal repo", 19),
    # genai_llm — AIMLInterviews
    ("llm_genai", "Walk through a single transformer block, start to finish.", "AIMLInterviews", 1),
    ("llm_genai", "Why is the attention score divided by the square root of the key dimension?", "AIMLInterviews", 2),
    ("llm_genai", "What is the KV cache, and why does it matter for inference latency and memory?", "AIMLInterviews", 3),
    ("llm_genai", "Compare multi-head, multi-query, and grouped-query attention — why did some models move away from full MHA?", "AIMLInterviews", 4),
    ("llm_genai", "What is RoPE (rotary positional embedding), and why is it preferred over learned position embeddings?", "AIMLInterviews", 5),
    ("llm_genai", "Walk through the pretraining → SFT → RLHF/alignment pipeline behind a model like ChatGPT.", "AIMLInterviews", 6),
    ("llm_genai", "Compare SFT, DPO, and RLHF-with-a-reward-model as alignment strategies.", "AIMLInterviews", 7),
    ("llm_genai", "What is LoRA/QLoRA, and when would you reach for parameter-efficient fine-tuning over full fine-tuning?", "AIMLInterviews", 8),
    ("llm_genai", "Explain quantization (INT8/INT4) and its latency/accuracy tradeoff for serving an LLM.", "AIMLInterviews", 9),
    ("llm_genai", "How does speculative decoding speed up autoregressive generation?", "AIMLInterviews", 10),
    ("llm_genai", "When would you choose RAG over fine-tuning, or over just using a long context window?", "AIMLInterviews", 11),
    ("llm_genai", "How do you evaluate a RAG system — what is the 'RAG triad,' and what does LLM-as-judge add?", "AIMLInterviews", 12),
    ("llm_genai", "What is a Mixture-of-Experts model, and what's the difference between active and total parameters?", "AIMLInterviews", 13),
    ("llm_genai", "How does masked self-attention in a transformer decoder differ from the regular (bidirectional) self-attention in an encoder?", "personal repo", 14),
    ("llm_genai", "What role do the encoder and decoder each play in the original transformer architecture?", "personal repo", 15),
    ("llm_genai", "Compare how transformers and RNNs handle long-range dependencies in a sequence.", "personal repo", 16),
    ("llm_genai", "What are the fundamental limitations of the transformer architecture itself?", "personal repo", 17),
    ("llm_genai", "What are the practical limitations of RAG, and where does it fall short?", "personal repo", 18),
    ("llm_genai", "What role can a knowledge graph play inside a RAG pipeline?", "personal repo", 19),
    ("llm_genai", "What ethical considerations come up when deploying a RAG system in production?", "personal repo", 20),
    ("llm_genai", "How does knowledge distillation let a smaller model benefit from a larger one?", "personal repo", 21),
    ("llm_genai", "At a high level, what choices define an architecture like LLaMA relative to the original transformer?", "personal repo", 22),
    ("llm_genai", "What are ROUGE scores, and why are they the standard metric for summarization?", "personal repo", 23),
    ("llm_genai", "How would you evaluate an NLP model's robustness to adversarial inputs?", "personal repo", 24),
    ("llm_genai", "What is domain adaptation, and how do you evaluate whether it worked after fine-tuning on domain-specific data?", "personal repo", 25),
    ("llm_genai", "Compare word embeddings and sentence embeddings — when does each fit better?", "personal repo", 26),
    ("llm_genai", "What are contextual embeddings, and why do they outperform static word embeddings like word2vec?", "personal repo", 27),
    ("llm_genai", "What is triplet loss, and why is a margin parameter needed in the objective?", "personal repo", 28),
    ("llm_genai", "What is multimodal AI, and why does it matter for modern ML applications?", "personal repo", 29),
    ("llm_genai", "How do CLIP and DALL-E each combine text and image data, and what did they make possible?", "personal repo", 30),
    ("llm_genai", "What are vector databases, and how do they differ from a traditional relational database?", "personal repo", 31),
    ("llm_genai", "What makes indexing and searching high-dimensional vector spaces hard at scale?", "personal repo", 32),
    ("llm_genai", "Where does vector similarity actually get used — recommendation, RAG, dedup — and how does the choice of metric change?", "personal repo", 33),
    # ml_system_design — AIMLInterviews
    ("ml_system_design", "Walk through your framework for an open-ended ML system design interview, start to finish.", "AIMLInterviews", 1),
    ("ml_system_design", "Design a video or movie recommendation system (Netflix/YouTube-style).", "AIMLInterviews", 2),
    ("ml_system_design", "Design a 'people you may know' / friend-recommendation system.", "AIMLInterviews", 3),
    ("ml_system_design", "Design a text search system — how do full-text and semantic (embedding) search differ in this architecture?", "AIMLInterviews", 4),
    ("ml_system_design", "Design a social-media newsfeed ranking system.", "AIMLInterviews", 5),
    ("ml_system_design", "Design an ads click-prediction / ads-ranking system.", "AIMLInterviews", 6),
    ("ml_system_design", "Design a harmful-content or spam detection system.", "AIMLInterviews", 7),
    ("ml_system_design", "Why does a large-scale recommender split into a candidate-generation stage and a ranking stage instead of scoring everything directly?", "AIMLInterviews", 8),
    ("ml_system_design", "Compare offline ranking metrics (Recall@k, MRR, nDCG) — what does each capture that the others miss?", "AIMLInterviews", 9),
    ("ml_system_design", "How would you design the online A/B test for a ranking-model change, and what could make the online result diverge from your offline metric?", "AIMLInterviews", 10),
    ("ml_system_design", "Design an autocomplete/typeahead suggestion system.", "AIMLInterviews", 11),
    ("ml_system_design", "How would you build a ChatGPT-like conversational system end to end?", "personal repo", 12),
    ("ml_system_design", "Design an LLM-based system for code generation — what makes this harder than plain text generation?", "personal repo", 13),
    ("ml_system_design", "Design an LLM-based question-answering system for a specific, complex domain (e.g. legal or medical).", "personal repo", 14),
    ("ml_system_design", "What design considerations change when building a multi-turn conversational system versus a single-turn one?", "personal repo", 15),
    ("ml_system_design", "Your LLM product needs to handle a massive, near-real-time influx of queries — how do you approach scaling and load balancing?", "personal repo", 16),
    # agentic_ai — Agentic-AI-Systems
    ("agentic_ai", "Design an LLM-powered customer-support chatbot with guardrails and a fallback to a human agent.", "Agentic-AI-Systems", 1),
    ("agentic_ai", "Design an enterprise 'chat with your documents' RAG assistant.", "Agentic-AI-Systems", 2),
    ("agentic_ai", "Design a multi-step agentic workflow that triages and resolves support tickets.", "Agentic-AI-Systems", 3),
    ("agentic_ai", "Design a multi-agent research system that produces a cited report.", "Agentic-AI-Systems", 4),
    ("agentic_ai", "Design an AI coding assistant that reads a codebase and proposes changes.", "Agentic-AI-Systems", 5),
    ("agentic_ai", "What guardrails would you put around an agent that has access to real tools (email, calendar, payments)?", "Agentic-AI-Systems", 6),
    ("agentic_ai", "How does a ReAct-style agent loop (reason, act, observe) differ from a single-shot LLM call?", "Agentic-AI-Systems", 7),
    ("agentic_ai", "How would you design cross-conversation memory for a chat assistant?", "Agentic-AI-Systems", 8),
    ("agentic_ai", "Your chat product needs to scale to 1M daily active users — how do you cut LLM inference cost without hurting answer quality?", "Agentic-AI-Systems", 9),
    ("agentic_ai", "How would you route a query between a small, cheap model and a large, expensive one?", "Agentic-AI-Systems", 10),
    ("agentic_ai", "What tradeoffs would push you toward a single powerful agent vs. a multi-agent (orchestrator + specialists) architecture?", "Agentic-AI-Systems", 11),
    # production_mlops — Production-Level-Deep-Learning
    ("mlops", "Walk through the full lifecycle of a production ML system, from data collection to monitoring.", "Production-Level-Deep-Learning", 1),
    ("mlops", "What is training/serving skew, and how does it quietly break a model that worked fine in a notebook?", "Production-Level-Deep-Learning", 2),
    ("mlops", "Why does data versioning matter as much as code versioning for a production ML system?", "Production-Level-Deep-Learning", 3),
    ("mlops", "Compare batch and online (real-time) inference — what pushes a system toward one or the other?", "Production-Level-Deep-Learning", 4),
    ("mlops", "What is a canary release or shadow deployment, and why not just replace the old model outright?", "Production-Level-Deep-Learning", 5),
    ("mlops", "Distinguish data drift from concept drift — how would you detect each in production?", "Production-Level-Deep-Learning", 6),
    ("mlops", "What does an experiment-tracking system (e.g. MLflow-style) need to record to make a training run reproducible?", "Production-Level-Deep-Learning", 7),
    ("mlops", "Compare data-parallel and model-parallel distributed training — when do you need each?", "Production-Level-Deep-Learning", 8),
    ("mlops", "How would you design CI/CD for a machine learning pipeline, not just application code?", "Production-Level-Deep-Learning", 9),
    ("mlops", "What monitoring would tell you a deployed model is failing before your users complain?", "Production-Level-Deep-Learning", 10),
    ("mlops", "What does a feature store solve that a shared feature-engineering script doesn't?", "Production-Level-Deep-Learning", 11),
    ("mlops", "How would you add caching to an LLM-based system, and what's actually safe to cache?", "personal repo", 12),
    ("mlops", "How would you shrink a model to fit a resource-constrained deployment target, like a phone?", "personal repo", 13),
    ("mlops", "GPU vs. TPU vs. other accelerators for serving a large model — what's the real tradeoff?", "personal repo", 14),
    ("mlops", "What would you actually monitor once an LLM-backed system is in production?", "personal repo", 15),
    ("mlops", "How would you detect that an LLM's real-world performance has drifted since launch?", "personal repo", 16),
    # agentic_ai — inspired by aakriti1318/interview_questions' topic areas
    ("agentic_ai", "How would you keep a multi-agent system's outputs consistent when several agents can act on shared state?", "aakriti1318/interview_questions", 12),
    ("agentic_ai", "What is a prompt injection attack, and how would you defend an agent that reads untrusted content?", "aakriti1318/interview_questions", 13),
    ("agentic_ai", "How would you design observability and graceful fallbacks for an agent pipeline that calls an LLM and external tools?", "aakriti1318/interview_questions", 14),
    ("agentic_ai", "When would you build an agent platform in-house versus buy/adopt an existing framework?", "aakriti1318/interview_questions", 15),
    ("agentic_ai", "What would you need to log and expose to make an agentic system auditable for compliance?", "aakriti1318/interview_questions", 16),
    ("agentic_ai", "How would you manage context and memory for a very long-running conversation without blowing the context window?", "aakriti1318/interview_questions", 17),
]
