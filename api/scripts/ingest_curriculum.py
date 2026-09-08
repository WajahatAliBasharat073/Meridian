"""Seed the interview curriculum: modules + source-derived question records.

Everything here is *parsed from cloned repositories*, not written from
memory. That is the whole point: a question bank that claims "Meta asks
this" has to be able to show where that came from, and a parser can be
re-run and diffed when the upstream repo changes.

Sources and what each one licenses:

  external/AIMLInterviews            MIT (c) 2021 Alireza Dirafzoon
  external/Agentic-AI-Systems        MIT (c) 2025 Alireza Dirafzoon

  external/Production-Level-Deep-Learning
      NO LICENSE FILE. No licence is granted by default, so none of its
      text is copied here. It is used only as a topic checklist for
      Module U, whose submodules are named in curriculum_modules.py.

Company tags come from AIMLInterviews' ML-coding tables, which state their
own provenance: "Company tags appear only when a reference associates the
company with the same implementation problem. They are historical
preparation signals, not claims about a current interview loop." That
caveat travels with the data into `tests_for`, so it reaches the UI rather
than being lost at import.

Usage:
    python -m scripts.ingest_curriculum            # dry run, counts only
    python -m scripts.ingest_curriculum --apply
"""

from __future__ import annotations

import asyncio
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import delete, select

from app.db import SessionLocal
from app.models.questions import InterviewModule, Question
from scripts.curriculum_modules import MODULES

REPO_ROOT = Path(__file__).resolve().parents[2]
EXTERNAL = REPO_ROOT / "external"
AIML = EXTERNAL / "AIMLInterviews"
AGENTIC = EXTERNAL / "Agentic-AI-Systems"

AIML_BLOB = "https://github.com/alirezadir/AIMLInterviews/blob/main"
AGENTIC_BLOB = "https://github.com/alirezadir/Agentic-AI-Systems/blob/main"

COMPANY_TAG_CAVEAT = (
    "Company tags are the source repo's historical preparation signals — a reference "
    "associated that company with this implementation problem. They are not claims "
    "about a current interview loop."
)

DIFFICULTY_MAP = {"easy": "beginner", "medium": "intermediate", "hard": "advanced"}

# Letters whose *name* begins with a vowel sound, so an acronym spelled out
# letter-by-letter takes "an": an LLM, an OCR, an SVM.
_VOWEL_SOUND_LETTERS = set("AEFHILMNORSX")

# Acronyms pronounced as words rather than spelled out, so they follow the
# ordinary vowel rule: "a RAG pipeline", not "an RAG pipeline".
_WORD_ACRONYMS = {"RAG", "GAN", "GANS", "ROC", "SOTA", "MOE", "LORA"}


def _as_design_prompt(title: str) -> str:
    """Turn a topic label into a grammatical design prompt.

    Naively lowercasing the first character turns "RAG document Q&A" into
    "rAG document Q&A", and a fixed "a" gives "a agentic workflow" and
    "a LLM assistant". Both are the kind of detail that makes a generated
    bank look generated.
    """
    title = title.strip().rstrip(".")
    if not title:
        return title
    if title.lower().startswith("design"):
        return f"{title}."

    first = title.split()[0]
    is_acronymish = first.isupper() or (len(first) > 1 and any(c.isupper() for c in first[1:]))
    lead = title if is_acronymish else title[0].lower() + title[1:]

    head = lead.lstrip("(\"'")
    spelled_out = (
        head[:1].isupper()
        and head[1:2].isupper()
        and re.split(r"[^A-Za-z]", head)[0].upper() not in _WORD_ACRONYMS
    )
    if spelled_out and head[:1] in _VOWEL_SOUND_LETTERS:
        article = "an"  # acronym: an LLM, an OCR
    else:
        article = "an" if head[:1].lower() in "aeiou" else "a"
    return f"Design {article} {lead}."


@dataclass
class QRecord:
    category: str
    title: str
    source: str
    module_code: str
    submodule: str | None = None
    question_type: str = "concept"
    difficulty: str | None = None
    seniority: str | None = None
    priority: str = "P1"
    frequency: str = "unknown"
    evidence: str = "derived"
    source_url: str | None = None
    tests_for: str | None = None
    companies: list[str] = field(default_factory=list)
    answer_dimensions: list[str] = field(default_factory=list)
    follow_ups: list[str] = field(default_factory=list)
    common_mistakes: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    strong_signal: str | None = None
    weak_signal: str | None = None
    reference_solution: str | None = None


