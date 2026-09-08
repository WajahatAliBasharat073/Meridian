# AI/ML Interview Curriculum

Generated from the Meridian question bank by `api/scripts/build_curriculum_doc.py`.
Every count here is a query result, not a hand-typed figure — re-run the
generator after any ingestion rather than editing this file.

**724 canonical questions across 32 modules.**
174 carry `reported` evidence (a named, linkable source);
63 name a company, and none may do so without both `evidence='reported'`
and a `source_url` — that rule is a database check constraint, not a convention.

Evidence tiers: `reported` (a named source ties this question to a company or a
candidate report) · `common` (appears across several independent prep sources) ·
`fundamental` (core knowledge, no company claim made) · `derived` (generated from
a topic outline).

## OUTPUT 1 — Interview Master Map

| Module | Title | Priority | Questions | Target seniority | Submodules |
| --- | --- | --- | ---: | --- | ---: |
| A | General Coding & DSA | P0 | 36 | junior, mid, senior, staff | 15 |
| B | ML Coding | P0 | 43 | junior, mid, senior, staff | 7 |
| C | Mathematics & Statistics | P0 | 12 | junior, mid, senior, staff | 6 |
| D | Classical Machine Learning | P0 | 119 | junior, mid, senior, staff | 11 |
| E | ML Fundamentals & Breadth | P0 | 28 | junior, mid, senior, staff | 11 |
| F | Model Evaluation | P0 | 10 | junior, mid, senior, staff | 7 |
| G | Experimentation & A/B Testing | P1 | 10 | mid, senior, staff | 9 |
| H | Deep Learning | P0 | 31 | junior, mid, senior, staff | 11 |
| I | Computer Vision | P2 | 13 | mid, senior, staff | 10 |
| J | NLP | P1 | 14 | junior, mid, senior, staff | 9 |
| K | Transformers | P0 | 20 | junior, mid, senior, staff | 10 |
| L | Foundation Models & LLMs | P0 | 31 | junior, mid, senior, staff | 13 |
| M | RAG | P0 | 29 | junior, mid, senior, staff | 14 |
| N | AI Agents | P1 | 19 | mid, senior, staff | 14 |
| O | Context Engineering | P1 | 1 | mid, senior, staff | 9 |
| P | MCP / A2A / AI Protocols | P2 | 2 | mid, senior, staff | 10 |
| Q | Multimodal AI | P2 | 7 | mid, senior, staff | 7 |
| R | ML System Design | P0 | 42 | mid, senior, staff, principal | 17 |
| S | GenAI System Design | P0 | 42 | mid, senior, staff, principal | 11 |
| T | Agentic System Design | P1 | 7 | senior, staff, principal | 10 |
| U | Production ML & MLOps | P1 | 16 | mid, senior, staff, principal | 14 |
| V | LLMOps & AI Operations | P1 | 6 | mid, senior, staff | 12 |
| W | ML Infrastructure | P2 | 15 | senior, staff, principal | 12 |
| X | Recommendation Systems | P1 | 6 | mid, senior, staff | 10 |
| Y | Search & Information Retrieval | P1 | 11 | mid, senior, staff | 10 |
| Z | ML Debugging | P1 | 11 | mid, senior, staff, principal | 10 |
| AA | ML Case Studies | P1 | 52 | mid, senior, staff, principal | 14 |
| AB | AI Product & Business Reasoning | P1 | 9 | senior, staff, principal | 8 |
| AC | Research & Paper Understanding | P2 | 12 | senior, staff, principal | 12 |
| AD | Project Deep Dive | P0 | 27 | junior, mid, senior, staff, principal | 12 |
| AE | Responsible AI & Security | P2 | 5 | mid, senior, staff, principal | 12 |
| AF | Behavioral & Leadership | P0 | 38 | junior, mid, senior, staff, principal | 9 |

## OUTPUT 2 — Complete Question Bank

The full bank lives in the database and is browsable at `/curriculum` in the app, where each question shows what the interviewer is testing, its follow-ups, its strong/weak signals, its source link, and your 0-7 mastery. Reproduced here by module, capped for readability.

### Module A — General Coding & DSA (36 questions, P0)

_One or two rounds in nearly every loop, in the same format as a SWE coding round. Prepared by pattern, not by problem count — recognising the pattern from the statement is the skill being tested._

- 1-D dynamic programming: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- 2-D dynamic programming: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Advanced graphs and greedy: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Arrays, strings, and hashing: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Backtracking: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Binary search: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Graphs: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Intervals: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Linked lists: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Math, geometry, and bit manipulation: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Stack and monotonic stack: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Trees (BFS, DFS, BST): what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Tries, heaps, and priority queues: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Two pointers and sliding window: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Build a key-value database starting with basic operations (SET/GET/DELETE) — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/)
- Credits management system - track credit state across issued and used credits with different expiration rules and usage requirements, with increasing complexity — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Find the Excel column name from its column number (e.g., column 702 = "AAA") — *P1 · intermediate · Microsoft* [ai-engineering-field-guide](https://www.reddit.com/r/csMajors/comments/1nqfzhq/microsoft_swe_applied_aiml_summer_2026_redmond)
- Implement a website crawler (my personal experience) — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/)
- In-Memory Database: Implement SQL-Like Operations — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- LeetCode 2408: Design SQL — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- _…and 16 more in the app._

### Module B — ML Coding (43 questions, P0)

_A separate round from DSA: implement ML primitives from scratch in NumPy/PyTorch. Tests whether the maths is understood at implementation depth — shapes, numerical stability, and edge cases, not library calls._

- Implement: LoRA update for a linear layer — *P0 · intermediate · Meta, Google, Anthropic, OpenAI, Databricks* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Append-only KV cache — *P0 · intermediate · Anthropic, OpenAI, Meta, Perplexity* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: k-means clustering — *P0 · intermediate · Uber, LinkedIn, Google, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Numerically stable softmax and cross-entropy — *P0 · beginner · Apple, Meta, Google, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Symmetric contrastive loss — *P0 · intermediate · OpenAI, Anthropic, DeepMind, Midjourney* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: k-nearest neighbors — *P0 · intermediate · Uber, LinkedIn, Meta* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Temperature, top-k, and top-p sampling — *P0 · intermediate · Anthropic, OpenAI, DeepMind* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: 2D convolution — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Binary metrics and ROC-AUC — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Build a causal attention mask — *P0 · beginner* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Classifier-free guidance combination — *P0 · beginner* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Decision-tree split — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Exact cosine top-k retrieval for RAG — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Feature standardization with training statistics — *P0 · beginner* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Learn and apply byte-pair encoding — *P0 · beginner* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Linear regression with gradient descent — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Linear SVM and hinge loss — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Matrix factorization for recommendations — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Missing values and unseen categories — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Multiclass metrics and macro averaging — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- _…and 23 more in the app._

### Module C — Mathematics & Statistics (12 questions, P0)

_Applied, not recited. Questions are posed as scenarios with numbers (base rates, power, estimator choice) rather than definitions._

- A fraud detector fires on 0.1% of transactions. The classifier has 99% sensitivity and 99% specificity. A transaction is flagged — what is the probability it is actually fraud, and what does that imply for the product? — *P0 · advanced* [curriculum spec]
- Compare gradient descent, SGD, momentum, RMSprop and Adam. What problem does each one fix in its predecessor? — *P0 · intermediate* [curriculum spec]
- Correlation is not causation — so what would you actually need to claim causation from observational data? — *P0 · advanced* [curriculum spec]
- Derive the gradient of the logistic loss with respect to the weights. — *P0 · advanced* [curriculum spec]
- Expected value, variance and covariance: define them, then tell me what covariance fails to capture. — *P0 · beginner* [curriculum spec]
- Explain eigenvalues and eigenvectors in terms of what PCA is actually doing. — *P0 · intermediate* [curriculum spec]
- Explain the Central Limit Theorem and where people misuse it. — *P0 · intermediate* [curriculum spec]
- What does the Hessian tell you that the gradient does not, and why do we mostly not use it? — *P0 · advanced* [curriculum spec]
- What is a confidence interval, and what does 95% actually refer to? — *P0 · intermediate* [curriculum spec]
- What is a p-value, stated precisely — and what is it not? — *P0 · intermediate* [curriculum spec]
- What is SVD, and why does it keep appearing in ML — recommendation, PCA, low-rank adaptation? — *P0 · advanced* [curriculum spec]
- Why is the loss surface of a deep network non-convex, and why does SGD work anyway? — *P0 · advanced* [curriculum spec]

### Module D — Classical Machine Learning (119 questions, P0)

_Still asked in 2026 loops and still where candidates who prepared only GenAI fail. Every algorithm carries the same 15-question interrogation: objective, assumptions, hyperparameters, failure modes, alternatives, production behaviour._

- Assumptions about linear regression: 3 residual errors follow a normal distribution and — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Assumptions about logistic regression? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Describe some criteria for model selection? Why is dimension reduction important? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- explain bagging vs boosting — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain boosting — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain collinearity: how is it possible to have negative coefficient in glm? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain how you select the best model? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain logistic regression? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain MAP — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain MLE — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain MLP: kind of fully connected feedforward neural network that use sigmoid or tanh as activation functions, widely used for classification task similar to logistic regression — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain PCA. What is physical intuition? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- explain random forest — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain SVM — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain the concept of bias vs variance — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain the decision tree — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain TPE hyperparameter optimization. explain hyper optimization — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- general ML questions like generative v.s — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- How do you choose the best model among all possible models? explain neural network assumptions of linear regression models if you have a large number of predictors how do you handle them? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- How do you find an anomaly in a distribution? How do you investigate that a certain trend in distribution is due to anomaly? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- _…and 99 more in the app._

### Module E — ML Fundamentals & Breadth (28 questions, P0)

_The breadth round. Follows a consistent structure across interviewers, which makes it the highest-ROI module to over-prepare._

- Can we have both L1 and L2 regularization components in a linear model? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Can we use L1 regularization for feature selection? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Can we use L2 regularization for feature selection? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Can you explain how cross-validation works? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we choose K in K-fold cross-validation? What’s your favorite K? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we interpret weights in linear models? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we select the right regularization parameters? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How does L2 regularization look like in a linear model? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How L1 regularization looks like in a linear model? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How to validate your models? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- If a weight for one variable is higher than for another  —  can we say that this variable is more important? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Is feature selection important for linear models? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What happens to our linear regression model if the column z in the data is a sum of columns x and y and some random noise? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What happens to our linear regression model if we have three columns in our data: x, y, z  —  and z is a sum of x and y? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is feature selection? Why do we need it? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is K-fold cross-validation? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is overfitting? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is regularization? Why do we need it? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What kind of regularization techniques are applicable to linear models? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What’s the difference between grid search parameter tuning strategy and random search? When to use one or another? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- _…and 8 more in the app._

### Module F — Model Evaluation (10 questions, P0)

_Kept separate from algorithms on purpose. The recurring question is never 'what is F1' but 'why this metric instead of that one, for this decision'._

- How do you evaluate a chatbot? — *P0 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.reddit.com/r/cscareerquestions/)
- How do you detect and mitigate hallucinations? — *P0 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/cscareerquestions/)
- What metrics do you consider when evaluating LLM performance? — *P0 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=leXRiJ5TuQo)
- How do you debug a RAG chatbot giving confident but wrong answers? — *P1 · intermediate · Mistral* [ai-engineering-field-guide](https://www.reddit.com/r/cscareerquestions/)
- How do you evaluate an agent whose output is a trajectory rather than a label? — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)
- How do you build a golden dataset for evaluation? — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=leXRiJ5TuQo)
- How do you ensure the output from LLMs is consistent and accurate? — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=leXRiJ5TuQo)
- How do you evaluate a RAG pipeline? — *P1 · intermediate* [ai-engineering-field-guide](https://mimansajaiswal.github.io/posts/llm-ml-job-interviews-resources/)
- How do you evaluate agent performance? What metrics matter (tool selection quality, action advancement, context adherence)? — *P1 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/AI_Agents/comments/1qrxchn/interview_prep_deep_learning_agentic_systems_what)
- How would you prevent factual errors in a summarization system? — *P1 · intermediate* [ai-engineering-field-guide](https://www.interviewnode.com/post/generative-ai-system-design-interview-patterns-you-should-know)

### Module G — Experimentation & A/B Testing (10 questions, P1)

_Heavier for product-facing ML and Applied Scientist roles. The good questions are contradictions to resolve, not formulas to state._

- A test showed a positive lift that decayed to zero over three weeks. What happened? — *P1 · advanced* [curriculum spec]
- CTR went up 4% and revenue went down 2%. The result is significant. What do you do? — *P1 · advanced* [curriculum spec]
- How do you compute the sample size you need, and what happens if you peek before reaching it? — *P1 · advanced* [curriculum spec]
- Model accuracy improved and user retention fell. How do you reconcile that? — *P1 · advanced* [curriculum spec]
- Walk me through designing an A/B test for a new ranking model: hypothesis, unit of randomisation, metric, and how long you run it. — *P1 · advanced* [curriculum spec]
- What is experiment contamination, and how would you detect it after the fact? — *P1 · advanced* [curriculum spec]
- What is statistical power, and what is the practical cost of an underpowered test? — *P1 · advanced* [curriculum spec]
- When is sequential testing worth the extra complexity over a fixed-horizon test? — *P1 · advanced* [curriculum spec]
- You are running 20 experiments at once. What is the problem and what do you do about it? — *P1 · advanced* [curriculum spec]
- Your result is statistically significant with a 0.1% effect. Ship it or not? — *P1 · advanced* [curriculum spec]

### Module H — Deep Learning (31 questions, P0)

_Separate from classical ML. Every concept is asked as WHAT / HOW / WHY / MATH / FAILURE / TRADE-OFF / PRODUCTION._

- Explain all standard activation functions? tanh, relu, leakyRelu, sigmoid, softmax, softplus — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain RNN Problem — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- How does a neural network with one layer and one input and output compare to logistic regression? It’s the same with logistic regression if the NN is using sigmoid function and logistic regression? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Can you tell us how you approach the model training process? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Do we want to have a constant learning rate or we better change it throughout training? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we decide when to stop training a neural net? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we use SGD (stochastic gradient descent) for training a neural net? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How does a usual fully-connected feed-forward neural network work? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How to set the learning rate? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How we can initialize the weights of a neural network? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What are the problems with sigmoid as an activation function? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What happens when the learning rate is too large? Too small? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What if we set all the weights of a neural network to 0? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is Adam? What’s the main difference between Adam and SGD? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is backpropagation? How does it work? Why do we need it? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is dropout? Why is it useful? How does it work? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is model checkpointing? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is ReLU? How is it better than sigmoid or tanh? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What kind of problems neural nets can solve? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What regularization techniques for neural nets do you know? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- _…and 11 more in the app._

### Module I — Computer Vision (13 questions, P2)

_Role-dependent. P0 for a CV-titled role, P2 otherwise — but multimodal work has pulled the embedding and detection parts back into general relevance._

- How does max pooling work? Are there other pooling techniques? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How to choose which augmentations to use? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How we can use neural nets for computer vision? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What are augmentations? Why do we need them? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is transfer learning? How does it work? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What kind of augmentations do you know? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What’s a convolutional layer? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What’s pooling in CNN? Why do we need it? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Why do we actually need convolutions? Can’t we use fully-connected layers for that? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Are CNNs resistant to rotations? What happens to the predictions of a CNN if an image is rotated? — *P1 · advanced* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is object detection? Do you know any architectures for that? — *P1 · advanced* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is object segmentation? Do you know any architectures for that? — *P1 · advanced* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What kind of CNN architectures for classification do you know? — *P1 · advanced* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)

### Module J — NLP (14 questions, P1)

