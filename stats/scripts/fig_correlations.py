"""Figure 5.5: Metric correlation -- median Jaccard vs mean BERTScore per model.

Scatter with one point per model, colored by model. Labels use display names
with smart placement to avoid overlaps. No redundant legend.

Usage:
    python stats/scripts/fig_correlations.py [--tier test|experiment]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats as sp

from model_display import MODEL_COLORS, display_name


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--tier", choices=["test", "experiment"], default="experiment")
    args = parser.parse_args()

    if args.input is None:
        args.input = Path(f"stats/data/{args.tier}_runs.csv")
    output_dir = Path(f"stats/visuals_{args.tier}")

    df = pd.read_csv(args.input).dropna(subset=["jaccard_all", "bertscore_f1"])

    model_stats = df.groupby("model").agg(
        jaccard=("jaccard_all", "median"),
        bertscore=("bertscore_f1", "mean"),
    )

    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot points
    for model, row in model_stats.iterrows():
        color = MODEL_COLORS.get(model, "#888888")
        ax.scatter(
            row["jaccard"],
            row["bertscore"],
            color=color,
            s=140,
            zorder=3,
            edgecolors="white",
            linewidth=1.5,
        )

    # Smart label placement: try to avoid overlaps
    points = [(row["jaccard"], row["bertscore"], model) for model, row in model_stats.iterrows()]
    points.sort(key=lambda p: (p[0], p[1]))

    for x, y, model in points:
        name = display_name(model)
        color = MODEL_COLORS.get(model, "#888888")

        # Default: label to the right
        ha, dx, dy = "left", 10, 0

        # Adjust for specific crowded regions
        if model == "qwen35_27b":
            dx, dy = 10, 8
        elif model == "qwen35_397b":
            dx, dy = 10, -8
        elif model == "llama70b":
            dx, dy = -10, 8
            ha = "right"
        elif model == "mistral_small4":
            dx, dy = 10, -10

        ax.annotate(
            name,
            (x, y),
            textcoords="offset points",
            xytext=(dx, dy),
            fontsize=8,
            ha=ha,
            color=color,
            fontweight="bold",
        )

    # Spearman on model-level aggregates
    n = len(model_stats)
    if n >= 3:
        rho, p = sp.spearmanr(model_stats["jaccard"], model_stats["bertscore"])
        label = f"Spearman rho = {rho:.3f}"
        if p < 0.001:
            label += ", p < 0.001"
        else:
            label += f", p = {p:.3f}"
        label += f" (N = {n} models)"

        ax.annotate(
            label,
            xy=(0.05, 0.95),
            xycoords="axes fraction",
            fontsize=9,
            va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
        )

    ax.set_xlabel("Median Jaccard similarity (strategy consistency)", fontsize=10)
    ax.set_ylabel("Mean BERTScore F1 (semantic consistency)", fontsize=10)
    ax.set_title("Strategy consistency vs semantic consistency")

    ax.set_xlim(0.3, 1.05)
    ax.set_ylim(0.65, 1.0)

    fig.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "fig_5_5_correlations.pdf", bbox_inches="tight")
    fig.savefig(output_dir / "fig_5_5_correlations.png", bbox_inches="tight", dpi=150)
    print(f"Saved fig_5_5 to {output_dir}/")
    plt.close(fig)


if __name__ == "__main__":
    main()
