# Thesis Structure

**Measuring Drift in Therapeutic AI: A Stability-Based Evaluation of Sovereign LLMs in Nightmare Therapy**

> **Supervisor feedback applied (2026-03-23):**
> 1. Term discipline: define key terms early, reuse minimal set consistently
> 2. Descriptive method labels: avoid theoretically loaded names ("Cognitive Stability" -> "Plan Consistency")
> 3. Novelty claims: position relative to closest existing work, not as "first ever"
> 4. Paragraph structure: topic sentence, supporting arguments with examples, summary/transition

---

## Key Terms (defined once, used throughout)

These terms are introduced and defined in the sections indicated, then reused without re-explanation:

| Term | Definition | Introduced in |
|------|-----------|---------------|
| **Stability** | Whether a model produces the same therapeutic decisions and responses when given identical input across independent runs | 1.3 |
| **Treatment fidelity** | The degree to which a therapist (human or AI) delivers an intervention as prescribed by its protocol. Two components: adherence (doing the right things) and competence (doing them well) | 2.2 |
| **Frozen history** | A pre-generated conversation saved to disk and used as identical input for every evaluation trial, eliminating upstream context variation | 3.3 |
| **Declared intent** | The strategy the model commits to in its `<plan>` block before responding. Framed as a structured output, not a claim about internal reasoning | 3.4 |
| **Stochastic cost** | The gap in measured stability between T=0.0 (deterministic) and T=0.7 (realistic deployment). Quantifies how much consistency a model loses from sampling | 3.7 |
| **Rescripting** | The IRT stage where the patient and therapist collaboratively transform the nightmare narrative. The phase requiring active strategy decisions | 2.1 |

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
\-- 3.4 Plan Mechanism and Strategy Taxonomy
\-- 3.5 Evaluation Metrics
\-  3.5.1 Method 1: Plan Consistency
\-  3.5.2 Method 2: Response Similarity
\-  3.5.3 Method 3: Plan-Response Alignment
\-- 3.6 Model Selection
\-- 3.7 Experimental Conditions
\-- 3.8 Statistical Analysis

4 Implementation
\-- 4.1 Software Architecture
\-- 4.2 Experiment Execution and Aggregation

5 Results
\-- 5.1 Plan Validity and Strategy Distribution
\-- 5.2 Plan Consistency (Method 1)
\-- 5.3 Response Similarity (Method 2)
\-- 5.4 Plan-Response Alignment (Method 3)
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

Nightmare disorder affects roughly 5% of adults and often co-occurs with PTSD and depression. Imagery Rehearsal Therapy (IRT) is the recommended treatment (Morgenthaler et al., 2018). IRT follows a five-stage protocol. The rescripting stage is the focus of this study because it is the only stage that requires the therapist to make active strategy decisions (what kind of change to introduce into the nightmare). A shortage of trained therapists motivates exploring AI-assisted delivery.

### 1.2 AI-Assisted Psychotherapy and Deployment Context

LLMs are increasingly deployed in mental health, from empathy-based tools to protocol-driven agents that deliver structured interventions (Stade et al., 2024). reDreamAI is the deployment context for this study: a consumer-facing IRT chatbot that guides users through all five protocol stages.

reDreamAI is not a general-purpose assistant. It follows a clinical protocol, which means its responses must be consistent across sessions. If the model selects different therapeutic strategies for the same patient input on different runs, the patient receives inconsistent care. This inconsistency is the problem this thesis measures.

IRT targets nightmares rather than psychiatric diagnoses, which lowers the clinical risk relative to full psychotherapy. Ethical considerations are discussed in 6.4 and 7.2.

The EU AI Act and data sovereignty requirements constrain the choice of deployment model to EU-resident options (motivates 3.6).

### 1.3 The Evaluation Gap

Standard benchmarks measure what a model can do (capability), not whether it does the same thing reliably (stability). A model can score well on a single evaluation while producing different therapeutic strategies on repeated runs of the same input.

