# Thesis Structure

**Measuring Drift in Therapeutic AI: A Stability-Based Evaluation of Sovereign LLMs in Nightmare Therapy**

Daniel Menzel, Institute of Cognitive Science, University of Osnabruck
Supervisors: Moritz Hartstang, Sebastian Musslick

---

## Table of Contents

1. Introduction
2. Background
3. Methods
4. Implementation
5. Results
6. Discussion
7. Conclusion
Appendices: A Strategy Taxonomy, B Prompts, C Architecture Diagrams, D Supplementary Results

---

## 1 Introduction

IRT is a manualized protocol where a chatbot must make consistent strategic decisions. Standard benchmarks measure capability, not reliability across runs. EU sovereignty constraints narrow the candidate set.

The thesis contributes a three-level evaluation framework (plan consistency, output consistency, plan-output alignment) and applies it across sovereign, proprietary, and open-weight LLMs in the IRT rescripting phase.

**1.1 Nightmare Disorder and Imagery Rehearsal Therapy**
\- ~5% prevalence, comorbidity with PTSD/depression. IRT as evidence-based gold standard with rigid phase structure. Rescripting as the cognitive core. Clinician shortage as motivation for scalable AI delivery.

**1.2 AI-Assisted Psychotherapy and Deployment Context**
\- LLM deployment in mental health from empathy tools to full protocol agents (Stade et al., 2024). reDreamAI as applied deployment context: consumer-facing IRT chatbot, not a general assistant. Protocol agent where consistency is a clinical obligation, not optional. Ethical scope: IRT targets nightmares (not diagnosis), lowering clinical risk, but AI-generated therapeutic responses still carry responsibility. Full ethical discussion in 6.4 and 7.2. EU AI Act and data sovereignty as constraints on model selection (→ 3.6).

**1.3 The Evaluation Gap**
\- Standard benchmarks measure capability, not reliability across runs. No existing metrics for intent stability, protocol adherence, or strategic consistency. Prior therapeutic AI evaluation is qualitative, post-hoc, or single-session. No systematic framework for quantifying therapeutic consistency under stochastic conditions.

**1.4 Research Objectives**
\- **RQ:** How consistent is LLM clinical reasoning across stochastic runs in a structured therapeutic protocol?
\- **Contribution 1:** Three-level evaluation framework (plan, output, alignment)
\- **Contribution 2:** Cross-model comparison (sovereign, proprietary, open-weight)
\- **Scope:** IRT rescripting phase, isolated to eliminate stage-routing confounds

---

## 2 Background

Each section establishes one conceptual prerequisite for the methods and ends with an unresolved tension that motivates a specific design decision later. The chapter functions as integrated related work: literature is reviewed where it grounds a methodological choice, not collected in a standalone block.

**2.1 Imagery Rehearsal Therapy**

Defines what correct IRT delivery looks like as the clinical standard the model is evaluated against. Five-stage protocol (recording, rewriting, summary, rehearsal, final) with rescripting as the phase requiring active therapeutic strategy decisions. Reviews treatment fidelity instruments (ENACT, NIH BCC) that grade therapist adherence on a ternary scale: absent, partial, implemented → provides the scoring foundation for Method 3 (3.5.3). The strategy taxonomy scope (→ 3.4) derives from the space of legitimate rescripting moves.

**Tension:** Fidelity assessment exists for human therapists delivering manualized protocols. No equivalent exists for LLM-based agents.

**2.2 Large Language Models in Healthcare**

Grounds the general-vs-protocol distinction from 1.2 in the clinical literature. Treatment fidelity research (Webb et al., 2010; Waltz et al., 1993) formalises adherence (doing the prescribed things) and competence (doing them well). For rule-based chatbots, adherence is built in by construction. For LLM-based protocol agents, adherence becomes probabilistic and must be measured across runs, not assumed from a single review. Establishes that stability is a necessary precondition for clinical deployment, not a byproduct of capability: a model can produce high-quality individual responses while being clinically unreliable across sessions. Reviews documented failure modes (hallucination, strategy drift, stage confusion, persona inconsistency), each mapping to one evaluation method in → 3.5. Regulatory framing: EU AI Act high-risk classification, sovereignty as a legal constraint (→ 3.6).

