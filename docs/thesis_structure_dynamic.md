# Thesis Structure

**Measuring Drift in Therapeutic AI: A Stability-Based Evaluation of Sovereign LLMs in Nightmare Therapy**

---

## Table of Contents

1 Introduction
\-- 1.1 Nightmare Disorder and Imagery Rehearsal Therapy
\-- 1.2 AI-Assisted Psychotherapy and Deployment Context
\-- 1.3 The Evaluation Gap
\-- 1.4 Research Objectives

2 Background
\-- 2.1 Imagery Rehearsal Therapy
\-- 2.2 Treatment Fidelity in LLM-Based Interventions
\-- 2.3 Stochastic Behaviour in Language Models
\-- 2.4 Evaluation Metrics for Text Generation

3 Methods
\-- 3.1 System Overview and Design Rationale
\-- 3.2 Dialogue Generation
\-- 3.3 Evaluation Design (Frozen Histories and Evaluation Stack)
\-- 3.4 Plan Mechanism and Strategy Taxonomy (incl. CoT faithfulness resolution)
\-- 3.5 Evaluation Metrics
\-  3.5.1 Method 1: Cognitive Stability (Plan Consistency)
\-  3.5.2 Method 2: Output Consistency (Semantic Stability)
\-  3.5.3 Method 3: Plan-Output Alignment
\-- 3.6 Model Selection
\-- 3.7 Experimental Conditions
\-- 3.8 Statistical Analysis

4 Implementation
\-- 4.1 Software Architecture
\-- 4.2 Experiment Execution and Aggregation

5 Results
\-- 5.1 Plan Validity and Strategy Distribution
\-- 5.2 Cognitive Stability (Method 1)
\-- 5.3 Output Consistency (Method 2)
\-- 5.4 Plan-Output Alignment (Method 3)
\-- 5.5 Cross-Method Analysis
\-- 5.6 Secondary Effects

6 Discussion
\-- 6.1 Interpreting the Three-Level Framework
\-- 6.2 Cross-Model Comparison
\-- 6.3 Temperature and Clinical Deployment
\-- 6.4 Evaluation Framework Reflections

7 Conclusion
\-- 7.1 Summary of Findings
\-- 7.2 Limitations
\-- 7.3 Future Work

Appendices A-D

---

## 1 Introduction

### 1.1 Nightmare Disorder and Imagery Rehearsal Therapy
- ~5% prevalence, comorbidity with PTSD/depression
- IRT as evidence-based gold standard with rigid five-stage structure
- Rescripting as the cognitive core, the phase where active therapeutic strategy decisions happen
- Clinician shortage as motivation for scalable AI delivery

### 1.2 AI-Assisted Psychotherapy and Deployment Context
- LLM deployment in mental health: from empathy tools to full protocol agents (Stade et al., 2024)
- reDreamAI as the concrete deployment context
  \-- Consumer-facing IRT chatbot guiding users through all five protocol stages
  \-- Not a general assistant: a protocol-driven agent where consistency is a clinical obligation
  \-- Why this matters: inconsistency in a manualized intervention is not stylistic variation but a potential clinical failure
- Ethical scope
  \-- IRT targets nightmares (not psychiatric diagnosis), lowering clinical risk relative to full psychotherapy
  \-- Still requires awareness: AI-generated therapeutic responses carry responsibility even below diagnostic thresholds
  \-- Full ethical discussion in 6.4 and 7.2
- EU AI Act and data sovereignty as constraints on model selection (motivates 3.6)

### 1.3 The Evaluation Gap
- Standard benchmarks measure capability, not reliability across repeated runs
  \-- Why this is a problem: a model can produce high-quality individual responses while being clinically unreliable across sessions
- No existing metrics for intent stability, protocol adherence, or strategic consistency
- Prior therapeutic AI evaluation is qualitative, post-hoc, or single-session
  \-- No systematic framework for quantifying therapeutic consistency under stochastic conditions

### 1.4 Research Objectives
- RQ: How consistent is LLM clinical reasoning across stochastic runs in a structured therapeutic protocol?
- Contribution 1: three-level evaluation framework (plan, output, alignment)
- Contribution 2: cross-model comparison (sovereign, proprietary, open-weight)
- Scope: IRT rescripting phase only
  \-- Why rescripting only: highest-stakes intervention point, requires active strategy decisions (unlike recording or rehearsal), isolates therapist model from upstream classification error

