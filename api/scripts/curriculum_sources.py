"""Parsers for the six additional source repositories.

Each function returns `QRecord`s. Nothing in this file writes prose from
memory — every question is lifted or derived from a cloned file, and every
record carries the repo it came from.

LICENCE STATUS, and why it changes what we extract:

  applied-ml                            MIT
  awesome-production-machine-learning   MIT
  Data-Science-Interview-Resources      MIT
  data-science-interviews               CC BY 4.0  (attribution required)
  ai-engineering-field-guide            NO LICENCE FILE
  machine-learning-interview            NO LICENCE FILE

The last two grant no redistribution rights. Their content is extracted
into this **single-user, private** database for personal study, with the
repo and the original candidate-report URL attached to every row. It must
not be published or redistributed out of Meridian. `external/` is
gitignored precisely so the clones never enter this repo's history.

The field guide is the most valuable source here because it footnotes each
question with the candidate report it came from — Reddit threads, HN,
interview write-ups. That is a real `reported` evidence tier with a URL
you can open, rather than an assertion that "Meta asks this".
"""

from __future__ import annotations

import re

from scripts.ingest_curriculum import EXTERNAL, QRecord, _strip_md

FIELD_GUIDE = EXTERNAL / "ai-engineering-field-guide"
KHANGICH = EXTERNAL / "machine-learning-interview"
DS_INTERVIEWS = EXTERNAL / "data-science-interviews"
APPLIED_ML = EXTERNAL / "applied-ml"

FG_BLOB = "https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main"
KH_BLOB = "https://github.com/khangich/machine-learning-interview/blob/master"
DSI_BLOB = "https://github.com/alexeygrigorev/data-science-interviews/blob/master"
AML_BLOB = "https://github.com/eugeneyan/applied-ml/blob/main"

# Companies we will attribute, and the spellings that appear in footnote
# keys and labels. Only these are recognised — a company name is a claim,
# so guessing from an unfamiliar token is not allowed.
COMPANY_ALIASES: dict[str, str] = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "deepmind": "DeepMind",
    "google": "Google",
    "meta": "Meta",
    "facebook": "Meta",
    "amazon": "Amazon",
    "netflix": "Netflix",
    "microsoft": "Microsoft",
    "apple": "Apple",
    "nvidia": "NVIDIA",
    "uber": "Uber",
    "airbnb": "Airbnb",
    "linkedin": "LinkedIn",
    "databricks": "Databricks",
    "spotify": "Spotify",
    "stripe": "Stripe",
    "mistral": "Mistral",
    "perplexity": "Perplexity",
}

# Words that look like a company in a URL but are not one here.
_COMPANY_FALSE_FRIENDS = re.compile(r"(google\.com|googleusercontent|meta-llama)", re.I)


def _companies_from(text: str) -> list[str]:
    """Company names appearing in a footnote key or label.

    Deliberately conservative: matched on word boundaries against a fixed
    alias list, with the obvious URL false-friends excluded. A citation
    that merely links to a Google-hosted PDF is not evidence that Google
    asked the question.
    """
    cleaned = _COMPANY_FALSE_FRIENDS.sub(" ", text)
    found: list[str] = []
    for alias, name in COMPANY_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", cleaned, re.I) and name not in found:
            found.append(name)
    return found


def _footnote_index(text: str) -> dict[str, tuple[str, str]]:
    """key -> (label, url) from a markdown footnote-definition block."""
    out: dict[str, tuple[str, str]] = {}
    for key, label, url in re.findall(
        r"^\[\^([^\]]+)\]:\s*\[([^\]]+)\]\((https?://[^)]+)\)", text, re.M
    ):
        out[key] = (label.strip(), url.strip())
    return out


def _split_refs(line: str) -> tuple[str, list[str]]:
    """Strip trailing [^ref] markers off a bullet, returning (text, keys)."""
    keys = re.findall(r"\[\^([^\]]+)\]", line)
    body = re.sub(r"\[\^[^\]]+\]", "", line)
    body = re.sub(r"^\s*-\s+", "", body)  # drop the bullet marker itself
    return _strip_md(body).strip(" .").strip(), keys