**Tension:** Stability is a deployment precondition, but no existing evaluation framework measures it for protocol-driven LLM agents.

**2.3 Stochastic Behaviour in Language Models**

Makes "drift" mechanistically concrete. At T>0, token selection is probabilistic and small per-token variance compounds across a full therapeutic response through autoregressive cascading. Clinical consequence: the same patient on two different days may receive strategically inconsistent care. Reviews prior stability work targeting factual consistency or output diversity, not therapeutic strategy stability or protocol adherence.

**Tension:** The mechanical source of instability is well understood, but its impact on structured therapeutic decision-making has not been quantified → justifies the temperature conditions in 3.7.

**2.4 Evaluation Metrics for Text Generation**

Surveys the metric landscape and rules out alternatives. BLEU/ROUGE penalise valid therapeutic paraphrasing (surface overlap fails when stylistic variation is legitimate). BERTScore (Zhang et al., 2020) captures semantic equivalence independent of surface form, with DeBERTa-XLarge-MNLI showing the highest human correlation (r = 0.778) through NLI fine-tuning → grounds Method 2 (3.5.2). LLM-as-judge can assess criteria no scalar metric captures (e.g. "does this response implement a confrontation strategy?") but introduces known biases (self-preference, position, verbosity) → mitigated in Method 3 (3.5.3) through cross-model judging, deterministic decoding, and transparent rubrics.

**Tension:** Embedding similarity captures semantic equivalence but cannot assess strategic intent. LLM judges can assess intent but introduce their own reliability concerns. No single metric covers what clinical stability requires.

**2.5 Chain-of-Thought and Plan Faithfulness**

Addresses a conceptual problem that must be resolved before the plan mechanism can be introduced. CoT prompting (Wei et al., 2022) improves output structure, but the faithfulness literature (Turpin et al., 2023; Lanham et al., 2023) shows that CoT explanations often do not reflect actual computation. The spectrum runs from faithful step-by-step reasoning to pure post-hoc rationalisation.

**Tension:** If a model declares its therapeutic strategy before responding, that declaration may not reflect its actual decision-making. Measuring strategy consistency would then capture surface declarations, not real decisions. This must be resolved before any plan-based evaluation can be designed → resolved in 3.4 through the declared-intent framing.

---

## 3 Methods

The architecture decouples dialogue generation from stability evaluation so that any measured instability is attributable to the model under test, not to upstream context differences. Frozen conversation histories provide identical entry points for every trial. The plan mechanism resolves the faithfulness tension from the background by framing strategy declarations as declared intent rather than a window into model cognition. Three evaluation methods target distinct layers of the generation process, each addressing one dimension of the multi-metric gap identified in 2.4.

**3.1 System Overview and Design Rationale**

Two decoupled stacks: generation (dialogue creation) and evaluation (stability measurement). Decoupling prevents generation-side randomness from contaminating stability measurement. Data flow: vignettes → generation → frozen histories → evaluation → aggregation.

**3.2 Dialogue Generation**

Three-agent loop: patient (BDI-profiled vignette), router (stage classifier), therapist (stage-appropriate response). Six vignettes (anxious, avoidant, cooperative, resistant, skeptic, trauma) covering the range of clinical presentation difficulty. Full five-stage IRT traversal (grounded in 2.1) produces naturalistic conversation histories used as frozen evaluation entry points.

**3.3 Evaluation Design**

Frozen conversation histories as deterministic entry points. Conversations sliced at rewriting-turn boundaries: slice_1, slice_2, slice_3. Each slice is identical across all trials and all models. Three depths test whether stability changes as therapeutic context accumulates. Router bypassed in evaluation, rescripting prompt injected directly (isolates therapist model from stage-classification error). Fused generation: `<plan>` block declaring 1-2 strategies, then therapeutic response conditioned on that declaration. 10 independent trials per condition sample the stochastic output distribution (C(10,2) = 45 pairwise comparisons).

