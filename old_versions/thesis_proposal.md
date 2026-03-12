## **Measuring Drift in Therapeutic AI:**  **A Stability-Based Evaluation of Sovereign LLMs in Nightmare Therapy**

**Author:** Daniel Menzel
**Supervisors:** Moritz Hartstang, Sebastian Musslick
**Date:** January 2026
**Institution:** Institute of Cognitive Science, University of Osnabrück

### **1\. Introduction**

Nightmare disorder affects approximately 5% of the general population and is highly comorbid with PTSD and depression. Its gold-standard treatment, Imagery Rehearsal Therapy (IRT), relies on a structured protocol involving psychoeducation, rescripting, and rehearsal. However, widespread implementation is constrained by clinician shortages.

Scalable AI interventions such as the reDreamAI project offer a potential solution but face regulatory and practical tension. General-purpose models (frontier proprietary LLMs) often demonstrate strong reasoning and conversational capabilities, yet their deployment can conflict with European data protection and sovereignty requirements. In contrast, EU-sovereign models such as Mistral Large 3 (675B MoE, 41B active, Apache 2.0) satisfy regulatory constraints but currently lack validated clinical efficacy. Moreover, standard NLP benchmarks are insufficient for such validation, as they do not assess properties critical for psychotherapy applications, including intent stability under stochastic variation, protocol adherence, and consistent persona behaviour.

### **2\. Research Objectives**

This thesis aims to validate an automated evaluation framework for sovereign LLM-based therapy. The primary objective is to quantify the clinical reasoning stability of Mistral Large 3, an EU-sovereign model, compared to proprietary baselines and open-weight models across size classes. The central question is whether a sovereign model achieves comparable therapeutic stability to proprietary systems, not merely comparable general-purpose benchmark scores.

The scope of the study isolates the Imagery Rescripting Phase (the cognitive core of IRT) to evaluate reasoning stability independent of conversation management tasks (the stage router).

### **3\. Methodology**

To ensure reproducibility, this study employs a "frozen history" experimental design, wherein models receive identical patient histories up to the point of intervention. Performance is assessed via a hierarchical framework consisting of three distinct levels of evaluation.

| Level / Focus | Rationale & Protocol | Primary Metric |
| :---- | :---- | :---- |
| **3.1 Cognitive Stability** *(Plan Consistency)* | **Rationale:** Clinical reliability necessitates stable therapeutic strategies rather than stochastic randomness. **Protocol:** The model generates a structured plan (a `<plan>` block declaring 1-2 strategies from the IRT Strategy Taxonomy) followed by a therapeutic response in a single Chain-of-Thought call across multiple independent trials per patient vignette at varying temperatures. Strategy sets are extracted and compared pairwise. | **Mean Pairwise Jaccard Similarity (0.0-1.0)** over all trial pairs. Plan validity rate as quality gate. |
| **3.2 Output Consistency** *(Semantic Stability)* | **Rationale:** Execution stability is measured independently of declared plans to detect behavioural drift. **Protocol:** BERTScore (DeBERTa-XLarge-MNLI) F1 computes pairwise semantic similarity across all trial response texts per condition, quantifying whether stochastic sampling produces therapeutically equivalent responses. | **Mean Pairwise BERTScore F1** across all trial pairs per condition. |
| **3.3 Plan-Output Alignment** *(Exploratory)* | **Rationale:** Instruction adherence is assessed by comparing declared strategies against executed interventions. **Protocol:** exploring fixed DeepSeek-V3.2 version with T=0.0 or SetFit for categorization. Each declared strategy is scored on a ternary scale: 0 = absent, 1 = partial, 2 = implemented. | **Alignment Score** per strategy, grounded in a ternary clinical fidelity scale. |

### **4\. Experimental Design**

The experimental subject is Mistral Large 3 (675B MoE, 41B active), an EU-sovereign, Apache 2.0 model from Mistral (France). It is compared against proprietary baselines and open-weight models across size classes. The dataset consists of 6 patient vignettes generated via Belief-Desire-Intention (BDI) profiling, representing diverse clinical presentations such as resistant patients or those exhibiting trauma-dumping behaviours. Each vignette produces frozen conversation histories sliced at rewriting-turn boundaries, yielding evaluation at different depths within the rescripting phase.

### **5\. Significance**

This research provides a quantitative assessment of EU-sovereign models in protocol-driven therapy. The proposed three-level evaluation framework establishes a methodology for automated "in silico clinical trials," decomposing therapeutic AI reliability into cognitive stability, output consistency, and plan-output alignment. The framework generalises beyond the specific sovereign-vs-proprietary comparison to any structured therapeutic protocol, contributing a reusable evaluation approach for the safety-critical validation of medical AI systems.