# Headings we never harvest bullets from: they describe the round or the
# preparation routine rather than listing questions.
_NON_QUESTION_HEADINGS = re.compile(
    r"^(format|how to prepare|sources|expectations|common mistakes|what interviewers"
    r"|coding round formats|structure your answer|what companies build"
    r"|ai system design vs system design)",
    re.I,
)


def _sections(text: str, levels: tuple[int, ...] = (2, 3)) -> list[tuple[str, list[str]]]:
    """[(heading, [bullet lines])] for headings at any of `levels`.

    The field guide mixes ## and ### for question groups ("## Implementation
    Rounds" sits beside "### ML / AI Coding"), so keying on a single level
    silently drops half the file.
    """
    pattern = re.compile(rf"^(#{{{min(levels)},{max(levels)}}})\s+(.*)")
    out: list[tuple[str, list[str]]] = []
    current: str | None = None
    bullets: list[str] = []
    for line in text.splitlines():
        h = pattern.match(line)
        if h and len(h.group(1)) in levels:
            if current:
                out.append((current, bullets))
            current, bullets = h.group(2).strip(), []
            continue
        if re.match(r"^#{1,6}\s", line) and not (h and len(h.group(1)) in levels):
            if current:
                out.append((current, bullets))
                current, bullets = None, []
            continue
        if current and re.match(r"^\s*-\s+\S", line):
            bullets.append(line)
    if current:
        out.append((current, bullets))
    return [(h, b) for h, b in out if not _NON_QUESTION_HEADINGS.match(h)]


# --------------------------------------------------------------------------
# ai-engineering-field-guide
# --------------------------------------------------------------------------

# (section heading) -> (module, submodule, category)
FG_THEORY_MAP: dict[str, tuple[str, str, str]] = {
    "LLM Practice": ("L", "Inference & decoding", "llm_genai"),
    "RAG Systems": ("M", "Retrieval evaluation", "rag"),
    "Agents and Tool Use": ("N", "Tool & function calling", "agentic_ai"),
    "Testing and Evaluation": ("F", "GenAI evaluation", "evaluation"),
    "Monitoring": ("V", "LLM observability", "llmops"),
    "Cost and Latency Optimization": ("W", "Inference optimization", "ml_infrastructure"),
    "Safety and Guardrails": ("AE", "Prompt injection", "responsible_ai"),
    "ML Fundamentals": ("E", "Bias & variance", "ml_fundamentals"),
    "Fine-tuning and Training": ("L", "Instruction tuning & SFT", "llm_genai"),
    "LLM Theory": ("K", "Q/K/V & scaled dot-product", "transformers"),
}


def _field_guide_file(
    relpath: str,
    section_map: dict[str, tuple[str, str, str]] | None,
    default: tuple[str, str, str],
    question_type: str,
    seniority: str = "mid",
    difficulty: str = "intermediate",
) -> list[QRecord]:
    path = FIELD_GUIDE / relpath
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    notes = _footnote_index(text)
    url = f"{FG_BLOB}/{relpath}"

    out: list[QRecord] = []
    for heading, bullets in _sections(text):
        module, submodule, category = (section_map or {}).get(heading, default)
        for line in bullets:
            body, keys = _split_refs(line)
            # Prose bullets describing the round's format are not questions.
            if len(body) < 12 or not keys:
                continue

            labels = " ".join(notes[k][0] for k in keys if k in notes)
            companies = _companies_from(" ".join(keys) + " " + labels)
            cite_urls = [notes[k][1] for k in keys if k in notes]

            out.append(
                QRecord(
                    category=category,
                    title=body if body.endswith("?") else f"{body}",
                    source="ai-engineering-field-guide",
                    module_code=module,
                    submodule=submodule,
                    question_type=question_type,
                    difficulty=difficulty,
                    seniority=seniority,
                    priority="P0" if len(keys) >= 3 else "P1",
                    # More independent candidate reports = more confidence
                    # that this is actually asked. The count is the signal.
                    frequency="very_high" if len(keys) >= 4 else "high" if len(keys) >= 2 else "medium",
                    evidence="reported",
                    source_url=cite_urls[0] if cite_urls else url,
                    companies=companies,
                    tests_for=(
                        f"Asked in the wild: {len(keys)} independent candidate "
                        f"{'report' if len(keys) == 1 else 'reports'} cite this question."
                    ),
                    answer_dimensions=[lbl for lbl in (notes[k][0] for k in keys if k in notes)][:6],
                    related=cite_urls[1:4],
                )
            )
    return out