def _strip_md(cell: str) -> str:
    """Markdown cell -> plain text: drop images, unwrap links, collapse space."""
    cell = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", cell)
    cell = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell)
    cell = cell.replace("`", "").replace("**", "")
    return re.sub(r"\s+", " ", cell).strip()


def _difficulty_from_cell(cell: str) -> str | None:
    m = re.search(r"difficulty-(easy|medium|hard)", cell, re.I) or re.search(
        r"\b(easy|medium|hard)\b", cell, re.I
    )
    return DIFFICULTY_MAP.get(m.group(1).lower()) if m else None


def _read_reference_solution(md_link_line: str) -> tuple[str | None, str | None]:
    """(docstring, full source) for the .py file an Answer-column cell
    links to, or (None, None) when the row has no Python answer (some
    rows link only to a Notebook).

    The docstring is read separately from the source because it becomes
    the enriched problem statement (tests_for); the source is the actual
    "coding of ml" content the table summary never carried.
    """
    m = re.search(r"\[Python\]\((\./problems/[^)]+\.py)\)", md_link_line)
    if not m:
        return None, None
    file_path = AIML / "src" / "MLC" / m.group(1)
    if not file_path.exists():
        return None, None
    source = file_path.read_text(encoding="utf-8")
    doc = re.match(r'^"""(.*?)"""', source, re.S)
    docstring = re.sub(r"\s+", " ", doc.group(1)).strip() if doc else None
    return docstring, source


def parse_ml_coding() -> list[QRecord]:
    """Module B — the four canonical ML-coding tables, enriched with the
    actual linked .py files rather than only the table's summary row.

    The table alone gives a title, difficulty, tags and a terse focus
    line. Each linked file adds what an "ML coding" question is supposed
    to have and the table never carried: the real problem statement (the
    module docstring — more specific than the focus column) and a working
    reference implementation, stored in `reference_solution`.
    """
    path = AIML / "src" / "MLC" / "ml-coding.md"
    text = path.read_text(encoding="utf-8")
    url = f"{AIML_BLOB}/src/MLC/ml-coding.md"

    section_to_submodule = {
        "Classic ML": "Classic ML primitives",
        "Language Models (LM)": "Language-model mechanics",
        "Generative AI (GenAI)": "GenAI primitives",
        "Agentic AI coding": "Agentic control-plane coding",
    }

    out: list[QRecord] = []
    current: str | None = None
    for line in text.splitlines():
        heading = re.match(r"^###\s+(.*)", line)
        if heading:
            current = section_to_submodule.get(heading.group(1).strip())
            continue
        if current is None or not line.startswith("|"):
            continue
        cells = [c for c in line.split("|")[1:-1]]
        if len(cells) < 6:
            continue
        title = _strip_md(cells[0])
        if not title or title.lower() in {"problem", "---"} or set(title) <= {"-", " "}:
            continue

        difficulty = _difficulty_from_cell(cells[1])
        tags = _strip_md(cells[2])
        company_cell = _strip_md(cells[3])
        focus = _strip_md(cells[5])
        docstring, reference_solution = _read_reference_solution(cells[4])

        companies = (
            []
            if company_cell in {"—", "-", ""}
            else [c.strip() for c in company_cell.split(",") if c.strip()]
        )

        # The docstring's "Interview prompt: ..." sentence is the real
        # problem statement; fall back to the table's terse focus column
        # for the handful of rows with no linked .py file (notebook-only).
        tests_for = docstring or focus
        if tests_for and not tests_for.endswith("."):
            tests_for += "."
        if companies:
            tests_for = f"{tests_for} {COMPANY_TAG_CAVEAT}"

        out.append(
            QRecord(
                category="ml_coding",
                title=f"Implement: {title}",
                source="AIMLInterviews",
                module_code="B",
                submodule=current,
                question_type="coding",
                difficulty=difficulty,
                # An implementation round is asked from junior up; the bar
                # rises with the follow-ups, not with the prompt.
                seniority="mid",
                priority="P0" if difficulty in {"beginner", "intermediate"} else "P1",
                frequency="unknown",
                evidence="reported" if companies else "common",
                source_url=url,
                companies=companies,
                tests_for=tests_for,
                reference_solution=reference_solution,
                answer_dimensions=[t.strip() for t in tags.split(",") if t.strip()],
                follow_ups=[
                    "State shapes, dtypes and assumptions before coding.",
                    "Give time and space complexity, including large intermediates.",
                    "Handle numerical stability, empty input, ties and invalid labels.",
                    "How does this change on GPU, distributed, or at production scale?",
                ],
                strong_signal="Correct baseline first, then optimises the actual bottleneck; "
                "tests a boundary case unprompted.",
                weak_signal="Reaches for a library call, or cannot state the shapes.",
            )
        )
    return out


