Thesis Outline - Table of Contents
Measuring Drift in Therapeutic AI: A Stability-Based Evaluation of Sovereign LLMs in Nightmare Therapy
Abstract
	…

1 Introduction
1.1 Nightmare Disorder and Imagery Rehearsal Therapy
- IRT as gold-standard; AI as a solution to clinician shortages.
1.2 AI-Assisted Psychotherapy
- Protocol-driven agents vs. general AI; regulatory constraints (EU AI Act).
1.3 The Evaluation Gap
- Lack of metrics for intent stability and clinical protocol adherence.
1.4 Research Objectives
- RQ: Measuring LLM reasoning consistency via a three-level framework.

2 Background
2.1 Imagery Rehearsal Therapy
- Rescripting as the core cognitive mechanism of the IRT protocol.
2.2 Large Language Models in Healthcare
- Risks of drift and inconsistency in high-stakes clinical settings.
2.3 Stochastic Behaviour in Language Models
- Variance under temperature scaling; reproducibility challenges.
2.4 Evaluation Metrics for Text Generation
- Transition from traditional metrics to BERTScore and LLM-as-judge.
2.5 Chain-of-Thought and Plan Faithfulness
- Planning as a consistency mechanism vs. post-hoc rationalisation.
3 Methods
3.1 System Overview
- Decoupled stacks: generation (dialogue) and evaluation (stability).
3.2 Dialogue Generation
- Three-agent loop testing six BDI-profiled patient vignettes.
3.3 Frozen History Design
- Deterministic slicing to evaluate consistency at varying depths.
3.4 Evaluation Stack
- Fused CoT generation across 10 independent stochastic trials.
3.5 The Plan Mechanism
- Using declared intent as a stable metric for clinical oversight.
3.6 Strategy Taxonomy Development
- Iterative creation of a 7-category taxonomy for IRT strategies.
3.7 Evaluation Metrics
3.7.1 Method 1 - Cognitive Stability (Plan Consistency)
- Jaccard similarity over strategy sets (therapeutic decision stability).
3.7.2 Method 2 - Output Consistency (Semantic Stability)
- BERTScore F1 (DeBERTa) to measure semantic equivalence.
3.7.3 Method 3 - Plan-Output Alignment (Exploratory)
- Ternary LLM-judge scoring for strategy implementation fidelity.

3.8 Model Selection
- Sovereign (Mistral) vs. Proprietary (GPT) and open-weight peers.
3.9 Experimental Conditions
- Multi-dimensional testing: models, vignettes, slices, and temperatures.

4 Implementation
4.1 Software Architecture
- Python async pipeline with multi-provider abstraction (OpenRouter/Google).
4.2 Experiment Execution
- Config-driven orchestration of parallel multi-trial sampling.
4.3 Aggregation Pipeline
- Result collection across models, vignettes, and temperature states.
5 Results
5.1 Plan Validity and Strategy Distribution
- Strategy frequency and validity rates across vignettes.
5.2 Cognitive Stability (Method 1)
- Impact of temperature (T=0.7) on decision consistency.
5.3 Output Consistency (Method 2)
- Semantic stability trends and cross-model benchmarks.
5.4 Plan-Output Alignment (Method 3)
- Execution fidelity of declared plans via judge analysis.
5.5 Cross-Method Analysis
- Correlation between planning stability and semantic drift.
6 Discussion
6.1 Cross-Model Comparison
- Sovereignty dimension: efficiency vs. stability in self-hostable models.
6.2 Temperature and Therapeutic Stability
- Clinical recommendations for deployment temperature settings.
6.3 Vignette-Dependent Behaviour
- Stability variance across different patient clinical presentations.
6.4 Evaluation Framework Reflections
- Impact of taxonomy design on measured therapeutic drift.
6.5 Toward In Silico Clinical Trials
- Regulatory implications for automated stability certification.
7 Conclusion
7.1 Summary
- Synthesis of findings and final answer to the research question.
7.2 Limitations
- Synthetic simulation constraints and judge reliability factors.
7.3 Future Work
- Multi-language expansion and RAG-based guardrail integration.
References
…

Appendices
A Strategy Taxonomy
- Definitions of the 7-category strategy framework.
B Prompts
- System instructions, judge rubrics, and vignette profiles.
C Architecture Diagrams
…
D Supplementary Results
- Full per-experiment metric table


Complete Pipeline


Three Level Evaluation


