# Experiment Analysis

> Key findings from 300 runs (10 models x 6 vignettes x 5 temperatures x 20 trials = 6,000 trials).
> Data: `experiments/latest/`, aggregated in `stats/data/experiment_runs.csv`.
> Generated 2026-03-24.

## Models tested

| Group | Model | Size | Active params |
|---|---|---|---|
| EU-sovereign | Mistral Small 3.2 | 24B dense | 24B |
| EU-sovereign | Mistral Small 4 | 119B MoE | 6.5B |
| EU-sovereign | Mistral Large 3 | 675B MoE | 41B |
| Open-weight | Qwen 3.5 27B | 27B dense | 27B |
| Open-weight | Qwen 3.5 122B | 122B MoE | 10B |
| Open-weight | Qwen 3.5 397B | 397B MoE | 17B |
| Open-weight | OLMo 3.1 32B | 32B dense | 32B |
| Open-weight | Llama 3.3 70B | 70B dense | 70B |
| Proprietary | GPT-5.4 | closed | closed |
| Proprietary | Claude Sonnet 4.6 | closed | closed |

## Temperature scale

[0.0, 0.075, 0.15, 0.3, 0.6]. All models tested at all 5 points. T=0.075 added after initial 4-point run revealed Mistral peaks between 0.0 and 0.15.

## Jaccard (strategy consistency) by model and temperature

| Model | T=0.0 | T=0.075 | T=0.15 | T=0.3 | T=0.6 |
|---|---|---|---|---|---|
| Mistral Small 3.2 (24B) | 1.000 | 1.000 | 1.000 | 1.000 | 0.933 |
| Mistral Small 4 (119B) | 0.722 | 1.000 | 0.933 | 0.652 | 0.614 |
| Mistral Large 3 (675B) | 0.933 | 1.000 | 1.000 | 0.933 | 0.652 |
| Qwen 3.5 27B | 0.763 | 0.667 | 0.726 | 0.526 | 0.452 |
| Qwen 3.5 122B | 1.000 | 1.000 | 0.933 | 0.844 | 0.726 |
| Qwen 3.5 397B | 0.867 | 0.778 | 0.711 | 0.674 | 0.622 |
| OLMo 3.1 32B | 1.000 | 1.000 | 0.881 | 0.881 | 0.696 |
| Llama 3.3 70B | 0.756 | 0.881 | 0.778 | 0.674 | 0.652 |
| GPT-5.4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| Claude Sonnet 4.6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

## Statistical tests

All tests exploratory. Effect sizes reported alongside p-values.

### Temperature effect (pooled)

- Jaccard vs temperature: rho=-0.228, p<0.001. Higher temperature reduces strategy consistency.
- BERTScore vs temperature: rho=-0.486, p<0.001. Stronger effect on semantic wording than strategy choice.
- Alignment vs temperature: rho=-0.053, p=0.361. **Not significant.** Models implement chosen strategies equally well regardless of temperature.

### Temperature effect (per-model Spearman)

| Model | rho | p | Significant? |
|---|---|---|---|
| Mistral Small 3.2 | -0.190 | 0.315 | No |
| Mistral Small 4 | -0.196 | 0.299 | No |
| Mistral Large 3 | -0.277 | 0.139 | No |
| Qwen 3.5 27B | -0.576 | 0.001 | Yes |
| Qwen 3.5 122B | -0.513 | 0.009 | Yes |
| Qwen 3.5 397B | -0.232 | 0.217 | No |
| OLMo 3.1 32B | -0.632 | <0.001 | Yes |
| Llama 3.3 70B | -0.153 | 0.421 | No |
| GPT-5.4 | +0.075 | 0.695 | No |
| Claude Sonnet 4.6 | -0.063 | 0.741 | No |

Temperature-sensitive: OLMo, Qwen 27B, Qwen 122B.
Temperature-robust: all Mistrals, Llama, Qwen 397B, GPT-5.4, Sonnet.