**3.4 Plan Mechanism and Strategy Taxonomy**

Resolves the CoT faithfulness tension from 2.5. The `<plan>` block is framed as declared intent, not a reasoning trace. Valid measurement target regardless of whether it reflects internal computation, because variable declarations predict variable clinical responses either way. Enables three downstream uses: strategy-level consistency scoring (Method 1), plan-output alignment verification (Method 3), and human-readable clinical oversight. Fixed strategy taxonomy constrains declarations to the therapeutic domain. Taxonomy scope derives from the space of legitimate rescripting moves (grounded in 2.1). Iterative revision driven by observed distribution failures: v1 (8 categories, 87.7% skew on empowerment/mastery), v2 (merge to agency, 100% dominance), v3 (mechanism-level split distinguishing external action from internal transformation). Final 7 categories: confrontation, self_empowerment, safety, cognitive_reframe, emotional_regulation, social_support, sensory_modulation.

**3.5 Evaluation Metrics**

Three methods, each targeting a distinct layer, addressing the multi-metric gap from 2.4. Method 1: does the model make consistent therapeutic decisions? (planning layer). Method 2: does the model produce consistent therapeutic responses? (output layer). Method 3: does the model do what it says it will do? (alignment layer).

**3.5.1 Method 1: Cognitive Stability (Plan Consistency)**
\- Pairwise Jaccard similarity over strategy sets from `<plan>` blocks, mean over C(10,2) = 45 trial pairs. Validity rate as upstream quality gate. Set similarity is appropriate for unordered strategy combinations.

**3.5.2 Method 2: Output Consistency (Semantic Stability)**
\- Pairwise BERTScore F1, DeBERTa-XLarge-MNLI. NLI fine-tuning aligns with semantic equivalence, highest WMT16 human correlation (grounded in 2.4). Surface metrics ruled out because therapeutic paraphrasing is the norm.

**3.5.3 Method 3: Plan-Output Alignment**
\- LLM judge (cross-family, T=0.0) with ternary scoring per declared strategy: 0 = absent, 1 = partial, 2 = implemented. Ternary scale borrowed from clinical fidelity literature (ENACT, NIH BCC, grounded in 2.1). NLI cross-encoders rejected (F1 ceiling ~0.55, no reasoning trace). Mitigations for known biases (from 2.4): cross-model judging (judge never evaluates its own family), CoT justification, deterministic decoding, transparent rubric. Judge reliability is itself an open question (discussed in 6.4).

**3.6 Model Selection**

EU data sovereignty as primary criterion for the primary subject, a legal constraint grounded in 1.2.
\- **Primary subject:** Mistral Large 3 (675B MoE, 41B active, EU-sovereign, Apache 2.0)
\- **Proprietary ceiling:** upper bound on achievable stability
\- **Open-weight comparators:** size-class and provider diversity

**3.7 Experimental Conditions**

Full factorial: 6 vignettes x 3 slices x 10 trials x 2 temperatures x N models. T=0.0 as deterministic upper bound on stability (grounded in 2.3). T=0.7 as realistic clinical deployment range.

**3.8 Statistical Analysis**

Descriptive statistics: means, standard deviations, confidence intervals across 45 trial pairs per condition. Bootstrap 95% confidence intervals for model comparisons. Spearman rank correlations for cross-method analysis (5.5).

---

## 4 Implementation

Translates the methods into a concrete system. Engineering decisions follow directly from experimental requirements: parallel execution for the factorial design, strict validation to prevent malformed plan blocks from corrupting downstream metrics, and provider abstraction for model-agnostic evaluation.