---

## 2 Background

Each section establishes one conceptual prerequisite and ends with an open tension that the Methods chapter resolves.

### 2.1 Imagery Rehearsal Therapy
- Five-stage protocol: recording, rewriting, summary, rehearsal, final
  \-- Rescripting as the phase requiring active therapeutic strategy decisions
- Treatment fidelity instruments (ENACT, NIH BCC)
  \-- Grade therapist adherence on a ternary scale: absent, partial, implemented
  \-- Why this matters: provides the scoring foundation for Method 3 (3.5.3)
- Strategy taxonomy scope derives from the space of legitimate rescripting moves (grounds 3.4)
- Tension: fidelity assessment exists for human therapists but not for LLM-based agents

### 2.2 Treatment Fidelity in LLM-Based Interventions
- Scope: protocol adherence in manualized interventions, not the full LLM-healthcare landscape. General clinical AI is referenced only where it establishes failure modes relevant to stability measurement.
- Treatment fidelity research (Webb et al., 2010; Waltz et al., 1993)
  \-- Adherence (doing the prescribed things) vs competence (doing them well)
  \-- For rule-based chatbots, adherence is built in
  \-- For LLMs, adherence becomes probabilistic and must be measured across runs
- Documented failure modes that map to evaluation methods:
  \-- Strategy drift -> Method 1 (plan consistency)
  \-- Output variability -> Method 2 (semantic stability)
  \-- Plan-output mismatch -> Method 3 (alignment)
- Tension: stability is a deployment precondition, but no existing framework measures it for protocol-driven LLM agents

### 2.3 Stochastic Behaviour in Language Models
- At T>0, token selection is probabilistic
  \-- Small per-token variance compounds across a full response through autoregressive cascading
  \-- Clinical consequence: the same patient on two different days may receive strategically inconsistent care
- Prior stability work targets factual consistency or output diversity, not therapeutic strategy stability
- Tension: the mechanical source of instability is well understood, but its impact on structured therapeutic decision-making has not been quantified (justifies temperature conditions in 3.7)

### 2.4 Evaluation Metrics for Text Generation
- Surface metrics (BLEU/ROUGE)
  \-- Why ruled out: penalize valid therapeutic paraphrasing
- BERTScore (Zhang et al., 2020)
  \-- Captures semantic equivalence independent of surface form
  \-- DeBERTa-XLarge-MNLI: highest human correlation (r = 0.778)
  \-- Why selected for Method 2: matches the semantic equivalence question, robust to paraphrasing
- LLM-as-judge
  \-- Can assess criteria no scalar metric captures (e.g. "does this response implement a confrontation strategy?")
  \-- Known biases: self-preference, position, verbosity
  \-- Why still used: only approach that can assess strategic intent, mitigations in 3.5.3
- Tension: no single metric covers what clinical stability requires, motivating the multi-method design

---

## 3 Methods

### 3.1 System Overview and Design Rationale
- Two decoupled stacks: generation (dialogue creation) and evaluation (stability measurement)
  \-- Why decoupled: prevents generation-side randomness from contaminating stability measurement
  \-- Any measured instability is attributable to the model under test, not upstream context differences
- Data flow: vignettes -> generation -> frozen histories -> evaluation -> aggregation
  \-- Why this order: frozen histories create identical entry points, isolating the variable under test

VISUAL: diagram for two-stack pipeline with data flow and isolation boundary

### 3.2 Dialogue Generation
- Three-agent loop: patient, router, therapist
  \-- Patient: BDI-profiled vignette simulating clinical presentation
  \-- Router: stage classifier determining which IRT phase the conversation is in
  \-- Therapist: generates stage-appropriate therapeutic response
  \-- Why three agents: separates clinical reasoning from stage classification and patient simulation, matching reDreamAI's deployment architecture
- Six vignettes: anxious, avoidant, cooperative, resistant, skeptic, trauma
  \-- Why these six: cover the range of clinical presentation difficulty, from cooperative (easy) to trauma/resistant (hard)
  \-- Tests whether model stability varies with patient complexity
  \-- Vignette design informed by prior synthetic patient work (Wang et al., 2024, Roleplay-doh). Six profiles sample the difficulty range but do not claim exhaustive coverage (limitation in 7.2)

