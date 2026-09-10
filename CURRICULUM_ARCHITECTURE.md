# Curriculum Architecture

How Meridian decides what to ask you next.

Companion to [CURRICULUM_AUDIT.md](CURRICULUM_AUDIT.md), which measured the
problem this implements the fix for. Read the audit for *why*; this
document is *what was built*.

---

## The flow

```
Question Bank (724)
      ↓  scripts/ingest_curriculum_graph.py
Classification            axis · topic · phase · cognitive level · format
      ↓  scripts/curriculum_graph.py  (authored by hand)
Topic Graph (103 topics)  phase + prerequisites
      ↓
Prerequisites             AND semantics, hard exclusion
      ↓  question_progress (existing 0-7 ladder, unchanged)
Learner State             per-topic mastery fraction
      ↓  app/engines/curriculum.py
Learning Frontier         LOCKED / AVAILABLE / IN_PROGRESS / MASTERED
      ↓
Candidate Pool            only unlocked topics; violations excluded
      ↓
Ranking                   readiness first, interview priority last
      ↓
Daily Schedule            new · reinforce · review
```

---

## Two axes

The central idea. Of 724 questions, **294 are format, not knowledge** —
case studies, ML coding, behavioural, project deep dives, system design.
Previously they competed for the same daily slots as "What is linear
regression?", which is why a learner with no progress was served a Google
case study on day one.

| Axis | Field | Decides |
|---|---|---|
| **Knowledge** | `topic`, `phase`, `prerequisites`, `cognitive_level` | *what to learn next* |
| **Format** | `primary_format` | *how it is tested* |

A format question still carries a topic — that is what gates it — but it
never defines where the learner is. Behavioural and project deep dive are
`gated=False`: refusing to let someone rehearse their own project story
until they have mastered PCA would be absurd.

---

## Phases

Six, matching the spec:

| | | Knowledge Qs |
|---|---|---|
| P0 | Foundations | 12 |
| P1 | Classical Machine Learning | 165 |
| P2 | Deep Learning | 63 |
| P3 | NLP / LLM Foundations | 64 |
| P4 | Modern LLM / Generative AI | 41 |
| P5 | AI Systems / Agents / Advanced AI | 85 |

A phase is a coarse "roughly where am I" label. The actual sequencing
lives in the **prerequisite edges**, which is where it belongs.

### Curriculum phase ≠ interview priority

`questions.phase` is curriculum position. `questions.priority` (P0–P3) is
**interview** priority — how often something appears in a loop. They are
different fields and must never be conflated. Conflating them is the
original bug: GenAI System Design is a P0-*priority* module, which is how
"Design an LLM chatbot at scale" reached a beginner's day five.

In ranking, interview priority is weighted **5.0** against readiness
signals of 40–100, and is only consulted *after* eligibility. It answers
"how often does this come up", never "is this next".

---

## Topic graph

`api/scripts/curriculum_graph.py` — 103 topics, authored by hand, seeded
into `curriculum_topics`. This is the one part that cannot be generated:
it is a judgement about what genuinely depends on what.

```
Linear Regression ─► Logistic Regression ─► Neural Networks ─► Backprop
                                                    │
                                              CNN ──┴── RNN ─► Seq2Seq
                                                              │
                                                          Attention
                                                              │
                                                        Transformers
                                                              │
                                                      LLM Architecture
                                            ┌─────────────────┼──────────┐
                                       Embeddings        Tool Calling   NLP
                                            │                 │
                                      Vector Search       Agent Loop
                                            │                 │
                                           RAG ──────────► Agents ─► MCP/A2A
```

Prerequisites are **AND**. Keep them minimal — every extra edge is a wall,
and an over-gated curriculum gets overridden, which teaches nothing.

---

## Mastery

Reuses the existing 0–7 ladder in `question_progress`. **No second mastery
system was created.**

- A question is **cleared** at mastery ≥ 3 ("can solve").
- A topic's mastery is the fraction of its *core* questions cleared.
  Core = knowledge axis, not preview.
- A topic is **MASTERED** at ≥ 70%. Not 100%: one awkward question would
  otherwise permanently block everything downstream.

Cognitive level is a property of the **question**, not the learner:

| | |
|---|---|
| L0 | Recognition |
| L1 | Recall — "what is X?" |
| L2 | Understanding — "why does X work?" |
| L3 | Application — "implement X" |
| L4 | Analysis — "compare X and Y", "why did X fail?" |
| L5 | Design / synthesis — "design a system that…" |

Seeded from difficulty, overridden by an explicit verb in the title, with
a floor by format (a system-design question is L5 whatever its wording).

---

## The frontier

Four states per topic: `LOCKED → AVAILABLE → IN_PROGRESS → MASTERED`.

The frontier is the current topic plus everything unlocked. **It is the
only pool the picker may draw from** — a hard filter, not a sort order.
That is the mechanism preventing topic jumping.

`learner_frontier` stores only the current topic and placement fields.
Eligibility is derived from the graph plus `question_progress` on every
request, so there is no second copy of mastery to drift out of sync.

---

## Placement

**"No recorded progress" is not "beginner."** An experienced engineer
opening the app has an empty history, and sending them to "what is
supervised learning?" is how a tool gets abandoned.

`placement_status`: `UNASSESSED → ASSESSING → PLACED`

Two routes:

1. **From history** — reads existing `question_progress`. Zero friction
   for an established user.
2. **From probes** — `GET /api/curriculum/placement/probes` returns a
   short set spanning P0–P5 (four per phase, mid-level questions only: a
   definition proves too little, a synthesis question too much).

