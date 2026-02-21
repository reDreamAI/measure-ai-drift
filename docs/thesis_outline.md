# Thesis — Table of Contents

**Measuring Drift in Therapeutic AI: A Stability-Based Evaluation of Sovereign LLMs in Nightmare Therapy**

Daniel Menzel — Institute of Cognitive Science, University of Osnabruck
Supervisors: Moritz Hartstang, Sebastian Musslick

---

## Abstract

## 1 Introduction

### 1.1 Nightmare Disorder and Imagery Rehearsal Therapy
- ~5% prevalence, comorbidity with PTSD/depression
- IRT as gold-standard: structured protocol with rescripting at its core
- Clinician shortage → scalable AI interventions as potential solution

### 1.2 AI-Assisted Psychotherapy
- LLM-based therapeutic delivery (reDreamAI project as applied context)
- Distinction: general-purpose conversational AI vs. protocol-driven therapeutic agents
- EU regulatory context favours sovereign, self-hostable models — but their therapeutic reliability is unvalidated

### 1.3 The Evaluation Gap
- Standard NLP benchmarks do not assess therapeutic reliability
- Missing: intent stability under stochastic variation, protocol adherence, consistent persona
- Need for domain-specific in silico clinical trials

### 1.4 Research Objectives
- RQ: How consistent is LLM clinical reasoning across stochastic runs in a structured therapeutic protocol?
- Contribution 1: Three-level hierarchical evaluation framework for therapeutic AI stability
- Contribution 2: Quantitative comparison across model classes (sovereign, proprietary, open-weight)
- Scope: isolated rescripting phase (cognitive core of IRT)

---

## 2 Background

### 2.1 Imagery Rehearsal Therapy
- Five-stage IRT protocol: recording → rewriting → summary → rehearsal → final
- The rescripting phase as the core cognitive intervention
- Clinical evidence and treatment fidelity assessment in psychotherapy

### 2.2 Large Language Models in Healthcare
- Current therapeutic AI applications and their evaluation
- Challenges in high-stakes settings: hallucination, drift, inconsistency
- Regulatory landscape: EU AI Act, Medical Device Regulation

### 2.3 Stochastic Behaviour in Language Models
- Temperature-based sampling and output variance
- Reproducibility challenges across repeated generations
- Prior work on measuring LLM behavioural stability and drift

### 2.4 Evaluation Metrics for Text Generation
- Traditional metrics (BLEU, ROUGE) and their limitations for semantic comparison
- BERTScore: contextual embedding-based evaluation (Zhang et al., 2020)
- LLM-as-judge: paradigm, known biases, mitigation strategies

### 2.5 Chain-of-Thought and Plan Faithfulness
- CoT prompting (Wei et al., 2022)
- Faithfulness concerns: CoT as post-hoc rationalisation (Turpin et al., 2023; Lanham et al., 2023)
- Implications for structured plan mechanisms in evaluation

---

## 3 Methods

### 3.1 System Overview
- Two-stack architecture: generation stack (dialogue creation) and evaluation stack (stability measurement)
- Data flow: vignettes → generation → frozen histories → evaluation → aggregation
- Key design principle: separate dialogue creation from stability testing

### 3.2 Dialogue Generation
- Three-agent loop: Patient (BDI-profiled vignette), Router (stage classification), Therapist (stage-appropriate response)
- Six patient vignettes: anxious, avoidant, cooperative, resistant, skeptic, trauma
- Five-stage IRT protocol traversal

### 3.3 Frozen History Design
- Deterministic evaluation entry points: identical context for every trial
- Conversation slicing at rewriting-turn boundaries (slice_1, slice_2, slice_3)
- Rationale: evaluate at different conversation depths within the rescripting phase

### 3.4 Evaluation Stack
- Router bypass: rescripting prompt injected directly (stage is known a priori)
- Fused CoT generation: plan and response in a single call
  - `<plan>` block declares 1–2 strategies before the therapeutic response
  - Plan conditions the response tokens (Chain-of-Thought style)
- 10 independent trials per condition

### 3.5 The Plan Mechanism
- Plan as declared intent, not as explanation of internal reasoning
- Structured measurement independent of CoT faithfulness debate
- Enables: strategy-level consistency measurement, alignment verification, clinical oversight
- Fixed IRT strategy taxonomy constrains output to therapeutic domain

### 3.6 Strategy Taxonomy Development
- Initial 8-category taxonomy: severe distribution skew (empowerment/mastery = 87.7%)
- Revision 1 — merge to agency: failed (100% dominance, goal vs. mechanism confusion)
- Revision 2 — mechanism-specific split: confrontation (external action) vs. self_empowerment (internal transformation)
- Final 7 categories: confrontation, self_empowerment, safety, cognitive_reframe, emotional_regulation, social_support, sensory_modulation
- Prompt-level steering for category diversity

### 3.7 Evaluation Metrics

#### 3.7.1 Method 1 — Cognitive Stability (Plan Consistency)
- Pairwise Jaccard similarity over strategy sets: J(A,B) = |A ∩ B| / |A ∪ B|
- Mean over C(10,2) = 45 trial pairs
- Strategy extraction from `<plan>` blocks; validity rate as quality gate
- Measures: do stochastic runs produce the same therapeutic decisions?

#### 3.7.2 Method 2 — Output Consistency (Semantic Stability)
- Pairwise BERTScore F1 over response texts, mean over 45 pairs
- Embedding model: DeBERTa-XLarge-MNLI (He et al., 2021)
  - NLI fine-tuning aligns with semantic comparison task
  - Highest WMT16 correlation with human judgments (r = 0.778)
  - Disentangled attention handles surface-form variation in therapeutic language