The closest existing work is BOLT (Chiu et al., 2024), which evaluates LLM therapist behaviour using 13 behavioural codes from motivational interviewing. BOLT measures whether the model applies appropriate therapeutic techniques (quality). This study measures a different property: whether the model applies the *same* techniques across repeated runs (stability). BOLT evaluates single responses. This study evaluates the distribution of responses across 10 independent trials per condition.

Other therapeutic AI evaluations are qualitative, post-hoc, or single-session. They cannot detect cross-run inconsistency because they do not run the same input multiple times.

### 1.4 Research Objectives

**RQ:** How consistent are LLM therapeutic responses across independent runs when given the same patient context within a structured IRT protocol?

**Contribution 1:** A three-level evaluation framework that measures stability at three layers: plan consistency (do strategy selections repeat?), response similarity (do outputs mean the same thing?), and plan-response alignment (does the model do what it declared?).

**Contribution 2:** A cross-model comparison applying this framework to sovereign, proprietary, and open-weight models.

**Scope:** IRT rescripting phase only. Rescripting is the highest-stakes stage because it requires active strategy decisions. Isolating it removes stage-routing confounds and allows any measured instability to be attributed to the therapist model.

---

## 2 Background

Each section introduces one concept needed for the Methods chapter and ends with an open question that Methods resolves.

### 2.1 Imagery Rehearsal Therapy

IRT follows five stages: recording, rewriting, summary, rehearsal, final (Krakow and Zadra, 2006). The rewriting (rescripting) stage is where the therapist guides the patient to transform the nightmare. Unlike recording (listening) or rehearsal (repetition), rescripting requires the therapist to select a specific change strategy. Clinical research identifies distinct rescripting strategies with different prevalence rates (Harb et al., 2012; Germain et al., 2004). These categories ground the strategy taxonomy in 3.4.

Treatment fidelity instruments (ENACT, NIH BCC) grade whether a therapist delivers an intervention correctly on a three-level scale: absent, partial, implemented. This scale provides the scoring basis for Method 3 (3.5.3).

**Open question:** Fidelity instruments assume a human therapist. How should fidelity be assessed for an LLM that generates a new response on every run?

### 2.2 Treatment Fidelity in LLM-Based Interventions

Treatment fidelity has two components: adherence (doing the prescribed things) and competence (doing them well) (Mowbray et al., 2003; Bellg et al., 2004). For rule-based chatbots like Woebot (Fitzpatrick et al., 2017), adherence is built in because responses are pre-authored. For LLM-based agents, every response is a new sample from the output distribution. Adherence becomes probabilistic and must be measured across runs.

LLMs also face general failure modes such as hallucination, stage confusion, and persona inconsistency. These are important but fall outside the scope of this study. This study focuses on a specific problem: the probabilistic nature of LLM outputs creates variation even when the input is identical. When the same patient describes the same nightmare, stochastic sampling can produce different strategy selections and different therapeutic responses across runs.

The EU AI Act classifies autonomous therapeutic AI as high-risk, requiring auditability (Aboy et al., 2024; van Kolfschooten and van Oirschot, 2024). Data sovereignty pushes toward EU-resident models (Dale, 2025), constraining model selection (3.6).

**Open question:** Stability is a precondition for deployment, but existing evaluations (including BOLT) measure single-run quality, not cross-run consistency. How can consistency be measured systematically?

### 2.3 Stochastic Behaviour in Language Models

At temperature T > 0, LLM token selection is probabilistic. Higher temperatures flatten the probability distribution, increasing variance. Each token is conditioned on all preceding tokens, so a single divergent token early in a response can cascade into a different therapeutic strategy.

Prior stability research addresses different questions: factual consistency (do models give the same answer to knowledge questions?), output diversity (how much does generated text vary?), and benchmark reproducibility (are evaluation scores stable across runs?). None of these address whether an LLM makes the same *therapeutic decisions* when given the same patient context.

**Open question:** The mechanism of instability (temperature sampling + autoregressive cascading) is well understood. What is not known is how much this instability costs in therapeutic consistency. This motivates the temperature conditions in 3.7.

