"""Fills the modules the repo parsers left empty.

Two different kinds of content, kept apart on purpose:

1. `parse_agentic_2026` / `parse_rag_types` — parsed from
   Agentic-AI-Systems (MIT). Each themed section becomes one design
   question whose `answer_dimensions` are the section's own bullets, so
   the checklist you are marked against is the source's, not mine.

2. `SPEC_QUESTIONS` — the question sets enumerated in the build
   specification itself (Modules C, G, K, M, Z, AB, AC). These are
   `fundamental`: core knowledge asked across the industry, with no
   company attribution attached to any of them. Source is recorded as
   "curriculum spec" so it is never mistaken for a candidate report.

Nothing here carries a `companies` tag. A company claim requires a
citation, and none of this material has one.
"""

from __future__ import annotations

import re

from scripts.curriculum_sources import APPLIED_ML  # noqa: F401  (path constants live together)
from scripts.ingest_curriculum import AGENTIC, AGENTIC_BLOB, QRecord, _strip_md

SPEC_SOURCE = "curriculum spec"


# --------------------------------------------------------------------------
# Parsed: Agentic-AI-Systems 2026 design themes
# --------------------------------------------------------------------------

# theme heading -> (module, submodule, category, question)
THEME_MAP: dict[str, tuple[str, str, str, str]] = {
    "Harness Engineering": (
        "T", "Agent harness & orchestrator", "agentic_ai",
        "Design the harness around an agent: what runs deterministically in code, and what "
        "is left to the model?",
    ),
    "Context Engineering": (
        "O", "Context selection", "context_engineering",
        "Your agent has access to 100 documents and 20 tools. How do you decide what enters "
        "the context, and how do you prove where each claim came from?",
    ),
    "Long-Running and Scheduled Agents": (
        "N", "Long-running agents", "agentic_ai",
        "Design an agent that runs for hours across restarts. What is checkpointed, what is "
        "idempotent, and how does it resume without repeating side effects?",
    ),
    "AgentOps and Observability": (
        "V", "LLM observability", "llmops",
        "What do you trace, log and alert on for an agent in production, and what question "
        "does each signal let you answer during an incident?",
    ),
    "Evaluation-Driven Development": (
        "F", "Agentic evaluation", "evaluation",
        "How do you evaluate an agent whose output is a trajectory rather than a label?",
    ),
    "Protocols: MCP and A2A": (
        "P", "MCP clients & servers", "protocols",
        "Explain MCP and A2A: what each standardises, and why a protocol boundary is also a "
        "trust boundary.",
    ),
    "Security for Connected Agents": (
        "P", "Prompt injection", "responsible_ai",
        "An agent can read private data and take actions. Walk through the threat model and "
        "the controls you would put in place.",
    ),
    "Inference and Cost as First-Class Design": (
        "W", "Inference optimization", "ml_infrastructure",
        "Your LLM feature costs too much and its p99 is too slow. Walk through the levers, "
        "in the order you would pull them.",
    ),
}