_The classical half still matters: tokenization, TF-IDF and retrieval fundamentals underpin every RAG question in Module M._

- How can we use machine learning for text classification? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How large should be N for our bag of words when using N-grams? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- If you have a sentence with multiple words, you may need to combine multiple word embeddings into one. How would you do it? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What are N-grams? How can we use them? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What are the advantages and disadvantages of bag of words? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What are word embeddings? Why are they useful? Do you know Word2Vec? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is bag of words? How we can use it for text classification? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is TF-IDF? How is it useful for text classification? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Which model would you use for text classification with bag of words features? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Would you prefer gradient boosting trees model or logistic regression when doing text classification with bag of words? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Would you prefer gradient boosting trees model or logistic regression when doing text classification with embeddings? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Do you know any other ways to get word embeddings? — *P1 · advanced* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How can we use CNN for text classification? — *P1 · advanced* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How can you use neural nets for text classification? — *P1 · advanced* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)

### Module K — Transformers (20 questions, P0)

_A dedicated high-priority module. Architecture-level understanding is expected — why each design choice exists, not what the diagram looks like._

- How do transformers work? — *P0 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=Zt-h5BiBWH0)
- Explain the difference between encoder-only, decoder-only, and encoder-decoder Transformer architectures. When would you use each? — *P0 · intermediate* [ai-engineering-field-guide](https://github.com/TidorP/MLJobSearch2025)
- Encoder-only, decoder-only, encoder-decoder: what task shape does each suit, and why did decoder-only win for general LLMs? — *P0 · advanced* [curriculum spec]
- Explain Mixture of Experts: what is sparse about it, and what new failure modes does routing introduce? — *P0 · advanced* [curriculum spec]
- Explain RoPE. Why does rotating the query and key make relative position fall out of the dot product? — *P0 · advanced* [curriculum spec]
- MHA vs MQA vs GQA: what is shared in each, and what does that do to quality and to memory bandwidth at decode time? — *P0 · advanced* [curriculum spec]
- What does FlashAttention change? It computes the same attention — so where does the speedup come from? — *P0 · advanced* [curriculum spec]
- What is causal masking, where exactly is it applied, and what goes wrong if it is applied after the softmax? — *P0 · advanced* [curriculum spec]
- What is the KV cache, what exactly is stored, and how does its size grow with batch size, sequence length and model width? — *P0 · advanced* [curriculum spec]
- What is the time and memory complexity of self-attention, and which of the two actually binds first in practice? — *P0 · advanced* [curriculum spec]
- Where are the compute-bound and memory-bound bottlenecks in Transformer inference, and how does that differ between prefill and decode? — *P0 · advanced* [curriculum spec]
- Why do Transformers beat RNNs on long sequences, given that attention is quadratic and an RNN is linear? — *P0 · advanced* [curriculum spec]
- Why does a Transformer need positional information at all, and what do sinusoidal, learned and RoPE encodings each trade off? — *P0 · advanced* [curriculum spec]
- Why does attention use three separate projections — Q, K and V — rather than comparing the inputs directly? — *P0 · advanced* [curriculum spec]
- Why is the dot product divided by sqrt(d_k)? What breaks if you remove it? — *P0 · advanced* [curriculum spec]
- Why multi-head attention rather than one larger head? What do different heads end up representing? — *P0 · advanced* [curriculum spec]
- What is KV cache? How does it help in LLM inference? — *P1 · intermediate* [ai-engineering-field-guide](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
- What are the differences between BPE, WordPiece, and character-level tokenization? What are the trade-offs? — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=yr5dRHrnbCo)
- What is Mixture of Experts (MoE)? How does it improve efficiency? — *P1 · intermediate* [ai-engineering-field-guide](https://mimansajaiswal.github.io/posts/llm-ml-job-interviews-resources/)
- What is the self-attention mechanism? — *P1 · intermediate* [ai-engineering-field-guide](https://www.sundeepteki.org/advice/the-ultimate-ai-research-engineer-interview-guide-cracking-openai-anthropic-google-deepmind-top-ai-labs)

### Module L — Foundation Models & LLMs (31 questions, P0)

_Pretraining through post-training. The distinguishing questions are 'why' — why next-token prediction produces general capability, why DPO removes the reward model._

- What is PEFT/LoRA and when would you use it? — *P0 · intermediate · Meta* [ai-engineering-field-guide](https://www.youtube.com/watch?v=yr5dRHrnbCo)
- What is the context window and what happens when you exceed it? How do you handle long documents? — *P0 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.youtube.com/watch?v=yr5dRHrnbCo)
- When would you fine-tune vs use prompt engineering vs RAG? — *P0 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/cscareerquestions/)
- What is instruction tuning and how does it differ from pre-training? — *P0 · intermediate* [ai-engineering-field-guide](https://news.ycombinator.com/item?id=46319888)
- What is temperature and top-p sampling? How do they affect outputs? — *P0 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=yr5dRHrnbCo)
- At a high level, what choices define an architecture like LLaMA relative to the original transformer? — *P0 · intermediate* [personal repo]
- Compare how transformers and RNNs handle long-range dependencies in a sequence. — *P0 · intermediate* [personal repo]
- Compare word embeddings and sentence embeddings — when does each fit better? — *P0 · intermediate* [personal repo]
- How do CLIP and DALL-E each combine text and image data, and what did they make possible? — *P0 · intermediate* [personal repo]
- How does knowledge distillation let a smaller model benefit from a larger one? — *P0 · intermediate* [personal repo]
- How does masked self-attention in a transformer decoder differ from the regular (bidirectional) self-attention in an encoder? — *P0 · intermediate* [personal repo]
- How would you evaluate an NLP model's robustness to adversarial inputs? — *P0 · intermediate* [personal repo]
- What are contextual embeddings, and why do they outperform static word embeddings like word2vec? — *P0 · intermediate* [personal repo]
- What are ROUGE scores, and why are they the standard metric for summarization? — *P0 · intermediate* [personal repo]
- What are the fundamental limitations of the transformer architecture itself? — *P0 · intermediate* [personal repo]
- What are the practical limitations of RAG, and where does it fall short? — *P0 · intermediate* [personal repo]
- What are vector databases, and how do they differ from a traditional relational database? — *P0 · intermediate* [personal repo]
- What ethical considerations come up when deploying a RAG system in production? — *P0 · intermediate* [personal repo]
- What is domain adaptation, and how do you evaluate whether it worked after fine-tuning on domain-specific data? — *P0 · intermediate* [personal repo]
- What is multimodal AI, and why does it matter for modern ML applications? — *P0 · intermediate* [personal repo]
- _…and 11 more in the app._

### Module M — RAG (29 questions, P0)

_The most consistently asked GenAI system topic. The load-bearing question is diagnostic: is this failure retrieval or generation, and how do you know?_

- What are common RAG failure points and how do you debug them? — *P0 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/generativeAI/comments/1p4yrjk/how_to_clear_interviews_in_ai_gen_rag_llm/)
- What's RAG? Explain the complete process — *P0 · intermediate* [ai-engineering-field-guide](https://kaysnotes.medium.com/my-generative-ai-engineer-interview-experience-got-hired-6b3f1affc4e9)
- Explain Advanced RAGs: when is it the right choice, and what does it cost over the simpler option? — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Explain Agentic RAGs: when is it the right choice, and what does it cost over the simpler option? — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Explain Basic RAG: when is it the right choice, and what does it cost over the simpler option? — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Explain Multi-Modal RAGs: when is it the right choice, and what does it cost over the simpler option? — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Compare HNSW and IVF: what does each trade between recall, memory and build time? — *P0 · advanced* [curriculum spec]
- Dense retrieval vs BM25: which failure does each one have, and why do hybrid systems beat both? — *P0 · advanced* [curriculum spec]
- Explain HyDE. Why would generating a fake answer help you find the real one? — *P0 · advanced* [curriculum spec]
- How do you choose chunk size, and what does a too-small or too-large chunk actually break downstream? — *P0 · advanced* [curriculum spec]
- How do you combine sparse and dense scores in hybrid search without one dominating? — *P0 · advanced* [curriculum spec]
- How do you compress context without erasing the detail the answer depends on? — *P0 · advanced* [curriculum spec]
- How do you enforce metadata filtering and per-tenant access control inside a vector search without leaking across tenants? — *P0 · advanced* [curriculum spec]
- How do you evaluate retrieval separately from generation, and what metric do you use for each? — *P0 · advanced* [curriculum spec]
- How do you keep a RAG index fresh when the underlying documents change constantly? — *P0 · advanced* [curriculum spec]
- How do you produce citations that actually point at the span the claim came from? — *P0 · advanced* [curriculum spec]
- How would you scale a RAG system to 10M+ documents while keeping p99 under a second? — *P0 · advanced* [curriculum spec]
- Semantic chunking vs fixed-size: what does semantic chunking cost, and when is it worth it? — *P0 · advanced* [curriculum spec]
- What is chunk overlap for, and when does it stop helping? — *P0 · advanced* [curriculum spec]
- What is query rewriting for, and when does it make retrieval worse? — *P0 · advanced* [curriculum spec]
- _…and 9 more in the app._

### Module N — AI Agents (19 questions, P1)

_New as a distinct round. The senior signal is keeping permissions, budgets, retries and termination in deterministic code rather than in prompt text._

- How do you handle tool failures, retries, and idempotency? — *P0 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- What makes an AI system agentic? — *P0 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- What are the biggest security risks with tool-using agents? — *P0 · intermediate · Mistral* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- How do agents decide which tool to use? — *P0 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- How do you detect and stop infinite planning loops? — *P0 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- What are the essential components of an agent beyond an LLM? — *P0 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- How do you explain agentic systems to non-technical stakeholders? — *P1 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- How do you sandbox tool execution safely? — *P1 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- When agent is the wrong solution? — *P1 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- Design an agent that runs for hours across restarts. What is checkpointed, what is idempotent, and how does it resume without repeating side effects? — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)
- Build an agent reviewing code and suggesting improvements — *P1 · intermediate* [ai-engineering-field-guide](https://blog.promptlayer.com/the-agentic-system-design-interview-how-to-evaluate-ai-engineers/)
- How do you create an agent for analyzing customer support tickets, drafting responses, and escalating complex issues — *P1 · intermediate* [ai-engineering-field-guide](https://blog.promptlayer.com/the-agentic-system-design-interview-how-to-evaluate-ai-engineers/)
- How do you implement termination conditions in long-running agents? — *P1 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- How would you design observability and graceful fallbacks for an agent pipeline that calls an LLM and external tools? — *P1 · intermediate* [aakriti1318/interview_questions]
- How would you keep a multi-agent system's outputs consistent when several agents can act on shared state? — *P1 · intermediate* [aakriti1318/interview_questions]
- How would you manage context and memory for a very long-running conversation without blowing the context window? — *P1 · intermediate* [aakriti1318/interview_questions]
- What is a prompt injection attack, and how would you defend an agent that reads untrusted content? — *P1 · intermediate* [aakriti1318/interview_questions]
- What would you need to log and expose to make an agentic system auditable for compliance? — *P1 · intermediate* [aakriti1318/interview_questions]
- When would you build an agent platform in-house versus buy/adopt an existing framework? — *P1 · intermediate* [aakriti1318/interview_questions]

### Module O — Context Engineering (1 questions, P1)

_A 2026 module with no classical equivalent: what enters the context window is now a systems-design decision with cost, latency and correctness consequences._

- Your agent has access to 100 documents and 20 tools. How do you decide what enters the context, and how do you prove where each claim came from? — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)

### Module P — MCP / A2A / AI Protocols (2 questions, P2)

_Emerging and role-dependent, but the security half is asked well beyond agent roles._

- An agent can read private data and take actions. Walk through the threat model and the controls you would put in place. — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)
- Explain MCP and A2A: what each standardises, and why a protocol boundary is also a trust boundary. — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)

### Module Q — Multimodal AI (7 questions, P2)

_Rising. Strongly relevant for document-AI, search and assistant products._

- Design a document-intelligence pipeline: layout understanding, table extraction, and what you do when OCR is wrong. — *P2 · advanced* [curriculum spec]
- Design a visual search system: embedding choice, index, and how you handle near-duplicates. — *P2 · advanced* [curriculum spec]
- How do you evaluate a vision-language model on a task with no single correct answer? — *P2 · advanced* [curriculum spec]
- How does CLIP learn a shared image-text space, and what is the contrastive objective actually doing? — *P2 · advanced* [curriculum spec]
- How would you build a voice assistant end to end, and where does latency accumulate? — *P2 · advanced* [curriculum spec]
- How would you build multimodal RAG over documents that contain tables and diagrams? — *P2 · advanced* [curriculum spec]
- What breaks when you naively concatenate image and text embeddings, and what do fusion architectures do instead? — *P2 · advanced* [curriculum spec]

### Module R — ML System Design (42 questions, P0)

_One of the two largest modules. Every answer follows the same 20-point spine from requirements through failure modes; the spine is what separates a senior answer from a list of components._

