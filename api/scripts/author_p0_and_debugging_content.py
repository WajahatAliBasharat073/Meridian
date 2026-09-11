"""One-time content authoring pass: fills the specific gaps
LEARNING_SYSTEM_AUDIT.md and scripts/curriculum_gap_report.py identified
-- P0 Foundations topics with zero questions (python_for_ml,
numpy_vectorization, pandas_data), backpropagation (zero questions, a
core P2 topic), three thin P0 math topics, and a bank-wide debugging-
format push (11 of 722 before this ran).

Every question here is hand-classified (`classification_confidence =
"adjudicated"`) rather than run through the keyword/submodule pipeline
-- these are new content, not reclassified existing content, so there is
nothing for that pipeline to classify. Axis convention follows what the
existing bank actually does (verified by inspecting real rows before
writing this): `concept` and `debugging` question types are axis
"knowledge" (they advance the learner's frontier); `coding` is axis
"format" (it's a different presentation of already-established
knowledge). `evidence="fundamental"` throughout -- none of this claims a
company asked it, so `companies=[]` trivially satisfies the anti-
fabrication check constraint. `frequency="unknown"` throughout for the
same reason: no real frequency data exists for brand-new questions,
saying so plainly rather than inventing "high".

Idempotent: checks each title against the database before inserting, so
re-running this after a partial failure does not create duplicates.

Usage:
    python -m scripts.author_p0_and_debugging_content --apply
    python -m scripts.author_p0_and_debugging_content          # dry run
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from dataclasses import dataclass, field

from sqlalchemy import func, select

from app.db import SessionLocal
from app.models.questions import Question

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


@dataclass
class NewQuestion:
    title: str
    topic: str
    phase: int
    question_type: str  # concept | debugging | coding
    cognitive_level: int
    difficulty: str  # beginner | intermediate | advanced | expert
    category: str
    module_code: str
    seniority: str = "mid"
    tests_for: str | None = None
    follow_ups: list[str] = field(default_factory=list)
    reference_solution: str | None = None
    answer_dimensions: list[str] = field(default_factory=list)

    @property
    def axis(self) -> str:
        return "format" if self.question_type == "coding" else "knowledge"

    @property
    def primary_format(self) -> str:
        return {"concept": "concept", "coding": "implementation", "debugging": "debugging"}[
            self.question_type
        ]


# ---------------------------------------------------------------- python_for_ml

PYTHON_FOR_ML = [
    NewQuestion(
        title="What's the practical difference between a Python list and a NumPy array, and why does it matter once you're doing numerical ML work?",
        topic="python_for_ml", phase=0, question_type="concept", cognitive_level=1,
        difficulty="beginner", category="ml_fundamentals", module_code="E", seniority="junior",
    ),
    NewQuestion(
        title="Why are raw Python for-loops slow for numerical computation, and what's the general strategy ML code uses to avoid them?",
        topic="python_for_ml", phase=0, question_type="concept", cognitive_level=2,
        difficulty="intermediate", category="ml_fundamentals", module_code="E",
    ),
    NewQuestion(
        title="What is a Python generator, and why would you reach for one when streaming a dataset that doesn't fit in memory?",
        topic="python_for_ml", phase=0, question_type="concept", cognitive_level=2,
        difficulty="intermediate", category="ml_fundamentals", module_code="E",
    ),
    NewQuestion(
        title="Why is a mutable default argument like `def f(x, cache=[])` a classic Python bug, and where does it actually bite in a training pipeline?",
        topic="python_for_ml", phase=0, question_type="concept", cognitive_level=2,
        difficulty="intermediate", category="ml_fundamentals", module_code="E",
    ),
    NewQuestion(
        title="What's the difference between `copy.copy` and `copy.deepcopy` in Python, and why does it matter when you're caching or mutating a config dict in an ML pipeline?",
        topic="python_for_ml", phase=0, question_type="concept", cognitive_level=2,
        difficulty="intermediate", category="ml_fundamentals", module_code="E",
    ),
    NewQuestion(
        title="Your data-loading pipeline is training-time-bound: the GPU sits idle between batches. Walk through how you'd diagnose whether it's a Python-side bottleneck and what you'd try first.",
        topic="python_for_ml", phase=0, question_type="debugging", cognitive_level=4,
        difficulty="advanced", category="ml_debugging", module_code="Z", seniority="senior",
        tests_for="An ordered diagnosis of a data-loading bottleneck: confirm GPU idle time first, then narrow to CPU-bound preprocessing, I/O, or single-process serialization before reaching for a fix.",
        follow_ups=[
            "How would you confirm the GPU is actually idle rather than just running fast?",
            "What's the difference between fixing this with more DataLoader workers versus fixing it with a different data format on disk?",
            "How would you tell if the bottleneck is CPU-bound preprocessing versus disk I/O?",
        ],
    ),
    NewQuestion(
        title="Implement: batch an iterable into fixed-size chunks without loading the whole sequence into memory.",
        topic="python_for_ml", phase=0, question_type="coding", cognitive_level=3,
        difficulty="intermediate", category="ml_coding", module_code="B",
        tests_for="A streaming chunking utility that works on any iterable (including a generator), not just a list -- and correctly yields a final short chunk instead of dropping or erroring on it.",
        answer_dimensions=["python", "iterators", "memory-efficiency"],
        reference_solution=(
            '"""Batch an iterable into fixed-size chunks, streaming -- never\n'
            "materializes the whole input in memory, so it works on a generator or\n"
            "a file iterator just as well as a list.\n\n"
            "Interview prompt: implement `chunked`, discuss why `itertools.islice`\n"
            "is the right tool here rather than slicing a list, and what happens\n"
            'on the final, possibly-short chunk.\n"""\n\n'
            "from __future__ import annotations\n\n"
            "from collections.abc import Iterable, Iterator\n"
            "from itertools import islice\n\n\n"
            "def chunked(iterable: Iterable, size: int) -> Iterator[list]:\n"
            "    if size <= 0:\n"
            '        raise ValueError("size must be positive")\n'
            "    it = iter(iterable)\n"
            "    while True:\n"
            "        batch = list(islice(it, size))\n"
            "        if not batch:\n"
            "            return\n"
            "        yield batch\n"
        ),
    ),
]

