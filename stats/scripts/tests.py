"""Statistical tests (exploratory, bachelor's thesis scope).

Tests:
- Temperature effect: Wilcoxon signed-rank (paired by model+vignette)
- Model differences: Kruskal-Wallis H (across models)
- Vignette effect: Kruskal-Wallis H (across vignettes)
- Correlation: Spearman between Jaccard and BERTScore F1

Usage:
    python stats/scripts/tests.py [--input stats/data/all_runs.csv] [--output stats/data/test_results.json]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sp


def temperature_effect(df: pd.DataFrame, metric: str = "jaccard_all") -> dict:
    """Wilcoxon signed-rank test for temperature effect (paired by model+vignette).

    Pairs: same model+vignette at t=0.0 vs t=0.7.
    """
    t0 = df[df["temperature"] == 0.0].set_index(["model", "vignette"])[metric]
    t7 = df[df["temperature"] == 0.7].set_index(["model", "vignette"])[metric]

    # Only keep pairs that exist at both temperatures
    common = t0.index.intersection(t7.index)
    if len(common) < 5:
        return {
            "test": "wilcoxon_signed_rank",
            "metric": metric,
            "n_pairs": len(common),
            "note": "too few pairs for reliable test",
        }

    x = t0.loc[common].values
    y = t7.loc[common].values

    stat, p = sp.wilcoxon(x, y, alternative="two-sided")
    n = len(common)
    # Effect size: r = Z / sqrt(N), approximate Z from the statistic
    z = sp.norm.ppf(p / 2)  # two-sided p -> Z
    r = abs(z) / np.sqrt(n)

    return {
        "test": "wilcoxon_signed_rank",
        "metric": metric,
        "n_pairs": n,
        "statistic": float(stat),
        "p_value": float(p),
        "effect_size_r": float(r),
        "direction": "t0.0 > t0.7" if np.median(x) > np.median(y) else "t0.7 >= t0.0",
        "median_t0": float(np.median(x)),
        "median_t7": float(np.median(y)),
    }


def model_differences(df: pd.DataFrame, metric: str = "jaccard_all") -> dict:
    """Kruskal-Wallis H test across models."""
    groups = [group[metric].dropna().values for _, group in df.groupby("model")]
    groups = [g for g in groups if len(g) > 0]

    if len(groups) < 3:
        return {
            "test": "kruskal_wallis",
            "metric": metric,
            "n_groups": len(groups),
            "note": "fewer than 3 groups",
        }

    stat, p = sp.kruskal(*groups)
    n_total = sum(len(g) for g in groups)
    # Eta-squared approximation: H / (N - 1)
    eta_sq = float(stat) / (n_total - 1)

    result = {
        "test": "kruskal_wallis",
        "metric": metric,
        "n_groups": len(groups),
        "n_total": n_total,
        "H_statistic": float(stat),
        "p_value": float(p),
        "eta_squared": eta_sq,
    }

    # Pairwise Mann-Whitney U with Bonferroni if significant
    if p < 0.05:
        models = sorted(df["model"].unique())
        pairwise = []
        n_comparisons = len(models) * (len(models) - 1) // 2
        for i, m1 in enumerate(models):
            for m2 in models[i + 1:]:
                g1 = df[df["model"] == m1][metric].dropna().values
                g2 = df[df["model"] == m2][metric].dropna().values
                if len(g1) > 0 and len(g2) > 0:
                    u_stat, u_p = sp.mannwhitneyu(g1, g2, alternative="two-sided")
                    pairwise.append({
                        "pair": f"{m1} vs {m2}",
                        "U_statistic": float(u_stat),
                        "p_value": float(u_p),
                        "p_bonferroni": float(min(u_p * n_comparisons, 1.0)),
                    })
        result["pairwise"] = pairwise

    return result


def vignette_effect(df: pd.DataFrame, metric: str = "jaccard_all") -> dict:
    """Kruskal-Wallis H test across vignettes."""
    groups = [group[metric].dropna().values for _, group in df.groupby("vignette")]
    groups = [g for g in groups if len(g) > 0]

    if len(groups) < 3:
        return {
            "test": "kruskal_wallis",
            "metric": metric,
            "grouping": "vignette",
            "note": "fewer than 3 groups",
        }

    stat, p = sp.kruskal(*groups)
    n_total = sum(len(g) for g in groups)
    eta_sq = float(stat) / (n_total - 1)

    return {
        "test": "kruskal_wallis",
        "metric": metric,
        "grouping": "vignette",
        "n_groups": len(groups),
        "n_total": n_total,
        "H_statistic": float(stat),
        "p_value": float(p),
        "eta_squared": eta_sq,
    }


def metric_correlation(df: pd.DataFrame) -> dict:
    """Spearman rank correlation between Jaccard and BERTScore F1."""
    valid = df[["jaccard_all", "bertscore_f1"]].dropna()
    if len(valid) < 5:
        return {"test": "spearman", "note": "too few observations"}

    rho, p = sp.spearmanr(valid["jaccard_all"], valid["bertscore_f1"])

    return {
        "test": "spearman",
        "variables": ["jaccard_all", "bertscore_f1"],
        "n": len(valid),
        "rho": float(rho),
        "p_value": float(p),
    }


def run_all_tests(df: pd.DataFrame) -> dict:
    """Run all statistical tests and return results."""
    return {
        "temperature_effect_jaccard": temperature_effect(df, "jaccard_all"),
        "temperature_effect_bertscore": temperature_effect(df, "bertscore_f1"),
        "model_differences_jaccard": model_differences(df, "jaccard_all"),
        "model_differences_bertscore": model_differences(df, "bertscore_f1"),
        "vignette_effect_jaccard": vignette_effect(df, "jaccard_all"),
        "vignette_effect_bertscore": vignette_effect(df, "bertscore_f1"),
        "correlation_jaccard_bertscore": metric_correlation(df),
        "note": "All tests are exploratory given sample sizes. Effect sizes reported alongside p-values.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run statistical tests")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--tier", choices=["test", "experiment"], default="experiment")
    args = parser.parse_args()

    if args.input is None:
        args.input = Path(f"stats/data/{args.tier}_runs.csv")
    if args.output is None:
        args.output = Path(f"stats/data/{args.tier}_test_results.json")

    df = pd.read_csv(args.input)
    results = run_all_tests(df)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print(f"Test results -> {args.output}")
    for key, val in results.items():
        if key == "note":
            continue
        p = val.get("p_value")
        if p is not None:
            sig = "*" if p < 0.05 else ""
            print(f"  {key:40s}  p={p:.4f}{sig}")
        else:
            print(f"  {key:40s}  {val.get('note', 'n/a')}")


if __name__ == "__main__":
    main()
