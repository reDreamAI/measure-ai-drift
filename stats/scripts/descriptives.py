"""Step 1: Compute descriptive statistics from aggregated runs.

Reads stats/data/all_runs.csv and produces stats/data/descriptives.json
with summary statistics per model, per vignette, and per temperature.

Usage:
    python stats/scripts/descriptives.py [--input stats/data/all_runs.csv] [--output stats/data/descriptives.json]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

STRATEGY_CATEGORIES = [
    "confrontation",
    "self_empowerment",
    "safety",
    "cognitive_reframe",
    "social_support",
    "sensory_modulation",
]


def ordinal_summary(series: pd.Series) -> dict:
    """Summarize an ordinal metric (Jaccard, modal-set): median, IQR, min, max."""
    s = series.dropna()
    if s.empty:
        return {"median": None, "q1": None, "q3": None, "min": None, "max": None, "n": 0}
    return {
        "median": float(s.median()),
        "q1": float(s.quantile(0.25)),
        "q3": float(s.quantile(0.75)),
        "min": float(s.min()),
        "max": float(s.max()),
        "n": int(len(s)),
    }


def continuous_summary(series: pd.Series) -> dict:
    """Summarize a continuous metric (BERTScore): mean, SD, min, max."""
    s = series.dropna()
    if s.empty:
        return {"mean": None, "sd": None, "min": None, "max": None, "n": 0}
    return {
        "mean": float(s.mean()),
        "sd": float(s.std()),
        "min": float(s.min()),
        "max": float(s.max()),
        "n": int(len(s)),
    }


def summarize_group(group: pd.DataFrame) -> dict:
    """Compute all summary stats for a group of runs."""
    result = {
        "n_runs": len(group),
        "total_trials": int(group["n_trials"].sum()),
        "validity_rate": continuous_summary(group["validity_rate"]),
        "jaccard_all": ordinal_summary(group["jaccard_all"]),
        "jaccard_valid": ordinal_summary(group["jaccard_valid"]),
        "bertscore_f1": continuous_summary(group["bertscore_f1"]),
        "alignment_mean": continuous_summary(group["alignment_mean"]),
    }

    # Modal-set agreement (may be all NaN for older runs)
    if "modal_set_agreement" in group.columns:
        result["modal_set_agreement"] = ordinal_summary(group["modal_set_agreement"])

    # Strategy distribution (% of total picks)
    strat_cols = [f"n_{cat}" for cat in STRATEGY_CATEGORIES]
    available = [c for c in strat_cols if c in group.columns]
    if available:
        totals = {c: int(group[c].sum()) for c in available}
        grand_total = sum(totals.values())
        result["strategy_distribution"] = {
            c.replace("n_", ""): {
                "count": totals[c],
                "pct": round(totals[c] / grand_total * 100, 1) if grand_total > 0 else 0,
            }
            for c in available
        }

    return result


def compute_descriptives(df: pd.DataFrame) -> dict:
    """Compute descriptive statistics grouped by model, vignette, and temperature."""
    result = {}

    # Per model (collapsed across vignettes)
    result["by_model"] = {}
    for model, group in df.groupby("model"):
        result["by_model"][model] = summarize_group(group)

    # Per vignette (collapsed across models)
    result["by_vignette"] = {}
    for vignette, group in df.groupby("vignette"):
        result["by_vignette"][vignette] = summarize_group(group)

    # Per temperature
    result["by_temperature"] = {}
    for temp, group in df.groupby("temperature"):
        result["by_temperature"][str(temp)] = summarize_group(group)

    # Per model x temperature (for paired comparisons)
    result["by_model_temperature"] = {}
    for (model, temp), group in df.groupby(["model", "temperature"]):
        key = f"{model}_t{temp}"
        result["by_model_temperature"][key] = summarize_group(group)

    # Overall
    result["overall"] = summarize_group(df)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute descriptive statistics")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--tier", choices=["test", "experiment"], default="experiment")
    args = parser.parse_args()

    if args.input is None:
        args.input = Path(f"stats/data/{args.tier}_runs.csv")
    if args.output is None:
        args.output = Path(f"stats/data/{args.tier}_descriptives.json")

    df = pd.read_csv(args.input)
    result = compute_descriptives(df)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)

    # Print quick summary
    print(f"Descriptives computed from {len(df)} runs -> {args.output}")
    for model, stats in result["by_model"].items():
        j = stats["jaccard_all"]
        b = stats["bertscore_f1"]
        print(f"  {model:20s}  Jaccard median={j['median']:.3f}  BERTScore mean={b['mean']:.3f}")


if __name__ == "__main__":
    main()