def parse_dsa_patterns() -> list[QRecord]:
    """Module A — patterns, not a LeetCode dump.

    The source table is (pattern, signals). Each becomes one question about
    *recognising* the pattern, which is the skill the round tests.
    """
    path = AIML / "src" / "lc-coding.md"
    text = path.read_text(encoding="utf-8")
    url = f"{AIML_BLOB}/src/lc-coding.md"

    out: list[QRecord] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Pattern focus"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                break
            cells = line.split("|")[1:-1]
            if len(cells) < 2:
                continue
            pattern = _strip_md(cells[0])
            signals = _strip_md(cells[1])
            if not pattern or set(pattern) <= {"-", " "}:
                continue
            out.append(
                QRecord(
                    category="dsa",
                    title=f"{pattern}: what in a problem statement tells you to reach for this, "
                    f"and what is the complexity you should quote?",
                    source="AIMLInterviews",
                    module_code="A",
                    submodule=pattern,
                    question_type="coding",
                    difficulty="intermediate",
                    seniority="junior",
                    priority="P0",
                    frequency="high",
                    evidence="common",
                    source_url=url,
                    tests_for=f"Pattern recognition from the statement. Signals: {signals}.",
                    answer_dimensions=[s.strip() for s in signals.split(",") if s.strip()],
                    follow_ups=[
                        "Give a problem where this pattern looks right but is wrong.",
                        "What is the brute force, and what does this pattern buy over it?",
                        "How does the approach change if the input does not fit in memory?",
                    ],
                    strong_signal="Names the signal in the statement before naming the algorithm.",
                    weak_signal="Recites a memorised solution to a specific problem.",
                )
            )
    return out


def parse_mlsd_prompts() -> list[QRecord]:
    """Modules R and S — the ML system design sample-question list."""
    path = AIML / "src" / "MLSD" / "ml-system-design.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    url = f"{AIML_BLOB}/src/MLSD/ml-system-design.md"

    # Only the "2. ML System Design Sample Questions" section.
    try:
        start = next(i for i, ln in enumerate(lines) if ln.startswith("# 2. ML System Design Sample"))
        end = next(i for i, ln in enumerate(lines[start + 1 :], start + 1) if ln.startswith("# 3."))
    except StopIteration:
        return []

    genai_sections = {"Generative AI / LLM Systems (2026)"}
    section_module = {
        "Recommendation Systems": ("R", "Recommendation systems"),
        "Search systems (retrieval, ranking)": ("R", "Search & ranking"),
        "Ranking systems": ("R", "Ads & newsfeed"),
        "NLP": ("R", "Search & ranking"),
        "CV": ("R", "Architecture & MVP logic"),
        "AV": ("R", "Architecture & MVP logic"),
        "Other": ("R", "Fraud, spam & moderation"),
    }

    out: list[QRecord] = []
    current_section: str | None = None
    seen: set[str] = set()
    for ln in lines[start:end]:
        h = re.match(r"^#{2,3}\s+(.*)", ln)
        if h:
            current_section = h.group(1).strip()
            continue
        item = re.match(r"^\s*-\s+(.*)", ln)
        if not item or current_section is None:
            continue
        title = _strip_md(item.group(1))
        # Drop parenthetical company examples: "(Netflix, Youtube)" is the
        # repo naming a product domain, not reporting an interview question.
        title = re.sub(r"\s*\([^)]*\)\s*$", "", title).strip()
        title = title.rstrip(",;:. ")
        # ", and " marks a list of sub-topics ("Perception, Prediction, and
        # Planning"), which is a deep-dive checklist rather than a design
        # prompt — it belongs to its parent question, not beside it.
        if not title or len(title) < 4 or ", and " in title or title.lower() in seen:
            continue
        seen.add(title.lower())

        is_genai = current_section in genai_sections
        module, submodule = ("S", "Enterprise RAG assistant") if is_genai else section_module.get(
            current_section, ("R", "Architecture & MVP logic")
        )
        out.append(
            QRecord(
                category="ml_system_design" if not is_genai else "genai_system_design",
                title=_as_design_prompt(title),
                source="AIMLInterviews",
                module_code=module,
                submodule=submodule,
                question_type="system_design",
                difficulty="advanced",
                seniority="senior",
                priority="P0",
                frequency="high",
                evidence="common",
                source_url=url,
                tests_for="Whether the 9-step design spine is driven rather than wandered through: "
                "problem formulation, metrics, architecture, data, features, model, serving, "
                "online testing, scaling and monitoring.",
                answer_dimensions=[
                    "Requirements & business objective", "Offline and online metrics",
                    "Architecture & MVP", "Data & labels", "Features", "Model choice",
                    "Serving & latency", "Online testing", "Monitoring & drift",
                    "Retraining & rollback", "Cost", "Failure modes",
                ],
                follow_ups=[
                    "What is your fallback when the model service is down?",
                    "How do you detect that this has degraded before a user reports it?",
                    "Do the rough QPS, storage and cost maths.",
                    "What would you cut to ship this in one quarter?",
                ],
                strong_signal="Converts ambiguity into measurable goals and explicit scope cuts; "
                "names discarded alternatives and why.",
                weak_signal="Lists components without decisions, metrics, or failure modes.",
            )
        )
    return out