def parse_agentic_2026() -> list[QRecord]:
    path = AGENTIC / "03_system_design" / "2026-agentic-ai-system-design.md"
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    url = f"{AGENTIC_BLOB}/03_system_design/2026-agentic-ai-system-design.md"

    # Collect each "### N. Theme" section's bullets, keyed by sub-heading
    # ("Core components", "Design trade-offs", "Threat model", "Controls").
    sections: dict[str, dict[str, list[str]]] = {}
    theme: str | None = None
    label = "body"
    for line in lines:
        h3 = re.match(r"^###\s+\d+\.\s+(.*)", line)
        if h3:
            theme = h3.group(1).strip()
            sections[theme] = {}
            label = "body"
            continue
        if re.match(r"^##\s", line):
            theme = None
            continue
        if theme is None:
            continue
        sub = re.match(r"^([A-Z][A-Za-z \-]+):\s*$", line.strip())
        if sub:
            label = sub.group(1).strip()
            continue
        b = re.match(r"^\s*-\s+(.*)", line)
        if b:
            sections[theme].setdefault(label, []).append(_strip_md(b.group(1)).rstrip("."))

    out: list[QRecord] = []
    for theme, groups in sections.items():
        mapped = THEME_MAP.get(theme)
        if not mapped:
            continue
        module, submodule, category, question = mapped

        dimensions: list[str] = []
        for key in ("Core components", "Design implications", "Threat model", "Controls", "body"):
            dimensions += groups.get(key, [])
        tradeoffs = groups.get("Design trade-offs", [])

        out.append(
            QRecord(
                category=category,
                title=question,
                source="Agentic-AI-Systems",
                module_code=module,
                submodule=submodule,
                question_type="system_design",
                difficulty="advanced",
                seniority="senior",
                priority="P0" if module in {"O", "P"} else "P1",
                frequency="high",
                evidence="common",
                source_url=url,
                tests_for=f"2026 design theme: {theme}. The answer is expected to name the "
                f"components, then the trade-offs each one buys and costs.",
                answer_dimensions=dimensions[:12],
                follow_ups=[f"Trade-off to defend: {t}" for t in tradeoffs[:4]],
                strong_signal="Names the discarded alternative and why; keeps guarantees in "
                "code rather than in prompt text.",
                weak_signal="Describes the happy path only, with no failure mode or cost.",
            )
        )
    return out


def parse_rag_types() -> list[QRecord]:
    """Module M — the RAG chapter's own taxonomy."""
    path = AGENTIC / "03_system_design" / "RAGs" / "README.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    url = f"{AGENTIC_BLOB}/03_system_design/RAGs/README.md"

    out: list[QRecord] = []
    for heading in re.findall(r"^##\s+\d+\.\s+(.*)", text, re.M):
        name = _strip_md(heading).strip()
        if not name:
            continue
        out.append(
            QRecord(
                category="rag",
                title=f"Explain {name}: when is it the right choice, and what does it cost "
                f"over the simpler option?",
                source="Agentic-AI-Systems",
                module_code="M",
                submodule="Retrieval evaluation",
                question_type="concept",
                difficulty="advanced",
                seniority="senior",
                priority="P0",
                frequency="high",
                evidence="common",
                source_url=url,
                tests_for="Whether the added machinery is justified by a failure the simpler "
                "pipeline actually has.",
            )
        )
    return out


# --------------------------------------------------------------------------
# Spec-enumerated question sets for the modules no repo covered
# --------------------------------------------------------------------------

def _q(
    module: str,
    submodule: str,
    category: str,
    title: str,
    *,
    qtype: str = "concept",
    difficulty: str = "intermediate",
    seniority: str = "mid",
    priority: str = "P0",
    tests_for: str | None = None,
    follow_ups: list[str] | None = None,
) -> QRecord:
    return QRecord(
        category=category,
        title=title,
        source=SPEC_SOURCE,
        module_code=module,
        submodule=submodule,
        question_type=qtype,
        difficulty=difficulty,
        seniority=seniority,
        priority=priority,
        frequency="high",
        evidence="fundamental",
        source_url=None,
        tests_for=tests_for,
        follow_ups=follow_ups or [],
    )