# ------------------------------------------------------------ numpy_vectorization

NUMPY_VECTORIZATION = [
    NewQuestion(
        title="What does 'vectorization' mean in NumPy, and why is `a + b` on two arrays faster than looping and adding element by element?",
        topic="numpy_vectorization", phase=0, question_type="concept", cognitive_level=1,
        difficulty="beginner", category="ml_fundamentals", module_code="E", seniority="junior",
    ),
    NewQuestion(
        title="Explain NumPy's broadcasting rules -- when can arrays of different shapes be combined in one operation, and when does it fail?",
        topic="numpy_vectorization", phase=0, question_type="concept", cognitive_level=2,
        difficulty="intermediate", category="ml_fundamentals", module_code="E",
    ),
    NewQuestion(
        title="What's the difference between a NumPy view and a copy, and why can modifying a slice silently change the original array?",
        topic="numpy_vectorization", phase=0, question_type="concept", cognitive_level=2,
        difficulty="intermediate", category="ml_fundamentals", module_code="E",
    ),
    NewQuestion(
        title="Why is `np.dot` / `@` preferred over a hand-written triple-nested loop for matrix multiplication, beyond just raw speed?",
        topic="numpy_vectorization", phase=0, question_type="concept", cognitive_level=2,
        difficulty="intermediate", category="ml_fundamentals", module_code="E",
    ),
    NewQuestion(
        title="Why does `array.reshape(...)` sometimes fail with 'cannot reshape array of size X into shape Y', and what has to be true of a reshape for it to be valid?",
        topic="numpy_vectorization", phase=0, question_type="concept", cognitive_level=2,
        difficulty="intermediate", category="ml_fundamentals", module_code="E",
    ),
    NewQuestion(
        title="A NumPy operation you expected to broadcast is instead throwing a `ValueError: operands could not be broadcast together`. Walk through how you'd diagnose the shape mismatch.",
        topic="numpy_vectorization", phase=0, question_type="debugging", cognitive_level=4,
        difficulty="advanced", category="ml_debugging", module_code="Z", seniority="senior",
        tests_for="Diagnosing a broadcasting failure by actually comparing the two shapes dimension-by-dimension from the trailing axis, not guessing-and-checking with random reshapes.",
        follow_ups=[
            "How would you fix it if the intent was to broadcast a per-row vector, but the shapes are (n,) and (n, m)?",
            "What's the fastest way to check both arrays' shapes without adding print statements everywhere?",
        ],
    ),
    NewQuestion(
        title="Implement: a numerically stable row-wise softmax over a matrix of logits, without overflowing for large values.",
        topic="numpy_vectorization", phase=0, question_type="coding", cognitive_level=3,
        difficulty="intermediate", category="ml_coding", module_code="B",
        tests_for="The max-subtraction trick for numerical stability, applied per-row (axis=1) with keepdims so the subtraction and final division broadcast correctly.",
        answer_dimensions=["numpy", "numerical-stability", "softmax"],
        reference_solution=(
            '"""Row-wise softmax over a matrix of logits, numerically stable via\n'
            "the max-subtraction trick: subtracting each row's max before\n"
            "exponentiating does not change the softmax's value (it cancels in\n"
            "the ratio) but keeps every exponent <= 0, so it can never overflow\n"
            "the way exp(1000) would.\n\n"
            "Interview prompt: implement it, and explain why subtracting the max\n"
            "is safe and why summing along axis=1 with keepdims=True matters.\n"
            '"""\n\n'
            "from __future__ import annotations\n\n"
            "import numpy as np\n\n\n"
            "def softmax(logits: np.ndarray) -> np.ndarray:\n"
            "    shifted = logits - np.max(logits, axis=1, keepdims=True)\n"
            "    exp = np.exp(shifted)\n"
            "    return exp / np.sum(exp, axis=1, keepdims=True)\n"
        ),
    ),
]