def parse_agentic_prompts() -> list[QRecord]:
    """Modules S, T and W — the GenAI/agentic interview question bank."""
    path = AGENTIC / "06_interview_prep" / "genai-agentic-system-design.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    url = f"{AGENTIC_BLOB}/06_interview_prep/genai-agentic-system-design.md"

    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == "## Interview Question Bank")
        end = next(i for i, ln in enumerate(lines[start + 1 :], start + 1) if ln.startswith("## Practice"))
    except StopIteration:
        return []

    # Tier 1/2/3 in the repo's topic map is a frequency signal, so carry it.
    tier_text = "\n".join(lines)
    tier1 = re.search(r"### Tier 1: Almost Always\n(.*?)\n###", tier_text, re.S)
    tier1_items = (
        [_strip_md(x).rstrip(".").lower() for x in re.findall(r"^-\s+(.*)$", tier1.group(1), re.M)]
        if tier1
        else []
    )

    section_map = {
        "GenAI System Design": ("S", "genai_system_design", "system_design", "senior"),
        "Agentic AI System Design": ("T", "agentic_ai", "system_design", "senior"),
        "Inference and Cost Probes": ("W", "ml_infrastructure", "concept", "senior"),
    }

    out: list[QRecord] = []
    current: tuple[str, str, str, str] | None = None
    for ln in lines[start:end]:
        h = re.match(r"^###\s+(.*)", ln)
        if h:
            current = section_map.get(h.group(1).strip())
            continue
        item = re.match(r"^\s*-\s+(.*)", ln)
        if not item or current is None:
            continue
        title = _strip_md(item.group(1))
        if not title:
            continue
        module, category, qtype, seniority = current

        stem = title.lower().rstrip(".").replace("design an ", "").replace("design a ", "")
        frequency = "very_high" if any(stem in t or t in stem for t in tier1_items) else "high"

        out.append(
            QRecord(
                category=category,
                title=title,
                source="Agentic-AI-Systems",
                module_code=module,
                submodule=None,
                question_type=qtype,
                difficulty="advanced",
                seniority=seniority,
                priority="P0" if frequency == "very_high" else "P1",
                frequency=frequency,
                evidence="common",
                source_url=url,
                tests_for="The five-step framing (users, constraints, metrics, scope), then "
                "architecture, three deep dives, five failure modes, and one cost calculation.",
                answer_dimensions=[
                    "Models & routing", "Prompting & context", "RAG", "Caching", "Streaming",
                    "Latency (p50/p99)", "Token cost", "Safety & guardrails", "Evaluation",
                    "Observability", "Fallbacks",
                ]
                if module in {"S", "T"}
                else ["Throughput", "Latency", "Memory", "Cost per token", "Utilization"],
                follow_ups=[
                    "Scale it to 1M daily active users and cut the cost.",
                    "How do you reduce p99 without reducing answer quality?",
                    "What breaks first, how would you detect it, and what is the blast radius?",
                ],
                common_mistakes=[
                    "Jumping to an architecture before defining success.",
                    "No evaluation or monitoring in the design.",
                    "Unnecessary agentic complexity where a workflow would do.",
                ],
                strong_signal="Does rough QPS/token/GPU/cost maths and defends discarded options.",
                weak_signal="Says 'it scales' without numbers; happy path only.",
            )
        )
    return out