VISUAL: diagram for three-agent generation loop with example exchange

### 3.3 Evaluation Design
- Frozen conversation histories as deterministic entry points
  \-- Conversations sliced at rewriting-turn boundaries: slice_1, slice_2, slice_3
  \-- Each slice is identical across all trials and all models
  \-- Why three depths: tests whether stability changes as therapeutic context accumulates
  \-- Why slice at turn boundaries: clean cut points that preserve conversational coherence
VISUAL: short representation of frozen history and slicing at 3 points
- Evaluation stack
  \-- Router bypassed, rescripting prompt injected directly (isolates therapist model from stage-classification error)
  \-- Fused generation: `<plan>` block declaring 1-2 strategies, then therapeutic response conditioned on that declaration
  \-- Why fused: plan and response in a single pass, so the response is directly conditioned on the declared plan (enables Method 3)
  \-- 10 independent trials per condition: C(10,2) = 45 pairwise comparisons, balancing statistical power with compute cost

### 3.4 Plan Mechanism and Strategy Taxonomy
- The CoT faithfulness problem: CoT prompting (Wei et al., 2022) improves output structure, but faithfulness literature (Turpin et al., 2023; Lanham et al., 2023) shows that CoT explanations often do not reflect actual computation. If a model declares its strategy before responding, that declaration may be post-hoc rationalization rather than a window into its decision-making.
- Resolution: the `<plan>` block is framed as declared intent, not a reasoning trace
  \-- Why declared intent: sidesteps the faithfulness debate entirely
  \-- Whether or not the declaration reflects internal computation, variable declarations predict variable clinical responses
  \-- The plan captures what the model commits to, which is what matters for clinical oversight
- Three downstream uses:
  \-- Strategy-level consistency scoring (Method 1)
  \-- Plan-output alignment verification (Method 3)
  \-- Human-readable clinical oversight (practical deployment value)
- Fixed taxonomy constrains declarations to 7 discrete categories
  \-- Why fixed: free-text plans cannot be aggregated into Jaccard scores
  \-- Categories: confrontation, self_empowerment, safety, cognitive_reframe, emotional_regulation, social_support, sensory_modulation
  \-- Why these: derived from legitimate IRT rescripting moves (grounded in 2.1), refined through iterative testing
- Development process
  \-- v1: 8 categories, 87.7% skew on empowerment/mastery (too coarse)
  \-- v2: merge to agency, 100% dominance (worse)
  \-- v3: mechanism-level split distinguishing external action from internal transformation (resolved)
  \-- Why document the iteration: shows that taxonomy design directly affects measured consistency (discussed in 6.4)

### 3.5 Evaluation Metrics

Three methods targeting distinct layers, addressing the multi-metric gap from 2.4.

VISUAL: diagram for three-level evaluation framework (central figure)

#### 3.5.1 Method 1: Cognitive Stability (Plan Consistency)
- Measures: does the model make consistent therapeutic decisions?
- Pairwise Jaccard similarity over strategy sets from `<plan>` blocks
  \-- Mean over C(10,2) = 45 trial pairs
  \-- Why Jaccard: set similarity for unordered strategy combinations, order does not matter clinically
- Validity rate as upstream quality gate
  \-- Why a quality gate: malformed plan blocks cannot be scored, validity rate shows whether the model can follow the structured output format at all

#### 3.5.2 Method 2: Output Consistency (Semantic Stability)
- Measures: does the model produce consistent therapeutic responses?
- Pairwise BERTScore F1 using DeBERTa-XLarge-MNLI
  \-- Why this model: NLI fine-tuning aligns with semantic equivalence, highest WMT16 human correlation (grounded in 2.4)
  \-- Why not surface metrics: therapeutic paraphrasing is the norm, surface overlap penalizes valid variation

#### 3.5.3 Method 3: Plan-Output Alignment
- Measures: does the model do what it says it will do?
- LLM judge with ternary scoring per declared strategy: 0 = absent, 1 = partial, 2 = implemented
  \-- Why ternary: borrowed from clinical fidelity literature (ENACT, NIH BCC, grounded in 2.1)
  \-- Why not NLI cross-encoders: tested and rejected (F1 ceiling ~0.55, no reasoning trace)