def parse_field_guide_theory() -> list[QRecord]:
    return _field_guide_file(
        "interview/questions/01-theory.md",
        FG_THEORY_MAP,
        ("E", "Bias & variance", "ml_fundamentals"),
        "concept",
    )


def parse_field_guide_coding() -> list[QRecord]:
    return _field_guide_file(
        "interview/questions/02-coding.md",
        {
            "ML / AI Coding": ("B", "GenAI primitives", "ml_coding"),
            "Implementation Rounds": ("A", "Complexity analysis", "dsa"),
            "Algorithm Rounds": ("A", "Complexity analysis", "dsa"),
        },
        ("B", "Classic ML primitives", "ml_coding"),
        "coding",
    )


def parse_field_guide_project() -> list[QRecord]:
    return _field_guide_file(
        "interview/questions/03-project-deep-dive.md",
        {
            "Business Problem and Context": ("AD", "Why this problem & why ML", "project_deep_dive"),
            "Decisions and Trade-offs": ("AD", "Baseline & alternatives", "project_deep_dive"),
            "Problems and Debugging": ("AD", "What failed & how you debugged it", "project_deep_dive"),
            "Evaluation and Results": ("AD", "Metric choice", "project_deep_dive"),
            "Learning and Reflection": ("AD", "What you'd change", "project_deep_dive"),
        },
        ("AD", "Why this problem & why ML", "project_deep_dive"),
        "project_deep_dive",
        seniority="senior",
    )


def parse_field_guide_sysdesign() -> list[QRecord]:
    return _field_guide_file(
        "interview/questions/04-ai-system-design.md",
        {
            "Typical AI System Design Questions": ("S", "Enterprise RAG assistant", "genai_system_design"),
            "Near-AI / AI Serving Systems / Platforms (more Engineering)": (
                "S", "LLM inference & serving platform", "genai_system_design",
            ),
        },
        ("S", "Enterprise RAG assistant", "genai_system_design"),
        "system_design",
        seniority="senior",
        difficulty="advanced",
    )


def parse_field_guide_behavioral() -> list[QRecord]:
    return _field_guide_file(
        "interview/questions/05-behavioral.md",
        {
            "AI-Specific Behavioral": ("AF", "Technical trade-offs", "behavioral"),
            "Conflict & Collaboration": ("AF", "Disagreement & influence", "behavioral"),
            "Leadership & Ownership": ("AF", "Cross-team influence", "behavioral"),
            "Technical Decision-Making": ("AF", "Technical trade-offs", "behavioral"),
            "Failure & Learning": ("AF", "Failed models & post-mortems", "behavioral"),
            "Culture Fit & Values": ("AF", "Ambiguity & prioritization", "behavioral"),
            "Career Motivation": ("AF", "Ambiguity & prioritization", "behavioral"),
        },
        ("AF", "Technical trade-offs", "behavioral"),
        "behavioral",
    )


# --------------------------------------------------------------------------
# khangich/machine-learning-interview
# --------------------------------------------------------------------------

KH_SECTION_MAP: dict[str, tuple[str, str, str]] = {
    "Machine Learning fundamentals": ("D", "Regression", "classical_ml"),
    "Deep learning fundamentals": ("H", "Neural network basics", "deep_learning"),
}