def parse_behavioral() -> list[QRecord]:
    """Module AF — the repo's common behavioral list."""
    path = AIML / "src" / "behavioral" / "behavior.md"
    text = path.read_text(encoding="utf-8")
    url = f"{AIML_BLOB}/src/behavioral/behavior.md"

    section = re.search(r"## Common Questions\n(.*?)\n\n", text, re.S)
    if not section:
        return []

    out: list[QRecord] = []
    for raw in re.findall(r"^\*\s+(.*)$", section.group(1), re.M):
        title = _strip_md(raw)
        if not title:
            continue
        out.append(
            QRecord(
                category="behavioral",
                title=title,
                source="AIMLInterviews",
                module_code="AF",
                submodule=None,
                question_type="behavioral",
                difficulty="intermediate",
                seniority="mid",
                priority="P0",
                frequency="very_high",
                evidence="common",
                source_url=url,
                tests_for="A STAR-structured story carrying real technical depth — the decision "
                "you personally made and what it cost.",
                answer_dimensions=["Situation", "Task", "Action", "Result", "What you'd change"],
                follow_ups=[
                    "What would you do differently now?",
                    "What was the hardest technical decision *you personally* made there?",
                    "Who disagreed with you, and how did that resolve?",
                ],
                weak_signal="Says 'we' throughout and never names their own decision.",
            )
        )
    return out


# The 121 questions from the earlier ingestion pass predate the master map.
# They are this assistant's own phrasing of standard interview topics, so
# they are `fundamental` — core knowledge with no company claim attached —
# rather than `reported`. Mapping them in rather than re-writing them keeps
# the bank deduplicated.
LEGACY_CATEGORY_TO_MODULE: dict[str, tuple[str, str]] = {
    "classical_ml": ("D", "P0"),
    "deep_learning": ("H", "P0"),
    "llm_genai": ("L", "P0"),
    "ml_system_design": ("R", "P0"),
    "agentic_ai": ("N", "P1"),
    "mlops": ("U", "P1"),
}


async def backfill_legacy(session) -> int:  # type: ignore[no-untyped-def]
    """Give the pre-master-map questions a module, priority and evidence tier."""
    rows = (
        await session.execute(select(Question).where(Question.module_code.is_(None)))
    ).scalars().all()
    for q in rows:
        module, priority = LEGACY_CATEGORY_TO_MODULE.get(q.category, ("E", "P1"))
        q.module_code = module
        q.priority = priority
        q.evidence = "fundamental"
        q.question_type = "system_design" if q.category == "ml_system_design" else "concept"
        q.difficulty = q.difficulty or "intermediate"
        q.seniority = q.seniority or "mid"
        q.frequency = q.frequency or "unknown"
    await session.commit()
    return len(rows)


# Words that carry no distinguishing meaning when comparing two question
# phrasings. "Explain the concept of bias vs variance" and "What is the
# bias-variance tradeoff" must land on the same canonical question.
_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "being", "been", "do", "does", "did",
    "what", "which", "who", "whom", "how", "why", "when", "where", "can", "could", "would",
    "should", "will", "shall", "may", "might", "must", "of", "in", "on", "at", "to", "for",
    "with", "about", "against", "between", "into", "through", "and", "or", "but", "if",
    "then", "than", "that", "this", "these", "those", "it", "its", "you", "your", "we",
    "our", "i", "me", "my", "s", "t", "explain", "describe", "define", "tell", "give",
    "concept", "main", "some", "any", "there", "here", "please", "vs", "versus", "difference",
    "differences",
}