def spec_transformers() -> list[QRecord]:
    """Module K. Architecture-level 'why', not 'what'."""
    items: list[tuple[str, str]] = [
        ("Why does attention use three separate projections — Q, K and V — rather than "
         "comparing the inputs directly?", "Q/K/V & scaled dot-product"),
        ("Why is the dot product divided by sqrt(d_k)? What breaks if you remove it?",
         "Q/K/V & scaled dot-product"),
        ("Why multi-head attention rather than one larger head? What do different heads "
         "end up representing?", "Multi-head attention"),
        ("Why does a Transformer need positional information at all, and what do sinusoidal, "
         "learned and RoPE encodings each trade off?", "Positional encoding & RoPE"),
        ("Explain RoPE. Why does rotating the query and key make relative position fall out "
         "of the dot product?", "Positional encoding & RoPE"),
        ("What is causal masking, where exactly is it applied, and what goes wrong if it is "
         "applied after the softmax?", "Causal masking"),
        ("Encoder-only, decoder-only, encoder-decoder: what task shape does each suit, and "
         "why did decoder-only win for general LLMs?", "Encoder vs decoder"),
        ("Why do Transformers beat RNNs on long sequences, given that attention is quadratic "
         "and an RNN is linear?", "Attention complexity"),
        ("What is the time and memory complexity of self-attention, and which of the two "
         "actually binds first in practice?", "Attention complexity"),
        ("What is the KV cache, what exactly is stored, and how does its size grow with batch "
         "size, sequence length and model width?", "KV cache"),
        ("MHA vs MQA vs GQA: what is shared in each, and what does that do to quality and to "
         "memory bandwidth at decode time?", "MHA / MQA / GQA"),
        ("What does FlashAttention change? It computes the same attention — so where does the "
         "speedup come from?", "FlashAttention"),
        ("Explain Mixture of Experts: what is sparse about it, and what new failure modes does "
         "routing introduce?", "Mixture of Experts"),
        ("Where are the compute-bound and memory-bound bottlenecks in Transformer inference, "
         "and how does that differ between prefill and decode?", "KV cache"),
    ]
    return [
        _q("K", sub, "transformers", title, difficulty="advanced", seniority="senior",
           tests_for="Architecture-level understanding: the design decision and what it buys, "
                     "not a recital of the diagram.")
        for title, sub in items
    ]


def spec_rag() -> list[QRecord]:
    """Module M. The pipeline stage by stage, ending on the diagnostic."""
    items: list[tuple[str, str]] = [
        ("How do you choose chunk size, and what does a too-small or too-large chunk actually "
         "break downstream?", "Parsing & chunking"),
        ("What is chunk overlap for, and when does it stop helping?", "Parsing & chunking"),
        ("Semantic chunking vs fixed-size: what does semantic chunking cost, and when is it "
         "worth it?", "Parsing & chunking"),
        ("Dense retrieval vs BM25: which failure does each one have, and why do hybrid systems "
         "beat both?", "Dense vs BM25"),
        ("How do you combine sparse and dense scores in hybrid search without one dominating?",
         "Hybrid search"),
        ("Compare HNSW and IVF: what does each trade between recall, memory and build time?",
         "Vector indexes (HNSW/IVF)"),
        ("Why add a cross-encoder reranker when the retriever already ranked the results?",
         "Reranking"),
        ("What is query rewriting for, and when does it make retrieval worse?",
         "Query rewriting & HyDE"),
        ("Explain HyDE. Why would generating a fake answer help you find the real one?",
         "Query rewriting & HyDE"),
        ("How do you enforce metadata filtering and per-tenant access control inside a vector "
         "search without leaking across tenants?", "Multi-tenancy & access control"),
        ("How do you compress context without erasing the detail the answer depends on?",
         "Context construction & compression"),
        ("How do you produce citations that actually point at the span the claim came from?",
         "Citations & grounding"),
        ("How do you keep a RAG index fresh when the underlying documents change constantly?",
         "Freshness"),
        ("How do you evaluate retrieval separately from generation, and what metric do you use "
         "for each?", "Retrieval evaluation"),
        ("Your RAG system gives a wrong answer. How do you determine whether the failure is in "
         "retrieval or in generation?", "Retrieval evaluation"),
        ("How would you scale a RAG system to 10M+ documents while keeping p99 under a second?",
         "Vector indexes (HNSW/IVF)"),
    ]
    return [
        _q("M", sub, "rag", title, difficulty="advanced", seniority="senior",
           tests_for="Whether you can reason about one stage of the pipeline without losing "
                     "sight of its effect on the others.")
        for title, sub in items
    ]