### 2.4 Evaluation Metrics for Text Generation

Measuring consistency between text outputs requires a similarity metric. Three types exist, each with limitations for therapeutic language:

**Surface metrics** (BLEU, ROUGE) measure token overlap. They penalise valid therapeutic paraphrasing (same strategy, different words) and reward surface similarity between strategically divergent responses. Ruled out.

**Embedding similarity** (BERTScore, Zhang et al., 2020) compares texts in contextual embedding space. Captures semantic equivalence independent of wording. DeBERTa-XLarge-MNLI achieves the highest human correlation (r = 0.778) among available models. Selected for Method 2.

**LLM-as-judge** (Zheng et al., 2023) can assess criteria that scalar metrics cannot (e.g. "does this response implement a confrontation strategy?"). Known biases: self-preference, position, verbosity. Mitigations exist (cross-model judging, structured rubrics, deterministic decoding).

**Open question:** Embedding similarity captures whether two responses mean the same thing but cannot determine whether they implement the same therapeutic strategy. LLM judges can assess strategy but introduce their own reliability concerns. No single metric covers therapeutic stability, motivating the three-method design in 3.5.

---

## 3 Methods

### 3.1 System Overview and Design Rationale

The system has two decoupled stacks: generation (creates therapy dialogues) and evaluation (measures stability). Decoupling ensures that any measured instability comes from the model under test, not from variation in the input context.

Data flow: vignettes -> generation stack -> frozen histories -> evaluation stack -> aggregation.

VISUAL: diagram for two-stack pipeline with data flow and isolation boundary

### 3.2 Dialogue Generation

A three-agent loop generates therapy sessions: the patient agent (BDI-profiled vignette), the router agent (classifies the current IRT stage), and the therapist agent (generates a stage-appropriate response). This architecture mirrors reDreamAI's deployment structure.

Six vignettes cover different patient presentations: anxious, avoidant, cooperative, resistant, skeptic, trauma. These range from easy (cooperative) to difficult (trauma, resistant) and test whether stability varies with patient complexity. The vignette design draws on synthetic patient work (Wang et al., 2024a; Wang et al., 2024b). Six profiles sample the difficulty range but do not claim exhaustive coverage (limitation in 7.2).

VISUAL: diagram for three-agent generation loop with example exchange

### 3.3 Evaluation Design

**Frozen histories** are pre-generated conversations saved to disk and used as identical input for every trial. Each vignette is sliced at three rewriting-turn boundaries (slice_1, slice_2, slice_3), creating evaluation contexts at different conversation depths. Every trial, across all models and temperatures, receives the same frozen history.

The **evaluation stack** bypasses the router and injects the rescripting prompt directly. The model produces a `<plan>` block (declaring 1-2 strategies) followed by the therapeutic response in a single fused call. The plan tokens condition the response tokens, so the response is directly shaped by the declared strategy.

10 independent trials per condition yield C(10,2) = 45 pairwise comparisons.

VISUAL: frozen history and slicing at 3 points

### 3.4 Plan Mechanism and Strategy Taxonomy

The `<plan>` block uses chain-of-thought-style prompting (Wei et al., 2022), but the faithfulness literature shows that CoT explanations do not always reflect actual computation (Turpin et al., 2023; Lanham et al., 2023). This study frames the plan as **declared intent**: a structured output that captures what the model commits to, not a window into its reasoning. Whether or not the declaration reflects internal computation, variable declarations predict variable responses.

Three uses: (1) measuring whether strategy selections repeat across trials (Method 1), (2) checking whether the response matches the declared strategy (Method 3), (3) providing a human-readable summary for clinical oversight.

A **fixed taxonomy** of 6 rescripting strategies constrains the plan to categories that can be compared quantitatively (free-text plans cannot be aggregated into similarity scores). The categories are: confrontation, self_empowerment, safety, cognitive_reframe, social_support, sensory_modulation. They describe therapeutic *mechanisms* (how the change works) rather than goals (what the patient achieves), based on clinical rescripting research (Germain et al., 2004; Harb et al., 2012).