# Two questions whose *distinctive* words overlap this much are the same
# question wearing different clothes. Tuned by inspecting --show-merges
# against the real corpus:
#
#   0.80  merges more rephrasings, but also merged two different SQL
#         prompts ("...per campaign" vs "...per active advertiser")
#   0.88  no false merges observed; costs one genuine merge
#         ("What is KV cache?" stays separate from "What is KV-cache and
#         how does it help inference?")
#
# 0.88 is the deliberate choice: a surviving near-duplicate costs a little
# repeated study, while a wrong merge silently deletes a distinct question
# and its sources. Re-run with --show-merges after adding a source.
_DUPLICATE_THRESHOLD = 0.88


def _content_tokens(title: str) -> frozenset[str]:
    """Distinctive words in a question title.

    Single-character tokens are dropped as noise *except* digits: "1-D
    dynamic programming" and "2-D dynamic programming" differ only in a
    one-character token, and discarding it made the two titles identical
    to the comparer — which merged two genuinely different DP patterns.
    """
    words = re.sub(r"[^a-z0-9\s]+", " ", title.lower()).split()
    return frozenset(
        w for w in words if w not in _STOPWORDS and (len(w) > 1 or w.isdigit())
    )


def _idf_weights(records: list[QRecord]) -> dict[str, float]:
    """Inverse document frequency over every question title.

    Plain token overlap merged "1-D dynamic programming: what in a problem
    statement tells you to reach for this..." into the 2-D version, because
    the shared template is most of the sentence. Weighting by IDF drives
    boilerplate to almost zero and lets "1-D" vs "2-D" — the words that
    actually distinguish the two — decide.
    """
    total = max(1, len(records))
    df: Counter[str] = Counter()
    for r in records:
        df.update(_content_tokens(r.title))
    return {tok: math.log(total / (1 + n)) + 0.1 for tok, n in df.items()}


def _weighted_similarity(a: frozenset[str], b: frozenset[str], w: dict[str, float]) -> float:
    union = a | b
    if not union:
        return 0.0
    denom = sum(w.get(t, 1.0) for t in union)
    if denom <= 0:
        return 0.0
    return sum(w.get(t, 1.0) for t in a & b) / denom


def deduplicate(records: list[QRecord]) -> tuple[list[QRecord], int, list[tuple[str, str]]]:
    """One canonical question per concept, with every source attached.

    Exact-title matching is not enough: nine repositories phrase "explain
    bias vs variance" nine ways, and shipping all nine would make the bank
    look large while teaching the same thing repeatedly.

    Comparison is *global*, not per-module: the same question genuinely
    lands in different modules depending on which repo it came from (one
    repo files bias-variance under "Validation", another under "ML
    fundamentals"), so scoping the comparison by module would let those
    two copies both survive — which is the exact failure this exists to
    prevent. The surviving record keeps the richer body (more follow-ups)
    plus the union of company tags and sources.
    """
    weights = _idf_weights(records)
    scanned: list[tuple[frozenset[str], QRecord]] = []
    kept: list[QRecord] = []
    merged = 0
    log: list[tuple[str, str]] = []

    for r in records:
        tokens = _content_tokens(r.title)

        match: QRecord | None = None
        for other_tokens, other in scanned:
            # A design prompt and a concept question about the same subject
            # are different interviews; never collapse across those.
            if other.question_type != r.question_type:
                continue
            if _weighted_similarity(tokens, other_tokens, weights) >= _DUPLICATE_THRESHOLD:
                match = other
                break

        if match is None:
            scanned.append((tokens, r))
            kept.append(r)
            continue

        merged += 1
        log.append((match.title, r.title))
        for c in r.companies:
            if c not in match.companies:
                match.companies.append(c)
        # A second independent source raises confidence that it is real.
        if r.source not in (match.related or []):
            match.related.append(r.source)
        if r.evidence == "reported" and match.evidence != "reported":
            match.evidence, match.source_url = "reported", r.source_url
        # Keep whichever phrasing carries more interrogation behind it.
        if len(r.follow_ups) > len(match.follow_ups):
            match.follow_ups = r.follow_ups
        if not match.tests_for and r.tests_for:
            match.tests_for = r.tests_for
        # A real reference implementation is the rarer, more valuable side
        # of a merge — never let it be silently dropped in favour of a
        # record that only has a title.
        if not match.reference_solution and r.reference_solution:
            match.reference_solution = r.reference_solution

    return kept, merged, log