def spec_debugging() -> list[QRecord]:
    """Module Z. Each is a symptom; the answer is an ordered investigation."""
    scenarios: list[tuple[str, str]] = [
        ("Training loss is still falling but validation loss has started rising. Walk me "
         "through your investigation.", "Training/validation divergence"),
        ("Production accuracy dropped sharply overnight with no deploy. Diagnose it.",
         "Production accuracy drops"),
        ("Your offline metric improved by 3% but the business KPI fell. What do you check, "
         "and in what order?", "Offline-online metric mismatch"),
        ("Your RAG system is retrieving irrelevant documents for queries that used to work. "
         "Diagnose it.", "RAG retrieval failures"),
        ("Hallucination reports tripled this week. Nothing was deployed. Where do you look?",
         "Hallucination spikes"),
        ("An agent has started calling the same tool over and over until it hits the budget "
         "cap. Diagnose and fix it.", "Agent tool-call loops"),
        ("Inference p99 latency doubled while p50 stayed flat. What does that pattern tell "
         "you, and what do you check first?", "Latency regressions"),
        ("Your GPUs sit at 20% utilisation during training. Find the bottleneck.",
         "GPU under-utilization"),
        ("The model scores well in training and offline eval but fails in production. What is "
         "the differential diagnosis?", "Train/serve skew"),
        ("Aggregate metrics look fine but one user segment is being served badly. How do you "
         "find it and what do you do about it?", "Segment-level failures"),
        ("A feature's distribution shifted in production. How do you detect it, and how do you "
         "decide whether to retrain or roll back?", "Train/serve skew"),
    ]
    return [
        _q("Z", sub, "ml_debugging", title, qtype="debugging", difficulty="advanced",
           seniority="senior",
           tests_for="An ordered investigation, not a list of guesses: symptom, hypotheses "
                     "ranked by prior, the cheapest discriminating check first.",
           follow_ups=[
               "What is the cheapest check that would rule out half your hypotheses?",
               "How would you have detected this before a user did?",
               "What would you add to monitoring so this is caught automatically next time?",
           ])
        for title, sub in scenarios
    ]


def spec_product_reasoning() -> list[QRecord]:
    """Module AB. The right answer is often 'don't'."""
    items: list[tuple[str, str]] = [
        ("This problem could be solved with a rules engine or with ML. How do you decide, and "
         "what would make you choose the heuristic?", "Should this use ML at all?"),
        ("When is an LLM the wrong tool for a task that involves text?", "Should this use an LLM?"),
        ("Build vs buy for this AI capability: what factors decide it, and what would change "
         "your answer in a year?", "Build vs buy"),
        ("RAG or fine-tuning? Give the decision rule, not the definitions.",
         "RAG vs fine-tuning"),
        ("When does a small model beat a large one in production, all-in?",
         "Small vs large model"),
        ("The product wants 200ms p99 and the accurate model takes 900ms. What are your options?",
         "Accuracy vs latency"),
        ("Your LLM feature is profitable at 10k users and loss-making at 1M. What do you change?",
         "Quality vs cost"),
        ("Where do you put a human in the loop, and what is the cost of putting them in the "
         "wrong place?", "Automation vs human review"),
        ("How would you measure the ROI of this ML system, and what would you do if it were "
         "negative?", "Should this use ML at all?"),
    ]
    return [
        _q("AB", sub, "product_reasoning", title, difficulty="advanced", seniority="senior",
           priority="P1",
           tests_for="Engineering judgement. Saying 'don't use ML here' when that is correct "
                     "is the signal being looked for.")
        for title, sub in items
    ]