# ------------------------------------------------------------------- pandas_data

PANDAS_DATA = [
    NewQuestion(
        title="What's the difference between `.loc` and `.iloc` in pandas?",
        topic="pandas_data", phase=0, question_type="concept", cognitive_level=1,
        difficulty="beginner", category="ml_fundamentals", module_code="E", seniority="junior",
    ),
    NewQuestion(
        title="When should you reach for a vectorized pandas operation over `.apply()`, and when does `.apply()` actually make sense?",
        topic="pandas_data", phase=0, question_type="concept", cognitive_level=2,
        difficulty="intermediate", category="ml_fundamentals", module_code="E",
    ),
    NewQuestion(
        title="What is a `SettingWithCopyWarning` in pandas, and what's actually going wrong under the hood when you see one?",
        topic="pandas_data", phase=0, question_type="concept", cognitive_level=2,
        difficulty="intermediate", category="ml_fundamentals", module_code="E",
    ),
    NewQuestion(
        title="What can make a merge/join between two large DataFrames slow or blow up memory, and how would you avoid it?",
        topic="pandas_data", phase=0, question_type="concept", cognitive_level=3,
        difficulty="advanced", category="ml_fundamentals", module_code="E",
    ),
    NewQuestion(
        title="What's the difference between a pandas Series and a single-column DataFrame, and where does that distinction actually trip people up?",
        topic="pandas_data", phase=0, question_type="concept", cognitive_level=1,
        difficulty="beginner", category="ml_fundamentals", module_code="E", seniority="junior",
    ),
    NewQuestion(
        title="A groupby-aggregation that used to run in seconds now takes minutes after the input grew 3x. Walk through how you'd find the actual bottleneck.",
        topic="pandas_data", phase=0, question_type="debugging", cognitive_level=4,
        difficulty="advanced", category="ml_debugging", module_code="Z", seniority="senior",
        tests_for="Checking dtype bloat (object columns forcing slow Python-level iteration), cardinality of the group key, and whether the aggregation function itself is vectorized, before assuming it's 'just more data'.",
        follow_ups=[
            "Would switching to a categorical dtype for the group key help, and why?",
            "How would you tell if the slowdown is superlinear (something worse than the 3x data growth) versus just proportional?",
        ],
    ),
    NewQuestion(
        title="Implement: given a DataFrame of timestamped user events, compute each user's number of distinct active days in the trailing 7 days, as of each day they were active.",
        topic="pandas_data", phase=0, question_type="coding", cognitive_level=3,
        difficulty="advanced", category="ml_coding", module_code="B",
        tests_for="Deduping to one row per (user, day) before rolling, then using a time-based rolling window (not a fixed row-count window) so gaps in activity are handled correctly.",
        answer_dimensions=["pandas", "time-series", "groupby"],
        reference_solution=(
            '"""For each user and each day they were active, count how many\n'
            "distinct days out of the trailing 7 (including today) they were also\n"
            "active -- a simple recency/engagement feature.\n\n"
            "Interview prompt: implement it, and explain why you dedupe to one\n"
            "row per (user, day) before rolling, and why a time-based\n"
            'rolling("7D") window is used instead of a fixed-row-count window.\n'
            '"""\n\n'
            "from __future__ import annotations\n\n"
            "import pandas as pd\n\n\n"
            "def rolling_active_days(events: pd.DataFrame) -> pd.DataFrame:\n"
            '    daily = (\n        events.assign(day=pd.to_datetime(events["timestamp"]).dt.normalize())\n'
            '        .drop_duplicates(subset=["user_id", "day"])\n'
            '        .sort_values(["user_id", "day"])\n'
            "    )\n"
            '    daily = daily.set_index("day")\n'
            '    daily["active_days_last_7"] = (\n'
            '        daily.groupby("user_id")["user_id"]\n'
            '        .rolling("7D")\n'
            "        .count()\n"
            "        .reset_index(level=0, drop=True)\n"
            "    )\n"
            '    return daily.reset_index()[["user_id", "day", "active_days_last_7"]]\n'
        ),
    ),
]

