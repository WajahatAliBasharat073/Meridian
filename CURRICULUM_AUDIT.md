# Curriculum Rebuild — Audit & Proposed Architecture

**Status: audit only. No code has been changed.**

Every number in this document is a query against the live bank
(724 questions, 32 modules), not an estimate. Where something is a
proposal rather than a measurement, it says so.

---

## 1. Verdict

The complaint is correct, and it is worse than "occasionally shows an
unrelated question". I ran the current daily picker against a
zero-progress learner. These are its first six days, unedited:

| Day | Questions served |
|---|---|
| 1 | Case study — Google: Smart Reply · How do you evaluate a chatbot? · How do you manage projects under pressure? |
| 2 | Case study — DoorDash: Retraining ML Models · Tell me about a time you made a mistake · How do you measure hallucination rate in production? |
| 3 | Case study — LinkedIn: Preventing Abuse · What is the context window? · What's your proudest project? |
| 4 | Case study — Google: Diagnose with LSTM · Prompt injection and jailbreaking · Communicating to non-technical stakeholders |
| 5 | Case study — Microsoft: Speech transcription · Design an LLM chatbot at scale · Fine-tune vs prompt vs RAG |
| 6 | Case study — Twitter: Embeddings@Twitter · Tell me about a time you made a mistake · What is PEFT/LoRA? |

Across the **first 30 questions** a new learner receives:

```
ml_case_study      10      classical_ml        0
behavioral          7      ml_fundamentals     0
llm_genai           3      math_stats          0
responsible_ai      3      deep_learning       0
evaluation          2
genai_system_design 2
llmops / infra / agentic  3
```

Zero Classical ML. Zero fundamentals. Zero mathematics. Day 1 of learning
machine learning is *"Case study — Google Smart Reply"* and *"How do you
manage projects under pressure?"*

This is not near-random. It is close to reverse-ordered: the bank's most
advanced, most applied material is served first.