Both are **conservative**: a phase is credited only with independent
evidence across ≥ 3 topics, and confidence is reported alongside. Below
0.6 the estimate is shown but not acted on.

Both are **prerequisite-safe** (invariant 8): the estimate is clamped to
what the graph allows. Someone strong at P4 with a hole at P2 is placed at
the hole, and `clamped_by_prerequisites` says so.

---

## The scheduler

Three slots per day, roles rather than topic quotas:

| Slot | Draws from |
|---|---|
| `new` | current topic, next unmastered level |
| `reinforce` | a prerequisite topic, or the current topic lower down |
| `review` | spaced-review queue, else an application/format question |

**All three may be the same topic.** A day of nothing but linear
regression is a good day when linear regression is what you are learning.
That is the direct replacement for the old module-diversity rule, which
made curriculum coherence structurally impossible.

### Format share

Configurable in `FORMAT_RATIO_BY_PHASE`:

| Phase reached | Format share |
|---|---|
| P0–P1 | 10% |
| P2–P3 | 25% |
| P4–P5 | 40% |

And a minimum phase per format (`FORMAT_MIN_PHASE`) — a case study needs
P1 reached, a system-design question P2. **There is no unconditional case
study quota.** That was `case_study_count = 1` firing every single day.

### Ranking

```
score = current_topic(100) + prerequisite_of_current(60) + review_due(50)
      + current_phase(40) + mastery_gap(30) + cognitive_fit(25)
      + format_fit(15) + interview_priority(5)
      - cognitive_overreach(20)
      - day-seeded jitter          # rotates ties across days
```

Weights live in `Weights`, a frozen dataclass. Two properties matter more
than the numbers: **readiness outranks interview priority**, and
**prerequisite violations are excluded before scoring** — no score can buy
past them.

The jitter is small enough to reorder near-equals only. Without it, a
learner who rates nothing sees the identical three questions tomorrow,
because nothing about their state moved.

---

## Explanations

Every selection carries structured reason codes:

```
READY · PREREQUISITES_MET · CURRENT_TOPIC · CURRENT_PHASE
MASTERY_GAP · REVIEW_DUE · FORMAT_APPROPRIATE · COGNITIVE_FIT
```

and every rejection carries why:

```
LOCKED_PREREQUISITE · PHASE_TOO_ADVANCED · ALREADY_MASTERED
FORMAT_NOT_YET_UNLOCKED · COGNITIVE_TOO_ADVANCED · NOT_YET_DUE · NO_TOPIC
```

`GET /api/curriculum/explain?include_rejections=true` returns both. The
old picker returned three questions and no account of itself.

---

## Validation

```bash
python -m scripts.validate_curriculum          # human
python -m scripts.validate_curriculum --json   # CI
```

Exits non-zero on any integrity error: unmapped questions, invalid
prerequisite references, cycles, phase inversions, invalid levels or axes.

**Phase completeness is measured on the knowledge axis only.** P0 holds
108 questions, of which 96 are DSA, behavioural and project deep dives.
Counting those would report P0 as healthy while Python, NumPy, Pandas and
calculus remain missing.

---

## Simulation

```bash
python -m scripts.simulate_learner --profile beginner --days 10
python -m scripts.simulate_learner --profile uneven --days 15 --explain
```

Profiles: `beginner`, `intermediate`, `advanced`, `uneven`, `weak`. The
uneven learner — strong Python, medium ML, weak deep learning, strong LLM
— is the realistic and hardest case: someone who ships LLM features
without having learned backprop.

The old picker's failure was only visible by running it, so the
replacement ships with the means to run it too.

---

## Known content gaps

These are **real and unfixed**. The engine reports them rather than
papering over them.

| | |
|---|---|
| **P0 Foundations** | **INCOMPLETE — 12 knowledge questions.** 0 Python, 0 Pandas, 0 calculus, 1 NumPy. Module C is advanced interview statistics (p-values, SVD, the Hessian), not a foundation course. |
| Empty topics | 35 gated topics have no knowledge questions |
| Needs review | 177 questions (24%) classified by module fallback |

**Invariant 7** keeps these from blocking anyone: a topic with no
questions is treated as satisfied for unlocking purposes, so an empty
prerequisite never walls off the curriculum. The gap is reported by the
validator instead.

The practical consequence today: a beginner's first questions are
linear-algebra questions written at interview level ("What is SVD?"),
because that is the only P0 content that exists. The sequencing is
correct; the material to sequence is missing.

---

## Files

| File | Role |
|---|---|
| `api/scripts/curriculum_graph.py` | **the knowledge model** — 103 topics, authored |
| `api/scripts/ingest_curriculum_graph.py` | seeds topics, classifies all 724 |
| `api/scripts/validate_curriculum.py` | integrity check, CI-ready |
| `api/scripts/simulate_learner.py` | N-day simulation, 5 profiles |
| `api/app/engines/curriculum.py` | frontier, eligibility, ranking, daily plan |
| `api/app/engines/placement.py` | placement estimation, conservative + clamped |
| `api/app/repositories/curriculum.py` | ORM → fixtures |
| `api/app/routers/curriculum.py` | state, explain, placement |
| `api/alembic/versions/0019_curriculum_graph.py` | schema |
| `api/tests/test_curriculum_engine.py` | the 8 acceptance tests |
| `api/tests/test_placement_engine.py` | placement invariants |

`api/app/engines/daily_theory.py` is retained as a fallback for a database
where the graph has not been seeded. It is no longer the live path.