### Model differences

- Jaccard: p<0.001 (Kruskal-Wallis). Models differ significantly.
- BERTScore: p<0.001.
- Alignment: p<0.001.

### Vignette effect

- Jaccard: p=0.007. Some vignettes are harder than others.
- BERTScore: p=0.015.

### Metric correlations

- Jaccard vs BERTScore: rho=0.560, p<0.001. Moderate. Related but distinct dimensions.
- Jaccard vs Alignment: rho=0.285, p<0.001. Weak.
- BERTScore vs Alignment: rho=0.376, p<0.001. Weak-moderate.

## Key findings

### 1. Four stability tiers

1. **Temperature-immune:** GPT-5.4, Sonnet 4.6. J=1.000 at all temperatures. Proprietary character/safety training creates stability that sampling temperature cannot disrupt.
2. **Temperature-robust:** Mistral family, Llama, Qwen 397B. No statistically significant degradation. Peaks at low temperatures, gentle decline.
3. **Temperature-sensitive:** OLMo, Qwen 122B. High peak at T=0.0, significant degradation as temperature increases.
4. **Consistently variable:** Qwen 27B. Lower baseline, significant degradation. Smallest model in the set.

### 2. T=0.0 is not optimal for all models

Mistral Small 4 scores J=0.722 at T=0.0 but J=1.000 at T=0.075. Deterministic decoding is actively harmful for this model. A tiny amount of sampling variance produces more consistent therapeutic strategy selection than pure greedy decoding. This pattern holds for Mistral Large (0.933 to 1.000) and Llama (0.756 to 0.881).

### 3. T=0.075 as a universal sweet spot

Most medium-to-large models achieve their peak or near-peak Jaccard at T=0.075. Models that do not benefit (Qwen 27B, Qwen 397B) are either too small to show the effect or already operate differently at that scale.

### 4. Alignment is temperature-independent

Models do not get worse at implementing strategies as temperature rises. They pick *different* strategies more often (lower Jaccard) but implement whichever strategies they pick equally well (stable alignment). The instability is in *decision-making*, not *execution*.

### 5. Vignette difficulty matters

Significant vignette effect (p=0.007). Some patient profiles produce more consistent therapeutic responses than others. Worth investigating per-vignette patterns in the heatmaps.

### 6. BERTScore is insensitive to plan-level instability

BERTScore correlates with Jaccard (rho=0.560) but measures a different, shallower dimension. The slice depth analysis confirms this: across conversation depths, Jaccard varies visibly (deeper slices anchor strategy choice) while BERTScore stays flat. The model produces semantically similar therapeutic text regardless of which strategies it picks. Swapping "confrontation" for "cognitive reframe" changes the plan but not the response surface enough for BERTScore to detect it.

This means BERTScore captures response *style* consistency, not decision *content* consistency. It serves as a sanity check (if BERTScore were low, the model would be generating erratic text) but does not distinguish between clinically different plans. The real signal for therapeutic stability lives in Jaccard (strategy decisions) and Alignment (plan-response coherence). Discuss this limitation in Ch6.

## Figures

| Figure | Description | File |
|---|---|---|
| 5.1 | Strategy distribution by model | `fig_5_1_strategy_distribution` |
| 5.2 | Jaccard + modal-set by temperature (line plots) | `fig_5_2_jaccard` |
| 5.3 | BERTScore by temperature (line plot) | `fig_5_3_bertscore` |
| 5.4 | Vignette heatmaps per temperature | `fig_5_4_vignette_slice` |
| 5.5 | Strategy vs semantic consistency (scatter) | `fig_5_5_correlations` |
| 5.6a | Alignment by temperature + per model | `fig_5_6_alignment` |
| 5.6b | Per-temperature correlation panels | `fig_5_6_correlations_by_temp` |
| A.1 | Plan validity rate (appendix) | `fig_A1_validity` |

All in `stats/visuals_experiment/`, PDF + PNG.