# ------------------------------------------------------------------ backpropagation

BACKPROPAGATION = [
    NewQuestion(
        title="In plain terms, what problem does backpropagation solve, and why can't you just guess-and-check every weight individually?",
        topic="backpropagation", phase=2, question_type="concept", cognitive_level=1,
        difficulty="beginner", category="deep_learning", module_code="H", seniority="junior",
    ),
    NewQuestion(
        title="Derive the gradient of a single hidden layer's loss with respect to its weights using the chain rule, starting from the output error.",
        topic="backpropagation", phase=2, question_type="concept", cognitive_level=3,
        difficulty="advanced", category="deep_learning", module_code="H",
    ),
    NewQuestion(
        title="What is a computational graph, and how does the forward pass through it differ from the backward pass?",
        topic="backpropagation", phase=2, question_type="concept", cognitive_level=2,
        difficulty="intermediate", category="deep_learning", module_code="H",
    ),
    NewQuestion(
        title="Why do gradients vanish in deep networks that use sigmoid or tanh activations, and how does switching to ReLU help?",
        topic="backpropagation", phase=2, question_type="concept", cognitive_level=3,
        difficulty="advanced", category="deep_learning", module_code="H",
    ),
    NewQuestion(
        title="Why do gradients explode in deep or recurrent networks, mathematically, and what are the standard mitigations?",
        topic="backpropagation", phase=2, question_type="concept", cognitive_level=3,
        difficulty="advanced", category="deep_learning", module_code="H",
    ),
    NewQuestion(
        title="How does numerical gradient checking work, and why is it used only to verify backprop's correctness rather than to actually train a network?",
        topic="backpropagation", phase=2, question_type="concept", cognitive_level=2,
        difficulty="intermediate", category="deep_learning", module_code="H",
    ),
    NewQuestion(
        title="Your network's loss goes to NaN after a few hundred training steps. Walk through how you'd determine whether this is an exploding-gradient problem, and how you'd fix it if so.",
        topic="backpropagation", phase=2, question_type="debugging", cognitive_level=4,
        difficulty="advanced", category="ml_debugging", module_code="Z", seniority="senior",
        tests_for="An ordered diagnosis (check gradient norms before assuming exploding gradients specifically; rule out a bad learning rate or a data issue like an unnormalized input first) rather than jumping straight to gradient clipping.",
        follow_ups=[
            "What's the difference between fixing this with gradient clipping versus fixing it with a lower learning rate or better initialization?",
            "How would you distinguish an exploding-gradient NaN from a NaN caused by a divide-by-zero or log(0) elsewhere in the loss?",
        ],
    ),
    NewQuestion(
        title="Implement: manual forward and backward pass for a 2-layer (one hidden layer) network with sigmoid activations and MSE loss, using only NumPy.",
        topic="backpropagation", phase=2, question_type="coding", cognitive_level=3,
        difficulty="advanced", category="ml_coding", module_code="B",
        tests_for="Correctly applying the chain rule layer-by-layer: dL/dy_hat through the sigmoid derivative to get dz2, then back through w2 to da1 and the layer-1 sigmoid derivative to get dz1, with weight gradients as the correct matrix product at each layer.",
        answer_dimensions=["deep-learning", "backpropagation", "numpy"],
        reference_solution=(
            '"""Forward and backward pass for a 2-layer network (one hidden\n'
            "layer, sigmoid activations, MSE loss) implemented from scratch --\n"
            "the point of the exercise is applying the chain rule by hand, not\n"
            "using autograd.\n\n"
            "Interview prompt: implement `forward` and `backward`, and be able to\n"
            'explain each backward-pass line as "this is dL/d(that quantity)".\n'
            '"""\n\n'
            "from __future__ import annotations\n\n"
            "import numpy as np\n\n\n"
            "def sigmoid(z: np.ndarray) -> np.ndarray:\n"
            "    return 1.0 / (1.0 + np.exp(-z))\n\n\n"
            "def forward(x, w1, b1, w2, b2):\n"
            "    z1 = x @ w1 + b1\n"
            "    a1 = sigmoid(z1)\n"
            "    z2 = a1 @ w2 + b2\n"
            "    y_hat = sigmoid(z2)\n"
            "    cache = (x, z1, a1, z2, y_hat)\n"
            "    return y_hat, cache\n\n\n"
            "def backward(y, cache, w2):\n"
            "    x, z1, a1, z2, y_hat = cache\n"
            "    m = y.size  # total elements -- mean() below averages over all of them,\n"
            "    # not just rows, so the gradient must divide by the same count.\n\n"
            "    # dL/dz2: MSE loss (mean((y_hat - y) ** 2)) through sigmoid.\n"
            "    dL_dyhat = 2.0 * (y_hat - y) / m\n"
            "    dyhat_dz2 = y_hat * (1 - y_hat)\n"
            "    dz2 = dL_dyhat * dyhat_dz2\n\n"
            "    dw2 = a1.T @ dz2\n"
            "    db2 = dz2.sum(axis=0)\n\n"
            "    da1 = dz2 @ w2.T\n"
            "    dz1 = da1 * a1 * (1 - a1)\n\n"
            "    dw1 = x.T @ dz1\n"
            "    db1 = dz1.sum(axis=0)\n\n"
            "    return dw1, db1, dw2, db2\n"
        ),
    ),
]