- Design a fraud detection system. — *P0 · advanced* [AIMLInterviews](https://www.reddit.com/r/learnmachinelearning/comments/1pzcw2y/from_software_developer_to_ai_engineer_the_exact/)
- Design a chatbot system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a document search. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a food delivery time approximation. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a friends / follower recommendation. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a game recommendation. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a harmful content / Spam detection system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a healthcare diagnosis system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a language identification system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a multimodal harmful content detection. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a multimodal search. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a named entity linking system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a newsfeed system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a pedestrian jaywalking detection. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a place recommendation. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a proximity service / Yelp. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a question answering system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a rental recommendation. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a replacement product recommendation. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a ride matching system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- _…and 22 more in the app._

### Module S — GenAI System Design (42 questions, P0)

_Now frequently a separate round. The same design spine with a GenAI lens: models, prompting, context, RAG, caching, streaming, latency, cost, safety, evals, fallbacks._

- Design an AI chatbot (ChatGPT, Claude chat service) — *P0 · advanced · OpenAI* [ai-engineering-field-guide](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
- Design an LLM chatbot at scale. — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design an LLM-powered enterprise search or RAG assistant. — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design a code assistant / coding agent. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a content generation / summarization at scale. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a RAG document Q&A / "chat with your docs". — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an agentic workflow / AI assistant. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an enterprise / semantic search with LLM answers. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an LLM-based recommendation / personalization. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an LLM-powered customer-support chatbot. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a Document Q&A Assistant / RAG system — *P1 · advanced* [ai-engineering-field-guide](https://bhavishyapandit9.substack.com/p/7-deep-cut-ai-system-design-interview)
- Design an AI-powered Candidate Sourcing System — *P1 · advanced* [ai-engineering-field-guide](https://levelup.gitconnected.com/how-i-fought-and-passed-technical-interviews-with-llms-in-2025-f328e9df8e84)
- Design a content or policy-violation moderation system. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design a large-scale LLM inference and serving platform. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design a real-time LLM search engine. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design a recommendation or ranking system. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design an on-device or small-model LLM assistant. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design cross-conversation memory for a chat assistant. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design a large-scale AI model deployment system - model serving, GPU scaling, model versioning, result caching. (OpenAI) — *P1 · advanced · OpenAI* [ai-engineering-field-guide](https://www.designgurus.io/blog/openai-system-design-interview-questions)
- Design a unified query engine across dispersed data sources like email, calendar, documents, and chat — *P1 · advanced · Google* [ai-engineering-field-guide](https://x.com/_avichawla/status/1986320178783867036)
- _…and 22 more in the app._

### Module T — Agentic System Design (7 questions, P1)

_The 2026 addition to the design round. Must explicitly cover harness, orchestrator, permissions, checkpoints, recovery, approval, budgets and observability._

- Design a multi-agent research system that produces a cited report. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design a multi-step agentic workflow for support-ticket triage and resolution. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design a unified agent over email, calendar, docs, and chat. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design an agent that drafts customer replies and escalates complex cases. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design an AI coding assistant that reads code and suggests improvements. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design guardrails for an agent with access to private tools. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design the harness around an agent: what runs deterministically in code, and what is left to the model? — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)

### Module U — Production ML & MLOps (16 questions, P1)

_Training a model is not the end of the project. This module is where senior candidates separate from strong juniors._

- Compare batch and online (real-time) inference — what pushes a system toward one or the other? — *P1 · intermediate* [Production-Level-Deep-Learning]
- Compare data-parallel and model-parallel distributed training — when do you need each? — *P1 · intermediate* [Production-Level-Deep-Learning]
- Distinguish data drift from concept drift — how would you detect each in production? — *P1 · intermediate* [Production-Level-Deep-Learning]
- GPU vs. TPU vs. other accelerators for serving a large model — what's the real tradeoff? — *P1 · intermediate* [personal repo]
- How would you add caching to an LLM-based system, and what's actually safe to cache? — *P1 · intermediate* [personal repo]
- How would you design CI/CD for a machine learning pipeline, not just application code? — *P1 · intermediate* [Production-Level-Deep-Learning]
- How would you detect that an LLM's real-world performance has drifted since launch? — *P1 · intermediate* [personal repo]
- How would you shrink a model to fit a resource-constrained deployment target, like a phone? — *P1 · intermediate* [personal repo]
- Walk through the full lifecycle of a production ML system, from data collection to monitoring. — *P1 · intermediate* [Production-Level-Deep-Learning]
- What does a feature store solve that a shared feature-engineering script doesn't? — *P1 · intermediate* [Production-Level-Deep-Learning]
- What does an experiment-tracking system (e.g. MLflow-style) need to record to make a training run reproducible? — *P1 · intermediate* [Production-Level-Deep-Learning]
- What is a canary release or shadow deployment, and why not just replace the old model outright? — *P1 · intermediate* [Production-Level-Deep-Learning]
- What is training/serving skew, and how does it quietly break a model that worked fine in a notebook? — *P1 · intermediate* [Production-Level-Deep-Learning]
- What monitoring would tell you a deployed model is failing before your users complain? — *P1 · intermediate* [Production-Level-Deep-Learning]
- What would you actually monitor once an LLM-backed system is in production? — *P1 · intermediate* [personal repo]
- Why does data versioning matter as much as code versioning for a production ML system? — *P1 · intermediate* [Production-Level-Deep-Learning]

### Module V — LLMOps & AI Operations (6 questions, P1)

_The operational layer specific to LLM products: what you version, trace, cache, route and regression-test when the model is not yours._

- How do you measure hallucination rate in production? — *P0 · intermediate* [ai-engineering-field-guide](https://buildml.substack.com/p/top-24-llm-questions-asked-at-deepmind)
- How would you test a new model before full deployment? — *P1 · intermediate · Netflix* [ai-engineering-field-guide](https://x.com/akshay_pachaar/status/1990034795909582860)
- How do you monitor and observe autonomous agent behavior in production? — *P1 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/ExperiencedDevs/comments/1r78ipa/agentic_ai_agents_system_design_interview)
- What do you trace, log and alert on for an agent in production, and what question does each signal let you answer during an incident? — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)
- How would you evaluate and monitor a model in production, not just offline? — *P1 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/learnmachinelearning/comments/1pzcw2y/from_software_developer_to_ai_engineer_the_exact/)
- What operational/business metrics matter for AI systems? — *P1 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/developersIndia/comments/1pbaj11/need_advice_for_eightfoldai_agentic_ai_engineer)

### Module W — ML Infrastructure (15 questions, P2)

_P0 for infra-titled roles, P2 otherwise — but inference optimization has become general knowledge for anyone shipping LLM products._

- How do you reduce token costs? — *P0 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/cscareerquestions/)
- What is model tiering? When do you route to a small distilled model vs. a large LLM? — *P0 · intermediate* [ai-engineering-field-guide](https://www.interviewnode.com/post/generative-ai-system-design-interview-patterns-you-should-know)
- Cost vs. quality trade-offs: when is a small open-source model "good enough"? — *P1 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/learnmachinelearning/comments/1ppgsf3/interview_questions_gen_ai)
- How would you reduce p99 latency without reducing answer quality? — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- How would you route between small and large models? — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Scale an AI chat feature to 1M daily active users and cut cost. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- What is KV-cache and how does it help inference? — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- When would you use batching, continuous batching, quantization, or speculative decoding? — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Your app receives 1M LLM queries per day. How do you optimize cost? — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Your LLM feature costs too much and its p99 is too slow. Walk through the levers, in the order you would pull them. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)
- Estimate the budget for a RAG pipeline at enterprise scale (e.g., 300,000 legal contracts) — *P1 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/developersIndia/comments/1oq5fdi/got_an_interview_tomorrow_for_a_generative_ai)
- How do you reduce latency in GenAI applications? — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=Zt-h5BiBWH0)
- How would you benchmark each LLM call in a multi-step pipeline to identify latency bottlenecks? — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=leXRiJ5TuQo)
- What is time to first token and why does it matter for user experience? — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=leXRiJ5TuQo)
- Your app gets 1M queries/day - how do you optimize cost? — *P1 · intermediate* [ai-engineering-field-guide](https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main/interview/questions/01-theory.md)

### Module X — Recommendation Systems (6 questions, P1)

_P0 at Meta/Netflix/Amazon-style product companies. The two-tower / retrieval-then-rank structure is the single most reused system-design pattern in these loops._

- How we can incorporate implicit feedback (clicks, etc) into our recommender systems? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Possible approaches to solving the cold start problem? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What are good baselines when building a recommender system? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is a recommender system? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is collaborative filtering? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is the cold start problem? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)

### Module Y — Search & Information Retrieval (11 questions, P1)

_Underpins both classical search design and every RAG question in Module M._

- Can we formulate the search problem as a classification problem? How? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How can we get training data for our ranking algorithms? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How can we use machine learning for search? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do you do an online evaluation of a new ranking algorithm? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How would you evaluate your ranking algorithms? Which offline metrics would you use? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What are good unsupervised baselines for text information retrieval? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is mean average precision at k? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is precision and recall at k? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is the ranking problem? Which models can you use to solve them? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Do you know how to use gradient boosting trees for ranking? — *P1 · advanced* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How can we use clicks data as the training data for ranking algorithms? — *P1 · advanced* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)

### Module Z — ML Debugging (11 questions, P1)

_Scenario-driven. Each item is a symptom; the answer is an ordered investigation, not a guess. This is the module that most reliably finds the boundary of someone's understanding._

- A feature's distribution shifted in production. How do you detect it, and how do you decide whether to retrain or roll back? — *P0 · advanced* [curriculum spec]
- Aggregate metrics look fine but one user segment is being served badly. How do you find it and what do you do about it? — *P0 · advanced* [curriculum spec]
- An agent has started calling the same tool over and over until it hits the budget cap. Diagnose and fix it. — *P0 · advanced* [curriculum spec]
- Hallucination reports tripled this week. Nothing was deployed. Where do you look? — *P0 · advanced* [curriculum spec]
- Inference p99 latency doubled while p50 stayed flat. What does that pattern tell you, and what do you check first? — *P0 · advanced* [curriculum spec]
- Production accuracy dropped sharply overnight with no deploy. Diagnose it. — *P0 · advanced* [curriculum spec]
- The model scores well in training and offline eval but fails in production. What is the differential diagnosis? — *P0 · advanced* [curriculum spec]
- Training loss is still falling but validation loss has started rising. Walk me through your investigation. — *P0 · advanced* [curriculum spec]
- Your GPUs sit at 20% utilisation during training. Find the bottleneck. — *P0 · advanced* [curriculum spec]
- Your offline metric improved by 3% but the business KPI fell. What do you check, and in what order? — *P0 · advanced* [curriculum spec]
- Your RAG system is retrieving irrelevant documents for queries that used to work. Diagnose it. — *P0 · advanced* [curriculum spec]

### Module AA — ML Case Studies (52 questions, P1)

_Realistic constraints only: millions of users, latency budgets, missing labels, privacy limits, drift. Toy cases teach nothing that survives an interview follow-up._

- Case study — Airbnb: Amenity Detection and Beyond — New Frontiers of Computer Vision at Airbnb. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://medium.com/airbnb-engineering/amenity-detection-and-beyond-new-frontiers-of-computer-vision-at-airbnb-144a4441b72e)
- Case study — Airbnb: Categorizing Listing Photos at Airbnb. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://medium.com/airbnb-engineering/categorizing-listing-photos-at-airbnb-f9483f3ab7e3)
- Case study — Airbnb: Discovering and Classifying In-app Message Intent at Airbnb. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://medium.com/airbnb-engineering/discovering-and-classifying-in-app-message-intent-at-airbnb-6a55f5400a0c)
- Case study — Airbnb: Listing Embeddings in Search Ranking. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://medium.com/airbnb-engineering/listing-embeddings-for-similar-listing-recommendations-and-real-time-personalization-in-search-601172f7603e)
- Case study — Alibaba: Billion-scale Commodity Embedding for E-commerce Recommendation in Alibaba. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://arxiv.org/abs/1803.02349)
- Case study — Amazon: Amazon Search: The Joy of Ranking Products. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://www.amazon.science/publications/amazon-search-the-joy-of-ranking-products)
- Case study — Amazon: Amazon.com Recommendations: Item-to-Item Collaborative Filtering. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://ieeexplore.ieee.org/document/1167344)
- Case study — Amazon: Goal-Oriented End-to-End Conversational Models with Profile Features in a Real-World Setting. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://www.amazon.science/publications/goal-oriented-end-to-end-chatbots-with-profile-features-in-a-real-world-setting)
- Case study — Ant Financial: Uncovering Insurance Fraud Conspiracy with Network Learning. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://arxiv.org/abs/2002.12789)
- Case study — Deepomatic: How we Improved Computer Vision Metrics by More Than 5% Only by Cleaning Labelling Errors. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://deepomatic.com/en/how-we-improved-computer-vision-metrics-by-more-than-5-percent-only-by-cleaning-labelling-errors/)
- Case study — DoorDash: Retraining Machine Learning Models in the Wake of COVID-19. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://doordash.engineering/2020/09/15/retraining-ml-models-covid-19/)
- Case study — Dropbox: Creating a Modern OCR Pipeline Using Computer Vision and Deep Learning. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://dropbox.tech/machine-learning/creating-a-modern-ocr-pipeline-using-computer-vision-and-deep-learning)
- Case study — Etsy: An Ensemble-based Approach to Click-Through Rate Prediction for Promoted Listings at Etsy. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://arxiv.org/abs/1711.01377)
- Case study — Facebook: Powered by AI: Advancing product understanding and building new shopping experiences. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://ai.facebook.com/blog/powered-by-ai-advancing-product-understanding-and-building-new-shopping-experiences/)
- Case study — Gojek: Under the Hood of Gojek’s Automated Forecasting Tool. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://www.gojek.io/blog/under-the-hood-of-gojeks-automated-forecasting-tool)
- Case study — Google: BusTr: Predicting Bus Travel Times from Real-Time Traffic. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://dl.acm.org/doi/abs/10.1145/3394486.3403376)
- Case study — Google: Gmail Smart Compose: Real-Time Assisted Writing. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://arxiv.org/abs/1906.00080)
- Case study — Google: Learning to Diagnose with LSTM Recurrent Neural Networks. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://arxiv.org/abs/1511.03677)
- Case study — Google: Learning to Rank Recommendations with the k -Order Statistic Loss. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://dl.acm.org/doi/10.1145/2507157.2507210)
- Case study — Google: Prediction of Advertiser Churn for Google AdWords. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://research.google/pubs/pub36678/)
- _…and 32 more in the app._

### Module AB — AI Product & Business Reasoning (9 questions, P1)

_Tests engineering judgement rather than knowledge. The correct answer is often 'don't use ML for this', and saying so is the signal._

- Build vs buy for this AI capability: what factors decide it, and what would change your answer in a year? — *P1 · advanced* [curriculum spec]
- How would you measure the ROI of this ML system, and what would you do if it were negative? — *P1 · advanced* [curriculum spec]
- RAG or fine-tuning? Give the decision rule, not the definitions. — *P1 · advanced* [curriculum spec]
- The product wants 200ms p99 and the accurate model takes 900ms. What are your options? — *P1 · advanced* [curriculum spec]
- This problem could be solved with a rules engine or with ML. How do you decide, and what would make you choose the heuristic? — *P1 · advanced* [curriculum spec]
- When does a small model beat a large one in production, all-in? — *P1 · advanced* [curriculum spec]
- When is an LLM the wrong tool for a task that involves text? — *P1 · advanced* [curriculum spec]
- Where do you put a human in the loop, and what is the cost of putting them in the wrong place? — *P1 · advanced* [curriculum spec]
- Your LLM feature is profitable at 10k users and loss-making at 1M. What do you change? — *P1 · advanced* [curriculum spec]

### Module AC — Research & Paper Understanding (12 questions, P2)

_P0 for Applied Scientist and research-adjacent roles. Each paper is interrogated as problem → prior limitation → contribution → results → limitations._