def parse_khangich_questions() -> list[QRecord]:
    """Numbered questions, with their lettered sub-parts as follow-ups.

    The source interleaves answers into the question text ("50. what is
    cross-validation: the purpose is to estimate..."). We keep only the
    part before the first colon-answer so the prompt stays a prompt.
    """
    path = KHANGICH / "questions.md"
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    url = f"{KH_BLOB}/questions.md"

    out: list[QRecord] = []
    section: tuple[str, str, str] | None = None
    pending: QRecord | None = None

    for line in lines:
        h = re.match(r"^##\s+(.*)", line)
        if h:
            section = KH_SECTION_MAP.get(h.group(1).strip())
            pending = None
            continue
        if section is None:
            continue

        numbered = re.match(r"^(\d+)\.\s+(.*)", line)
        if numbered:
            body = _strip_md(numbered.group(2))
            # Drop the appended answer: "Explain X: it is ..." keeps "Explain X".
            body = re.split(r"(?<=[a-z\)])[:.]\s+[A-Z]", body)[0].strip(" .:")
            if len(body) < 8:
                pending = None
                continue
            module, submodule, category = section
            pending = QRecord(
                category=category,
                title=body if body.endswith("?") else f"{body}?" if body.lower().startswith(
                    ("what", "how", "why", "when", "which", "is ", "are ", "can ", "do ")
                ) else body,
                source="khangich/machine-learning-interview",
                module_code=module,
                submodule=submodule,
                question_type="concept",
                difficulty="intermediate",
                seniority="mid",
                priority="P0",
                frequency="high",
                # The repo is a curated aggregation, not a per-question
                # candidate report, so this is `common`, not `reported`.
                evidence="common",
                source_url=url,
                tests_for="Whether the concept is understood rather than memorised — the "
                "sub-questions below are where a recited definition runs out.",
            )
            out.append(pending)
            continue

        sub = re.match(r"^\s*([a-z]|[ivx]+)\.\s+(.*)", line)
        if sub and pending is not None:
            follow = _strip_md(sub.group(2))
            if len(follow) > 4:
                pending.follow_ups.append(follow)

    return out


def parse_khangich_design() -> list[QRecord]:
    """The ML system-design use-cases (`## <Use case>` headings)."""
    # design.md carries one worked example; the use-case *list* is the
    # table in README.md, so read both.
    names: list[str] = []
    design = KHANGICH / "design.md"
    if design.exists():
        # design.md is all use-cases, so its ## headings are all design problems.
        names += [_strip_md(h) for h in re.findall(r"^##\s+(.*)", design.read_text(encoding="utf-8"), re.M)]
    readme = KHANGICH / "README.md"
    if readme.exists():
        # README's ## headings are navigation ("Getting Started", "Testimonials").
        # Only the numbered table rows are use-cases.
        names += [
            _strip_md(m)
            for m in re.findall(r"^\|\s*\d+\.\s*\[([^\]]+)\]", readme.read_text(encoding="utf-8"), re.M)
        ]
    url = f"{KH_BLOB}/design.md"

    out: list[QRecord] = []
    seen: set[str] = set()
    for raw in names:
        name = raw.strip(" .")
        low = name.lower()
        if not name or len(name) < 5 or low in seen:
            continue
        # Table rows include navigation entries, not design problems.
        if any(w in low for w in ("component", "notes", "chapter", "table of", "contents")):
            continue
        seen.add(low)
        out.append(
            QRecord(
                category="ml_system_design",
                title=f"Design: {name}.",
                source="khangich/machine-learning-interview",
                module_code="R",
                submodule="Ads & newsfeed" if "ad " in name.lower() or "click" in name.lower() else "Architecture & MVP logic",
                question_type="system_design",
                difficulty="advanced",
                seniority="senior",
                priority="P0",
                frequency="high",
                evidence="common",
                source_url=url,
                tests_for="Requirements, metrics, architecture, data, features, model, serving, "
                "online evaluation, monitoring, drift, retraining, rollback, cost, failure modes.",
                follow_ups=[
                    "What is the offline metric, and what is the online metric it should move?",
                    "How is the training data labelled, and where does leakage creep in?",
                    "What is your fallback when the model service is unavailable?",
                    "Do the rough QPS, storage and cost maths.",
                ],
            )
        )
    return out


# --------------------------------------------------------------------------
# alexeygrigorev/data-science-interviews  (CC BY 4.0)
# --------------------------------------------------------------------------

# Difficulty legend from the source README: 👶 easy, ⭐️ medium, 🚀 expert.
DSI_DIFFICULTY = {"👶": "beginner", "⭐": "intermediate", "🚀": "advanced"}