The taxonomy evolved through four iterations to resolve a distribution skew where empowerment/mastery consumed 87.7% of selections (documented in 6.4).

### 3.5 Evaluation Metrics

Three methods, each targeting a different layer. Together they address the limitation identified in 2.4 (no single metric covers therapeutic stability).

VISUAL: diagram for three-level evaluation framework (central figure)

#### 3.5.1 Method 1: Plan Consistency

**Question:** Does the model select the same strategies across independent trials?

Pairwise Jaccard similarity over strategy sets from `<plan>` blocks. Mean over C(10,2) = 45 trial pairs. Jaccard is appropriate because strategy combinations are unordered sets.

Validity rate serves as a quality gate: the proportion of trials where the `<plan>` block parses into valid strategy identifiers.

#### 3.5.2 Method 2: Response Similarity

**Question:** Does the model produce semantically equivalent responses across trials?

Pairwise BERTScore F1 over response texts (plan blocks excluded), using DeBERTa-XLarge-MNLI. Captures semantic equivalence regardless of surface wording (grounded in 2.4).

#### 3.5.3 Method 3: Plan-Response Alignment

**Question:** Does the model's response implement the strategies it declared?

An LLM judge (Gemini 3.1 Pro, T=1.0) scores each declared strategy on a three-level scale: 0 = absent, 1 = partial, 2 = implemented. This scale is borrowed from clinical fidelity instruments (ENACT, NIH BCC, introduced in 2.1).