# --------------------------------------------------------- thin P0 math topics

MATH_ADDITIONS = [
    NewQuestion(
        title="What does it mean for a matrix to be positive semi-definite, and why does that property matter for covariance matrices and kernel functions in ML?",
        topic="linear_algebra", phase=0, question_type="concept", cognitive_level=3,
        difficulty="advanced", category="ml_fundamentals", module_code="C",
    ),
    NewQuestion(
        title="You're inverting a matrix directly (e.g. for the closed-form linear regression solution) and getting wildly unstable results or a singular-matrix error. Walk through how you'd diagnose and fix it.",
        topic="linear_algebra", phase=0, question_type="debugging", cognitive_level=4,
        difficulty="advanced", category="ml_debugging", module_code="Z", seniority="senior",
        tests_for="Recognizing multicollinearity / near-singularity as the likely cause, and knowing that the practical fix is usually regularization (ridge) or an alternative decomposition, not a more 'precise' matrix inverse.",
        follow_ups=[
            "Why does adding a small ridge penalty fix a singular normal-equations matrix?",
            "Why would you prefer solving the linear system directly over explicitly computing the matrix inverse, even when it's not singular?",
        ],
    ),
    NewQuestion(
        title="What's the difference between a local minimum and a saddle point, and why are saddle points actually the more common obstacle in high-dimensional neural network loss landscapes?",
        topic="calculus_optimization", phase=0, question_type="concept", cognitive_level=3,
        difficulty="advanced", category="ml_fundamentals", module_code="C",
    ),
    NewQuestion(
        title="Why does adding momentum to gradient descent help it converge faster, in terms of the shape of the loss surface it's compensating for?",
        topic="calculus_optimization", phase=0, question_type="concept", cognitive_level=3,
        difficulty="advanced", category="ml_fundamentals", module_code="C",
    ),
    NewQuestion(
        title="What's the difference between a frequentist and a Bayesian interpretation of probability, and when does that distinction actually change how you'd approach a modeling problem?",
        topic="probability", phase=0, question_type="concept", cognitive_level=2,
        difficulty="intermediate", category="ml_fundamentals", module_code="C",
    ),
    NewQuestion(
        title="Explain the bias-variance tradeoff in terms of the expected value and variance of an estimator, not just the informal 'underfitting vs. overfitting' description.",
        topic="probability", phase=0, question_type="concept", cognitive_level=3,
        difficulty="advanced", category="ml_fundamentals", module_code="C",
    ),
]