> Caveat on the simulation: I passed empty progress on every day, so a
> question can recur across days (it does — "Tell me about a time you made
> a mistake" appears on days 2 and 6). In real use, answering records
> progress and suppresses it. The topic *distribution* above is unaffected.

---

## 2. Current structure, measured

**724 questions · 32 modules (A–AF) · every question has a module · no
question is orphaned.**

| | |
|---|---|
| Exact-normalised duplicate titles | **0** |
| Questions with no `module_code` | **0** |
| Modules with zero questions | **0** |

The bank is in far better shape than the sequencing suggests. This is a
**structure problem, not a content problem.**

### By difficulty

| | count | share |
|---|---|---|
| beginner | 49 | 7% |
| intermediate | 418 | 58% |
| advanced | 257 | 35% |

### By question type

| | count |
|---|---|
| concept | 419 |
| system_design | 98 |
| coding | 79 |
| case_study | 52 |
| behavioral | 38 |
| project_deep_dive | 27 |
| debugging | 11 |

### Module inventory

| Code | Module | P | Qs |
|---|---|---|---|
| A | General Coding & DSA | P0 | 36 |
| B | ML Coding | P0 | 43 |
| C | Mathematics & Statistics | P0 | 12 |
| D | Classical Machine Learning | P0 | 119 |
| E | ML Fundamentals & Breadth | P0 | 28 |
| F | Model Evaluation | P0 | 10 |
| G | Experimentation & A/B Testing | P1 | 10 |
| H | Deep Learning | P0 | 31 |
| I | Computer Vision | P2 | 13 |
| J | NLP | P1 | 14 |
| K | Transformers | P0 | 20 |
| L | Foundation Models & LLMs | P0 | 31 |
| M | RAG | P0 | 29 |
| N | AI Agents | P1 | 19 |
| O | Context Engineering | P1 | **1** |
| P | MCP / A2A / AI Protocols | P2 | **2** |
| Q | Multimodal AI | P2 | 7 |
| R | ML System Design | P0 | 42 |
| S | GenAI System Design | P0 | 42 |
| T | Agentic System Design | P1 | 7 |
| U | Production ML & MLOps | P1 | 16 |
| V | LLMOps & AI Operations | P1 | 6 |
| W | ML Infrastructure | P2 | 15 |
| X | Recommendation Systems | P1 | 6 |
| Y | Search & Information Retrieval | P1 | 11 |
| Z | ML Debugging | P1 | 11 |
| AA | ML Case Studies | P1 | 52 |
| AB | AI Product & Business Reasoning | P1 | 9 |
| AC | Research & Paper Understanding | P2 | 12 |
| AD | Project Deep Dive | P0 | 27 |
| AE | Responsible AI & Security | P2 | 5 |
| AF | Behavioral & Leadership | P0 | 38 |

---

## 3. Why it fails — three mechanisms, not one

Reading `api/app/engines/daily_theory.py` against the data:

**(a) Module diversity is the scatter engine.** `_pick_diverse()` enforces
*no two questions from the same module per day*. It was written to prevent
monotony. Its actual effect is to guarantee that a learner can never spend
a day inside one topic — the rule that would make Linear Regression day
possible is explicitly forbidden.

**(b) The case-study quota fires unconditionally.** `case_study_count=1`
means one applied industry case study every single day, drawn from module
AA (52 questions), regardless of whether the learner knows what a loss
function is. That is why AA appears on 10 out of 10 days.

**(c) There is no notion of "foundational".** For a zero-progress learner
every question is tier 1 (never seen), so ranking collapses to
`priority_rank → frequency_rank`. Priority is *interview* priority (P0 =
appears in most loops), which correlates with **advanced**, not with
**first**. The bank's P0 modules include GenAI System Design and
Foundation Models.

The picker is doing exactly what it was built to do. The model underneath
it has no concept of prerequisite, phase, or readiness — so there is
nothing for it to respect.

### What the schema is missing

`Question` currently has: `category, module_code, submodule, concept,
question_type, difficulty, seniority, priority, frequency, evidence`.

It has **no** `phase`, **no** `prerequisites`, **no** `learning_objective`,
**no** cognitive level, **no** `preview` flag. The dependency graph the
request asks for does not exist in any form — it cannot be "fixed" in the
picker, because the picker has no data to sort on.

---

## 4. The core proposal: two axes, not one

This is the central idea, and it comes straight out of the data.

Of 724 questions, **217 (30%) are not knowledge topics at all** — they are
*formats*: DSA coding, ML coding, case studies, project deep dives,
behavioral, product reasoning, research reading. Today they sit in the same
list as "What is Linear Regression?" and compete for the same daily slots.

Split them:

```
KNOWLEDGE AXIS  ──►  what should I learn next?      (drives sequencing)
     phase → topic → subtopic → prerequisites

FORMAT AXIS     ──►  how should this be tested?     (drives presentation)
     concept · intuition · maths · derivation · implementation ·
     debugging · comparison · tradeoff · practical · case study ·
     system design · interview
```

**Every question keeps exactly one knowledge location and one primary
format.** A case study about fraud detection is not "phase: case studies" —
it is *Classification + Imbalance, tested as a case study*, and it becomes
eligible when those topics are mastered, not before.

That single change removes the entire class of bug in §1: case studies stop
being a daily quota and become a consolidation format that unlocks with
its subject matter.

---

## 5. Proposed phase hierarchy — with real counts

Mapping all 32 modules onto the requested canonical curriculum. Every one
of the 724 places cleanly; nothing is unmapped.

### Knowledge axis — 507 questions

| Phase | Qs | From modules |
|---|---|---|
| P0 Prerequisites | 12 | C |
| P1 ML Foundations | 28 | E |
| P2–P4 Classical ML | 119 | D |
| P5 Practical ML / Evaluation | 31 | F, G, Z |
| P6–P7 Deep Learning | 31 | H |
| P7 Attention / Transformers | 20 | K |
| P8 NLP | 14 | J |
| P9 Computer Vision | 13 | I |
| P10 LLM Foundations | 31 | L |
| P11 Retrieval / RAG | 40 | M, Y |
| P12 Agents | 19 | N |
| P13 Context Engineering | 1 | O |
| P13 Protocols (MCP/A2A) | 2 | P |
| P14 Multimodal | 7 | Q |
| P15 ML Systems / MLOps | 42 | U, V, W, AE |
| P16 System Design | 97 | R, S, T, X |

### Format axis — 217 questions

| Format | Qs | Sequenced by |
|---|---|---|
| Case study | 52 | the topics each case exercises |
| ML coding | 43 | the algorithm being implemented |
| Behavioral | 38 | not gated — always available |
| DSA coding | 36 | its own parallel track |
| Project deep dive | 27 | not gated — always available |
| Research reading | 12 | the topic of the paper |
| Product reasoning | 9 | P16 |

### The headline number

```
reachable in phases P0–P5 :  190  (26%)
gated behind Deep Learning+ :  317  (44%)
```

Only about a quarter of the bank is legitimately available to someone
working through Classical ML. Today, **100% of it is available on day
one** — which is precisely the reported symptom.

---

## 6. Dependency graph

AND-dependencies unless noted. Topic-level, not question-level.

```
Python/NumPy ─┐
Linear Algebra├─► ML Foundations ─► Linear Regression ─► Regularization ─┐
Probability  ─┘         │                    │                          │
                        │                    └─► Gradient Descent ──────┤
                        │                                               ▼
                        └────────────────────────────► Logistic Regression
                                                              │
                        ┌─────────────────────────────────────┤
                        ▼                                     ▼
                Classification Metrics                  Decision Trees
                        │                                     │
                        ├──────────► SVM / Kernels            ▼
                        │                            Bagging ─► Boosting
                        ▼
              Unsupervised (k-Means, PCA)
                        │
                        ▼
        Practical ML / Evaluation / Model Debugging
                        │
                        ▼
     Neural Networks ─► Backpropagation ─► Training Stability
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
            CNN                  RNN / LSTM
              │                   │
              └────────┬──────────┘
                       ▼
                   Attention ─► Transformers ─► LLM Foundations
                                                      │
                       ┌──────────────────────────────┼──────────────┐
                       ▼                              ▼              ▼
                  Embeddings                    Tool Calling       NLP
                       │                              │
                       ▼                              ▼
              Vector Search ─► RAG            Agent Loop ─► Agents
                       │                              │
                       └──────────┬───────────────────┘
                                  ▼
                    Context Engineering / MCP / A2A

ML Foundations + Evaluation ─► ML Systems / MLOps ─► ML System Design
                                                          │
                              RAG + Agents ───────────────┴─► GenAI System Design
```

**Hard ordering constraints** (these become tests):
Attention **before** Transformers · Transformers **before** LLM
architecture · Embeddings **before** RAG · LLM + tool calling **before**
Agents · Agents **before** MCP/A2A · MLOps **before** ML System Design ·
RAG/Agents **before** GenAI System Design.

---

## 7. Question metadata model

Additive. Nothing existing is dropped, so current `question_progress` rows
survive untouched.

| Field | Type | Purpose |
|---|---|---|
| `phase` | int 0–16 | coarse curriculum position |
| `topic` | str | **the** knowledge location — one per question |
| `subtopic` | str? | finer grouping inside a topic |
| `prerequisites` | str[] | topic slugs, AND semantics |
| `cognitive_level` | int 1–9 | recognise → understand → explain → maths → implement → debug → compare → apply → interview |
| `primary_format` | enum | the format axis (§4) |
| `learning_objective` | str | one sentence: what you can do after this |
| `preview` | bool | visible early, never advances the frontier |
| `interview_relevance` | 1–5 | for Interview Mode ranking |
| `production_relevance` | 1–5 | for the systems track |

### Reconciling the two "mastery" scales

The request describes a 9-level scale (§12). The app already ships a **0–7
self-rated ladder** with real user data in `question_progress`. These are
not the same thing and should not be merged:

- **`cognitive_level` (1–9)** is a property of the **question** — how hard
  a thing it asks you to do. This is §9's progression.
- **mastery 0–7** stays a property of the **learner** — their confidence,
  already recorded, already driving spaced repetition.

Topic mastery is then *derived*: the highest cognitive level at which the
learner has cleared enough questions. That gives the 9-level model the
request asks for without a destructive migration.

---

## 8. Mastery, unlocking, and the frontier

**Topic state** is one of `locked → available → in_progress → mastered`.

**Unlock rule.** A topic becomes `available` when *every* prerequisite
topic is `mastered`.

**Mastery rule (proposed thresholds — tune after real use).** A topic is
`mastered` when:
1. ≥ 70% of its **core** questions (non-preview) have been attempted, and
2. the learner has cleared at least cognitive level **5 (implement)** for
   topics that have implementation questions, or level **4 (maths)** where
   they do not, and
3. no question in the topic sits at self-rated mastery ≤ 1.

Rule 3 matters: it stops one forgotten fundamental from being averaged away.

**The frontier** is `(current_phase, current_topic)` plus the set of
`available` topics. It is the *only* pool the daily picker may draw new
questions from. This is the mechanism that prevents topic jumping — not a
sort order, a hard filter.

**Explicitly non-advancing:** preview questions, Interview Mode answers,
and format-axis questions (behavioral, project deep dive) never move the
frontier and never count toward prerequisite mastery.

---

## 9. Daily 3 — proposed algorithm

```
learner state
  └─► frontier (current topic + unlocked set)
        └─► eligible questions  = topic ∈ unlocked
                                ∧ prerequisites satisfied
                                ∧ cognitive_level ≤ learner level + 1
              └─► slot assignment
```

| Slot | Draws from | Purpose |
|---|---|---|
| **Q1** | current topic, next unmastered cognitive level | forward progress |
| **Q2** | direct prerequisite topics, or current topic at a lower level | reinforcement |
| **Q3** | spaced-review queue; falls back to an application/format question **from a mastered topic** | retention |

Three changes from today's engine:

1. **Delete the module-diversity rule.** Replaced by slot roles. Spending a
   day inside Linear Regression is the goal, not a failure.
2. **Delete the unconditional case-study quota.** Case studies re-enter as
   Q3 application questions once their subject topics are mastered.
3. **Never draw from outside the frontier.** Today the pool is all 724.

### Worked example — learner at Linear Regression

| | Q1 (new) | Q2 (reinforce) | Q3 (review/apply) |
|---|---|---|---|
| Day 1 | What is Linear Regression? | What is supervised learning? | What is overfitting? |
| Day 2 | How is it trained? | Why a validation set? | Bias vs variance |
| Day 3 | What is MSE? | Gradient descent | When does regularization help? |
| Day 4 | Derive the normal equation | Learning rate | *implement MSE* (ML coding, same topic) |
| Day 5 | Regression assumptions | Multicollinearity | Compare with a tree model *(locked until trees mastered — falls back)* |

Note day 5: the natural comparison question is *not yet eligible*. The
fallback must be graceful, and that is a real design constraint.

---

## 10. Spaced review

Reuse the existing `REVIEW_INTERVAL_DAYS` ladder in `daily_theory.py` —
it already works and has user data behind it. One constraint added:

> **Review draws only from topics at or behind the frontier.**

Reinforcement must never be the back door through which future domains
appear. This is the rule that today's engine lacks, and it is a two-line
filter once `phase` exists.

---

## 11. Learning Mode vs Interview Mode

| | Learning Mode | Interview Mode |
|---|---|---|
| Pool | frontier only | **all mastered topics**, sampled broadly |
| Order | prerequisite-driven | deliberately mixed, cross-topic |
| Formats | concept → maths → implement | comparison, tradeoff, case study, system design |
| Advances frontier | **yes** | **no** |
| Records mastery | yes | yes (as review, never as unlock) |

The separation is what makes broad sampling safe: once Classical ML is
mastered, Interview Mode can legitimately ask *"Compare SVM and gradient
boosting"* or *"Design a fraud detection system"* without that implying the
learner has moved on to system design.

---

## 12. Validation rules (implement as tests)

Curriculum-integrity failures, checkable in CI against the graph:

| # | Rule |
|---|---|
| V1 | Every question has exactly one `topic`, and that topic exists in the graph |
| V2 | Every `prerequisites` entry resolves to a real topic |
| V3 | The prerequisite graph is acyclic |
| V4 | A topic's `phase` ≥ max(phase of its prerequisites) |
| V5 | Attention precedes Transformers precedes LLM architecture |
| V6 | Embeddings precede vector search precede RAG |
| V7 | LLM + tool calling precede agent loop precede agents precede MCP/A2A |
| V8 | ML foundations precede DL; DL precedes attention |
| V9 | MLOps precedes ML system design; RAG/agents precede GenAI system design |
| V10 | No implementation question in a topic with no conceptual question |
| V11 | The daily picker never returns a question outside the frontier |
| V12 | A preview question never changes frontier or unlock state |
| V13 | Every topic reachable from the start (no orphan islands) |
| V14 | Every phase has ≥ 1 question at cognitive level ≤ 2 (an entry point) |

V14 currently **fails** for several phases — see §13.

---

## 13. Gap analysis

### The serious gap: Phase 0 barely exists

Text search across all 724 titles and `tests_for` fields:

| Prerequisite area | Questions |
|---|---|
| Python basics / OOP / generators / decorators | **0** |
| Pandas / DataFrame / groupby | **0** |
| Calculus / derivatives / chain rule | **0** |
| NumPy / vectorisation / broadcasting | **1** |
| Linear algebra | 10 *(7 of them inside ML Coding, not taught as maths)* |
| Probability / Bayes | 9 |

Module C ("Mathematics & Statistics", 12 questions) is not a foundation
course — it is **advanced statistics for interviews**: p-values, CLT
misuse, SVD, the Hessian, a Bayes fraud puzzle, deriving the logistic
gradient. Six of its twelve are tagged `advanced`; exactly one is
`beginner`.

**So the curriculum has no on-ramp.** Phase 0 as specified in the request
must largely be authored.

### Thin phases

| Phase | Qs | Note |
|---|---|---|
| Context Engineering | 1 | a stub |
| MCP / A2A | 2 | a stub |
| Multimodal | 7 | thin for a whole phase |
| Model Evaluation | 10 | thin given it gates all of DL |
| Computer Vision | 13 | acceptable if CV is a branch, not a trunk |

### Beginner runway

49 beginner questions total, and they cluster in D (22), B (9), E (9).
Phases P6–P16 have **almost no level-1/2 entry points** — so even after
unlocking, a learner is dropped straight into intermediate material.

### What is *not* a gap

- **No duplicates to merge.** 0 exact-normalised title collisions.
- The 28 near-duplicate pairs (≥ 0.8 token overlap) are **all** in module A
  and are a deliberate template family — *"Arrays and hashing: what in a
  problem statement tells you to reach for it?"*, *"Binary search: what in
  a problem statement…"*. Parallel by design. **Do not merge these.**

---

## 14. Question audit — what I can and cannot assert

The request (§14/§15) asks for a per-question verdict across six buckets.
Being straight about what has actually been established:

### Done — structural, deterministic, covers all 724

| Bucket | Count | Basis |
|---|---|---|
| **KEEP** (knowledge, correct phase) | 507 | module → phase mapping, §5 |
| **MOVE** (format questions needing topic-linking) | 217 | they have no knowledge topic today; every one needs a topic assigned so it can be gated |
| **MERGE** | **0** | measured: no duplicate titles |
| **GAP** (must be authored) | ~40–60 | Phase 0 (§13) plus level-1/2 entry points for thin phases |

The 217 MOVE questions are not mis-filed so much as **un-filed on the axis
that matters**. Case studies and ML-coding questions currently have no
knowledge location at all, which is exactly why they surface on day one.

### Not done — needs a second pass, and I will not invent it

`RETIRE` and `REVIEW` require judging *content quality and correctness*
question by question — audit items 7–12 in §14 of the request. That cannot
be derived from metadata, and asserting 724 verdicts I have not actually
formed would be fabrication of the kind this codebase has already been
cleaned of twice.

Two honest routes:
1. **LLM-assisted pass** using the existing `app/grading.py` plumbing —
   classify topic, prerequisites, cognitive level and quality flag per
   question, then review only the low-confidence tail by hand.
2. **Targeted manual review** of the cohorts most likely to be wrong: the
   257 `advanced` questions, the 52 case studies, and module C.

Route 1 is what I would do, with route 2 on its output.

---

## 15. Simulations

**Test A — brand-new learner: measured, and it fails.** Full output in §1.

**Tests B, C, D — specified, not measured.** The frontier engine does not
exist yet, so there is nothing to run them against. Running them today
would just reproduce §1. They become the acceptance tests:

| Test | Given mastered | Expected next 20, in this direction |
|---|---|---|
| **B** Classical ML | foundations, linear + logistic regression, regularization, basic classification | Decision Trees → Random Forest → Boosting → SVM → Unsupervised → Evaluation |
| **C** Deep Learning | Classical ML + DL foundations | CNN / RNN → Attention → Transformers → NLP / LLM foundations |
| **D** Modern AI | Transformers, LLM fundamentals, embeddings, retrieval | RAG → RAG evaluation → Tool calling → Agents → Context engineering |

Each becomes an automated test asserting **zero** questions from phases
beyond the frontier — the same assertion as V11, applied to a fixture
learner.

---

## 16. Risks and edge cases

**You are not a beginner — and the model as specified would treat you as
one.** This is the biggest practical risk. Starting the frontier at Phase 0
would lock 74% of the bank and serve you "what is supervised learning?"
Mitigations, in order of preference: a **placement pass** (answer a short
set at level 4–6 per phase to fast-forward), plus per-topic manual
"I already know this", plus your existing `question_progress` seeding
initial mastery.

**Over-gating kills the tool.** If the gate is strict and Phase 0 is empty,
the learner is blocked on content that does not exist. Phase 0 authoring
must land *before* gating is enforced, or gating must start at P1.

**A graceful fallback is required.** Day 5 in §9 shows the natural next
question being ineligible. Without a good fallback the third slot degrades
into repetition. This needs design attention, not a default.

**Migration must not destroy progress.** `question_progress` has real
mastery data. The metadata additions are additive for exactly this reason.

**Classification drift.** If an LLM assigns topics and prerequisites, two
runs can disagree. The graph should be authored once, reviewed, and
committed as data — not regenerated on each ingestion.

**Interview Mode is the pressure valve.** If Learning Mode feels
restrictive, the answer is to use Interview Mode, not to loosen the gate.
Make it prominent, or the gate will be resented and bypassed.

---

## 17. Recommended implementation plan

Each stage is independently shippable and independently useful.

| # | Stage | Deliverable | Gate to next |
|---|---|---|---|
| 1 | **Topic graph as data** | `curriculum_topics` + `topic_prerequisites`, authored by hand, ~60–80 topics | V1–V9, V13 pass in CI |
| 2 | **Question metadata** | migration adding `topic`, `phase`, `cognitive_level`, `primary_format`, `preview` | every question has a topic; V10 passes |
| 3 | **Classify the 724** | LLM-assisted pass + manual review of the low-confidence tail | ≥ 95% assigned with confidence; rest flagged REVIEW |
| 4 | **Author Phase 0** | ~40–60 questions: Python, NumPy, Pandas, calculus, linear algebra | V14 passes for P0–P2 |
| 5 | **Frontier engine** | pure function: learner state → eligible set. Mirrors `topic_gate.py` in shape | Tests A–D pass |
| 6 | **Rewrite the daily picker** | slot-based Q1/Q2/Q3; delete diversity rule and case-study quota | Test A shows a coherent first 30 |
| 7 | **Placement flow** | fast-forward for existing knowledge | you are not sent to Phase 0 |
| 8 | **Interview Mode** | separate entry point, frontier-neutral | mode switch never moves the frontier |

**Stage 1 is the whole game.** The graph is the knowledge model; everything
after it is plumbing. It is also the one part that cannot be automated —
it is a senior-engineer judgement call about what genuinely depends on
what, and it should be reviewed by hand before anything is built on it.

Suggested first move: author the Phase 0–P5 slice of the graph (roughly 25
topics covering prerequisites through Practical ML) and validate the
approach against the 190 questions already in that range, before extending
to the modern-AI half.

---

## Appendix — how each number here was obtained

| Claim | Method |
|---|---|
| 724 / 32 modules / counts | `SELECT count(*) GROUP BY` on `questions` |
| Test A output | `pick_daily_theory()` run against real fixtures, 10 days, empty progress |
| 0 duplicates | normalised-title collision check across all 724 |
| 28 near-dup pairs | pairwise Jaccard ≥ 0.8 on title tokens |
| Phase 0 coverage | regex over `title` + `tests_for` |
| Phase mapping / 507 vs 217 | module → phase table applied to all 724, zero unmapped |
| Failure mechanisms | reading `app/engines/daily_theory.py` |
