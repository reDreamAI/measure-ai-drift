"""Figure 5.5: Metric correlation -- median Jaccard vs median BERTScore per model.

Scatter with one point per model, colored by model. Jaccard on x-axis,
BERTScore on y-axis, each with its own scale. Spearman rho on model-level
medians (one value per model).

Usage:
    python stats/scripts/fig_correlations.py [--tier test|experiment]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats as sp

# One color per model -- will fall back to gray for unknown models
MODEL_COLORS = {
    # Mistral EU-sovereign (reds)
    "mistral_small4": "#e63946",
    "mistral_large": "#9b2226",
    "mistral_small32": "#d4756b",
    # Qwen family (yellows/ambers)
    "qwen35_122b": "#e9c46a",
    "qwen35_397b": "#c8961e",
    "qwen35_27b": "#f4d08f",
    # Dense comparators
    "olmo3_32b": "#f4a261",
    "llama70b": "#2a9d8f",
    # Proprietary ceiling
    "gpt54": "#457b9d",
    "sonnet46": "#6a0dad",
    # Test
    "llama70b_test": "#a8dadc",
    "gpt_oss_test": "#6d6875",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--tier", choices=["test", "experiment"], default="experiment")
    args = parser.parse_args()

    if args.input is None:
        args.input = Path(f"stats/data/{args.tier}_runs.csv")
    output_dir = Path(f"stats/visuals_{args.tier}")

    df = pd.read_csv(args.input).dropna(subset=["jaccard_all", "bertscore_f1"])

    # Aggregate to one value per model
    # Median for Jaccard (ordinal/discrete), mean for BERTScore (continuous)
    model_stats = df.groupby("model").agg(
        jaccard=("jaccard_all", "median"),
        bertscore=("bertscore_f1", "mean"),
    )

    fig, ax = plt.subplots(figsize=(7, 6))

    for model, row in model_stats.iterrows():
        color = MODEL_COLORS.get(model, "#888888")
        ax.scatter(
            row["jaccard"],
            row["bertscore"],
            color=color,
            s=120,
            zorder=3,
            edgecolors="white",
            linewidth=1,
            label=model,
        )
        ax.annotate(
            model,
            (row["jaccard"], row["bertscore"]),
            textcoords="offset points",
            xytext=(8, -4),
            fontsize=8,
        )

    # Spearman on model-level medians
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

    ax.set_xlabel("Median Jaccard similarity", fontsize=10)
    ax.set_ylabel("Mean BERTScore F1", fontsize=10)
    ax.set_title("Strategy consistency vs semantic consistency")

    ax.set_xlim(0, 1.1)
    ax.set_ylim(0.5, 1.0)

    ax.legend(fontsize=8, loc="lower right")

    fig.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "fig_5_5_correlations.pdf", bbox_inches="tight")
    fig.savefig(output_dir / "fig_5_5_correlations.png", bbox_inches="tight", dpi=150)
    print(f"Saved fig_5_5 to {output_dir}/")
    plt.close(fig)


if __name__ == "__main__":
    main()
