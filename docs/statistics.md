# Statistics and Visualization Plan

> Defines all analyses and figures for Chapter 5 (Results).
> Scripts go in `stats/scripts/`, output goes in `stats/visuals/`.
> All figures use the same data: `experiments/runs/` aggregated into a single DataFrame.

## Known measurement constraints

These shape the analysis design:

1. **Jaccard is discrete.** With 1-2 picks from 6 categories, Jaccard only takes values {0, 0.33, 0.5, 0.67, 1.0}. Treat as ordinal, not continuous. Report medians and IQR, not means and SD.
2. **Alignment likely at ceiling.** Smoke tests scored 1.0 on all trials. If the full run shows similar ceiling effects, alignment becomes a validation check ("models implement what they declare") rather than a comparative metric. Do not build figures around it unless variance appears.
3. **BERTScore confound.** IRT responses share formulaic structure ("imagine the dream changing..."). High BERTScore may reflect protocol adherence rather than true semantic similarity. Interpret alongside Jaccard, not independently.
4. **Small N for inferential tests.** With 6 models, Kruskal-Wallis has low power. Report effect sizes. Treat p-values as exploratory, not confirmatory.
5. **Random Jaccard baseline.** Expected Jaccard for random 2-of-6 picks is ~0.2. Include as reference line in all Jaccard figures.

## Data pipeline

### Step 0: Aggregate raw runs into a single DataFrame

**Script:** `stats/scripts/aggregate.py`
**Input:** `experiments/runs/**/metrics.json` + `config.yaml`
**Output:** `stats/data/all_runs.csv`

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

Also extract `alignment_per_strategy` into separate columns for per-strategy analysis.

### Step 1: Descriptive statistics

**Script:** `stats/scripts/descriptives.py`
**Input:** `stats/data/all_runs.csv`
**Output:** `stats/data/descriptives.json`

Per model (collapsed across vignettes):
- Median, IQR, min, max for Jaccard and modal-set agreement (ordinal metrics)
- Mean, SD for BERTScore F1 (continuous metric)
- Total valid trials / total trials (validity rate)
- Strategy distribution (% of picks per category)

Per vignette (collapsed across models):
- Same metrics, to identify "hard" vs "easy" vignettes

Per temperature (5-point scale: 0.0, 0.25, 0.5, 0.7, 1.0):
- Summary stats at each temperature level, collapsed across models and vignettes

Alignment: report overall mean as validation check. Only break down per-model if variance appears in the full run.

---

## Figures

All figures saved as PDF (for LaTeX) and PNG (for preview) in `stats/visuals/`.

### Figure 5.1: Validity and strategy distribution

**Script:** `stats/scripts/fig_validity_strategy.py`

Two subplots side by side:
- **Left:** Bar chart of validity rate per model (should be near 100% for all). Simple sanity check.
- **Right:** Stacked bar chart of strategy frequency per model. Each bar is one model, segments are the 6 categories. Shows which strategies each model favors.

### Figure 5.2: Jaccard and modal-set stability by temperature (headline figure)

**Script:** `stats/scripts/fig_jaccard.py`

Two subplots:
- **Left:** Line plot: x-axis = temperature (0.0, 0.25, 0.5, 0.7, 1.0), one line per model, y-axis = median Jaccard (IQR shading). Reference lines at 1.0 (perfect) and ~0.2 (random baseline for 2-of-6 picks). Shows the stability curve per model across the full temperature scale.
- **Right:** Same layout for modal-set agreement rate. Complements Jaccard by showing exact agreement.

### Figure 5.3: BERTScore by model and temperature

**Script:** `stats/scripts/fig_bertscore.py`

Line plot: x-axis = temperature (0.0, 0.25, 0.5, 0.7, 1.0), one line per model, y-axis = mean BERTScore F1 (SD shading). Shows where semantic consistency degrades as temperature increases. Interpret alongside Jaccard (high BERTScore alone may reflect formulaic IRT structure).

### Figure 5.4: Vignette difficulty and slice depth

**Script:** `stats/scripts/fig_vignette_slice.py`

Two subplots:
- **Left:** Heatmap of model x vignette, colored by median Jaccard. Identifies where instability concentrates (e.g., resistant vignette hardest).
- **Right:** Line plot of median Jaccard by slice depth (slice_1, slice_2, slice_3), one line per model. Shows if stability changes with conversation depth.

### Figure 5.5: Metric correlations

**Script:** `stats/scripts/fig_correlations.py`

Scatter: median Jaccard (x) vs mean BERTScore F1 (y), one colored point per model. Spearman rho computed on model-level aggregates. Shows whether strategy consistency predicts semantic consistency.

> **Dropped: dedicated alignment figure.** If alignment shows ceiling effects (all near 1.0), report the overall mean in text and skip the figure. If variance appears, add a simple bar chart as Figure 5.6.

---

## Statistical tests

Keep simple (bachelor's thesis scope). All tests are **exploratory** given sample sizes.

- **Temperature effect:** Spearman correlation (metric vs temperature) for monotonic trend, plus Kruskal-Wallis across the 5 temperature groups. Best-powered test (N = 6 models x 6 vignettes x 5 temps = 180 observations).
- **Model differences:** Kruskal-Wallis H test across models. Low power with 6 groups. Report effect size (eta-squared). Pairwise Mann-Whitney U with Bonferroni only if H is significant.
- **Vignette effect:** Same as model but grouped by vignette.
- **Correlation:** Spearman rank correlation between Jaccard and BERTScore F1. Do not correlate alignment (likely at ceiling).

All tests in `stats/scripts/tests.py`, results saved to `stats/data/test_results.json`.

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
    all_runs.csv          # Aggregated data
    descriptives.json     # Summary statistics
    test_results.json     # Statistical test results
  visuals/
    fig_5_1_validity_strategy.pdf
    fig_5_2_jaccard.pdf
    fig_5_3_bertscore.pdf
    fig_5_4_vignette_slice.pdf
    fig_5_5_correlations.pdf
```

## Dependencies

- pandas (data handling)
- matplotlib + seaborn (figures)
- scipy.stats (Wilcoxon, Kruskal-Wallis, Mann-Whitney, Spearman)

All already available in the project venv.

## Approach

1. Build `aggregate.py` first, test on smoke test data (March 12 runs)
2. Build figure scripts one at a time, preview on smoke data
3. Re-run on full experiment data when available
4. Review figures before including in thesis