def spec_papers() -> list[QRecord]:
    """Module AC. One record per paper, interrogated the same way."""
    papers: list[tuple[str, str, str]] = [
        ("Attention Is All You Need (Vaswani et al., 2017)", "Attention Is All You Need",
         "https://arxiv.org/abs/1706.03762"),
        ("BERT (Devlin et al., 2018)", "BERT", "https://arxiv.org/abs/1810.04805"),
        ("GPT-2 / GPT-3 (Radford et al., 2019; Brown et al., 2020)", "GPT series",
         "https://arxiv.org/abs/2005.14165"),
        ("Deep Residual Learning (He et al., 2015)", "ResNet", "https://arxiv.org/abs/1512.03385"),
        ("Word2Vec (Mikolov et al., 2013)", "Word2Vec", "https://arxiv.org/abs/1301.3781"),
        ("CLIP (Radford et al., 2021)", "CLIP", "https://arxiv.org/abs/2103.00020"),
        ("LoRA (Hu et al., 2021)", "LoRA & QLoRA", "https://arxiv.org/abs/2106.09685"),
        ("QLoRA (Dettmers et al., 2023)", "LoRA & QLoRA", "https://arxiv.org/abs/2305.14314"),
        ("InstructGPT / RLHF (Ouyang et al., 2022)", "RLHF (InstructGPT)",
         "https://arxiv.org/abs/2203.02155"),
        ("Direct Preference Optimization (Rafailov et al., 2023)", "DPO",
         "https://arxiv.org/abs/2305.18290"),
        ("FlashAttention (Dao et al., 2022)", "FlashAttention", "https://arxiv.org/abs/2205.14135"),
        ("Sparsely-Gated Mixture-of-Experts (Shazeer et al., 2017)", "Mixture of Experts",
         "https://arxiv.org/abs/1701.06538"),
    ]
    out: list[QRecord] = []
    for label, submodule, url in papers:
        r = _q(
            "AC", submodule, "research_papers",
            f"{label} — what problem did it solve, what was the prior limitation, and what "
            f"is the one idea that made it work?",
            difficulty="advanced", seniority="senior", priority="P1",
            tests_for="Whether you have read the paper or read about the paper.",
            follow_ups=[
                "What did the prior state of the art do, and why was it insufficient?",
                "What were the results, and on which benchmark — and does that benchmark still mean anything?",
                "What are its limitations and failure modes?",
                "What does this change about how you would build a system today?",
            ],
        )
        r.source_url = url
        out.append(r)
    return out


def spec_statistics() -> list[QRecord]:
    """Module C. Applied, posed with numbers."""
    items: list[tuple[str, str, str]] = [
        ("A fraud detector fires on 0.1% of transactions. The classifier has 99% sensitivity "
         "and 99% specificity. A transaction is flagged — what is the probability it is "
         "actually fraud, and what does that imply for the product?", "Probability", "advanced"),
        ("Explain eigenvalues and eigenvectors in terms of what PCA is actually doing.",
         "Linear algebra", "intermediate"),
        ("What is SVD, and why does it keep appearing in ML — recommendation, PCA, "
         "low-rank adaptation?", "Linear algebra", "advanced"),
        ("Derive the gradient of the logistic loss with respect to the weights.",
         "Calculus & gradients", "advanced"),
        ("What does the Hessian tell you that the gradient does not, and why do we mostly not "
         "use it?", "Calculus & gradients", "advanced"),
        ("Explain the Central Limit Theorem and where people misuse it.", "Statistics & inference",
         "intermediate"),
        ("What is a p-value, stated precisely — and what is it not?", "Statistics & inference",
         "intermediate"),
        ("What is a confidence interval, and what does 95% actually refer to?",
         "Statistics & inference", "intermediate"),
        ("Expected value, variance and covariance: define them, then tell me what covariance "
         "fails to capture.", "Probability", "beginner"),
        ("Compare gradient descent, SGD, momentum, RMSprop and Adam. What problem does each "
         "one fix in its predecessor?", "Optimization", "intermediate"),
        ("Why is the loss surface of a deep network non-convex, and why does SGD work anyway?",
         "Optimization", "advanced"),
        ("Correlation is not causation — so what would you actually need to claim causation "
         "from observational data?", "Statistics & inference", "advanced"),
    ]
    return [
        _q("C", sub, "math_stats", title, difficulty=diff,
           seniority="senior" if diff == "advanced" else "mid",
           tests_for="Application. A definition alone does not survive the follow-up.")
        for title, sub, diff in items
    ]