**4.1 Software Architecture**
\- Python async pipeline, YAML-driven config, Pydantic validation at every data boundary. Provider abstraction (OpenRouter, Google, Mistral API) enables model swaps without changing evaluation logic.

**4.2 Experiment Execution and Aggregation**
\- Config-driven orchestration with parallel trial execution. Artefacts per run: config, frozen history (irreplaceable), trials, metrics, judgments (recomputable). Cross-condition alignment into a single analysis frame indexed by model, vignette, slice, and temperature. Required for the cross-method analysis in → 5.5.

---

## 5 Results

Results are reported per method before examining how the three levels relate. The central questions are whether plan consistency and output consistency are coupled or decoupled, which models and patient profiles show the highest and lowest stability, and whether accumulating therapeutic context helps or hurts consistency. Divergence cases where one method shows high stability while another does not reveal different types of clinical risk that no single metric could detect.

**5.1 Plan Validity and Strategy Distribution**
\- Validity rates across models and temperatures as quality gate. Strategy frequency distribution, expected vs. observed per vignette.

**5.2 Cognitive Stability (Method 1)**
\- Jaccard scores by model, vignette, temperature, slice. Stochastic cost: T=0.0 vs. T=0.7. Context depth effect across slices.

**5.3 Output Consistency (Method 2)**
\- BERTScore F1 across all conditions. Coupling question: does stable planning predict stable output?

**5.4 Plan-Output Alignment (Method 3)**
\- Alignment scores by model and vignette. Per-strategy scoring distributions (absent / partial / implemented).

**5.5 Cross-Method Analysis**
\- Correlations across all three levels. Divergence cases and what they reveal about model behaviour. Per-model stability profiles. Effect of conversation depth.

---

## 6 Discussion

The discussion interprets the three-level framework as a diagnostic tool: different divergence patterns between methods indicate different sources of instability, and localising whether the problem originates in planning, output generation, or the coupling between them has direct implications for mitigation. The cross-model comparison addresses the sovereignty question from the introduction. Temperature effects have direct deployment implications.

**6.1 Interpreting the Three-Level Framework**
\- Three methods as diagnostic tool for locating instability sources. Divergence patterns map to different types of clinical risk. Vignette-dependent behaviour: which patient profiles challenge consistency most, implications for deployment safety.

**6.2 Cross-Model Comparison**
\- Does Mistral Large match the proprietary ceiling on stability? Does self-hostability come at a stability cost? Size-class effects across the model range. Stability as a dimension independent of capability.

**6.3 Temperature and Clinical Deployment**
\- Greedy decoding as upper bound. Which models degrade most under stochastic sampling? Practical deployment recommendations.

**6.4 Evaluation Framework Reflections**
\- Taxonomy sensitivity: how category design shapes measured consistency. Declared-intent framing: what it enables and what it cannot claim about model cognition. Method 3 limitations: judge reliability, cross-family mitigation effectiveness. Ethical considerations: IRT as lower-risk entry point (no diagnosis) but stability as necessary precondition for safe deployment. Generalisability to CBT, DBT, other manualized protocols.

**6.5 Toward Systematic Computational Evaluation**
\- Framework as reusable validation template for protocol-driven AI agents. What stability testing can certify vs. what it cannot replace. Computational evaluation complements but does not substitute clinical validation.

---

## 7 Conclusion

Answers the research question directly across all three evaluation levels. Acknowledges key limitations (single protocol phase, synthetic patients, Method 3 judge reliability, fixed taxonomy). Outlines future extensions to other manualized therapies, longitudinal version drift, multi-language evaluation for reDreamAI, and clinical validation with human therapist ratings.

**7.1** Summary of Findings
**7.2** Limitations
**7.3** Future Work

---

## Appendices

**A** Strategy Taxonomy: full 7-category definitions with revision history
**B** Prompts: fused plan+response system prompt, judge prompt and rubric, patient vignette profiles
**C** Architecture Diagrams: pipeline, three-level framework, three-agent loop
**D** Supplementary Results: full per-condition metric tables