- Attention Is All You Need (Vaswani et al., 2017) — what problem did it solve, what was the prior limitation, and what is the one idea that made it work? — *P1 · advanced* [curriculum spec](https://arxiv.org/abs/1706.03762)
- BERT (Devlin et al., 2018) — what problem did it solve, what was the prior limitation, and what is the one idea that made it work? — *P1 · advanced* [curriculum spec](https://arxiv.org/abs/1810.04805)
- CLIP (Radford et al., 2021) — what problem did it solve, what was the prior limitation, and what is the one idea that made it work? — *P1 · advanced* [curriculum spec](https://arxiv.org/abs/2103.00020)
- Deep Residual Learning (He et al., 2015) — what problem did it solve, what was the prior limitation, and what is the one idea that made it work? — *P1 · advanced* [curriculum spec](https://arxiv.org/abs/1512.03385)
- Direct Preference Optimization (Rafailov et al., 2023) — what problem did it solve, what was the prior limitation, and what is the one idea that made it work? — *P1 · advanced* [curriculum spec](https://arxiv.org/abs/2305.18290)
- FlashAttention (Dao et al., 2022) — what problem did it solve, what was the prior limitation, and what is the one idea that made it work? — *P1 · advanced* [curriculum spec](https://arxiv.org/abs/2205.14135)
- GPT-2 / GPT-3 (Radford et al., 2019; Brown et al., 2020) — what problem did it solve, what was the prior limitation, and what is the one idea that made it work? — *P1 · advanced* [curriculum spec](https://arxiv.org/abs/2005.14165)
- InstructGPT / RLHF (Ouyang et al., 2022) — what problem did it solve, what was the prior limitation, and what is the one idea that made it work? — *P1 · advanced* [curriculum spec](https://arxiv.org/abs/2203.02155)
- LoRA (Hu et al., 2021) — what problem did it solve, what was the prior limitation, and what is the one idea that made it work? — *P1 · advanced* [curriculum spec](https://arxiv.org/abs/2106.09685)
- QLoRA (Dettmers et al., 2023) — what problem did it solve, what was the prior limitation, and what is the one idea that made it work? — *P1 · advanced* [curriculum spec](https://arxiv.org/abs/2305.14314)
- Sparsely-Gated Mixture-of-Experts (Shazeer et al., 2017) — what problem did it solve, what was the prior limitation, and what is the one idea that made it work? — *P1 · advanced* [curriculum spec](https://arxiv.org/abs/1701.06538)
- Word2Vec (Mikolov et al., 2013) — what problem did it solve, what was the prior limitation, and what is the one idea that made it work? — *P1 · advanced* [curriculum spec](https://arxiv.org/abs/1301.3781)

### Module AD — Project Deep Dive (27 questions, P0)

_The ML-depth round, and the easiest to under-prepare because it is your own work. Structured as an interviewer attack tree that keeps descending until you stop having answers._

- What were the trade-offs you made, and are you still comfortable with them? — *P1 · intermediate · OpenAI, Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- Walk me through your most technically challenging project — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Walk through a recent technical project — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.tryexponent.com/questions?role=ml-engineer&type=behavioral)
- Why did you choose that particular approach over alternatives? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Did the solution actually work? How do you know? What metrics did you track? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- How did you communicate technical decisions to stakeholders? — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- How did you debug production issues? — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/)
- How did you handle data quality and preprocessing challenges? — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/)
- How do you monitor the model post-deployment for drift or degradation? — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/)
- How would you handle different requirements or scale constraints? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- Is there an actual eval framework here, or is it vibes-based? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Tell me about a recent/favorite project and some of the difficulties you had — *P1 · intermediate · Meta* [ai-engineering-field-guide](https://igotanoffer.com/blogs/tech/facebook-machine-learning-engineer-interview)
- Tell me about the greatest accomplishment of your career — *P1 · intermediate · Meta* [ai-engineering-field-guide](https://igotanoffer.com/blogs/tech/facebook-machine-learning-engineer-interview)
- What was the most challenging technical decision and how did you make it? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- What went wrong? What was harder than expected? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- What would you do differently if you started this project over? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- What would you explore next if you had more time? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- Why did you pick that particular tech stack for data processing? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Describe a challenging prompt engineering problem that you solved — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=Zt-h5BiBWH0)
- Describe a time you had to optimize an existing process or workflow for efficiency or scalability — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=Zt-h5BiBWH0)
- _…and 7 more in the app._

### Module AE — Responsible AI & Security (5 questions, P2)

_The security half (prompt injection, exfiltration, access control) has moved from P3 to genuinely expected for anyone building agents or RAG over private data._

- How do you protect against prompt injection and jailbreaking? — *P0 · intermediate* [ai-engineering-field-guide](https://www.systemdesignhandbook.com/guides/generative-ai-system-design-interview/)
- How do you handle data privacy and PII in prompts and logs? — *P1 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/learnmachinelearning/comments/1ppgsf3/interview_questions_gen_ai)
- How would you build a system that detects whether content violates policy or contains offensive material? — *P1 · intermediate* [ai-engineering-field-guide](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
- When and how would you implement LLM guardrails? — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=leXRiJ5TuQo)
- Your application generates code that gets executed. How do you prevent malicious code generation and execution? — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=leXRiJ5TuQo)

### Module AF — Behavioral & Leadership (38 questions, P0)

_Every loop has one, and at staff+ it is often the round that decides the level. STAR format, but the stories must carry technical depth, not just narrative._

- Tell me about a specific conflict with another person — *P0 · intermediate · OpenAI, Meta* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Tell me about yourself. — *P0 · intermediate* [AIMLInterviews](https://www.tryexponent.com/questions?role=ml-engineer&type=behavioral)
- Why do you want to work here? — *P0 · intermediate* [AIMLInterviews](https://www.tryexponent.com/questions?role=ml-engineer&type=behavioral)
- How do you manage projects under pressure? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/behavioral/behavior.md)
- How do you stay up-to-date on advances in ML? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/behavioral/behavior.md)
- How would you communicate technical challenges to non-technical stakeholders? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/behavioral/behavior.md)
- Tell me about a time you had a conflict with a team member. — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/behavioral/behavior.md)
- Tell me about a time you made a mistake. — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/behavioral/behavior.md)
- What's your proudest project? — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/behavioral/behavior.md)
- Describe a project that didn't go as planned or where your AI solution failed — *P1 · intermediate · Anthropic, DeepMind, Google* [ai-engineering-field-guide](https://www.interviewquery.com/interview-guides/anthropic)
- Tell me about a time you led an initiative or took ownership of a challenging task — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://igotanoffer.com/en/advice/openai-interview-questions)
- Describe a time you had to quickly learn a new technology or methodology — *P1 · intermediate* [ai-engineering-field-guide](https://www.interviewnode.com/post/acing-the-behavioral-interview-a-guide-for-ml-engineers-by-interviewnode)
- Tell me about a time you handled a difficult stakeholder — *P1 · intermediate* [ai-engineering-field-guide](https://www.tryexponent.com/questions?role=ml-engineer&type=behavioral)
- What side projects have you built with AI? What frameworks and models have you worked with? — *P1 · intermediate* [ai-engineering-field-guide](https://blog.promptlayer.com/the-agentic-system-design-interview-how-to-evaluate-ai-engineers/)
- What's a mistake you made, and what did you learn from it? — *P1 · intermediate* [ai-engineering-field-guide](https://www.interviewnode.com/post/acing-the-behavioral-interview-a-guide-for-ml-engineers-by-interviewnode)
- Describe a time you drove an architectural decision that affected multiple teams — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- Describe career decisions and cultural alignment — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- Describe failure impact and resolve cross-functional conflict — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- Discuss career decisions and culture fit — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- Discuss culture, collaboration, and mission alignment — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- _…and 18 more in the app._

## OUTPUT 3 — Top 200 Must-Know Questions

_200 of 724 shown, highest-ROI first._

- Tell me about a specific conflict with another person — *`AF` · P0 · intermediate · OpenAI, Meta* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Design an AI chatbot (ChatGPT, Claude chat service) — *`S` · P0 · advanced · OpenAI* [ai-engineering-field-guide](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
- How do you evaluate a chatbot? — *`F` · P0 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.reddit.com/r/cscareerquestions/)
- What is PEFT/LoRA and when would you use it? — *`L` · P0 · intermediate · Meta* [ai-engineering-field-guide](https://www.youtube.com/watch?v=yr5dRHrnbCo)
- What is the context window and what happens when you exceed it? How do you handle long documents? — *`L` · P0 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.youtube.com/watch?v=yr5dRHrnbCo)
- How do transformers work? — *`K` · P0 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=Zt-h5BiBWH0)
- How do you detect and mitigate hallucinations? — *`F` · P0 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/cscareerquestions/)
- How do you handle tool failures, retries, and idempotency? — *`N` · P0 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- How do you measure hallucination rate in production? — *`V` · P0 · intermediate* [ai-engineering-field-guide](https://buildml.substack.com/p/top-24-llm-questions-asked-at-deepmind)
- How do you protect against prompt injection and jailbreaking? — *`AE` · P0 · intermediate* [ai-engineering-field-guide](https://www.systemdesignhandbook.com/guides/generative-ai-system-design-interview/)
- How do you reduce token costs? — *`W` · P0 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/cscareerquestions/)
- Tell me about yourself. — *`AF` · P0 · intermediate* [AIMLInterviews](https://www.tryexponent.com/questions?role=ml-engineer&type=behavioral)
- What makes an AI system agentic? — *`N` · P0 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- What metrics do you consider when evaluating LLM performance? — *`F` · P0 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=leXRiJ5TuQo)
- When would you fine-tune vs use prompt engineering vs RAG? — *`L` · P0 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/cscareerquestions/)
- Why do you want to work here? — *`AF` · P0 · intermediate* [AIMLInterviews](https://www.tryexponent.com/questions?role=ml-engineer&type=behavioral)
- Design an LLM chatbot at scale. — *`S` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design an LLM-powered enterprise search or RAG assistant. — *`S` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- How do you manage projects under pressure? — *`AF` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/behavioral/behavior.md)
- How do you stay up-to-date on advances in ML? — *`AF` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/behavioral/behavior.md)
- How would you communicate technical challenges to non-technical stakeholders? — *`AF` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/behavioral/behavior.md)
- Tell me about a time you had a conflict with a team member. — *`AF` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/behavioral/behavior.md)
- Tell me about a time you made a mistake. — *`AF` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/behavioral/behavior.md)
- What's your proudest project? — *`AF` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/behavioral/behavior.md)
- What are the biggest security risks with tool-using agents? — *`N` · P0 · intermediate · Mistral* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- Design a fraud detection system. — *`R` · P0 · advanced* [AIMLInterviews](https://www.reddit.com/r/learnmachinelearning/comments/1pzcw2y/from_software_developer_to_ai_engineer_the_exact/)
- Explain the difference between encoder-only, decoder-only, and encoder-decoder Transformer architectures. When would you use each? — *`K` · P0 · intermediate* [ai-engineering-field-guide](https://github.com/TidorP/MLJobSearch2025)
- How do agents decide which tool to use? — *`N` · P0 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- How do you detect and stop infinite planning loops? — *`N` · P0 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- What are common RAG failure points and how do you debug them? — *`M` · P0 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/generativeAI/comments/1p4yrjk/how_to_clear_interviews_in_ai_gen_rag_llm/)
- What are the essential components of an agent beyond an LLM? — *`N` · P0 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- What is instruction tuning and how does it differ from pre-training? — *`L` · P0 · intermediate* [ai-engineering-field-guide](https://news.ycombinator.com/item?id=46319888)
- What is model tiering? When do you route to a small distilled model vs. a large LLM? — *`W` · P0 · intermediate* [ai-engineering-field-guide](https://www.interviewnode.com/post/generative-ai-system-design-interview-patterns-you-should-know)
- What is temperature and top-p sampling? How do they affect outputs? — *`L` · P0 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=yr5dRHrnbCo)
- What's RAG? Explain the complete process — *`M` · P0 · intermediate* [ai-engineering-field-guide](https://kaysnotes.medium.com/my-generative-ai-engineer-interview-experience-got-hired-6b3f1affc4e9)
- 1-D dynamic programming: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *`A` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- 2-D dynamic programming: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *`A` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Advanced graphs and greedy: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *`A` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- An agent can read private data and take actions. Walk through the threat model and the controls you would put in place. — *`P` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)
- Arrays, strings, and hashing: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *`A` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Assumptions about linear regression: 3 residual errors follow a normal distribution and — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Assumptions about logistic regression? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Backtracking: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *`A` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Binary search: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *`A` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Describe some criteria for model selection? Why is dimension reduction important? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Design a chatbot system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a code assistant / coding agent. — *`S` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a content generation / summarization at scale. — *`S` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a document search. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a food delivery time approximation. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a friends / follower recommendation. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a game recommendation. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a harmful content / Spam detection system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a healthcare diagnosis system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a language identification system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a multimodal harmful content detection. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a multimodal search. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a named entity linking system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a newsfeed system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a pedestrian jaywalking detection. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a place recommendation. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a proximity service / Yelp. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a question answering system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a RAG document Q&A / "chat with your docs". — *`S` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a rental recommendation. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a replacement product recommendation. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a ride matching system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a self-driving car. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a sentiment analysis system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a text query search (full text, semantic). — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a Video/Movie recommendation. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an ads click prediction. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an ads serving system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an agentic workflow / AI assistant. — *`S` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an autocompletion / typeahead suggestion system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an enterprise / semantic search with LLM answers. — *`S` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an event recommendation system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an image blurring system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an Image/Video search. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an LLM-based recommendation / personalization. — *`S` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an LLM-powered customer-support chatbot. — *`S` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an OCR/Text recognition system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design: Ad Click Prediction for Social Networks. — *`R` · P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design: Ad Click Prediction. — *`R` · P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design: Airbnb Search ranking. — *`R` · P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design: Estimate Delivery time. — *`R` · P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design: LinkedIn Feed Ranking. — *`R` · P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design: Youtube Recommendation. — *`R` · P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Explain Advanced RAGs: when is it the right choice, and what does it cost over the simpler option? — *`M` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Explain Agentic RAGs: when is it the right choice, and what does it cost over the simpler option? — *`M` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Explain all standard activation functions? tanh, relu, leakyRelu, sigmoid, softmax, softplus — *`H` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- explain bagging vs boosting — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain Basic RAG: when is it the right choice, and what does it cost over the simpler option? — *`M` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Explain boosting — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain collinearity: how is it possible to have negative coefficient in glm? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain how you select the best model? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain logistic regression? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain MAP — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain MCP and A2A: what each standardises, and why a protocol boundary is also a trust boundary. — *`P` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)
- Explain MLE — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain MLP: kind of fully connected feedforward neural network that use sigmoid or tanh as activation functions, widely used for classification task similar to logistic regression — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain Multi-Modal RAGs: when is it the right choice, and what does it cost over the simpler option? — *`M` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Explain PCA. What is physical intuition? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- explain random forest — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain RNN Problem — *`H` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain SVM — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain the concept of bias vs variance — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain the decision tree — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain TPE hyperparameter optimization. explain hyper optimization — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- general ML questions like generative v.s — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Graphs: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *`A` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- How do you choose the best model among all possible models? explain neural network assumptions of linear regression models if you have a large number of predictors how do you handle them? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- How do you find an anomaly in a distribution? How do you investigate that a certain trend in distribution is due to anomaly? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- how do you inspect missing data and when are they important? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- How does a neural network with one layer and one input and output compare to logistic regression? It’s the same with logistic regression if the NN is using sigmoid function and logistic regression? — *`H` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- How does the optimization algorithm work i.e to minimize the cost function? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- How GMM works (EM algorithm)? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- how to compare two regressions? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- how to handle unbalanced data? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Intervals: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *`A` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Is random forest bagging or boosting? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Linked lists: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *`A` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Math, geometry, and bit manipulation: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *`A` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Overfitting how to avoid — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- pros and cons of random forest and why — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Stack and monotonic stack: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *`A` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- SVM: how to choose the model and how to determine if a model is better than another — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Trees (BFS, DFS, BST): what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *`A` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Tries, heaps, and priority queues: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *`A` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Two pointers and sliding window: what in a problem statement tells you to reach for this, and what is the complexity you should quote? — *`A` · P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/lc-coding.md)
- Type of regularization, which one easier to use — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What are the different metrics to classify the dataset? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- what is cross-validation: the purpose is to estimate how a model performs on unseen data by partition data set into many sets and pick a model with higher? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is k-mean? What is kmean loss function? what kind of distance metric would you choose, what if different features have a different dynamic range Kmeans is an algorithm to group similar data points into the same groups? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is regularization? How does it solve bias, variance problems? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is selection bias? It is the bias introduced by the selection from groups that is not? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is the bias-variance tradeoff? How is XGBoost handling bias-variance tradeoff? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is the difference between type I vs type II error? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is the learning curve tool? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is the linear regression? What do the terms p-value, coefficient, and r-squared? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is the meaning of the contour visualization of the cost function in linear regression? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- When using the Gaussian mixture model, how do you know it is applicable? — *`D` · P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Your agent has access to 100 documents and 20 tools. How do you decide what enters the context, and how do you prove where each claim came from? — *`O` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)
- A feature's distribution shifted in production. How do you detect it, and how do you decide whether to retrain or roll back? — *`Z` · P0 · advanced* [curriculum spec]
- A fraud detector fires on 0.1% of transactions. The classifier has 99% sensitivity and 99% specificity. A transaction is flagged — what is the probability it is actually fraud, and what does that imply for the product? — *`C` · P0 · advanced* [curriculum spec]
- Aggregate metrics look fine but one user segment is being served badly. How do you find it and what do you do about it? — *`Z` · P0 · advanced* [curriculum spec]
- An agent has started calling the same tool over and over until it hits the budget cap. Diagnose and fix it. — *`Z` · P0 · advanced* [curriculum spec]
- Can we formulate the search problem as a classification problem? How? ‍ — *`Y` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Can we have both L1 and L2 regularization components in a linear model? ‍ — *`E` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Can we use L1 regularization for feature selection? ‍ — *`E` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Can we use L2 regularization for feature selection? ‍ — *`E` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Can you explain how cross-validation works? — *`E` · P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Can you tell us how you approach the model training process? ‍ — *`H` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Compare gradient descent, SGD, momentum, RMSprop and Adam. What problem does each one fix in its predecessor? — *`C` · P0 · intermediate* [curriculum spec]
- Compare HNSW and IVF: what does each trade between recall, memory and build time? — *`M` · P0 · advanced* [curriculum spec]
- Correlation is not causation — so what would you actually need to claim causation from observational data? — *`C` · P0 · advanced* [curriculum spec]
- Dense retrieval vs BM25: which failure does each one have, and why do hybrid systems beat both? — *`M` · P0 · advanced* [curriculum spec]
- Derive the gradient of the logistic loss with respect to the weights. — *`C` · P0 · advanced* [curriculum spec]
- Do we want to have a constant learning rate or we better change it throughout training? ‍ — *`H` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Do you know any dimensionality reduction techniques? ‍ — *`D` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Do you know how DBScan works? ‍ — *`D` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Do you know how K-means works? ‍ — *`D` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Encoder-only, decoder-only, encoder-decoder: what task shape does each suit, and why did decoder-only win for general LLMs? — *`K` · P0 · advanced* [curriculum spec]
- Expected value, variance and covariance: define them, then tell me what covariance fails to capture. — *`C` · P0 · beginner* [curriculum spec]
- Explain eigenvalues and eigenvectors in terms of what PCA is actually doing. — *`C` · P0 · intermediate* [curriculum spec]
- Explain HyDE. Why would generating a fake answer help you find the real one? — *`M` · P0 · advanced* [curriculum spec]
- Explain Mixture of Experts: what is sparse about it, and what new failure modes does routing introduce? — *`K` · P0 · advanced* [curriculum spec]
- Explain RoPE. Why does rotating the query and key make relative position fall out of the dot product? — *`K` · P0 · advanced* [curriculum spec]
- Explain the Central Limit Theorem and where people misuse it. — *`C` · P0 · intermediate* [curriculum spec]
- Feature importance in gradient boosting trees  —  what are possible options? ‍ — *`D` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Hallucination reports tripled this week. Nothing was deployed. Where do you look? — *`Z` · P0 · advanced* [curriculum spec]
- How can we get training data for our ranking algorithms? ‍ — *`Y` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How can we know which features are more important for the decision tree model? ‍ — *`D` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How can we use machine learning for search? ‍ — *`Y` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How can we use machine learning for text classification? ‍ — *`J` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we check if a variable follows the normal distribution? ‍ — *`D` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we choose K in K-fold cross-validation? What’s your favorite K? — *`E` · P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we decide when to stop training a neural net? — *`H` · P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we evaluate classification models? — *`D` · P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we handle categorical variables in decision trees? ‍ — *`D` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we interpret weights in linear models? ‍ — *`E` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we know how many trees we need in random forest? ‍ — *`D` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we select the depth of the trees in random forest? ‍ — *`D` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we select the right regularization parameters? — *`E` · P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we train decision trees? ‍ — *`D` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we use SGD (stochastic gradient descent) for training a neural net? ‍ — *`H` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do you choose chunk size, and what does a too-small or too-large chunk actually break downstream? — *`M` · P0 · advanced* [curriculum spec]
- How do you combine sparse and dense scores in hybrid search without one dominating? — *`M` · P0 · advanced* [curriculum spec]
- How do you compress context without erasing the detail the answer depends on? — *`M` · P0 · advanced* [curriculum spec]
- How do you do an online evaluation of a new ranking algorithm? ‍ — *`Y` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do you enforce metadata filtering and per-tenant access control inside a vector search without leaking across tenants? — *`M` · P0 · advanced* [curriculum spec]
- How do you evaluate retrieval separately from generation, and what metric do you use for each? — *`M` · P0 · advanced* [curriculum spec]
- How do you keep a RAG index fresh when the underlying documents change constantly? — *`M` · P0 · advanced* [curriculum spec]
- How do you produce citations that actually point at the span the claim came from? — *`M` · P0 · advanced* [curriculum spec]
- How do you select the number of trees in the gradient boosting model? ‍ — *`D` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How does a usual fully-connected feed-forward neural network work? ‍ — *`H` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How does L2 regularization look like in a linear model? ‍ — *`E` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How does max pooling work? Are there other pooling techniques? ‍ — *`I` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How is time series different from the usual regression problem? — *`D` · P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How L1 regularization looks like in a linear model? ‍ — *`E` · P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)

