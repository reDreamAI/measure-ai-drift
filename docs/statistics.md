# Statistics and Visualization Plan

> Defines all analyses and figures for Chapter 5 (Results).
> Scripts go in `stats/scripts/`, output goes in `stats/visuals_experiment/`.
> All figures use the same data: `experiments/latest/` aggregated into a single DataFrame.

## Known measurement constraints

These shape the analysis design:

1. **Jaccard is discrete.** With 1-2 picks from 6 categories, Jaccard only takes values {0, 0.33, 0.5, 0.67, 1.0}. Treat as ordinal, not continuous. Report medians and IQR, not means and SD.
2. **Alignment varies by model and judge.** Scored by Gemini 3 Flash (near-Pro reasoning). Pro fallback for zero-scored trials. Alignment shows genuine model differences (p<0.001) but is temperature-independent.
3. **BERTScore confound.** IRT responses share formulaic structure ("imagine the dream changing..."). High BERTScore may reflect protocol adherence rather than true semantic similarity. Interpret alongside Jaccard, not independently.
4. **Small N for inferential tests.** With 8 models, Kruskal-Wallis has moderate power. Report effect sizes. Treat p-values as exploratory, not confirmatory.
5. **Random Jaccard baseline.** Expected Jaccard for random 2-of-6 picks is ~0.2. Include as reference line in all Jaccard figures.

## Data pipeline

### Step 0: Aggregate raw runs into a single DataFrame

**Script:** `stats/scripts/aggregate.py`
**Input:** `experiments/latest/**/metrics.json` + `config.yaml`
**Output:** `stats/data/experiment_runs.csv`

One row per run (= one model x one vignette x one temperature x one slice). Columns:

| Column | Source | Type |
|--------|--------|------|
| model | config.yaml | str |
| vignette | config.yaml | str |
| temperature | config.yaml | float |
| slice | config.yaml | int |
| n_trials | metrics.json | int |
| validity_rate | metrics.json | float |
| jaccard_all | metrics.json | float |
| jaccard_valid | metrics.json | float |
| modal_set_agreement | metrics.json | float |
| bertscore_f1 | metrics.json | float |
| alignment_mean | metrics.json | float |
| strategy_counts | metrics.json | dict (expand to 6 columns) |

Strategy count columns: `n_confrontation`, `n_self_empowerment`, `n_safety`, `n_cognitive_reframe`, `n_social_support`, `n_sensory_modulation`.

### Step 1: Descriptive statistics

**Script:** `stats/scripts/descriptives.py`
**Input:** `stats/data/experiment_runs.csv`
**Output:** `stats/data/experiment_descriptives.json`

Per model (collapsed across vignettes):
- Median, IQR, min, max for Jaccard and modal-set agreement (ordinal metrics)
- Mean, SD for BERTScore F1 (continuous metric)
- Total valid trials / total trials (validity rate)
- Strategy distribution (% of picks per category)

Per vignette (collapsed across models):
- Same metrics, to identify "hard" vs "easy" vignettes

Per temperature (4-point scale: 0.0, 0.15, 0.3, 0.6):
- Summary stats at each temperature level, collapsed across models and vignettes

---

## Figures

All figures saved as PDF (for LaTeX) and PNG (for preview) in `stats/visuals_experiment/`.

### Figure 5.1: Validity and strategy distribution

**Script:** `stats/scripts/fig_validity_strategy.py`

Two subplots side by side:
- **Left:** Bar chart of validity rate per model (should be near 100% for all). Simple sanity check.
- **Right:** Stacked bar chart of strategy frequency per model. Each bar is one model, segments are the 6 categories. Shows which strategies each model favors.

### Figure 5.2: Jaccard and modal-set stability by temperature (headline figure)

**Script:** `stats/scripts/fig_jaccard.py`

Two subplots:
- **Left:** Line plot: x-axis = temperature (0.0, 0.15, 0.3, 0.6), one line per model, y-axis = median Jaccard (IQR shading). Reference lines at 1.0 (perfect) and ~0.2 (random baseline for 2-of-6 picks). Shows the stability curve per model across the temperature scale.
- **Right:** Same layout for modal-set agreement rate. Complements Jaccard by showing exact agreement.

### Figure 5.3: BERTScore by model and temperature

**Script:** `stats/scripts/fig_bertscore.py`

Line plot: x-axis = temperature (0.0, 0.15, 0.3, 0.6), one line per model, y-axis = mean BERTScore F1 (SD shading). Shows where semantic consistency degrades as temperature increases. Interpret alongside Jaccard (high BERTScore alone may reflect formulaic IRT structure).

### Figure 5.4: Vignette difficulty heatmap

**Script:** `stats/scripts/fig_vignette_slice.py`

Heatmap of model x vignette per temperature, colored by median Jaccard. Four panels (one per temperature). Identifies where instability concentrates.

### Figure 5.5: Metric correlations

**Script:** `stats/scripts/fig_correlations.py`

Scatter: median Jaccard (x) vs mean BERTScore F1 (y), one colored point per model. Spearman rho computed on model-level aggregates. Shows whether strategy consistency predicts semantic consistency.

---

## Statistical tests

**Script:** `stats/scripts/tests.py`

Keep simple (bachelor's thesis scope). All tests are **exploratory** given sample sizes.

- **Temperature effect (pooled):** Spearman correlation (metric vs temperature) for monotonic trend, plus Kruskal-Wallis across the 4 temperature groups.
- **Temperature effect (per-model):** Spearman correlation per model. Identifies which models are temperature-sensitive vs temperature-robust.
- **Model differences:** Kruskal-Wallis H test across models, for Jaccard, BERTScore, and Alignment. Pairwise Mann-Whitney U with Bonferroni if significant.
- **Vignette effect:** Kruskal-Wallis grouped by vignette.
- **Correlations:** Spearman between all metric pairs (Jaccard, BERTScore, Alignment).

Results saved to `stats/data/experiment_test_results.json`.

No complex modeling. Report effect sizes alongside p-values. Frame results as "the data suggest" rather than "we confirm".

---

## File structure

```
stats/
  scripts/
    aggregate.py          # Step 0: runs -> CSV
    descriptives.py       # Step 1: summary stats
    tests.py              # Statistical tests
    fig_validity_strategy.py   # Figure 5.1
    fig_jaccard.py             # Figure 5.2 (Jaccard + modal-set)
    fig_bertscore.py           # Figure 5.3
    fig_vignette_slice.py      # Figure 5.4
    fig_correlations.py        # Figure 5.5
  data/
    experiment_runs.csv        # Aggregated data
    experiment_descriptives.json
    experiment_test_results.json
  visuals_experiment/
    fig_5_1_validity_strategy.pdf
    fig_5_2_jaccard.pdf
    fig_5_3_bertscore.pdf
    fig_5_4_vignette_slice.pdf
    fig_5_5_correlations.pdf
```

## Dependencies

- pandas (data handling)
- matplotlib + seaborn (figures)
- scipy.stats (Kruskal-Wallis, Mann-Whitney, Spearman)