- Judge: Gemini 3.1 Pro (Google AI Studio, T=0.0), different model family than any evaluation target
  \-- Why cross-family: prevents model family bias
  \-- Why Gemini: thinking mode aids judgment accuracy, free credits, no OpenAI/Mistral/Meta models in eval targets
- Bias mitigations:
  \-- Cross-model judging (judge never evaluates its own family)
  \-- CoT justification (judge explains its rating)
  \-- Deterministic decoding (T=0.0)
  \-- Transparent rubric
- Acknowledged limitation: judge reliability is itself an open question (discussed in 6.4)
- Validation: human annotation of a random subset (~50 trials) scoring the same rubric. Cohen's kappa between human and judge as reliability estimate. If kappa is low, Method 3 results carry the caveat explicitly.

### 3.6 Model Selection
- EU data sovereignty as primary criterion for the primary subject (legal constraint from 1.2)
- Primary subject: Mistral Large 3 (675B MoE, 41B active, EU-sovereign, Apache 2.0)
  \-- Why: EU-sovereign flagship, the model reDreamAI would deploy
- Proprietary ceiling: GPT-5.4 (non-thinking variant, $2.50/$15.00)
  \-- Why GPT-5.4: strongest proprietary model without thinking overhead, fair comparison with all other non-thinking targets
- Open-weight comparators across three size classes, all non-thinking:
  \-- Small (24-32B dense): Qwen 3.5 27B, OLMo 3.1 32B
  \-- Mid (70B dense): Llama 3.3 70B (continuity with prior efficacy study)
  \-- Large (MoE): DeepSeek V3.2 671B (MoE comparator to Mistral Large)
  \-- Why these: size-class diversity, dense vs MoE architecture, provider diversity
- Qwen 3.5 runs with reasoning disabled (hybrid-thinking model) for fair comparison

### 3.7 Experimental Conditions
- Full factorial: 6 vignettes x 3 slices x 10 trials x 2 temperatures x N models
  \-- T=0.0 as deterministic upper bound on stability (grounded in 2.3)
  \-- T=0.7 as realistic clinical deployment range
  \-- Why both: T=0.0 shows the stability ceiling, the gap to T=0.7 quantifies the stochastic cost of realistic deployment

### 3.8 Statistical Analysis
- Descriptive statistics: means, standard deviations, confidence intervals across 45 trial pairs per condition
- Bootstrap 95% confidence intervals for model comparisons
- Spearman rank correlations for cross-method analysis (5.5)
  \-- Why Spearman: rank-based, robust to non-normal distributions from bounded similarity scores
- No fixed threshold for "stable enough." Results are interpreted comparatively (model vs model, T=0.0 vs T=0.7) rather than against an absolute cutoff. Clinical significance thresholds for LLM stability do not yet exist in the literature.

---

## 4 Implementation

### 4.1 Software Architecture
- Python async pipeline
  \-- Why async: factorial design requires many independent API calls, parallel execution essential for feasibility
- YAML-driven configuration
  \-- model swaps, temperature changes, vignette selection without code changes possible
- Pydantic validation at every data boundary
  \-- Why: prevents malformed plan blocks from corrupting downstream metrics
- Provider abstraction (OpenRouter, Google AI Studio)
  \-- Why: adding a new model means adding a config entry, not changing evaluation logic

### 4.2 Experiment Execution and Aggregation
- Config driven orchestration with parallel trial execution
- Artefact hierarchy per run:
  \-- Config snapshot (reproducibility)
  \-- Frozen history (irreplaceable, the experimental input)
  \-- Trials (raw model outputs)
  \-- Metrics and judgments (recomputable from trials)
  \-- Why this distinction: frozen histories cannot be regenerated, all downstream artefacts can be recomputed
- Aggregation: cross-condition alignment into a single analysis frame indexed by model, vignette, slice, temperature
  \-- Why unified: required for cross-method analysis in 5.5

---

## 5 Results

All main results reported at slice_2 (mid-rescripting), aggregated across vignettes. Full per-condition tables in Appendix D.