## OUTPUT 4 — Top Classical ML Questions

_40 of 119 shown, highest-ROI first._

- Assumptions about linear regression: 3 residual errors follow a normal distribution and — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Assumptions about logistic regression? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Describe some criteria for model selection? Why is dimension reduction important? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- explain bagging vs boosting — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain boosting — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain collinearity: how is it possible to have negative coefficient in glm? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain how you select the best model? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain logistic regression? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain MAP — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain MLE — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain MLP: kind of fully connected feedforward neural network that use sigmoid or tanh as activation functions, widely used for classification task similar to logistic regression — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain PCA. What is physical intuition? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- explain random forest — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain SVM — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain the concept of bias vs variance — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain the decision tree — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain TPE hyperparameter optimization. explain hyper optimization — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- general ML questions like generative v.s — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- How do you choose the best model among all possible models? explain neural network assumptions of linear regression models if you have a large number of predictors how do you handle them? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- How do you find an anomaly in a distribution? How do you investigate that a certain trend in distribution is due to anomaly? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- how do you inspect missing data and when are they important? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- How does the optimization algorithm work i.e to minimize the cost function? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- How GMM works (EM algorithm)? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- how to compare two regressions? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- how to handle unbalanced data? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Is random forest bagging or boosting? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Overfitting how to avoid — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- pros and cons of random forest and why — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- SVM: how to choose the model and how to determine if a model is better than another — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Type of regularization, which one easier to use — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What are the different metrics to classify the dataset? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- what is cross-validation: the purpose is to estimate how a model performs on unseen data by partition data set into many sets and pick a model with higher? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is k-mean? What is kmean loss function? what kind of distance metric would you choose, what if different features have a different dynamic range Kmeans is an algorithm to group similar data points into the same groups? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is regularization? How does it solve bias, variance problems? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is selection bias? It is the bias introduced by the selection from groups that is not? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is the bias-variance tradeoff? How is XGBoost handling bias-variance tradeoff? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is the difference between type I vs type II error? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is the learning curve tool? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is the linear regression? What do the terms p-value, coefficient, and r-squared? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- What is the meaning of the contour visualization of the cost function in linear regression? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)

## OUTPUT 5 — Top Deep Learning Questions

_31 of 31 shown, highest-ROI first._

