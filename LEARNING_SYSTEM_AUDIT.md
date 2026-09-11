# Learning System Audit

This does not redesign the curriculum sequencing/classification work already completed (documented in `CURRICULUM_ARCHITECTURE.md`). It answers the specific quality questions the product audit asked: is the *content* of the bank balanced, and where are the real gaps — grounded in a fresh run of `scripts/validate_curriculum` and a direct query of the live database, not estimation.

## 1. Current state (measured, 2026-09-10)

- 722 questions, 105 topics, 6 phases, 0 unmapped, 0 integrity errors (no missing topic/phase, no cycles, no phase inversions).
- P0 Foundations: **INCOMPLETE** (15 knowledge questions, 5 entry points) — the only phase flagged.
- P1–P5: all READY (158 / 64 / 66 / 49 / 77 knowledge questions respectively).
- 137 questions still classified by `module_default` (lowest-confidence tier) — not wrong, just unverified individually; 358 `exact`, 169 `keyword`, 58 hand-`adjudicated`.
- **27 gated topics have zero knowledge questions** and **20 more have only 1–2**.

## 2. Format/type balance — the "too many definitions, not enough X" question, answered with real counts

| Question type | Count | Share |
|---|---|---|
| concept (definition/explanation) | 418 | 58% |
| system_design | 97 | 13% |
| coding | 79 | 11% |
| case_study | 52 | 7% |
| behavioral | 38 | 5% |
| project_deep_dive | 27 | 4% |
| **debugging** | **11** | **1.5%** |

**Verdict**: yes, the bank is definition-heavy (58%) and debugging is critically thin (11 questions across the entire bank — effectively decorative, not a real practice category). System-design and coding are reasonably represented; case-study and behavioral are adequate for their role as periodic format variety rather than the bank's core.

## 3. Difficulty balance

| Difficulty | Count | Share |
|---|---|---|
| beginner | 49 | 6.8% |
| intermediate | 418 | 58% |
| advanced | 255 | 35% |

93% of the bank is intermediate-or-advanced. This is consistent with — and the direct cause of — P0's thinness: there simply isn't enough true-beginner content to give a Day-1 learner three real foundational questions a day without repeating.

## 4. Cognitive-level distribution (L0–L5)

L1=113, L2=273, L3=128, L4=99, L5=109 — a sane pyramid shape (heaviest in the middle, tapering at both ends), not the pathological L4/L5-skew the first classification pass produced before it was fixed (documented in `CURRICULUM_ARCHITECTURE.md`). No further action needed here.

## 5. Concrete gap-detection output

Applying the spec's own format (`Topic → current vs. recommended → what's missing → priority`) to the two most important real cases found:

```
Topic: backpropagation
Current questions: 0
Recommended: 6-8
Missing:
  - intuition (chain rule as credit assignment)
  - computational graph / forward-backward pass
  - vanishing gradients
  - exploding gradients
  - manual derivation for a 2-layer network
  - debugging (why is my gradient exploding/vanishing in practice)
Priority: P0 — this is core DL content, gated, and currently has NO
content at all. A learner cannot progress through P2 Deep Learning's
gated sequence past this topic on real content.
```

```
Topic: python_for_ml / numpy_vectorization / pandas_data
Current questions: 0 each
Recommended: 4-6 each
Missing: everything — these are P0 entry topics for a curriculum whose
own validator already flags P0 as INCOMPLETE.
Priority: P0 — same root cause as the phase-level finding above,
broken down to topic level. This is the single biggest content gap
in the bank: three foundational, universally-relevant topics with
zero questions.
```

The remaining 24 empty gated topics (`agent_evaluation`, `ai_protocols`, `calibration`, `classic_ml_system_design`, `context_engineering`, `data_leakage`, `detection_segmentation`, `dl_regularization`, `feature_engineering`, `genai_system_design`, `hierarchical_dbscan`, `image_classification`, `image_representation`, `knn`, `ml_system_design_process`, `naive_bayes`, `planning_reflection`, `rag_system_design`, `regularization_concepts`, `seq2seq`, `train_val_test`, `vision_transformers`, `agent_system_design`) are real gaps too, but lower urgency than P0/backpropagation because most sit in P2–P5 where the phase overall already has enough *other* content for a learner to keep progressing — the topic itself is just empty, meaning that specific concept never comes up. Each should get the same "current vs. recommended vs. missing sub-aspects" treatment before new questions are written, not just a raw count target.

## 6. Recommendation

Do not add breadth (more topics, more phases) — the taxonomy itself is sound and was just rebuilt. Add **depth in specific starved places**: P0 foundational content (python/numpy/pandas/backprop) first since it blocks the curriculum's own stated floor, then debugging-format questions bank-wide (11 is not a category, it's a rounding error), then the remaining empty gated topics in priority order by phase. This is a content-authoring task, not an engineering one — the classification/sequencing engine already has zero known bugs to fix here.