### 5.1 Plan Validity and Strategy Distribution
- Validity rates across models and temperatures (quality gate)
- Strategy frequency distribution: one heatmap (model x strategy category)

### 5.2 Cognitive Stability (Method 1)
- Mean Jaccard by model x temperature (headline figure)
- Stochastic cost: T=0.0 vs T=0.7 gap per model

### 5.3 Output Consistency (Method 2)
- Mean BERTScore F1 by model x temperature (same format as 5.2)

### 5.4 Plan-Output Alignment (Method 3)
- Mean alignment score by model x temperature
- Per-strategy scoring distributions (absent / partial / implemented)

### 5.5 Cross-Method Analysis
- Spearman rank correlations across all three method pairs (M1-M2, M1-M3, M2-M3)
- Per-model stability profiles across all three methods
- Divergence cases:
  \-- High plan consistency + low output consistency = stable intent, variable execution
  \-- Low plan consistency + high output consistency = different strategies, similar surface output

### 5.6 Secondary Effects
- Vignette difficulty: one heatmap (model x vignette) showing where instability concentrates
- Conversation depth: slice_1 vs slice_3 comparison for primary model. Early rescripting (less anchoring context) may show more variable strategy selection than later turns

---

## 6 Discussion

### 6.1 Interpreting the Three-Level Framework
- Three methods as diagnostic tool for locating instability sources
- Divergence patterns map to different clinical risks:
  \-- Planning instability -> unpredictable therapeutic decisions
  \-- Output instability -> inconsistent patient experience
  \-- Alignment failure -> model says one thing, does another
- Localizing the problem has direct implications for mitigation

### 6.2 Cross-Model Comparison
- Does Mistral Large match the proprietary ceiling on stability?
- Does self-hostability come at a stability cost?
- Size-class effects across model range
- Stability as a dimension independent of capability

### 6.3 Temperature and Clinical Deployment
- T=0.0 as upper bound: which models achieve near-deterministic stability?
- T=0.7 degradation: which models lose the most?
- Practical deployment recommendations

### 6.4 Evaluation Framework Reflections
- Taxonomy sensitivity: how category design shapes measured consistency (connects back to 3.4)
- Declared-intent framing: what it enables and what it cannot claim about model cognition
- Method 3 limitations: judge reliability, cross-family mitigation effectiveness
- Ethical considerations
  \-- IRT as lower-risk entry point (no diagnosis), but still requires safeguards
  \-- Stability as necessary but not sufficient for safe deployment
- Generalizability to other manualized protocols (CBT, DBT)
- Broader perspective: framework as reusable validation template for protocol-driven AI agents. Computational evaluation complements but does not substitute clinical validation.

---

## 7 Conclusion

### 7.1 Summary of Findings
- Direct answer to the research question across all three levels

### 7.2 Limitations
- Single protocol phase (rescripting only)
- Synthetic patients (no real clinical interactions)
- Six vignettes sample the difficulty range but cannot claim exhaustive coverage of patient variability
- Method 3 judge reliability
- Fixed taxonomy (alternative categorizations could yield different profiles)
- Computational stability does not equal clinical safety

### 7.3 Future Work
- Extension to other manualized therapies (CBT, DBT)
- Longitudinal version drift (same model across updates)
- Multi-language evaluation for reDreamAI
- Clinical validation with human therapist ratings
- Replication with future model generations to track whether stability improves across release cycles

---

## Appendices

A Strategy Taxonomy: full 7-category definitions with examples, revision history (v1 -> v3)
B Prompts: fused plan+response system prompt, judge rubric, patient vignette profiles
C Architecture Diagrams: detailed pipeline diagram (expanded version of 3.1)
D Supplementary Results: full per-condition metric tables

---

## Visualizations

Conceptual diagrams (draw before writing):
\-- 3.1: Two-stack pipeline (generation/evaluation isolation and data flow)
\-- 3.2: Three-agent loop (interaction cycle with example exchange for generation)
\-- frozen history + slicing
\-- 3.5: Three-level framework (central figure, shows how the three methods relate)

Results figures (TBD when data is in):
\-- Strategy distribution heatmap (models x strategies) ??
\-- Stability scores by model and temperature
\-- Cross-method comparison

cascading, metric coverage, plan mechanism only in text?