- Explain all standard activation functions? tanh, relu, leakyRelu, sigmoid, softmax, softplus — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Explain RNN Problem — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- How does a neural network with one layer and one input and output compare to logistic regression? It’s the same with logistic regression if the NN is using sigmoid function and logistic regression? — *P0 · intermediate* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/questions.md)
- Can you tell us how you approach the model training process? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Do we want to have a constant learning rate or we better change it throughout training? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we decide when to stop training a neural net? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How do we use SGD (stochastic gradient descent) for training a neural net? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How does a usual fully-connected feed-forward neural network work? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How to set the learning rate? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- How we can initialize the weights of a neural network? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What are the problems with sigmoid as an activation function? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What happens when the learning rate is too large? Too small? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What if we set all the weights of a neural network to 0? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is Adam? What’s the main difference between Adam and SGD? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is backpropagation? How does it work? Why do we need it? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is dropout? Why is it useful? How does it work? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is model checkpointing? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What is ReLU? How is it better than sigmoid or tanh? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What kind of problems neural nets can solve? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What regularization techniques for neural nets do you know? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- What’s the learning rate? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- When would you use Adam and when SGD? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Which optimization techniques for training neural nets do you know? ‍ — *P0 · intermediate* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Why do we need activation functions? — *P0 · beginner* [data-science-interviews (CC BY 4.0)](https://github.com/alexeygrigorev/data-science-interviews/blob/master/theory.md)
- Beyond CNNs and RNNs, what other neural architectures exist, and when would you reach for each? — *P0 · intermediate* [personal repo]
- Compare stochastic and mini-batch gradient descent — what does the batch size actually trade off? — *P0 · intermediate* [personal repo]
- Distinguish discriminative and generative models — what does each actually learn to model? — *P0 · intermediate* [personal repo]
- How do you choose a loss function for a given model and task? — *P0 · intermediate* [personal repo]
- How do you choose the number of layers and neurons when sizing a neural network for a new problem? — *P0 · intermediate* [personal repo]
- What are activation functions for, and how do the common choices (ReLU, sigmoid, tanh, GELU) differ? — *P0 · intermediate* [personal repo]
- What does a vanilla RNN struggle with, independent of the vanishing-gradient problem specifically? — *P0 · intermediate* [personal repo]

## OUTPUT 6 — Top LLM / GenAI Questions

_40 of 51 shown, highest-ROI first._

- What is PEFT/LoRA and when would you use it? — *P0 · intermediate · Meta* [ai-engineering-field-guide](https://www.youtube.com/watch?v=yr5dRHrnbCo)
- What is the context window and what happens when you exceed it? How do you handle long documents? — *P0 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.youtube.com/watch?v=yr5dRHrnbCo)
- How do transformers work? — *P0 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=Zt-h5BiBWH0)
- When would you fine-tune vs use prompt engineering vs RAG? — *P0 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/cscareerquestions/)
- Explain the difference between encoder-only, decoder-only, and encoder-decoder Transformer architectures. When would you use each? — *P0 · intermediate* [ai-engineering-field-guide](https://github.com/TidorP/MLJobSearch2025)
- What is instruction tuning and how does it differ from pre-training? — *P0 · intermediate* [ai-engineering-field-guide](https://news.ycombinator.com/item?id=46319888)
- What is temperature and top-p sampling? How do they affect outputs? — *P0 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=yr5dRHrnbCo)
- Encoder-only, decoder-only, encoder-decoder: what task shape does each suit, and why did decoder-only win for general LLMs? — *P0 · advanced* [curriculum spec]
- Explain Mixture of Experts: what is sparse about it, and what new failure modes does routing introduce? — *P0 · advanced* [curriculum spec]
- Explain RoPE. Why does rotating the query and key make relative position fall out of the dot product? — *P0 · advanced* [curriculum spec]
- MHA vs MQA vs GQA: what is shared in each, and what does that do to quality and to memory bandwidth at decode time? — *P0 · advanced* [curriculum spec]
- What does FlashAttention change? It computes the same attention — so where does the speedup come from? — *P0 · advanced* [curriculum spec]
- What is causal masking, where exactly is it applied, and what goes wrong if it is applied after the softmax? — *P0 · advanced* [curriculum spec]
- What is the KV cache, what exactly is stored, and how does its size grow with batch size, sequence length and model width? — *P0 · advanced* [curriculum spec]
- What is the time and memory complexity of self-attention, and which of the two actually binds first in practice? — *P0 · advanced* [curriculum spec]
- Where are the compute-bound and memory-bound bottlenecks in Transformer inference, and how does that differ between prefill and decode? — *P0 · advanced* [curriculum spec]
- Why do Transformers beat RNNs on long sequences, given that attention is quadratic and an RNN is linear? — *P0 · advanced* [curriculum spec]
- Why does a Transformer need positional information at all, and what do sinusoidal, learned and RoPE encodings each trade off? — *P0 · advanced* [curriculum spec]
- Why does attention use three separate projections — Q, K and V — rather than comparing the inputs directly? — *P0 · advanced* [curriculum spec]
- Why is the dot product divided by sqrt(d_k)? What breaks if you remove it? — *P0 · advanced* [curriculum spec]
- Why multi-head attention rather than one larger head? What do different heads end up representing? — *P0 · advanced* [curriculum spec]
- At a high level, what choices define an architecture like LLaMA relative to the original transformer? — *P0 · intermediate* [personal repo]
- Compare how transformers and RNNs handle long-range dependencies in a sequence. — *P0 · intermediate* [personal repo]
- Compare word embeddings and sentence embeddings — when does each fit better? — *P0 · intermediate* [personal repo]
- How do CLIP and DALL-E each combine text and image data, and what did they make possible? — *P0 · intermediate* [personal repo]
- How does knowledge distillation let a smaller model benefit from a larger one? — *P0 · intermediate* [personal repo]
- How does masked self-attention in a transformer decoder differ from the regular (bidirectional) self-attention in an encoder? — *P0 · intermediate* [personal repo]
- How would you evaluate an NLP model's robustness to adversarial inputs? — *P0 · intermediate* [personal repo]
- What are contextual embeddings, and why do they outperform static word embeddings like word2vec? — *P0 · intermediate* [personal repo]
- What are ROUGE scores, and why are they the standard metric for summarization? — *P0 · intermediate* [personal repo]
- What are the fundamental limitations of the transformer architecture itself? — *P0 · intermediate* [personal repo]
- What are the practical limitations of RAG, and where does it fall short? — *P0 · intermediate* [personal repo]
- What are vector databases, and how do they differ from a traditional relational database? — *P0 · intermediate* [personal repo]
- What ethical considerations come up when deploying a RAG system in production? — *P0 · intermediate* [personal repo]
- What is domain adaptation, and how do you evaluate whether it worked after fine-tuning on domain-specific data? — *P0 · intermediate* [personal repo]
- What is multimodal AI, and why does it matter for modern ML applications? — *P0 · intermediate* [personal repo]
- What is triplet loss, and why is a margin parameter needed in the objective? — *P0 · intermediate* [personal repo]
- What makes indexing and searching high-dimensional vector spaces hard at scale? — *P0 · intermediate* [personal repo]
- What role can a knowledge graph play inside a RAG pipeline? — *P0 · intermediate* [personal repo]
- What role do the encoder and decoder each play in the original transformer architecture? — *P0 · intermediate* [personal repo]

## OUTPUT 7 — Top RAG Questions

_29 of 29 shown, highest-ROI first._

- What are common RAG failure points and how do you debug them? — *P0 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/generativeAI/comments/1p4yrjk/how_to_clear_interviews_in_ai_gen_rag_llm/)
- What's RAG? Explain the complete process — *P0 · intermediate* [ai-engineering-field-guide](https://kaysnotes.medium.com/my-generative-ai-engineer-interview-experience-got-hired-6b3f1affc4e9)
- Explain Advanced RAGs: when is it the right choice, and what does it cost over the simpler option? — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Explain Agentic RAGs: when is it the right choice, and what does it cost over the simpler option? — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Explain Basic RAG: when is it the right choice, and what does it cost over the simpler option? — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Explain Multi-Modal RAGs: when is it the right choice, and what does it cost over the simpler option? — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Compare HNSW and IVF: what does each trade between recall, memory and build time? — *P0 · advanced* [curriculum spec]
- Dense retrieval vs BM25: which failure does each one have, and why do hybrid systems beat both? — *P0 · advanced* [curriculum spec]
- Explain HyDE. Why would generating a fake answer help you find the real one? — *P0 · advanced* [curriculum spec]
- How do you choose chunk size, and what does a too-small or too-large chunk actually break downstream? — *P0 · advanced* [curriculum spec]
- How do you combine sparse and dense scores in hybrid search without one dominating? — *P0 · advanced* [curriculum spec]
- How do you compress context without erasing the detail the answer depends on? — *P0 · advanced* [curriculum spec]
- How do you enforce metadata filtering and per-tenant access control inside a vector search without leaking across tenants? — *P0 · advanced* [curriculum spec]
- How do you evaluate retrieval separately from generation, and what metric do you use for each? — *P0 · advanced* [curriculum spec]
- How do you keep a RAG index fresh when the underlying documents change constantly? — *P0 · advanced* [curriculum spec]
- How do you produce citations that actually point at the span the claim came from? — *P0 · advanced* [curriculum spec]
- How would you scale a RAG system to 10M+ documents while keeping p99 under a second? — *P0 · advanced* [curriculum spec]
- Semantic chunking vs fixed-size: what does semantic chunking cost, and when is it worth it? — *P0 · advanced* [curriculum spec]
- What is chunk overlap for, and when does it stop helping? — *P0 · advanced* [curriculum spec]
- What is query rewriting for, and when does it make retrieval worse? — *P0 · advanced* [curriculum spec]
- Why add a cross-encoder reranker when the retriever already ranked the results? — *P0 · advanced* [curriculum spec]
- Your RAG system gives a wrong answer. How do you determine whether the failure is in retrieval or in generation? — *P0 · advanced* [curriculum spec]
- What is semantic caching? — *P1 · intermediate* [ai-engineering-field-guide](https://www.designgurus.io/blog/system-design-for-rag)
- How do you handle citations and source attribution in a RAG system? — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=leXRiJ5TuQo)
- How do you scale a RAG system to 10M+ articles? — *P1 · intermediate* [ai-engineering-field-guide](https://bhavishyapandit9.substack.com/p/7-deep-cut-ai-system-design-interview)
- How would you handle the problem of a model hallucinating when no information is found in the given context? — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=Zt-h5BiBWH0)
- Text vs Vector search. When would you use each? — *P1 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/generativeAI/comments/1p4yrjk/how_to_clear_interviews_in_ai_gen_rag_llm/)
- What are the key tradeoffs when designing a RAG system? — *P1 · intermediate* [ai-engineering-field-guide](https://www.reddit.com/r/leetcode/comments/1rd6yki/technical_interview_for_genai_engineer_role_for_a)
- You're making a system for huge PDF reports. How would you process them? — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=leXRiJ5TuQo)

## OUTPUT 8 — Top Agentic AI Questions

_22 of 22 shown, highest-ROI first._

- How do you handle tool failures, retries, and idempotency? — *P0 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- What makes an AI system agentic? — *P0 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- What are the biggest security risks with tool-using agents? — *P0 · intermediate · Mistral* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- How do agents decide which tool to use? — *P0 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- How do you detect and stop infinite planning loops? — *P0 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- What are the essential components of an agent beyond an LLM? — *P0 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- An agent can read private data and take actions. Walk through the threat model and the controls you would put in place. — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)
- Explain MCP and A2A: what each standardises, and why a protocol boundary is also a trust boundary. — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)
- Your agent has access to 100 documents and 20 tools. How do you decide what enters the context, and how do you prove where each claim came from? — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)
- How do you explain agentic systems to non-technical stakeholders? — *P1 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- How do you sandbox tool execution safely? — *P1 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- When agent is the wrong solution? — *P1 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- Design an agent that runs for hours across restarts. What is checkpointed, what is idempotent, and how does it resume without repeating side effects? — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)
- Build an agent reviewing code and suggesting improvements — *P1 · intermediate* [ai-engineering-field-guide](https://blog.promptlayer.com/the-agentic-system-design-interview-how-to-evaluate-ai-engineers/)
- How do you create an agent for analyzing customer support tickets, drafting responses, and escalating complex issues — *P1 · intermediate* [ai-engineering-field-guide](https://blog.promptlayer.com/the-agentic-system-design-interview-how-to-evaluate-ai-engineers/)
- How do you implement termination conditions in long-running agents? — *P1 · intermediate* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- How would you design observability and graceful fallbacks for an agent pipeline that calls an LLM and external tools? — *P1 · intermediate* [aakriti1318/interview_questions]
- How would you keep a multi-agent system's outputs consistent when several agents can act on shared state? — *P1 · intermediate* [aakriti1318/interview_questions]
- How would you manage context and memory for a very long-running conversation without blowing the context window? — *P1 · intermediate* [aakriti1318/interview_questions]
- What is a prompt injection attack, and how would you defend an agent that reads untrusted content? — *P1 · intermediate* [aakriti1318/interview_questions]
- What would you need to log and expose to make an agentic system auditable for compliance? — *P1 · intermediate* [aakriti1318/interview_questions]
- When would you build an agent platform in-house versus buy/adopt an existing framework? — *P1 · intermediate* [aakriti1318/interview_questions]

## OUTPUT 9 — Top ML System Design Questions

_40 of 42 shown, highest-ROI first._

- Design a fraud detection system. — *P0 · advanced* [AIMLInterviews](https://www.reddit.com/r/learnmachinelearning/comments/1pzcw2y/from_software_developer_to_ai_engineer_the_exact/)
- Design a chatbot system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a document search. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a food delivery time approximation. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a friends / follower recommendation. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a game recommendation. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a harmful content / Spam detection system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a healthcare diagnosis system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a language identification system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a multimodal harmful content detection. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a multimodal search. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a named entity linking system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a newsfeed system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a pedestrian jaywalking detection. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a place recommendation. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a proximity service / Yelp. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a question answering system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a rental recommendation. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a replacement product recommendation. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a ride matching system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a self-driving car. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a sentiment analysis system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a text query search (full text, semantic). — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a Video/Movie recommendation. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an ads click prediction. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an ads serving system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an autocompletion / typeahead suggestion system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an event recommendation system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an image blurring system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an Image/Video search. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an OCR/Text recognition system. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design: Ad Click Prediction for Social Networks. — *P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design: Ad Click Prediction. — *P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design: Airbnb Search ranking. — *P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design: Estimate Delivery time. — *P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design: LinkedIn Feed Ranking. — *P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design: Youtube Recommendation. — *P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design an LLM-based question-answering system for a specific, complex domain (e.g. legal or medical). — *P0 · intermediate* [personal repo]
- Design an LLM-based system for code generation — what makes this harder than plain text generation? — *P0 · intermediate* [personal repo]
- How would you build a ChatGPT-like conversational system end to end? — *P0 · intermediate* [personal repo]

## OUTPUT 10 — Top GenAI System Design Questions

_40 of 42 shown, highest-ROI first._

- Design an AI chatbot (ChatGPT, Claude chat service) — *P0 · advanced · OpenAI* [ai-engineering-field-guide](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
- Design an LLM chatbot at scale. — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design an LLM-powered enterprise search or RAG assistant. — *P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design a code assistant / coding agent. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a content generation / summarization at scale. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a RAG document Q&A / "chat with your docs". — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an agentic workflow / AI assistant. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an enterprise / semantic search with LLM answers. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an LLM-based recommendation / personalization. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an LLM-powered customer-support chatbot. — *P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a Document Q&A Assistant / RAG system — *P1 · advanced* [ai-engineering-field-guide](https://bhavishyapandit9.substack.com/p/7-deep-cut-ai-system-design-interview)
- Design an AI-powered Candidate Sourcing System — *P1 · advanced* [ai-engineering-field-guide](https://levelup.gitconnected.com/how-i-fought-and-passed-technical-interviews-with-llms-in-2025-f328e9df8e84)
- Design a content or policy-violation moderation system. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design a large-scale LLM inference and serving platform. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design a real-time LLM search engine. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design a recommendation or ranking system. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design an on-device or small-model LLM assistant. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design cross-conversation memory for a chat assistant. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design a large-scale AI model deployment system - model serving, GPU scaling, model versioning, result caching. (OpenAI) — *P1 · advanced · OpenAI* [ai-engineering-field-guide](https://www.designgurus.io/blog/openai-system-design-interview-questions)
- Design a unified query engine across dispersed data sources like email, calendar, documents, and chat — *P1 · advanced · Google* [ai-engineering-field-guide](https://x.com/_avichawla/status/1986320178783867036)
- Design GitHub Actions — *P1 · advanced · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- Design Online Chess — *P1 · advanced · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- Design a content/policy violation detection system — *P1 · advanced* [ai-engineering-field-guide](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
- Design a distributed job queue for 100k+ GPU training jobs with preemption and checkpointing — *P1 · advanced* [ai-engineering-field-guide](https://www.reddit.com/r/leetcode/comments/1pjhw1i/xai_ai_engineer_backendinfra_interview_just/)
- Design a distributed key-value store (like DynamoDB / Cassandra) — *P1 · advanced* [ai-engineering-field-guide](https://levelup.gitconnected.com/how-i-fought-and-passed-technical-interviews-with-llms-in-2025-f328e9df8e84)
- Design a Hospital Voice Assistant (handle noise, privacy, latency, domain vocabulary) — *P1 · advanced* [ai-engineering-field-guide](https://bhavishyapandit9.substack.com/p/7-deep-cut-ai-system-design-interview)
- Design a Legal Contract Generation system with compliance requirements — *P1 · advanced* [ai-engineering-field-guide](https://bhavishyapandit9.substack.com/p/7-deep-cut-ai-system-design-interview)
- Design a multi-step agentic workflow (meeting scheduling, code review, email campaigns) — *P1 · advanced* [ai-engineering-field-guide](https://blog.promptlayer.com/the-agentic-system-design-interview-how-to-evaluate-ai-engineers/)
- Design a Perplexity.ai / real-time LLM-powered search engine — *P1 · advanced* [ai-engineering-field-guide](https://levelup.gitconnected.com/how-i-fought-and-passed-technical-interviews-with-llms-in-2025-f328e9df8e84)
- Design a rate limiter (global, per-user, distributed) — *P1 · advanced* [ai-engineering-field-guide](https://levelup.gitconnected.com/how-i-fought-and-passed-technical-interviews-with-llms-in-2025-f328e9df8e84)
- Design a scalable image-generation pipeline for millions of users — *P1 · advanced* [ai-engineering-field-guide](https://www.interviewnode.com/post/generative-ai-system-design-interview-patterns-you-should-know)
- Design a system that lets doctors automatically send billing info to insurers based on patient notes — *P1 · advanced* [ai-engineering-field-guide](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
- Design a system to process 10K user uploads/month (bank payslips, IDs, references) — *P1 · advanced* [ai-engineering-field-guide](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
- Design an AI co-pilot like GitHub Copilot — *P1 · advanced* [ai-engineering-field-guide](https://levelup.gitconnected.com/how-i-fought-and-passed-technical-interviews-with-llms-in-2025-f328e9df8e84)
- Design ChatGPT's cross-conversation memory feature — *P1 · advanced* [ai-engineering-field-guide](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
- Design Google Docs collaborative editing (real-time, eventually consistent) — *P1 · advanced* [ai-engineering-field-guide](https://levelup.gitconnected.com/how-i-fought-and-passed-technical-interviews-with-llms-in-2025-f328e9df8e84)
- Design Instagram / TikTok / X (timeline, posting, followers) — *P1 · advanced* [ai-engineering-field-guide](https://levelup.gitconnected.com/how-i-fought-and-passed-technical-interviews-with-llms-in-2025-f328e9df8e84)
- Design Uber (ride-sharing backend: matching, ETA, pricing surges) — *P1 · advanced* [ai-engineering-field-guide](https://levelup.gitconnected.com/how-i-fought-and-passed-technical-interviews-with-llms-in-2025-f328e9df8e84)
- Design WhatsApp / Messenger (1:1 + group chat at global scale) — *P1 · advanced* [ai-engineering-field-guide](https://levelup.gitconnected.com/how-i-fought-and-passed-technical-interviews-with-llms-in-2025-f328e9df8e84)
- Design YouTube / Netflix video streaming platform — *P1 · advanced* [ai-engineering-field-guide](https://levelup.gitconnected.com/how-i-fought-and-passed-technical-interviews-with-llms-in-2025-f328e9df8e84)

## OUTPUT 11 — Top Agentic System Design Questions

_7 of 7 shown, highest-ROI first._

- Design a multi-agent research system that produces a cited report. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design a multi-step agentic workflow for support-ticket triage and resolution. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design a unified agent over email, calendar, docs, and chat. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design an agent that drafts customer replies and escalates complex cases. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design an AI coding assistant that reads code and suggests improvements. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design guardrails for an agent with access to private tools. — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design the harness around an agent: what runs deterministically in code, and what is left to the model? — *P1 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)

## OUTPUT 12 — Top ML Coding Questions

_40 of 43 shown, highest-ROI first._

- Implement: LoRA update for a linear layer — *P0 · intermediate · Meta, Google, Anthropic, OpenAI, Databricks* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Append-only KV cache — *P0 · intermediate · Anthropic, OpenAI, Meta, Perplexity* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: k-means clustering — *P0 · intermediate · Uber, LinkedIn, Google, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Numerically stable softmax and cross-entropy — *P0 · beginner · Apple, Meta, Google, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Symmetric contrastive loss — *P0 · intermediate · OpenAI, Anthropic, DeepMind, Midjourney* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: k-nearest neighbors — *P0 · intermediate · Uber, LinkedIn, Meta* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Temperature, top-k, and top-p sampling — *P0 · intermediate · Anthropic, OpenAI, DeepMind* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: 2D convolution — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Binary metrics and ROC-AUC — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Build a causal attention mask — *P0 · beginner* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Classifier-free guidance combination — *P0 · beginner* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Decision-tree split — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Exact cosine top-k retrieval for RAG — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Feature standardization with training statistics — *P0 · beginner* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Learn and apply byte-pair encoding — *P0 · beginner* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Linear regression with gradient descent — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Linear SVM and hinge loss — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Matrix factorization for recommendations — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Missing values and unseen categories — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Multiclass metrics and macro averaging — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Multinomial Naive Bayes for text — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Pad variable-length token batches — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Perceptron learning rule — *P0 · beginner* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Permission-aware tool registry — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Planner/executor boundary — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Principal component analysis — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Reservoir sampling — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Retry with idempotency — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Sample-weighted losses and streaming metrics — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Scaled dot-product attention — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Sinusoidal positional encoding — *P0 · beginner* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Sliding-window conversation memory — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: TF-IDF — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Train/validation/test split without leakage — *P0 · beginner* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Uniform, weighted, and stratified sampling — *P0 · intermediate* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Validate JSON tool arguments — *P0 · beginner* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement logistic regression with SGD, L2 regularization, and early stopping in NumPy — *P1 · intermediate · Mistral* [ai-engineering-field-guide](https://www.datainterview.com/blog/mistral-machine-learning-engineer-interview)
- Debug code handling embeddings — *P1 · intermediate* [ai-engineering-field-guide](https://blog.promptlayer.com/the-agentic-system-design-interview-how-to-evaluate-ai-engineers/)
- Implement: Direct Preference Optimization loss — *P1 · advanced · Anthropic, OpenAI, DeepMind, Meta* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Logistic regression with gradient descent — *P1 · advanced · Google, Meta, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)

## OUTPUT 13 — Top Debugging Questions

_11 of 11 shown, highest-ROI first._

- A feature's distribution shifted in production. How do you detect it, and how do you decide whether to retrain or roll back? — *P0 · advanced* [curriculum spec]
- Aggregate metrics look fine but one user segment is being served badly. How do you find it and what do you do about it? — *P0 · advanced* [curriculum spec]
- An agent has started calling the same tool over and over until it hits the budget cap. Diagnose and fix it. — *P0 · advanced* [curriculum spec]
- Hallucination reports tripled this week. Nothing was deployed. Where do you look? — *P0 · advanced* [curriculum spec]
- Inference p99 latency doubled while p50 stayed flat. What does that pattern tell you, and what do you check first? — *P0 · advanced* [curriculum spec]
- Production accuracy dropped sharply overnight with no deploy. Diagnose it. — *P0 · advanced* [curriculum spec]
- The model scores well in training and offline eval but fails in production. What is the differential diagnosis? — *P0 · advanced* [curriculum spec]
- Training loss is still falling but validation loss has started rising. Walk me through your investigation. — *P0 · advanced* [curriculum spec]
- Your GPUs sit at 20% utilisation during training. Find the bottleneck. — *P0 · advanced* [curriculum spec]
- Your offline metric improved by 3% but the business KPI fell. What do you check, and in what order? — *P0 · advanced* [curriculum spec]
- Your RAG system is retrieving irrelevant documents for queries that used to work. Diagnose it. — *P0 · advanced* [curriculum spec]

## OUTPUT 14 — Top ML Case Studies

_40 of 52 shown, highest-ROI first._

- Case study — Airbnb: Amenity Detection and Beyond — New Frontiers of Computer Vision at Airbnb. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://medium.com/airbnb-engineering/amenity-detection-and-beyond-new-frontiers-of-computer-vision-at-airbnb-144a4441b72e)
- Case study — Airbnb: Categorizing Listing Photos at Airbnb. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://medium.com/airbnb-engineering/categorizing-listing-photos-at-airbnb-f9483f3ab7e3)
- Case study — Airbnb: Discovering and Classifying In-app Message Intent at Airbnb. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://medium.com/airbnb-engineering/discovering-and-classifying-in-app-message-intent-at-airbnb-6a55f5400a0c)
- Case study — Airbnb: Listing Embeddings in Search Ranking. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://medium.com/airbnb-engineering/listing-embeddings-for-similar-listing-recommendations-and-real-time-personalization-in-search-601172f7603e)
- Case study — Alibaba: Billion-scale Commodity Embedding for E-commerce Recommendation in Alibaba. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://arxiv.org/abs/1803.02349)
- Case study — Amazon: Amazon Search: The Joy of Ranking Products. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://www.amazon.science/publications/amazon-search-the-joy-of-ranking-products)
- Case study — Amazon: Amazon.com Recommendations: Item-to-Item Collaborative Filtering. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://ieeexplore.ieee.org/document/1167344)
- Case study — Amazon: Goal-Oriented End-to-End Conversational Models with Profile Features in a Real-World Setting. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://www.amazon.science/publications/goal-oriented-end-to-end-chatbots-with-profile-features-in-a-real-world-setting)
- Case study — Ant Financial: Uncovering Insurance Fraud Conspiracy with Network Learning. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://arxiv.org/abs/2002.12789)
- Case study — Deepomatic: How we Improved Computer Vision Metrics by More Than 5% Only by Cleaning Labelling Errors. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://deepomatic.com/en/how-we-improved-computer-vision-metrics-by-more-than-5-percent-only-by-cleaning-labelling-errors/)
- Case study — DoorDash: Retraining Machine Learning Models in the Wake of COVID-19. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://doordash.engineering/2020/09/15/retraining-ml-models-covid-19/)
- Case study — Dropbox: Creating a Modern OCR Pipeline Using Computer Vision and Deep Learning. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://dropbox.tech/machine-learning/creating-a-modern-ocr-pipeline-using-computer-vision-and-deep-learning)
- Case study — Etsy: An Ensemble-based Approach to Click-Through Rate Prediction for Promoted Listings at Etsy. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://arxiv.org/abs/1711.01377)
- Case study — Facebook: Powered by AI: Advancing product understanding and building new shopping experiences. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://ai.facebook.com/blog/powered-by-ai-advancing-product-understanding-and-building-new-shopping-experiences/)
- Case study — Gojek: Under the Hood of Gojek’s Automated Forecasting Tool. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://www.gojek.io/blog/under-the-hood-of-gojeks-automated-forecasting-tool)
- Case study — Google: BusTr: Predicting Bus Travel Times from Real-Time Traffic. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://dl.acm.org/doi/abs/10.1145/3394486.3403376)
- Case study — Google: Gmail Smart Compose: Real-Time Assisted Writing. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://arxiv.org/abs/1906.00080)
- Case study — Google: Learning to Diagnose with LSTM Recurrent Neural Networks. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://arxiv.org/abs/1511.03677)
- Case study — Google: Learning to Rank Recommendations with the k -Order Statistic Loss. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://dl.acm.org/doi/10.1145/2507157.2507210)
- Case study — Google: Prediction of Advertiser Churn for Google AdWords. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://research.google/pubs/pub36678/)
- Case study — Google: Smart Reply: Automated Response Suggestion for Email. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://research.google/pubs/pub45189/)
- Case study — Lazada: How Lazada Ranks Products to Improve Customer Experience and Conversion. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://www.slideshare.net/eugeneyan/how-lazada-ranks-products-to-improve-customer-experience-and-conversion)
- Case study — LinkedIn: Building Smart Replies for Member Messages. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://engineering.linkedin.com/blog/2017/10/building-smart-replies-for-member-messages)
- Case study — LinkedIn: Detecting and Preventing Abuse on LinkedIn using Isolation Forests. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://engineering.linkedin.com/blog/2019/isolation-forest)
- Case study — LinkedIn: High-Precision Phrase-Based Document Classification on a Modern Scale. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://engineering.linkedin.com/research/2011/high-precision-phrase-based-document-classification-on-a-modern-scale)
- Case study — LinkedIn: How Natural Language Processing Helps LinkedIn Members Get Support Easily. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://engineering.linkedin.com/blog/2019/04/how-natural-language-processing-help-support)
- Case study — LinkedIn: Learning to Rank Personalized Search Results in Professional Networks. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://arxiv.org/abs/1605.04624)
- Case study — LinkedIn: Preventing Abuse Using Unsupervised Learning. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://www.youtube.com/watch?v=sFRrFWYNAUI)
- Case study — LinkedIn: The Technology Behind Fighting Harassment on LinkedIn. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://engineering.linkedin.com/blog/2020/fighting-harassment)
- Case study — LinkedIn: Towards Deep and Representation Learning for Talent Search at LinkedIn. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://arxiv.org/abs/1809.06473)
- Case study — Microsoft: Making machines recognize and transcribe conversations in meetings using audio and video. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://www.microsoft.com/en-us/research/blog/making-machines-recognize-and-transcribe-conversations-in-meetings-using-audio-and-video/)
- Case study — Microsoft: Unit Test Case Generation with Transformers. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://arxiv.org/pdf/2009.05617.pdf)
- Case study — NAVER: Large-scale Item Categorization in e-Commerce Using Multiple Recurrent Neural Networks. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://www.kdd.org/kdd2016/subtopic/view/large-scale-item-categorization-in-e-commerce-using-multiple-recurrent-neur/)
- Case study — Netflix: Detecting Performance Anomalies in External Firmware Deployments. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://netflixtechblog.com/detecting-performance-anomalies-in-external-firmware-deployments-ed41b1bfcf46)
- Case study — Netflix: Learning a Personalized Homepage. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://netflixtechblog.com/learning-a-personalized-homepage-aa8ec670359a)
- Case study — Netflix: Netflix Recommendations: Beyond the 5 stars (Part 1. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://netflixtechblog.com/netflix-recommendations-beyond-the-5-stars-part-1-55838468f429)
- Case study — OpenAI: Better Language Models and Their Implications. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://openai.com/blog/better-language-models/)
- Case study — OpenAI: Language Models are Few-Shot Learners. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://arxiv.org/abs/2005.14165)
- Case study — Pixar: Deep Learned Super Resolution for Feature Film Production. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://graphics.pixar.com/library/SuperResolution/)
- Case study — Sears: Vector Representation Of Items, Customer And Cart To Build A Recommendation System. How would you have designed this, and where would your design have differed? — *P1 · advanced* [eugeneyan/applied-ml](https://arxiv.org/abs/1705.06338)

## OUTPUT 15 — Top Project Deep-Dive Questions

_27 of 27 shown, highest-ROI first._

- What were the trade-offs you made, and are you still comfortable with them? — *P1 · intermediate · OpenAI, Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- Walk me through your most technically challenging project — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Walk through a recent technical project — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.tryexponent.com/questions?role=ml-engineer&type=behavioral)
- Why did you choose that particular approach over alternatives? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Did the solution actually work? How do you know? What metrics did you track? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- How did you communicate technical decisions to stakeholders? — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- How did you debug production issues? — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/)
- How did you handle data quality and preprocessing challenges? — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/)
- How do you monitor the model post-deployment for drift or degradation? — *P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/)
- How would you handle different requirements or scale constraints? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- Is there an actual eval framework here, or is it vibes-based? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Tell me about a recent/favorite project and some of the difficulties you had — *P1 · intermediate · Meta* [ai-engineering-field-guide](https://igotanoffer.com/blogs/tech/facebook-machine-learning-engineer-interview)
- Tell me about the greatest accomplishment of your career — *P1 · intermediate · Meta* [ai-engineering-field-guide](https://igotanoffer.com/blogs/tech/facebook-machine-learning-engineer-interview)
- What was the most challenging technical decision and how did you make it? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- What went wrong? What was harder than expected? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- What would you do differently if you started this project over? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- What would you explore next if you had more time? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- Why did you pick that particular tech stack for data processing? — *P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Describe a challenging prompt engineering problem that you solved — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=Zt-h5BiBWH0)
- Describe a time you had to optimize an existing process or workflow for efficiency or scalability — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=Zt-h5BiBWH0)
- Tell me about a project you're most proud of, and what role you played — *P1 · intermediate* [ai-engineering-field-guide](https://www.youtube.com/watch?v=upwork-ai)
- Tell me about a technical challenge that you have overcome — *P1 · intermediate* [ai-engineering-field-guide](https://www.tryexponent.com/questions?role=ml-engineer&type=behavioral)
- Walk me through an AI project you built end-to-end — *P1 · intermediate* [ai-engineering-field-guide](https://medium.com/fonzi-ai/what-ive-learned-from-sitting-in-on-50-ai-engineer-interviews-c493696453c4)
- What business problem were you solving? Why was it a priority? — *P1 · intermediate* [ai-engineering-field-guide](https://medium.com/fonzi-ai/what-ive-learned-from-sitting-in-on-50-ai-engineer-interviews-c493696453c4)
- What was the outcome? How did stakeholders react? — *P1 · intermediate* [ai-engineering-field-guide](https://medium.com/fonzi-ai/what-ive-learned-from-sitting-in-on-50-ai-engineer-interviews-c493696453c4)
- What was your actual role in building this? — *P1 · intermediate* [ai-engineering-field-guide](https://medium.com/fonzi-ai/what-ive-learned-from-sitting-in-on-50-ai-engineer-interviews-c493696453c4)
- Who was the customer? Who benefited from this work? — *P1 · intermediate* [ai-engineering-field-guide](https://medium.com/fonzi-ai/what-ive-learned-from-sitting-in-on-50-ai-engineer-interviews-c493696453c4)

## OUTPUT 16 — Company-Specific Preparation

Only questions whose source explicitly ties them to a company appear here. This is a short list on purpose: the honest answer to "what does Meta ask?" is much smaller than any curriculum implies, and padding it with plausible-sounding guesses is what makes company-specific prep worthless.

| Company | Cited questions |
| --- | ---: |
| OpenAI | 32 |
| Anthropic | 21 |
| Meta | 10 |
| Google | 6 |
| DeepMind | 4 |
| Microsoft | 4 |
| Amazon | 3 |
| Mistral | 3 |
| Uber | 2 |
| LinkedIn | 2 |
| Apple | 1 |
| Perplexity | 1 |
| Databricks | 1 |
| Midjourney | 1 |
| Netflix | 1 |

### Meta (10 cited)

Concentrated in: B (6), AD (2), L (1), AF (1)

- Tell me about a specific conflict with another person — *`AF` · P0 · intermediate · OpenAI, Meta* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- What is PEFT/LoRA and when would you use it? — *`L` · P0 · intermediate · Meta* [ai-engineering-field-guide](https://www.youtube.com/watch?v=yr5dRHrnbCo)
- Implement: LoRA update for a linear layer — *`B` · P0 · intermediate · Meta, Google, Anthropic, OpenAI, Databricks* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Append-only KV cache — *`B` · P0 · intermediate · Anthropic, OpenAI, Meta, Perplexity* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Numerically stable softmax and cross-entropy — *`B` · P0 · beginner · Apple, Meta, Google, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: k-nearest neighbors — *`B` · P0 · intermediate · Uber, LinkedIn, Meta* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Tell me about a recent/favorite project and some of the difficulties you had — *`AD` · P1 · intermediate · Meta* [ai-engineering-field-guide](https://igotanoffer.com/blogs/tech/facebook-machine-learning-engineer-interview)
- Tell me about the greatest accomplishment of your career — *`AD` · P1 · intermediate · Meta* [ai-engineering-field-guide](https://igotanoffer.com/blogs/tech/facebook-machine-learning-engineer-interview)
- Implement: Direct Preference Optimization loss — *`B` · P1 · advanced · Anthropic, OpenAI, DeepMind, Meta* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Logistic regression with gradient descent — *`B` · P1 · advanced · Google, Meta, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)

### Amazon (3 cited)

Concentrated in: B (3)

- Implement: k-means clustering — *`B` · P0 · intermediate · Uber, LinkedIn, Google, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Numerically stable softmax and cross-entropy — *`B` · P0 · beginner · Apple, Meta, Google, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Logistic regression with gradient descent — *`B` · P1 · advanced · Google, Meta, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)

### Netflix (1 cited)

Concentrated in: V (1)

- How would you test a new model before full deployment? — *`V` · P1 · intermediate · Netflix* [ai-engineering-field-guide](https://x.com/akshay_pachaar/status/1990034795909582860)

### Google (6 cited)

Concentrated in: B (4), S (1), AF (1)

- Implement: LoRA update for a linear layer — *`B` · P0 · intermediate · Meta, Google, Anthropic, OpenAI, Databricks* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: k-means clustering — *`B` · P0 · intermediate · Uber, LinkedIn, Google, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Numerically stable softmax and cross-entropy — *`B` · P0 · beginner · Apple, Meta, Google, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Describe a project that didn't go as planned or where your AI solution failed — *`AF` · P1 · intermediate · Anthropic, DeepMind, Google* [ai-engineering-field-guide](https://www.interviewquery.com/interview-guides/anthropic)
- Design a unified query engine across dispersed data sources like email, calendar, documents, and chat — *`S` · P1 · advanced · Google* [ai-engineering-field-guide](https://x.com/_avichawla/status/1986320178783867036)
- Implement: Logistic regression with gradient descent — *`B` · P1 · advanced · Google, Meta, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)

### OpenAI (32 cited)

Concentrated in: AD (11), B (5), A (5), AF (5), S (4), L (1), F (1)

- Tell me about a specific conflict with another person — *`AF` · P0 · intermediate · OpenAI, Meta* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Design an AI chatbot (ChatGPT, Claude chat service) — *`S` · P0 · advanced · OpenAI* [ai-engineering-field-guide](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
- How do you evaluate a chatbot? — *`F` · P0 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.reddit.com/r/cscareerquestions/)
- What is the context window and what happens when you exceed it? How do you handle long documents? — *`L` · P0 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.youtube.com/watch?v=yr5dRHrnbCo)
- Implement: LoRA update for a linear layer — *`B` · P0 · intermediate · Meta, Google, Anthropic, OpenAI, Databricks* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Append-only KV cache — *`B` · P0 · intermediate · Anthropic, OpenAI, Meta, Perplexity* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Symmetric contrastive loss — *`B` · P0 · intermediate · OpenAI, Anthropic, DeepMind, Midjourney* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Temperature, top-k, and top-p sampling — *`B` · P0 · intermediate · Anthropic, OpenAI, DeepMind* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- What were the trade-offs you made, and are you still comfortable with them? — *`AD` · P1 · intermediate · OpenAI, Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- Tell me about a time you led an initiative or took ownership of a challenging task — *`AF` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://igotanoffer.com/en/advice/openai-interview-questions)
- Walk me through your most technically challenging project — *`AD` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Why did you choose that particular approach over alternatives? — *`AD` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Credits management system - track credit state across issued and used credits with different expiration rules and usage requirements, with increasing complexity — *`A` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Describe a time you drove an architectural decision that affected multiple teams — *`AF` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- Design a large-scale AI model deployment system - model serving, GPU scaling, model versioning, result caching. (OpenAI) — *`S` · P1 · advanced · OpenAI* [ai-engineering-field-guide](https://www.designgurus.io/blog/openai-system-design-interview-questions)
- Design GitHub Actions — *`S` · P1 · advanced · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- Design Online Chess — *`S` · P1 · advanced · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- Did the solution actually work? How do you know? What metrics did you track? — *`AD` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- How would you handle different requirements or scale constraints? — *`AD` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- In-Memory Database: Implement SQL-Like Operations — *`A` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- Is there an actual eval framework here, or is it vibes-based? — *`AD` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- LeetCode 2408: Design SQL — *`A` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- Refactor 100-120 lines of convoluted, deeply nested code — *`A` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Tell me about a time you mentored an engineer who went on to a senior role — *`AF` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- Unix cd command with symbolic link resolution — *`A` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- What was the most challenging technical decision and how did you make it? — *`AD` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- What went wrong? What was harder than expected? — *`AD` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- What would you do differently if you started this project over? — *`AD` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- What would you explore next if you had more time? — *`AD` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://www.hellointerview.com/guides/openai/l5)
- Why [company]? — *`AF` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Why did you pick that particular tech stack for data processing? — *`AD` · P1 · intermediate · OpenAI* [ai-engineering-field-guide](https://medium.com/exponent/what-its-actually-like-to-interview-at-openai-in-2026-03a646c9436c)
- Implement: Direct Preference Optimization loss — *`B` · P1 · advanced · Anthropic, OpenAI, DeepMind, Meta* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)

### Apple (1 cited)

Concentrated in: B (1)

- Implement: Numerically stable softmax and cross-entropy — *`B` · P0 · beginner · Apple, Meta, Google, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)

### Uber (2 cited)

Concentrated in: B (2)

- Implement: k-means clustering — *`B` · P0 · intermediate · Uber, LinkedIn, Google, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: k-nearest neighbors — *`B` · P0 · intermediate · Uber, LinkedIn, Meta* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)

### LinkedIn (2 cited)

Concentrated in: B (2)

- Implement: k-means clustering — *`B` · P0 · intermediate · Uber, LinkedIn, Google, Amazon* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: k-nearest neighbors — *`B` · P0 · intermediate · Uber, LinkedIn, Meta* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)

### Anthropic (21 cited)

Concentrated in: AF (8), AD (6), B (5), A (2)

- Implement: LoRA update for a linear layer — *`B` · P0 · intermediate · Meta, Google, Anthropic, OpenAI, Databricks* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Append-only KV cache — *`B` · P0 · intermediate · Anthropic, OpenAI, Meta, Perplexity* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Symmetric contrastive loss — *`B` · P0 · intermediate · OpenAI, Anthropic, DeepMind, Midjourney* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Temperature, top-k, and top-p sampling — *`B` · P0 · intermediate · Anthropic, OpenAI, DeepMind* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Describe a project that didn't go as planned or where your AI solution failed — *`AF` · P1 · intermediate · Anthropic, DeepMind, Google* [ai-engineering-field-guide](https://www.interviewquery.com/interview-guides/anthropic)
- What were the trade-offs you made, and are you still comfortable with them? — *`AD` · P1 · intermediate · OpenAI, Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- Walk through a recent technical project — *`AD` · P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.tryexponent.com/questions?role=ml-engineer&type=behavioral)
- Build a key-value database starting with basic operations (SET/GET/DELETE) — *`A` · P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/)
- Describe career decisions and cultural alignment — *`AF` · P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- Describe failure impact and resolve cross-functional conflict — *`AF` · P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- Discuss career decisions and culture fit — *`AF` · P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- Discuss culture, collaboration, and mission alignment — *`AF` · P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- How did you communicate technical decisions to stakeholders? — *`AD` · P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- How did you debug production issues? — *`AD` · P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/)
- How did you handle data quality and preprocessing challenges? — *`AD` · P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/)
- How do you lead under risk and uncertainty? — *`AF` · P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://prachub.com/companies/anthropic/categories/behavioral-and-leadership)
- How do you monitor the model post-deployment for drift or degradation? — *`AD` · P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/)
- Implement a website crawler (my personal experience) — *`A` · P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/)
- Tell me about a time when a technical misjudgment led to a project delay. What did you learn? — *`AF` · P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.linkjob.ai/interview-questions/anthropic-interview-process/)
- What would you do if, midway through a project, you realized it was unfeasible? — *`AF` · P1 · intermediate · Anthropic* [ai-engineering-field-guide](https://www.linkjob.ai/interview-questions/anthropic-interview-process/)
- Implement: Direct Preference Optimization loss — *`B` · P1 · advanced · Anthropic, OpenAI, DeepMind, Meta* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)

### DeepMind (4 cited)

Concentrated in: B (3), AF (1)

- Implement: Symmetric contrastive loss — *`B` · P0 · intermediate · OpenAI, Anthropic, DeepMind, Midjourney* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Implement: Temperature, top-k, and top-p sampling — *`B` · P0 · intermediate · Anthropic, OpenAI, DeepMind* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)
- Describe a project that didn't go as planned or where your AI solution failed — *`AF` · P1 · intermediate · Anthropic, DeepMind, Google* [ai-engineering-field-guide](https://www.interviewquery.com/interview-guides/anthropic)
- Implement: Direct Preference Optimization loss — *`B` · P1 · advanced · Anthropic, OpenAI, DeepMind, Meta* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)

### Perplexity (1 cited)

Concentrated in: B (1)

- Implement: Append-only KV cache — *`B` · P0 · intermediate · Anthropic, OpenAI, Meta, Perplexity* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)

### Databricks (1 cited)

Concentrated in: B (1)

- Implement: LoRA update for a linear layer — *`B` · P0 · intermediate · Meta, Google, Anthropic, OpenAI, Databricks* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)

### Midjourney (1 cited)

Concentrated in: B (1)

- Implement: Symmetric contrastive loss — *`B` · P0 · intermediate · OpenAI, Anthropic, DeepMind, Midjourney* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLC/ml-coding.md)

### Mistral (3 cited)

Concentrated in: N (1), F (1), B (1)

- What are the biggest security risks with tool-using agents? — *`N` · P0 · intermediate · Mistral* [ai-engineering-field-guide](https://medium.com/@techeon/the-complete-agentic-ai-system-design-interview-guide-2026)
- How do you debug a RAG chatbot giving confident but wrong answers? — *`F` · P1 · intermediate · Mistral* [ai-engineering-field-guide](https://www.reddit.com/r/cscareerquestions/)
- Implement logistic regression with SGD, L2 regularization, and early stopping in NumPy — *`B` · P1 · intermediate · Mistral* [ai-engineering-field-guide](https://www.datainterview.com/blog/mistral-machine-learning-engineer-interview)

### Microsoft (4 cited)

Concentrated in: A (2), AF (2)

- Find the Excel column name from its column number (e.g., column 702 = "AAA") — *`A` · P1 · intermediate · Microsoft* [ai-engineering-field-guide](https://www.reddit.com/r/csMajors/comments/1nqfzhq/microsoft_swe_applied_aiml_summer_2026_redmond)
- Open-ended behavioral at senior level: conflicts with managers, deadline pressure, design disagreements, mistakes — *`AF` · P1 · intermediate · Microsoft* [ai-engineering-field-guide](https://medium.com/@rohitverma_87831/microsoft-senior-engineer-interview-experience-2026-the-offer-that-took-me-three-attempts-e0d6e052bdb1)
- Reverse a linked list with constraints (AI-assisted coding round - candidate must prompt LLM effectively) — *`A` · P1 · intermediate · Microsoft* [ai-engineering-field-guide](https://www.reddit.com/r/csMajors/comments/1nqfzhq/microsoft_swe_applied_aiml_summer_2026_redmond)
- Why change now? — *`AF` · P1 · intermediate · Microsoft* [ai-engineering-field-guide](https://medium.com/@rohitverma_87831/microsoft-senior-engineer-interview-experience-2026-the-offer-that-took-me-three-attempts-e0d6e052bdb1)

## OUTPUT 17 — Senior Questions

_60 of 279 shown, highest-ROI first._

- Design an AI chatbot (ChatGPT, Claude chat service) — *`S` · P0 · advanced · OpenAI* [ai-engineering-field-guide](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
- Design an LLM chatbot at scale. — *`S` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design an LLM-powered enterprise search or RAG assistant. — *`S` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/06_interview_prep/genai-agentic-system-design.md)
- Design a fraud detection system. — *`R` · P0 · advanced* [AIMLInterviews](https://www.reddit.com/r/learnmachinelearning/comments/1pzcw2y/from_software_developer_to_ai_engineer_the_exact/)
- An agent can read private data and take actions. Walk through the threat model and the controls you would put in place. — *`P` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)
- Design a chatbot system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a code assistant / coding agent. — *`S` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a content generation / summarization at scale. — *`S` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a document search. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a food delivery time approximation. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a friends / follower recommendation. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a game recommendation. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a harmful content / Spam detection system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a healthcare diagnosis system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a language identification system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a multimodal harmful content detection. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a multimodal search. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a named entity linking system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a newsfeed system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a pedestrian jaywalking detection. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a place recommendation. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a proximity service / Yelp. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a question answering system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a RAG document Q&A / "chat with your docs". — *`S` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a rental recommendation. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a replacement product recommendation. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a ride matching system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a self-driving car. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a sentiment analysis system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a text query search (full text, semantic). — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design a Video/Movie recommendation. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an ads click prediction. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an ads serving system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an agentic workflow / AI assistant. — *`S` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an autocompletion / typeahead suggestion system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an enterprise / semantic search with LLM answers. — *`S` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an event recommendation system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an image blurring system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an Image/Video search. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an LLM-based recommendation / personalization. — *`S` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an LLM-powered customer-support chatbot. — *`S` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design an OCR/Text recognition system. — *`R` · P0 · advanced* [AIMLInterviews](https://github.com/alirezadir/AIMLInterviews/blob/main/src/MLSD/ml-system-design.md)
- Design: Ad Click Prediction for Social Networks. — *`R` · P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design: Ad Click Prediction. — *`R` · P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design: Airbnb Search ranking. — *`R` · P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design: Estimate Delivery time. — *`R` · P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design: LinkedIn Feed Ranking. — *`R` · P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Design: Youtube Recommendation. — *`R` · P0 · advanced* [khangich/machine-learning-interview](https://github.com/khangich/machine-learning-interview/blob/master/design.md)
- Explain Advanced RAGs: when is it the right choice, and what does it cost over the simpler option? — *`M` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Explain Agentic RAGs: when is it the right choice, and what does it cost over the simpler option? — *`M` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Explain Basic RAG: when is it the right choice, and what does it cost over the simpler option? — *`M` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Explain MCP and A2A: what each standardises, and why a protocol boundary is also a trust boundary. — *`P` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)
- Explain Multi-Modal RAGs: when is it the right choice, and what does it cost over the simpler option? — *`M` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/RAGs/README.md)
- Your agent has access to 100 documents and 20 tools. How do you decide what enters the context, and how do you prove where each claim came from? — *`O` · P0 · advanced* [Agentic-AI-Systems](https://github.com/alirezadir/Agentic-AI-Systems/blob/main/03_system_design/2026-agentic-ai-system-design.md)
- A feature's distribution shifted in production. How do you detect it, and how do you decide whether to retrain or roll back? — *`Z` · P0 · advanced* [curriculum spec]
- A fraud detector fires on 0.1% of transactions. The classifier has 99% sensitivity and 99% specificity. A transaction is flagged — what is the probability it is actually fraud, and what does that imply for the product? — *`C` · P0 · advanced* [curriculum spec]
- Aggregate metrics look fine but one user segment is being served badly. How do you find it and what do you do about it? — *`Z` · P0 · advanced* [curriculum spec]
- An agent has started calling the same tool over and over until it hits the budget cap. Diagnose and fix it. — *`Z` · P0 · advanced* [curriculum spec]
- Compare HNSW and IVF: what does each trade between recall, memory and build time? — *`M` · P0 · advanced* [curriculum spec]
- Correlation is not causation — so what would you actually need to claim causation from observational data? — *`C` · P0 · advanced* [curriculum spec]

## OUTPUT 18 — Resource Mapping

Which source produced the questions in each module.

| Module | Sources |
| --- | --- |
| A General Coding & DSA | AIMLInterviews (14), ai-engineering-field-guide (11), data-science-interviews (CC BY 4.0) (11) |
| B ML Coding | AIMLInterviews (41), ai-engineering-field-guide (2) |
| C Mathematics & Statistics | curriculum spec (12) |
| D Classical Machine Learning | data-science-interviews (CC BY 4.0) (72), khangich/machine-learning-interview (41), personal repo (6) |
| E ML Fundamentals & Breadth | data-science-interviews (CC BY 4.0) (28) |
| F Model Evaluation | ai-engineering-field-guide (9), Agentic-AI-Systems (1) |
| G Experimentation & A/B Testing | curriculum spec (10) |
| H Deep Learning | data-science-interviews (CC BY 4.0) (21), personal repo (7), khangich/machine-learning-interview (3) |
| I Computer Vision | data-science-interviews (CC BY 4.0) (13) |
| J NLP | data-science-interviews (CC BY 4.0) (14) |
| K Transformers | curriculum spec (14), ai-engineering-field-guide (6) |
| L Foundation Models & LLMs | personal repo (20), ai-engineering-field-guide (11) |
| M RAG | curriculum spec (16), ai-engineering-field-guide (9), Agentic-AI-Systems (4) |
| N AI Agents | ai-engineering-field-guide (12), aakriti1318/interview_questions (6), Agentic-AI-Systems (1) |
| O Context Engineering | Agentic-AI-Systems (1) |
| P MCP / A2A / AI Protocols | Agentic-AI-Systems (2) |
| Q Multimodal AI | curriculum spec (7) |
| R ML System Design | AIMLInterviews (31), khangich/machine-learning-interview (6), personal repo (5) |
| S GenAI System Design | ai-engineering-field-guide (27), Agentic-AI-Systems (8), AIMLInterviews (7) |
| T Agentic System Design | Agentic-AI-Systems (7) |
| U Production ML & MLOps | Production-Level-Deep-Learning (11), personal repo (5) |
| V LLMOps & AI Operations | ai-engineering-field-guide (5), Agentic-AI-Systems (1) |
| W ML Infrastructure | ai-engineering-field-guide (8), Agentic-AI-Systems (7) |
| X Recommendation Systems | data-science-interviews (CC BY 4.0) (6) |
| Y Search & Information Retrieval | data-science-interviews (CC BY 4.0) (11) |
| Z ML Debugging | curriculum spec (11) |
| AA ML Case Studies | eugeneyan/applied-ml (52) |
| AB AI Product & Business Reasoning | curriculum spec (9) |
| AC Research & Paper Understanding | curriculum spec (12) |
| AD Project Deep Dive | ai-engineering-field-guide (27) |
| AE Responsible AI & Security | ai-engineering-field-guide (5) |
| AF Behavioral & Leadership | ai-engineering-field-guide (30), AIMLInterviews (8) |

## OUTPUT 19 — Interview Readiness Checklist

Mastery is tracked per question on a 0-7 ladder, not a checkbox:

| Level | Meaning |
| ---: | --- |
| 0 | Never seen |
| 1 | Recognize |
| 2 | Can explain |
| 3 | Can solve |
| 4 | Can reason about trade-offs |
| 5 | Can answer follow-ups |
| 6 | Can design a production system |
| 7 | Can teach it |

**A question counts toward readiness only at level 4 or above.** Below that
it is recognition, and a progress bar that counts recognition as readiness
is the single easiest way to walk into an interview over-confident. The
module percentages in the app use this bar.
