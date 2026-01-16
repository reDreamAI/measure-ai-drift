## **Measuring Drift in Therapeutic AI:**  **A Stability-Based Evaluation of Sovereign LLMs in Nightmare Therapy**

**Author:** Daniel Menzel  
**Supervisors:** Moritz Hartstang, Sebastian Musslick  
**Date:** January 2026  
**Institution:** Institute of Cognitive Science, University of Osnabrück

### **1\. Introduction**

Nightmare disorder affects approximately 5% of the general population and is highly comorbid with PTSD and depression. Its gold-standard treatment, Imagery Rehearsal Therapy (IRT), relies on a structured protocol involving psychoeducation, rescripting, and rehearsal; however, widespread implementation is constrained by clinician shortages. 

Scalable AI interventions such as the reDreamAI project offer a potential solution but face regulatory and practical tension. General-purpose models (frontier proprietary LLMs) often demonstrate strong reasoning and conversational capabilities, yet their deployment can conflict with European data protection and sovereignty requirements. In contrast, EU-sovereign or self-hostable models (e.g., Mistral Small 3.2) satisfy regulatory constraints but currently lack validated clinical efficacy. Moreover, standard NLP benchmarks are insufficient for such validation, as they do not assess properties critical for psychotherapy applications, including intent stability under stochastic variation, protocol adherence and consistent persona behavior.

### **2\. Research Objectives**

This thesis aims to validate an automated evaluation framework for a part of a sovereign LLM stack in the context of psychotherapy. The primary objective is to quantify the clinical reasoning capabilities and consistency of Mistral Small 3.2 (24B) compared to industry baselines and models with similar size. The scope of the study isolates the Imagery Rescripting Phase (the cognitive core of IRT) to evaluate reasoning performance independent of conversation management tasks (the stage router).

### **3\. Methodology**

To ensure reproducibility, this study employs a "frozen history" experimental design, wherein models receive identical patient histories up to the point of intervention. Performance is assessed via a hierarchical framework consisting of three distinct levels of evaluation.

| Level / Focus | Rationale & Protocol | Primary Metric |
| :---- | :---- | :---- |
| **3.1 Cognitive Stability** *(Internal Consistency)* | **Rationale:** Clinical reliability necessitates stable strategies rather than stochastic randomness. **Protocol:** The model generates an internal plan (short \<plan\> instead of  CoT) across \~10 independent trials per patient vignette and temperature t=0 and t=0.7. These plans are subsequently classified into a standardized 8-item IRT Strategy Taxonomy. | **Consistency of Plan Set (0.0 – 1.0)** Quantifies Mean Jaccard across therapeutic plans across stochastic runs, measuring the clinical stability |
| **3.2 Output Consistency** *(Semantic Stability)* | **Rationale:** Execution stability is measured independently of declared plans to detect behavioral drift. **Protocol:** BERTScore (DeBERTa-XLarge-MNLI) F1 computes pairwise semantic similarity across all 10 trial outputs per vignette, quantifying whether stochastic sampling produces therapeutically equivalent responses. | **Execution Fidelity (%)** Mean BertScore F1 across all pairwise output comparison |
| **3.3 Exploratory:Plan-OutputAlignment** *(Intervention fit to Plan)* | **Rationale:** Instruction adherence assessed by comparing declared strategies against executed interventions \-\> does output fit the plan categories **Protocol:** exploring fixed DeepSeek-V3.2 version with t=0 or SetFit for categorization | **Alignment score** Scoring board to check whether the  categories fit the plans: Yes/Partially/No |

#### 

### **4\. Experimental Design**

The experimental subject is the Mistral Small 3.2 (24B) model, which will be compared against GPT-5 and potentially models closer in size like gpt-oss-20B, Llama 3.3 (70B), Qwen 3 (32B), and Gemma 3 (27B). The dataset consists of 6 Patient Vignettes generated via Belief-Desire-Intention (BDI) profiling, representing diverse clinical presentations such as resistant patients or those exhibiting trauma-dumping behaviors. 

### **5\. Significance**

This research provides a quantitative assessment of EU-sovereign models in protocol-driven therapy. The proposed Tri-Level Evaluation Framework establishes a robust methodology for "In Silico Clinical Trials," enabling the automated, safety-critical validation of medical AI systems required for regulatory certification.