- Measures: do stochastic runs produce therapeutically equivalent responses?

#### 3.7.3 Method 3 — Plan-Output Alignment (Exploratory)
- LLM judge (Gemini Flash, T=0.0) with ternary scoring per declared strategy
  - 0 = absent, 1 = partial, 2 = implemented
- Ternary scale grounded in clinical fidelity literature (ENACT, NIH BCC)
- Rejected alternatives: NLI cross-encoders (F1 ceiling ~0.55, task mismatch, no reasoning trace)
- Mitigations: cross-model judging, CoT justification, deterministic decoding, transparent rubric
- Measures: does the model's response implement its declared therapeutic plan?

### 3.8 Model Selection
- EU sovereignty as selection criterion: data protection, AI Act, self-hostability requirements
- Primary subject: Mistral Small 3.2 (24B) — EU-sovereign, self-hostable
- Proprietary baseline: GPT-5
- Open-weight comparisons: Llama 3.3 70B, Qwen 3 32B, Gemma 3 27B
- Selection rationale: size class diversity, provider diversity, sovereignty status

### 3.9 Experimental Conditions
- 6 vignettes × 3 slices × 10 trials × 2 temperatures (T=0.0, T=0.7) × N models
- T=0.0: deterministic baseline (greedy decoding)
- T=0.7: stochastic condition (clinical deployment temperature range)

---

## 4 Implementation

### 4.1 Software Architecture
- Python async-first pipeline, config-driven via YAML
- Pydantic models for type-safe data flow
- Multi-provider LLM abstraction (Groq, OpenAI, Scaleway, Gemini, OpenRouter)

### 4.2 Experiment Execution
- ExperimentRun orchestration with structured output
- Multi-trial sampling with parallel execution
- Output: config, frozen history, trials/, metrics.json, judgments.json

### 4.3 Aggregation Pipeline
- Cross-experiment result collection
- Per-model, per-vignette, per-slice, per-temperature breakdowns

---

## 5 Results

### 5.1 Plan Validity and Strategy Distribution
- Validity rates across models and temperatures
- Strategy frequency distribution across the 7 categories
- Comparison with expected vignette–strategy mappings

### 5.2 Cognitive Stability (Method 1)
- Jaccard scores by model, vignette, temperature, slice
- T=0.0 vs. T=0.7: how much does stochastic sampling destabilise strategy selection?
- Cross-model comparison: sovereign vs. proprietary

### 5.3 Output Consistency (Method 2)
- BERTScore F1 by model, vignette, temperature, slice
- Relationship to plan consistency: does stable planning produce stable output?
- Cross-model comparison

### 5.4 Plan-Output Alignment (Method 3)
- Alignment scores by model and vignette
- Per-strategy scoring distributions (absent / partial / implemented)
- Judge reasoning patterns

### 5.5 Cross-Method Analysis
- Correlations between the three evaluation levels
- Divergence cases: high plan consistency with low output consistency (or vice versa)
- Stability profiles per model
- Effect of conversation depth (slice_1 → slice_2 → slice_3)

---

## 6 Discussion

### 6.1 Cross-Model Comparison
- Mistral Small 3.2 performance relative to GPT-5 and size-class peers
- Sovereignty dimension: does self-hostability come at a stability cost?
- Size-class effects: 24B vs. 32B vs. 70B vs. frontier

### 6.2 Temperature and Therapeutic Stability
- Greedy decoding as a clinical deployment baseline
- Stochastic drift patterns and their clinical significance
- Recommendations for deployment temperature

### 6.3 Vignette-Dependent Behaviour
- Patient profiles that challenge model consistency (e.g., resistant, trauma)
- Strategy selection patterns across clinical presentations
- Implications for patient-specific adaptation

### 6.4 Evaluation Framework Reflections
- Strengths: hierarchical decomposition, reproducibility, clinical grounding
- Taxonomy sensitivity: how category design shapes measured consistency
- Plan-as-declared-intent: what this framing enables and what it cannot claim
- Generalisability beyond IRT to other structured therapeutic protocols

### 6.5 Toward In Silico Clinical Trials
- Framework as template for automated therapeutic AI validation
- Regulatory relevance: what stability testing can and cannot certify
- Gap between benchmark performance and clinical readiness

---

## 7 Conclusion

### 7.1 Summary
- Key findings across the three evaluation levels
- Answer to the research question

### 7.2 Limitations
- Single therapeutic protocol (IRT rescripting phase only)
- Synthetic patient simulation vs. real clinical interaction
- LLM-judge reliability (exploratory status of Method 3)
- Fixed taxonomy constraining measured strategy space

### 7.3 Future Work
- Extension to full IRT protocol (all five stages)
- Longitudinal drift: stability across model versions over time
- Local alignment alternatives (reranker-based judging)
- Multi-language evaluation (German therapeutic context)
- Clinical validation with human therapist ratings

---

## References

---

## Appendices

### A Strategy Taxonomy
- Full 7-category taxonomy with descriptions and evolution history (8 → 6 → 7)

### B Prompts
- Fused plan+response system prompt
- Alignment judge prompt and scoring rubric
- Patient vignette summaries

### C Architecture Diagrams
- Pipeline data flow diagram
- Evaluation methods diagram

### D Supplementary Results
- Full per-experiment metric tables
- Example trial outputs with judge reasoning