# ---------------------------------------------------------- bank-wide debugging push

DEBUGGING_PUSH = [
    NewQuestion(
        title="Your fraud model has 99.5% accuracy but catches almost none of the actual fraud cases. Walk through what's wrong with the evaluation and the training setup, and how you'd fix each.",
        topic="class_imbalance", phase=1, question_type="debugging", cognitive_level=4,
        difficulty="advanced", category="ml_debugging", module_code="Z", seniority="senior",
        tests_for="Recognizing accuracy as the wrong metric under severe class imbalance before proposing any fix, then addressing both the metric (precision/recall/PR-AUC) and the training-time imbalance (resampling, class weights) separately.",
        follow_ups=[
            "Why is PR-AUC usually more informative than ROC-AUC here?",
            "Would you fix this by resampling the training data, reweighting the loss, or both? What's the tradeoff?",
        ],
    ),
    NewQuestion(
        title="A model that performed well at launch has been quietly getting worse for three months with no code changes. Walk through how you'd confirm it's distribution shift and not something else.",
        topic="distribution_shift", phase=3, question_type="debugging", cognitive_level=4,
        difficulty="advanced", category="ml_debugging", module_code="Z", seniority="senior",
        tests_for="Ruling out a pipeline/labeling bug before concluding it's genuine distribution shift, then distinguishing covariate shift (input distribution changed) from concept shift (the input-output relationship changed).",
        follow_ups=[
            "What would you monitor so this is caught in week one instead of month three?",
            "How would you tell covariate shift apart from concept drift using only production data?",
        ],
    ),
    NewQuestion(
        title="Your learning-rate sweep shows wildly inconsistent validation loss between runs at the same hyperparameters. What would you check before trusting any of the sweep's results?",
        topic="hyperparameter_optimization", phase=1, question_type="debugging", cognitive_level=4,
        difficulty="advanced", category="ml_debugging", module_code="Z", seniority="senior",
        tests_for="Checking for unfixed randomness (seeding, data shuffling, non-deterministic ops) and too-small a validation set before concluding the hyperparameter itself is unstable.",
        follow_ups=[
            "How many repeated runs per configuration would you want before trusting a sweep result, and why?",
            "What's the difference between run-to-run noise and the hyperparameter genuinely being on a sharp, unstable part of the loss surface?",
        ],
    ),
    NewQuestion(
        title="Your model gets 98% validation accuracy but performs at roughly chance level in production. Walk through how you'd check for data leakage.",
        topic="data_leakage", phase=1, question_type="debugging", cognitive_level=4,
        difficulty="advanced", category="ml_debugging", module_code="Z", seniority="senior",
        tests_for="Systematically checking for leakage sources: features unavailable at prediction time, target leaking into a feature via aggregation, or a split that lets information cross from train into validation (e.g. via a shared entity or time leakage).",
        follow_ups=[
            "How would you specifically test whether a suspicious feature is the leak, without retraining the whole model?",
            "Why does a time-based split (not a random split) matter for catching this kind of leakage?",
        ],
    ),
    NewQuestion(
        title="Two runs of your training pipeline, same code and same seed, produce different final model weights. Where would you look for the source of nondeterminism?",
        topic="training_pipelines", phase=1, question_type="debugging", cognitive_level=4,
        difficulty="advanced", category="ml_debugging", module_code="Z", seniority="senior",
        tests_for="Checking the usual nondeterminism sources in order of likelihood: unseeded data shuffling/augmentation, GPU nondeterministic ops (e.g. atomic adds in cuDNN), and multi-threaded data loading order -- not assuming the model code itself is at fault.",
        follow_ups=[
            "Why can GPU training be nondeterministic even with every seed fixed?",
            "When is chasing perfect determinism worth the (often real) performance cost, and when isn't it?",
        ],
    ),
    NewQuestion(
        title="Your binary classifier's predicted probabilities are almost always near 0 or 1, and when you check calibration, it's systematically overconfident. How do you diagnose and fix this?",
        topic="calibration", phase=1, question_type="debugging", cognitive_level=4,
        difficulty="advanced", category="ml_debugging", module_code="Z", seniority="senior",
        tests_for="Reading a reliability diagram correctly (predicted probability vs. observed frequency) before reaching for a fix, then choosing between Platt scaling and isotonic regression based on how much labeled data is available and the shape of the miscalibration.",
        follow_ups=[
            "When would you prefer isotonic regression over Platt scaling for the fix, and why?",
            "Why can a model be highly accurate and still be badly miscalibrated?",
        ],
    ),
    NewQuestion(
        title="Your LLM agent gets stuck calling the same tool repeatedly without making progress toward the user's goal. How do you debug and fix this?",
        topic="agent_loop", phase=5, question_type="debugging", cognitive_level=4,
        difficulty="advanced", category="ml_debugging", module_code="Z", seniority="senior",
        tests_for="Distinguishing a few distinct causes -- the tool result isn't being incorporated into the next prompt, the model isn't told a loop-count limit exists, or the tool itself is silently failing and returning something that looks retriable -- rather than reaching straight for 'add a max-iterations cap'.",
        follow_ups=[
            "Why is a hard iteration cap a safety net rather than a real fix?",
            "How would you detect this pattern automatically in production, before a user reports it?",
        ],
    ),
    NewQuestion(
        title="Your RAG system's retrieval quality dropped sharply right after you re-indexed with a new, supposedly-better embedding model. What would you check first?",
        topic="vector_search", phase=4, question_type="debugging", cognitive_level=4,
        difficulty="advanced", category="ml_debugging", module_code="Z", seniority="senior",
        tests_for="Checking for a mismatch between the query-time and index-time embedding model (or a stale index that wasn't fully rebuilt) before concluding the new embedding model is actually worse, plus checking whether the similarity metric or normalization assumptions changed between the two models.",
        follow_ups=[
            "Why must the embedding model used to embed queries always match the one used to build the index?",
            "How would you evaluate the new embedding model in isolation, before blaming the index?",
        ],
    ),
    NewQuestion(
        title="Your KNN classifier has great training-set accuracy but is extremely slow and memory-hungry to serve, and accuracy craters as you add more features. Walk through what's going wrong and how you'd address each part.",
        topic="knn", phase=1, question_type="debugging", cognitive_level=4,
        difficulty="advanced", category="ml_debugging", module_code="Z", seniority="senior",
        tests_for="Connecting the accuracy drop to the curse of dimensionality (distances become less meaningful in high dimensions) and the serving cost to KNN's lack of a trained model (it stores and scans the full training set), then proposing distinct fixes for each -- dimensionality reduction/feature selection for one, an approximate-neighbor index or a different model family for the other.",
        follow_ups=[
            "Why does Euclidean distance become less discriminative as dimensionality grows?",
            "If you needed to keep using KNN at scale, how would you speed up the neighbor search?",
        ],
    ),
    NewQuestion(
        title="A newly added feature boosted your offline AUC by 5 points, but the online experiment showed no lift at all. What do you suspect first?",
        topic="feature_engineering", phase=1, question_type="debugging", cognitive_level=4,
        difficulty="advanced", category="ml_debugging", module_code="Z", seniority="senior",
        tests_for="Suspecting a training/serving skew in how the feature is computed (e.g. it uses information that isn't actually available, or is computed differently, at serving time) before trusting the offline number.",
        follow_ups=[
            "How would you specifically test whether the feature is available and identically computed at serving time?",
            "What's a general process for catching this kind of gap before it reaches an online experiment?",
        ],
    ),
]