def _all_parsers():  # noqa: ANN202
    """Repo parsers, in ingestion order. Imported lazily so this module can
    still be imported by curriculum_sources.py without a cycle."""
    from scripts.curriculum_gaps import SPEC_PARSERS
    from scripts.curriculum_sources import SOURCE_PARSERS

    return PARSERS + SOURCE_PARSERS + SPEC_PARSERS


PARSERS = [
    ("ML coding (Module B)", parse_ml_coding),
    ("DSA patterns (Module A)", parse_dsa_patterns),
    ("ML system design (Modules R/S)", parse_mlsd_prompts),
    ("GenAI & agentic design (Modules S/T/W)", parse_agentic_prompts),
    ("Behavioral (Module AF)", parse_behavioral),
]


async def main(apply: bool) -> None:
    required = [
        AIML, AGENTIC,
        EXTERNAL / "ai-engineering-field-guide",
        EXTERNAL / "machine-learning-interview",
        EXTERNAL / "data-science-interviews",
        EXTERNAL / "applied-ml",
    ]
    for repo in required:
        if not repo.exists():
            print(f"MISSING: {repo} — clone it first (see module docstring).")
            return

    records: list[QRecord] = []
    for label, parser in _all_parsers():
        got = parser()
        print(f"  {label}: {len(got)} questions")
        records.extend(got)

    records, dupes, merge_log = deduplicate(records)

    with_companies = sum(1 for r in records if r.companies)
    print(f"\n  {len(records)} canonical questions ({dupes} near-duplicates merged)")
    print(f"  {with_companies} carry company tags, all evidence='reported' with a source URL")
    print(f"  modules: {len(MODULES)}")
    if merge_log and "--show-merges" in sys.argv:
        print("\n  merges (dropped -> canonical):")
        for canonical, dropped in merge_log:
            print(f"    {dropped[:72]!r}\n      -> {canonical[:72]!r}")

    if not apply:
        print("\nDry run. Re-run with --apply to write.")
        return

    async with SessionLocal() as session:
        existing_modules = {
            m.code: m for m in (await session.execute(select(InterviewModule))).scalars().all()
        }
        for idx, (code, title, priority, seniority, summary, submodules) in enumerate(MODULES, 1):
            if code in existing_modules:
                m = existing_modules[code]
                m.title, m.summary, m.priority = title, summary, priority
                m.submodules, m.target_seniority, m.order_index = submodules, seniority, idx
            else:
                session.add(
                    InterviewModule(
                        code=code, title=title, summary=summary, priority=priority,
                        submodules=submodules, target_seniority=seniority, order_index=idx,
                    )
                )
        await session.commit()

        # Source-derived rows are replaceable as a set; the 121 curated
        # questions from the earlier pass have other `source` values and are
        # left untouched here.
        sources = {
            "AIMLInterviews",
            "Agentic-AI-Systems",
            "ai-engineering-field-guide",
            "khangich/machine-learning-interview",
            "data-science-interviews (CC BY 4.0)",
            "eugeneyan/applied-ml",
            "curriculum spec",
        }
        await session.execute(
            delete(Question).where(Question.source.in_(sources), Question.module_code.isnot(None))
        )
        await session.commit()

        for idx, r in enumerate(records, 1):
            session.add(
                Question(
                    category=r.category, title=r.title, source=r.source, order_index=idx,
                    module_code=r.module_code, submodule=r.submodule, concept=r.submodule,
                    question_type=r.question_type, difficulty=r.difficulty, seniority=r.seniority,
                    priority=r.priority, frequency=r.frequency, evidence=r.evidence,
                    source_url=r.source_url, tests_for=r.tests_for, companies=r.companies,
                    answer_dimensions=r.answer_dimensions, follow_ups=r.follow_ups,
                    common_mistakes=r.common_mistakes, prerequisites=r.prerequisites,
                    related=r.related, strong_signal=r.strong_signal, weak_signal=r.weak_signal,
                    reference_solution=r.reference_solution,
                )
            )
        await session.commit()

        mapped = await backfill_legacy(session)
        total = len((await session.execute(select(Question.id))).scalars().all())
        print(f"\nWrote {len(records)} source-derived questions.")
        print(f"Mapped {mapped} pre-existing questions into the master map.")
        print(f"Bank total: {total}")


if __name__ == "__main__":
    asyncio.run(main(apply="--apply" in sys.argv))