DSI_SECTION_MAP: dict[str, tuple[str, str, str]] = {
    "Supervised machine learning": ("D", "Regression", "classical_ml"),
    "Linear regression": ("D", "Regression", "classical_ml"),
    "Validation": ("E", "Cross-validation", "ml_fundamentals"),
    "Classification": ("D", "Classification", "classical_ml"),
    "Regularization": ("E", "Overfitting & regularization", "ml_fundamentals"),
    "Feature selection": ("E", "Feature selection", "ml_fundamentals"),
    "Decision trees": ("D", "Decision trees", "classical_ml"),
    "Random forest": ("D", "Ensembles (bagging/boosting)", "classical_ml"),
    "Gradient boosting": ("D", "Ensembles (bagging/boosting)", "classical_ml"),
    "Parameter tuning": ("E", "Cross-validation", "ml_fundamentals"),
    "Neural networks": ("H", "Neural network basics", "deep_learning"),
    "Optimization in neural networks": ("H", "Optimizers & schedules", "deep_learning"),
    "Neural networks for computer vision": ("I", "CNN architectures", "computer_vision"),
    "Text classification": ("J", "TF-IDF & sparse features", "nlp"),
    "Clustering": ("D", "Clustering", "classical_ml"),
    "Dimensionality reduction": ("D", "Dimensionality reduction", "classical_ml"),
    "Ranking and search": ("Y", "Learning to rank", "search_ir"),
    "Recommender systems": ("X", "Ranking", "recsys"),
    "Time series": ("D", "Regression", "classical_ml"),
}


def parse_ds_interviews_theory() -> list[QRecord]:
    path = DS_INTERVIEWS / "theory.md"
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    url = f"{DSI_BLOB}/theory.md"

    out: list[QRecord] = []
    section: tuple[str, str, str] | None = None
    in_toc = False
    for line in lines:
        h = re.match(r"^##\s+(.*)", line)
        if h:
            name = _strip_md(h.group(1)).strip()
            in_toc = name.lower().startswith("table of contents")
            section = DSI_SECTION_MAP.get(name)
            continue
        if section is None or in_toc:
            continue

        q = re.match(r"^\*\*(.+?)\*\*\s*$", line)
        if not q:
            continue
        raw = q.group(1).strip()
        marker = next((m for m in DSI_DIFFICULTY if m in raw), None)
        title = re.sub(r"[👶🚀⭐️⭐]", "", raw).strip()
        if len(title) < 10:
            continue

        module, submodule, category = section
        out.append(
            QRecord(
                category=category,
                title=title,
                source="data-science-interviews (CC BY 4.0)",
                module_code=module,
                submodule=submodule,
                question_type="concept",
                difficulty=DSI_DIFFICULTY.get(marker or "", "intermediate"),
                seniority="junior" if marker == "👶" else "senior" if marker == "🚀" else "mid",
                priority="P0" if marker in {"👶", "⭐"} else "P1",
                frequency="high",
                evidence="fundamental",
                source_url=url,
                tests_for="Core knowledge asked across essentially every ML loop.",
            )
        )
    return out


def parse_ds_interviews_sql() -> list[QRecord]:
    """Module A's SQL submodule — the one topic in the brief with no module
    of its own, so it lands beside the other coding-round material."""
    path = DS_INTERVIEWS / "technical.md"
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    url = f"{DSI_BLOB}/technical.md"

    out: list[QRecord] = []
    in_sql = False
    for line in lines:
        h = re.match(r"^##\s+(.*)", line)
        if h:
            in_sql = _strip_md(h.group(1)).strip().lower() == "sql"
            continue
        if not in_sql:
            continue
        # This section numbers its prompts inline: "**1)** The number of
        # active ads." — the bold wrapper holds only the number.
        q = re.match(r"^\*\*\d+\)\*\*\s*(.+)$", line) or re.match(r"^\*\*(.+?)\*\*\s*$", line)
        if not q:
            continue
        title = re.sub(r"[👶🚀⭐️⭐]", "", q.group(1)).strip()
        if len(title) < 10:
            continue
        out.append(
            QRecord(
                category="sql_data",
                title=f"Write the SQL: {title}" if not title.lower().startswith("write") else title,
                source="data-science-interviews (CC BY 4.0)",
                module_code="A",
                submodule="SQL & data manipulation",
                question_type="coding",
                difficulty="intermediate",
                seniority="mid",
                priority="P1",
                frequency="medium",
                evidence="fundamental",
                source_url=url,
                tests_for="Whether you can get the data out before you can model it — joins, "
                "grouping, window functions, and what the query costs.",
            )
        )
    return out


