# Plan-Output Alignment: Approach Analysis

## Purpose

Level 3.3 of the evaluation framework measures whether the therapist model's response actually implements the strategies it declared in its `<plan>` block. Where Level 3.1 (Jaccard) measures plan consistency and Level 3.2 (BERTScore) measures response consistency, Level 3.3 closes the loop: does the model do what it said it would?

This is an exploratory metric. The thesis proposal frames it as "intervention fit" — a measure of instruction adherence rather than self-awareness. The plan is a declared intent mechanism (see `plan_mechanism_analysis.md`), and alignment scoring tests whether the model follows its own declared intent when generating a therapeutic response.

## Scoring Scale: Ternary (0 / 1 / 2)

### Why not binary?

Binary (yes/no) scoring discards quality information. A response that mentions empowerment in passing and one that builds an entire therapeutic intervention around empowerment would both score "yes". In treatment fidelity research, binary scales consistently underestimate fidelity variance and reduce statistical power for detecting differences across conditions.

### Why not 5- or 7-point?

The Cognitive Therapy Rating Scale (CTRS) uses 7-point scales but requires expert raters with extensive training. For non-specialist raters — and by extension, for LLM judges — finer scales introduce noise without adding reliable signal. The ENACT scale (Enhancing Assessment of Common Therapeutic Factors), designed specifically for non-specialist treatment fidelity rating, uses a 3-point scale.

### The ternary scale

The scoring rubric uses three levels with concrete anchoring:

- **2 (implemented)**: The response clearly and specifically implements this strategy. The therapeutic technique is evident and developed — specific sentences or passages demonstrate it.
- **1 (partial)**: The response touches on this strategy but does not fully develop it. Elements are present but incomplete, only implied, or mentioned without therapeutic depth.
- **0 (absent)**: The response does not implement this strategy. No evidence of this technique in the response.

Per-trial alignment is computed as the mean score across declared strategies, normalised to 0.0-1.0 (i.e., divided by 2). Experiment-level alignment is the mean across trials.

### Clinical literature supporting ternary scales

- **ENACT** (Kohrt et al., 2015): 3-point scale for non-specialist treatment fidelity assessment — "needs improvement" / "done partially" / "done well". Designed for contexts where expert raters are unavailable.
- **NIH Behavioral Change Consortium** (Bellg et al., 2004): Treatment fidelity framework recommending ternary assessment for intervention delivery components.
- **Likert or Not** (arXiv:2505.19334): Binary scoring significantly underperforms ordinal scales in LLM evaluation tasks. Named categories with clear qualitative descriptions produce more stable ratings than numeric ranges.

## Approach: LLM-Based Zero-Shot Classification

The alignment check uses a fixed LLM judge (Gemini Flash at t=0.0) performing zero-shot classification against the strategy taxonomy. Each declared strategy is independently scored using the ternary rubric.

### Why LLM classification rather than NLI cross-encoders?

Natural Language Inference (NLI) models — the standard approach for textual entailment — were considered but rejected based on recent benchmarking evidence.

The BTZSC benchmark (Aarab, ICLR 2026) evaluates zero-shot text classification across NLI-based models, rerankers, and LLMs. Key findings:

- NLI cross-encoder performance plateaus with scale (F1 ~0.55-0.60), regardless of model size.
- Rerankers (e.g., Qwen3-Reranker-8B) reach F1 ~0.72 using instruction-aware binary relevance scoring.
- Commercial LLMs achieve F1 ~0.86+ on zero-shot classification, significantly outperforming both alternatives.

Our task is closer to zero-shot classification than entailment: given a strategy definition and a response, does the response implement the strategy? LLMs handle this well because they can reason about therapeutic content rather than relying on surface-level textual overlap.

### Why not rerankers?

Qwen3-Reranker-8B achieves SOTA on BTZSC (F1=0.72) and could serve as a local, deterministic alternative. However:

1. It requires a model download and GPU inference infrastructure, adding deployment complexity.
2. Its binary yes/no relevance scoring loses the ternary signal that distinguishes partial from full implementation.
3. The performance gap vs. LLMs (0.72 vs. 0.86+) is substantial.

Rerankers remain a viable future extension, particularly if a local, cost-free judge is needed for large-scale evaluation.

## Mitigations for Known LLM-Judge Weaknesses

LLM-as-judge approaches have well-documented failure modes. The design incorporates four mitigations:

### 1. Cross-model evaluation

Generation uses Llama 70B (via Groq), judgment uses Gemini Flash (via Google AI Studio). Using different model families avoids self-preference bias — the tendency for models to rate their own outputs higher (Panickssery et al., EMNLP 2025).

### 2. Chain-of-thought justification

The judge outputs reasoning before the score for each strategy. This improves alignment with human judgments and provides an auditable trace. The reasoning is saved in `judgments.json` for manual inspection.

### 3. Deterministic judging

The judge runs at t=0.0 (greedy decoding), eliminating stochastic variance in the judge itself. All variance in alignment scores comes from the therapist's stochastic responses, not from judge inconsistency.

### 4. Transparent rubric

The full judge prompt is published as a YAML file (`alignment_judge.yaml`) and referenced as an appendix in the thesis. The rubric uses concrete anchoring (specific criteria for each score level) rather than vague labels, following the RULERS framework for LLM evaluation prompts (arXiv:2601.08654).

## Implementation

The alignment metric integrates into the existing evaluation pipeline:

- `compute_alignment()` in `src/evaluation/metrics.py` handles judge calls and score parsing.
- The judge prompt is loaded from `data/prompts/evaluation/alignment_judge.yaml`.
- Strategy definitions are injected from the existing `strategy_taxonomy.yaml`.
- Results appear as `alignment_mean` in `metrics.json` alongside Jaccard and BERTScore.
- Raw judge outputs (reasoning + scores) are saved to `judgments.json` for transparency.

The judge model is config-driven: swapping from Gemini Flash to any other model requires only a `models.yaml` change.

## References

- Aarab, C. (2026). BTZSC: A Benchmark for Zero-Shot Text Classification. *ICLR 2026*.
- Bellg, A. J., et al. (2004). Enhancing Treatment Fidelity in Health Behavior Change Studies. *Health Psychology*, 23(5), 443-451.
- Kohrt, B. A., et al. (2015). The Role of Communities in Mental Health Care in Low- and Middle-Income Countries: A Meta-Review. *BMC Health Services Research*, 15, 347.
- Panickssery, A., et al. (2025). LLM Evaluators Recognize and Favor Their Own Generations. *EMNLP 2025*. https://arxiv.org/abs/2404.13076
- Zheng, B., et al. (2026). RULERS: Rubric-Based Evaluation for LLM Evaluators. *arXiv:2601.08654*.
