"""LLM-backed judgement for the topic-verification gate.

The division of labour with app/engines/topic_gate.py is deliberate: this
module decides *facts* an LLM can judge — does this code implement a
circular list, is this explanation of `prev` actually right — and the engine
decides *policy*: what fraction counts as covered, what score passes, how
long a pass lasts. Thresholds never live in a prompt.

No API key means verification cannot run. That returns an explicit error
rather than a default pass or a fabricated score: silently unlocking a topic
nobody checked is exactly the self-deception the gate exists to prevent.

No plagiarism detection is attempted anywhere here, because none of it
works. Authorship is established a different way — the defend stage asks
about the specific code that was submitted, and pasted code cannot be
defended.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from groq import Groq

from app.config import Settings

# Low temperature: this is assessment, not writing. Two runs over the same
# submission should not disagree about whether a doubly-linked list is
# present.
_TEMPERATURE = 0.1
_MAX_QUESTIONS = 5


class GradingUnavailableError(Exception):
    """No LLM configured, or the call failed — verification did not happen.

    Distinct from "failed verification" on purpose: the caller must not
    record a pass or a failure from this, only that it could not run."""


@dataclass(frozen=True)
class CoverageResult:
    covered: list[str]
    missing: list[str]
    concerns: list[str]
    required_count: int
    notes: str


@dataclass(frozen=True)
class GeneratedQuestion:
    question: str
    # "code" questions quote the submission back — the anti-paste mechanism.
    # "concept" questions come from the topic's own checklist.
    kind: str
    expects: str


@dataclass(frozen=True)
class GradedAnswer:
    verdict: str  # correct | partial | wrong — weighted by the engine
    feedback: str


def _client(settings: Settings) -> Groq:
    if not settings.groq_api_key:
        raise GradingUnavailableError(
            "No Groq API key is configured, so a submission cannot be assessed. "
            "Add one in Settings — the gate will not pass a topic it never checked."
        )
    return Groq(api_key=settings.groq_api_key)


def _complete(settings: Settings, system: str, user: str) -> dict[str, Any]:
    client = _client(settings)
    try:
        resp = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=_TEMPERATURE,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content or "{}"
        parsed = json.loads(raw)
    except GradingUnavailableError:
        raise
    except Exception as exc:  # noqa: BLE001 - any failure means "did not run"
        raise GradingUnavailableError(
            f"The assessment call failed, so nothing was recorded: {exc}"
        ) from exc
    if not isinstance(parsed, dict):
        raise GradingUnavailableError("The assessment returned an unexpected shape.")
    return parsed


def required_items(gate_requirements: list[Any]) -> list[str]:
    """The topic's gate checklist — the curated "must be able to do" list on
    the guide, not its reading list.

    Kept as a function rather than inlined so the one place that defines
    "what this gate demands" stays findable; an earlier version derived this
    from the guide's `types`/`operations` and ended up demanding that you
    implement a static array."""
    return [str(item) for item in gate_requirements if str(item).strip()]


def check_build_submission(
    settings: Settings,
    topic_display_name: str,
    required: list[str],
    code: str,
    notes: str,
) -> CoverageResult:
    """Does the submitted implementation actually cover the checklist?"""
    system = (
        "You assess whether a submitted implementation demonstrates each item on a "
        "required checklist "
        "for a data-structures topic. You are strict but fair: mark an item covered "
        "only if the code (or the notes, for a purely conceptual item) genuinely "
        "demonstrates it. Do not credit an item because a comment mentions it. "
        "Do not attempt to detect plagiarism or guess authorship — that is handled "
        "elsewhere. Reply with JSON only, shaped as: "
        '{"covered": [str], "missing": [str], "concerns": [str], "notes": str}. '
        "`covered` and `missing` must use the exact checklist strings given. "
        "`concerns` lists real correctness problems you can point to in the code "
        "(wrong edge case, leaked pointer, wrong complexity claim) — not style."
    )
    user = (
        f"Topic: {topic_display_name}\n\n"
        f"Required checklist ({len(required)} items):\n"
        + "\n".join(f"- {item}" for item in required)
        + f"\n\nSubmitted code:\n```\n{code[:20000]}\n```\n\n"
        f"Submitted notes:\n{notes[:6000] or '(none)'}\n"
    )
    data = _complete(settings, system, user)
    req_set = set(required)
    covered = [c for c in map(str, data.get("covered", []) or []) if c in req_set]
    missing = [m for m in map(str, data.get("missing", []) or []) if m in req_set]
    # Anything the model did not classify counts as missing — an unmentioned
    # item is not a demonstrated one.
    unclassified = [r for r in required if r not in set(covered) | set(missing)]
    return CoverageResult(
        covered=covered,
        missing=missing + unclassified,
        concerns=[str(c) for c in (data.get("concerns", []) or [])],
        required_count=len(required),
        notes=str(data.get("notes", "")),
    )


def generate_defend_questions(
    settings: Settings,
    topic_display_name: str,
    must_know: list[Any],
    pitfalls: list[Any],
    code: str,
    required: list[str] | None = None,
    studied: str = "",
) -> list[GeneratedQuestion]:
    """Closed-book questions, at least half of them about the submitted code.

    Questions must be *generative* — write the pointer sequence, say what
    breaks — rather than recognition, because recognising the right answer
    from a list is not the same as holding the model in your head.

    `studied` is the person's own learning log for this topic: the summary or
    transcript they pasted from a video, their notes, the snippets they kept.
    It exists so the questions land on the mental model they actually built
    rather than a generic one — but it deliberately does **not** bound the
    exam. One question is forced onto a checklist item the log never
    mentions, because otherwise the scope of the test would be chosen by the
    person sitting it, and what they skipped is the most informative thing
    to probe.
    """
    system = (
        "You write a short closed-book viva for someone who has just submitted an "
        "implementation of a data structure. Rules: "
        f"(1) exactly {_MAX_QUESTIONS} questions; "
        "(2) at least half must quote or refer to something specific in THEIR "
        "submitted code (a function they wrote, a variable they used, an ordering "
        "they chose) — these are the questions that cannot be answered by someone "
        "who pasted the code; "
        "(3) every question must be generative: ask them to state a sequence, "
        "explain why, or say what breaks. Never multiple-choice, never yes/no; "
        "(4) answerable in two or three sentences from memory, with no lookup; "
        "(5) their study log, when present, is the material they actually learned "
        "from — a summary or transcript they pasted, in their own or the source's "
        "words. Use it to pitch questions at their real vocabulary and mental "
        "model, and to probe claims it makes. Do NOT limit yourself to it: "
        "exactly one question must target a required checklist item the study log "
        "does not cover, since the gap between what they studied and what the "
        "topic demands is the most useful thing to test. Never quote the study "
        "log back as if it were the answer. "
        'Reply with JSON only: {"questions": [{"question": str, "kind": '
        '"code"|"concept", "expects": str}]}. `expects` is a one-line summary of '
        "what a correct answer must contain, for grading later."
    )
    user = (
        f"Topic: {topic_display_name}\n\n"
        "Techniques they should hold:\n"
        + "\n".join(f"- {m}" for m in must_know)
        + "\n\nKnown pitfalls for this topic:\n"
        + "\n".join(f"- {p}" for p in pitfalls)
        + (
            "\n\nRequired checklist for this topic:\n" + "\n".join(f"- {r}" for r in required)
            if required
            else ""
        )
        + (
            "\n\nTheir study log for this topic — what they say they learned and "
            "from where. Unverified: treat it as their claim, not as fact:\n" + studied
            if studied.strip()
            else "\n\nThey logged nothing about how they studied this topic, so you "
            "have no signal about their mental model — question the checklist "
            "and their code directly."
        )
        + f"\n\nTheir submitted code:\n```\n{code[:20000]}\n```\n"
    )
    data = _complete(settings, system, user)
    out: list[GeneratedQuestion] = []
    for q in (data.get("questions", []) or [])[:_MAX_QUESTIONS]:
        if not isinstance(q, dict) or not q.get("question"):
            continue
        kind = str(q.get("kind", "concept"))
        out.append(
            GeneratedQuestion(
                question=str(q["question"]),
                kind=kind if kind in ("code", "concept") else "concept",
                expects=str(q.get("expects", "")),
            )
        )
    if not out:
        raise GradingUnavailableError("No questions could be generated, so nothing was recorded.")
    return out


def grade_defend_answers(
    settings: Settings,
    topic_display_name: str,
    questions: list[dict[str, Any]],
    answers: list[str],
) -> list[GradedAnswer]:
    """Grade each answer correct / partial / wrong, with a reason."""
    system = (
        "You grade short closed-book answers about a data structure the candidate "
        "just implemented. For each question return one verdict: 'correct' (the "
        "substance is right), 'partial' (right idea, missing an edge case or a "
        "reason), or 'wrong' (mistaken, or restates the question without "
        "answering it). An empty or evasive answer is 'wrong'. Recognising "
        "terminology without explaining the mechanism is 'partial' at best. "
        'Reply with JSON only: {"grades": [{"verdict": str, "feedback": str}]}, '
        "one entry per question in the same order. `feedback` is one sentence "
        "naming what was right or what was missing."
    )
    lines = []
    for i, (q, a) in enumerate(zip(questions, answers, strict=False), start=1):
        lines.append(
            f"Q{i}: {q.get('question', '')}\n"
            f"A correct answer must contain: {q.get('expects', '(unspecified)')}\n"
            f"Their answer: {a.strip() or '(left blank)'}\n"
        )
    data = _complete(settings, system, f"Topic: {topic_display_name}\n\n" + "\n".join(lines))

    graded: list[GradedAnswer] = []
    for g in (data.get("grades", []) or [])[: len(questions)]:
        verdict = str(g.get("verdict", "wrong")).lower() if isinstance(g, dict) else "wrong"
        graded.append(
            GradedAnswer(
                verdict=verdict if verdict in ("correct", "partial", "wrong") else "wrong",
                feedback=str(g.get("feedback", "")) if isinstance(g, dict) else "",
            )
        )
    # A grader that returned fewer verdicts than questions leaves the rest
    # ungraded, which must not silently count as correct.
    while len(graded) < len(questions):
        graded.append(GradedAnswer(verdict="wrong", feedback="Not graded — treated as incorrect."))
    return graded