# --------------------------------------------------------------------------
# eugeneyan/applied-ml  (MIT)
# --------------------------------------------------------------------------

AML_SECTION_MAP: dict[str, str] = {
    "Recommendation": "Recommendation",
    "Search & Ranking": "Search & ranking",
    "Classification": "Fraud detection",
    "Forecasting": "Forecasting",
    "Anomaly Detection": "Anomaly detection",
    "Natural Language Processing": "Document AI & OCR",
    "Computer Vision": "Document AI & OCR",
    "Embeddings": "Recommendation",
    "Generation": "RAG products",
}

# Cap per section: this repo has ~400 entries, and a question bank that is
# 60% reading list stops being a question bank.
AML_PER_SECTION = 6


def parse_applied_ml_cases() -> list[QRecord]:
    """Module AA — real production systems, written up by the company.

    Note what is deliberately NOT set: `companies`. In this schema that
    field means "a source ties this *interview question* to that company".
    Here the company is whose *system* this is, which is a different claim,
    so it goes in the prompt text and the URL instead.
    """
    path = APPLIED_ML / "README.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    url = f"{AML_BLOB}/README.md"

    out: list[QRecord] = []
    section: str | None = None
    count = 0
    for line in text.splitlines():
        h = re.match(r"^##\s+(.*)", line)
        if h:
            section = AML_SECTION_MAP.get(_strip_md(h.group(1)).strip())
            count = 0
            continue
        if section is None or count >= AML_PER_SECTION:
            continue

        m = re.match(r"^\d+\.\s+\[([^\]]+)\]\((https?://[^)]+)\)(.*)", line)
        if not m:
            continue
        title, link, rest = _strip_md(m.group(1)), m.group(2), m.group(3)
        tags = re.findall(r"`([^`]+)`", rest)
        company = tags[0] if tags else None
        year = next((t for t in tags if re.fullmatch(r"(19|20)\d{2}", t)), None)
        if not company or company == year or len(title) < 12:
            continue
        count += 1

        out.append(
            QRecord(
                category="ml_case_study",
                title=f"Case study — {company}: {title}. How would you have designed this, "
                f"and where would your design have differed?",
                source="eugeneyan/applied-ml",
                module_code="AA",
                submodule=section,
                question_type="case_study",
                difficulty="advanced",
                seniority="senior",
                priority="P1",
                frequency="unknown",
                # A published engineering write-up, not an interview report.
                evidence="common",
                source_url=link,
                tests_for=f"Reading a real production system critically. Published by {company}"
                f"{f' in {year}' if year else ''}; read it, then argue with it.",
                answer_dimensions=[
                    "Business objective & constraints", "Data & labels", "Model choice",
                    "Serving & latency", "Evaluation (offline and online)", "What they traded away",
                ],
                follow_ups=[
                    "What would you do differently with today's tooling?",
                    "Which of their constraints no longer applies, and what does that change?",
                    "Where would this design break at 10x the scale?",
                ],
                related=[url],
            )
        )
    return out


SOURCE_PARSERS = [
    ("Field guide — theory (Modules L/M/N/F/V/W/AE/E/K)", parse_field_guide_theory),
    ("Field guide — coding (Modules A/B)", parse_field_guide_coding),
    ("Field guide — project deep dive (Module AD)", parse_field_guide_project),
    ("Field guide — AI system design (Module S)", parse_field_guide_sysdesign),
    ("Field guide — behavioral (Module AF)", parse_field_guide_behavioral),
    ("khangich — ML/DL fundamentals (Modules D/H)", parse_khangich_questions),
    ("khangich — MLSD use cases (Module R)", parse_khangich_design),
    ("data-science-interviews — theory (Modules C/D/E/F/H/I/J/X/Y)", parse_ds_interviews_theory),
    ("data-science-interviews — SQL (Module A)", parse_ds_interviews_sql),
    ("applied-ml — production case studies (Module AA)", parse_applied_ml_cases),
]