ALL_QUESTIONS: list[NewQuestion] = (
    PYTHON_FOR_ML + NUMPY_VECTORIZATION + PANDAS_DATA + BACKPROPAGATION + MATH_ADDITIONS + DEBUGGING_PUSH
)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    async with SessionLocal() as session:
        existing_titles = set((await session.execute(select(Question.title))).scalars().all())
        max_order_by_category: dict[str, int] = {}
        for cat in {q.category for q in ALL_QUESTIONS}:
            max_order = await session.scalar(
                select(func.coalesce(func.max(Question.order_index), 0)).where(Question.category == cat)
            )
            max_order_by_category[cat] = max_order or 0

        to_insert = [q for q in ALL_QUESTIONS if q.title not in existing_titles]
        skipped = len(ALL_QUESTIONS) - len(to_insert)

        print(f"{len(ALL_QUESTIONS)} authored, {skipped} already present, {len(to_insert)} to insert.")

        if not args.apply:
            print("Dry run -- pass --apply to write to the database.")
            for q in to_insert:
                print(f"  [{q.topic}/{q.question_type}] {q.title[:80]}")
            return

        for q in to_insert:
            max_order_by_category[q.category] += 1
            row = Question(
                category=q.category,
                title=q.title,
                source="curriculum spec",
                order_index=max_order_by_category[q.category],
                axis=q.axis,
                topic=q.topic,
                phase=q.phase,
                cognitive_level=q.cognitive_level,
                primary_format=q.primary_format,
                preview=False,
                classification_confidence="adjudicated",
                module_code=q.module_code,
                question_type=q.question_type,
                difficulty=q.difficulty,
                seniority=q.seniority,
                priority="P1" if q.question_type == "debugging" else "P0",
                frequency="unknown",
                evidence="fundamental",
                source_url=None,
                tests_for=q.tests_for,
                reference_solution=q.reference_solution,
                follow_ups=q.follow_ups,
                answer_dimensions=q.answer_dimensions,
                companies=[],
                common_mistakes=[],
                prerequisites=[],
                related=[],
            )
            session.add(row)

        await session.commit()
        print(f"Inserted {len(to_insert)} questions.")


if __name__ == "__main__":
    asyncio.run(main())