def spec_experimentation() -> list[QRecord]:
    """Module G. Mostly contradictions to resolve."""
    items: list[tuple[str, str]] = [
        ("Walk me through designing an A/B test for a new ranking model: hypothesis, unit of "
         "randomisation, metric, and how long you run it.", "Hypothesis testing"),
        ("How do you compute the sample size you need, and what happens if you peek before "
         "reaching it?", "Power & sample size"),
        ("What is statistical power, and what is the practical cost of an underpowered test?",
         "Power & sample size"),
        ("CTR went up 4% and revenue went down 2%. The result is significant. What do you do?",
         "Guardrail metrics"),
        ("Model accuracy improved and user retention fell. How do you reconcile that?",
         "Guardrail metrics"),
        ("Your result is statistically significant with a 0.1% effect. Ship it or not?",
         "Hypothesis testing"),
        ("You are running 20 experiments at once. What is the problem and what do you do "
         "about it?", "Multiple comparisons"),
        ("A test showed a positive lift that decayed to zero over three weeks. What happened?",
         "Novelty effects"),
        ("What is experiment contamination, and how would you detect it after the fact?",
         "Selection bias & contamination"),
        ("When is sequential testing worth the extra complexity over a fixed-horizon test?",
         "Sequential testing"),
    ]
    return [
        _q("G", sub, "experimentation", title, difficulty="advanced", seniority="senior",
           priority="P1",
           tests_for="Whether you can resolve a contradiction between metrics, rather than "
                     "recite a definition of a p-value.")
        for title, sub in items
    ]


def spec_multimodal() -> list[QRecord]:
    """Module Q."""
    items: list[tuple[str, str]] = [
        ("How does CLIP learn a shared image-text space, and what is the contrastive objective "
         "actually doing?", "Vision-language models"),
        ("How would you build multimodal RAG over documents that contain tables and diagrams?",
         "Multimodal RAG"),
        ("Design a document-intelligence pipeline: layout understanding, table extraction, and "
         "what you do when OCR is wrong.", "OCR & document intelligence"),
        ("How do you evaluate a vision-language model on a task with no single correct answer?",
         "Multimodal embeddings"),
        ("What breaks when you naively concatenate image and text embeddings, and what do "
         "fusion architectures do instead?", "Multimodal embeddings"),
        ("Design a visual search system: embedding choice, index, and how you handle "
         "near-duplicates.", "Multimodal embeddings"),
        ("How would you build a voice assistant end to end, and where does latency accumulate?",
         "Audio-language models"),
    ]
    return [
        _q("Q", sub, "multimodal", title, difficulty="advanced", seniority="senior",
           priority="P2",
           tests_for="Whether the multimodal part is understood as a design problem rather "
                     "than a model name.")
        for title, sub in items
    ]


SPEC_PARSERS = [
    ("Agentic 2026 themes (Modules O/P/T/N/V/W/F)", parse_agentic_2026),
    ("RAG taxonomy (Module M)", parse_rag_types),
    ("Spec — Transformers (Module K)", spec_transformers),
    ("Spec — RAG pipeline (Module M)", spec_rag),
    ("Spec — Debugging scenarios (Module Z)", spec_debugging),
    ("Spec — Product reasoning (Module AB)", spec_product_reasoning),
    ("Spec — Papers (Module AC)", spec_papers),
    ("Spec — Maths & statistics (Module C)", spec_statistics),
    ("Spec — Experimentation (Module G)", spec_experimentation),
    ("Spec — Multimodal (Module Q)", spec_multimodal),
]
