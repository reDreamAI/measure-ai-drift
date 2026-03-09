# Thesis Structure

**Measuring Drift in Therapeutic AI: A Stability-Based Evaluation of Sovereign LLMs in Nightmare Therapy**

Daniel Menzel
Institute of Cognitive Science, University of Osnabruck
Supervisors: Moritz Hartstang, Sebastian Musslick

---

## 1 Introduction

Imagery Rehearsal Therapy is a structured, manualized protocol for treating nightmare disorder, with rescripting as its cognitive core. The clinician shortage in this area has motivated scalable AI-assisted delivery, and the reDreamAI project provides the concrete deployment context: a consumer-facing IRT chatbot that guides users through all five protocol stages. Unlike a general-purpose assistant, where variability across sessions is acceptable, a protocol-driven therapeutic agent must make consistent strategic decisions, because inconsistency in a manualized intervention is not stylistic variation but a potential clinical failure. This distinction creates an evaluation problem: standard NLP benchmarks assess what a model can do, not whether it does the same thing reliably across repeated runs. At the same time, EU AI Act requirements and data sovereignty constraints push toward self-hosted, EU-resident models, which narrows the candidate set and raises the question of whether sovereign models can match proprietary ones on clinical reliability. The thesis contributes a three-level hierarchical evaluation framework that decomposes therapeutic stability into plan consistency, output consistency, and plan-output alignment, and applies it in a quantitative comparison across sovereign, proprietary, and open-weight model classes, scoped to the IRT rescripting phase as the highest-stakes intervention point.

### 1.1 Nightmare Disorder and Imagery Rehearsal Therapy
- ~5% prevalence, comorbidity with PTSD/depression
- IRT as evidence-based gold standard with rigid phase structure
- Rescripting as the cognitive core of the intervention
- Clinician shortage as motivation for scalable AI delivery

### 1.2 AI-Assisted Psychotherapy
- LLM deployment in mental health, from empathy tools to protocol agents
- reDreamAI as applied deployment context, not a research prototype
- General assistant vs. protocol agent: consistency is a clinical obligation, not optional
- EU AI Act and data sovereignty pushing toward self-hosted EU models

### 1.3 The Evaluation Gap
- Standard benchmarks measure capability, not reliability across runs
- No existing metrics for intent stability, protocol adherence, strategic consistency
- Prior therapeutic AI evaluation is qualitative, post-hoc, or single-session
- Case for systematic in silico clinical trials

### 1.4 Research Objectives
- RQ: How consistent is LLM clinical reasoning across stochastic runs in a structured therapeutic protocol?
- Contribution 1: three-level evaluation framework (plan, output, alignment)
- Contribution 2: cross-model comparison (sovereign, proprietary, open-weight)
- Scope: IRT rescripting phase, isolated to eliminate stage-routing confounds

---

## 2 Background

2.1 Imagery Rehearsal Therapy
2.2 Large Language Models in Healthcare
2.3 Stochastic Behaviour in Language Models
2.4 Evaluation Metrics for Text Generation
2.5 Chain-of-Thought and Plan Faithfulness

Each section establishes one conceptual prerequisite and ends with an open tension that the Methods chapter resolves. 2.1 defines what correct IRT delivery looks like. 2.2 grounds the distinction between general-purpose and protocol-driven AI agents. 2.3 explains where instability comes from mechanically. 2.4 surveys text similarity metrics and their limitations for therapeutic language. 2.5 addresses whether structured strategy declarations can be trusted as a measurement target, given the CoT faithfulness debate.

## 3 Methods

3.1 System Overview and Design Rationale
3.2 Dialogue Generation
3.3 Frozen History Design
3.4 Evaluation Stack
3.5 The Plan Mechanism
3.6 Strategy Taxonomy Development
3.7 Evaluation Metrics
    3.7.1 Method 1: Cognitive Stability (Plan Consistency)
    3.7.2 Method 2: Output Consistency (Semantic Stability)
    3.7.3 Method 3: Plan-Output Alignment (Exploratory)
3.8 Model Selection
3.9 Experimental Conditions

The core chapter. A two-stack architecture separates dialogue generation from stability evaluation. Frozen conversation histories provide deterministic entry points so that any measured instability is attributable to the model, not the context. The plan mechanism asks models to declare 1-2 therapeutic strategies from a fixed 7-category taxonomy before responding, framed as declared intent rather than a reasoning trace. Three evaluation methods target different layers: Jaccard similarity over strategy sets (planning), BERTScore F1 over responses (output), and LLM-judge alignment scoring (plan-to-output). The primary subject is Mistral Large 3 (EU-sovereign), compared against Gemini 3.1 Pro (proprietary ceiling) and open-weight models (Llama 3.3, Qwen 3, OLMo 3.1). Full factorial design: 6 vignettes, 3 slices, 10 trials, 2 temperatures.

## 4 Implementation

4.1 Software Architecture
4.2 Experiment Execution
4.3 Aggregation Pipeline

Translates the methods into a Python async pipeline with YAML-driven configuration, Pydantic validation, and multi-provider LLM abstraction -> focus on OpenRouter and Google AI Studio ofr simple and cheap pipeline. Describes the artefact structure and how cross-condition results are aggregated for analysis.

## 5 Results

5.1 Plan Validity and Strategy Distribution
5.2 Cognitive Stability (Method 1)
5.3 Output Consistency (Method 2)
5.4 Plan-Output Alignment (Method 3)
5.5 Cross-Method Analysis

Reports results for each evaluation method separately, then examines correlations across methods, divergence cases, per-model stability profiles, and the effect of conversation depth.

## 6 Discussion

6.1 Interpreting the Three-Level Framework
6.2 Cross-Model Comparison
6.3 Temperature and Clinical Deployment
6.4 Vignette-Dependent Behaviour
6.5 Evaluation Framework Reflections
6.6 Toward In Silico Clinical Trials

Interprets the three-level results as a diagnostic tool for locating instability sources. Compares Mistral Large against the proprietary ceiling and open-weight peers on the sovereignty-stability tradeoff. Examines temperature effects and vignette-dependent behaviour. Reflects on taxonomy sensitivity, the declared-intent framing, and generalisability to other manualized protocols. Positions the framework as a template for in silico clinical validation.

## 7 Conclusion

7.1 Summary of Findings
7.2 Limitations
7.3 Future Work

## Appendices

A Strategy Taxonomy
B Prompts
C Architecture Diagrams
D Supplementary Results