The judge runs at T=1.0 (Gemini 3's default) because Google's documentation warns against lowering temperature for Gemini 3 models, and empirical evidence shows no accuracy loss between T=0.0 and T=1.0 (Renze, 2024). Consistency comes from the structured rubric and scoring format, not from temperature.

Bias mitigations: cross-model judging (judge is from a different model family than all targets), CoT justification, transparent rubric. NLI cross-encoders were tested and rejected (F1 ceiling ~0.55, no reasoning trace).

Judge reliability is an open question. Validation through human annotation of ~50 trials with Cohen's kappa.

### 3.6 Model Selection

EU data sovereignty is the primary criterion for the main subject. All targets run in non-thinking mode.

- **Primary:** Mistral Large 3 (675B MoE, 41B active, EU-sovereign, Apache 2.0). The model reDreamAI would deploy
- **Proprietary ceiling:** GPT-5.4 (non-thinking). Upper-bound comparison
- **Open-weight comparators:** Qwen 3.5 27B, OLMo 3.1 32B (small), Llama 3.3 70B (mid), DeepSeek V3.2 671B MoE (large)
- Selection provides size-class diversity (27-675B), dense vs MoE, provider diversity
- Qwen 3.5 runs with reasoning disabled for fair comparison

% TODO: update after final model selection (check models.yaml)

### 3.7 Experimental Conditions

Full factorial: 6 vignettes x 3 slices x 10 trials x 2 temperatures x N models.

T=0.0 provides a deterministic upper bound on stability (greedy decoding). T=0.7 represents realistic deployment. The gap between them is the **stochastic cost**: how much consistency a model loses from sampling at a realistic temperature.

### 3.8 Statistical Analysis

Descriptive: medians/IQR for Jaccard (ordinal), means/SD for BERTScore and alignment. Bootstrap 95% confidence intervals.

Spearman rank correlations between method pairs (M1-M2, M1-M3, M2-M3). Spearman because Jaccard scores are ordinal and BERTScore distributions may be non-normal.

No fixed threshold for "stable enough." Results are interpreted comparatively (model vs model, T=0.0 vs T=0.7). Clinical thresholds for LLM stability do not yet exist.

---

## 4 Implementation

### 4.1 Software Architecture

Python async pipeline. YAML-driven configuration (model swaps, temperature changes without code changes). Pydantic validation at data boundaries. Provider abstraction (OpenRouter for evaluation targets, Google AI Studio for judge).

### 4.2 Experiment Execution and Aggregation

Config-driven orchestration with parallel trial execution. Artefact hierarchy: config snapshot, frozen history (irreplaceable), trials (raw outputs), metrics and judgments (recomputable). Aggregation aligns all conditions into a single analysis frame for cross-method comparison.

---

## 5 Results

All main results at slice_2 (mid-rescripting), aggregated across vignettes. Full per-condition tables in Appendix D.

### 5.1 Plan Validity and Strategy Distribution
- Validity rates across models and temperatures (quality gate)
- Strategy frequency distribution: heatmap (model x strategy category)

### 5.2 Plan Consistency (Method 1)
- Jaccard by model x temperature (headline figure)
- Stochastic cost: T=0.0 vs T=0.7 gap per model

### 5.3 Response Similarity (Method 2)
- BERTScore F1 by model x temperature

### 5.4 Plan-Response Alignment (Method 3)
- Alignment score by model x temperature
- Per-strategy scoring distributions (absent / partial / implemented)

### 5.5 Cross-Method Analysis
- Spearman correlations across method pairs
- Per-model stability profiles across all three methods
- Divergence cases: high plan consistency + low response similarity = same strategy selections, variable execution. The reverse = different strategies, similar surface output.

### 5.6 Secondary Effects
- Vignette difficulty: heatmap (model x vignette) showing where instability concentrates
- Conversation depth: slice_1 vs slice_3 for primary model

---

## 6 Discussion

### 6.1 Interpreting the Three-Level Framework
- Three methods as diagnostic tool: which layer is the source of instability?
- Divergence patterns map to different problems: inconsistent strategy selection, inconsistent response execution, or mismatch between the two

### 6.2 Cross-Model Comparison
- Does Mistral Large match the proprietary ceiling on stability?
- Does self-hostability come at a stability cost?
- Size-class effects
- Stability as a dimension independent of capability

### 6.3 Temperature and Clinical Deployment
- T=0.0 as upper bound: which models approach deterministic stability?
- T=0.7 degradation: which models lose the most?
- Practical deployment recommendations

### 6.4 Evaluation Framework Reflections
- Taxonomy sensitivity: how category design shapes measured consistency (connects back to 3.4)
- Declared-intent framing: what it enables and what it cannot claim about model reasoning
- Method 3 limitations: judge reliability, cross-family mitigation effectiveness
- Ethical considerations: IRT as lower-risk context, stability as necessary but not sufficient
- Generalisability to other structured protocols (CBT, DBT)

---

## 7 Conclusion

### 7.1 Summary of Findings
- Direct answer to the research question across all three levels

### 7.2 Limitations
- Single protocol phase (rescripting only)
- Synthetic patients (no real clinical interactions)
- Six vignettes sample the difficulty range but do not cover all patient variability
- Method 3 judge reliability
- Fixed taxonomy (different categories could yield different profiles)
- Measured stability is not the same as clinical safety

### 7.3 Future Work
- Extension to other structured therapies (CBT, DBT)
- Longitudinal drift (same model across version updates)
- Multi-language evaluation for reDreamAI
- Clinical validation with human therapist ratings
- Replication with future models

---

## Appendices

A Strategy Taxonomy: 6-category definitions, examples, revision history (v1-v4)
B Prompts: fused plan+response system prompt, judge rubric, vignette profiles
C Architecture Diagrams: expanded pipeline diagram
D Supplementary Results: full per-condition metric tables

---

## Visualizations

Conceptual diagrams (draw before writing):
\-- 3.1: Two-stack pipeline (generation/evaluation isolation and data flow)
\-- 3.2: Three-agent loop (interaction cycle with example exchange)
\-- 3.3: Frozen history + slicing at 3 points
\-- 3.5: Three-level framework (central figure)

Results figures (populate when data is in):
\-- 5.1: Validity rates + strategy frequency heatmap
\-- 5.2: Jaccard by model x temperature
\-- 5.3: BERTScore by model x temperature
\-- 5.4: Alignment scores + per-strategy stacked bar
\-- 5.5: Cross-method correlations
\-- 5.6: Vignette heatmap + slice depth comparison
