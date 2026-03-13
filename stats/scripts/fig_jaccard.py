"""Figure 5.2: Jaccard and modal-set stability by model and temperature (headline figure).

Left subplot: grouped bars of median Jaccard per model x temperature, with IQR error bars.
Right subplot: same layout for modal-set agreement rate.
Both include reference lines for perfect stability (1.0) and random baseline (~0.2).

Usage:
    python stats/scripts/fig_jaccard.py [--input stats/data/all_runs.csv]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RANDOM_BASELINE = 0.2  # Expected Jaccard for random 2-of-6 picks


def plot_metric(ax, df, metric, title, ylabel):
    """Plot grouped bars for a metric by model x temperature."""
    models = sorted(df["model"].unique())
    temps = sorted(df["temperature"].unique())
    n_models = len(models)
    n_temps = len(temps)
    bar_width = 0.35
    x = np.arange(n_models)

    colors = ["#264653", "#e9c46a"]

    for i, temp in enumerate(temps):
        subset = df[df["temperature"] == temp]
        medians = []
        q1s = []
        q3s = []
        for model in models:
            vals = subset[subset["model"] == model][metric].dropna()
            if vals.empty:
                medians.append(0)
                q1s.append(0)
                q3s.append(0)
            else:
                med = vals.median()
                medians.append(med)
                q1s.append(med - vals.quantile(0.25))
                q3s.append(vals.quantile(0.75) - med)

        offset = (i - (n_temps - 1) / 2) * bar_width
        ax.bar(
            x + offset,
            medians,
            bar_width,
            yerr=[q1s, q3s],
            label=f"T={temp}",
            color=colors[i % len(colors)],
            edgecolor="white",
            capsize=3,
        )

    ax.axhline(y=1.0, color="green", linestyle="--", alpha=0.4, label="Perfect")
    ax.axhline(y=RANDOM_BASELINE, color="red", linestyle=":", alpha=0.4, label=f"Random (~{RANDOM_BASELINE})")
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, 1.1)
    ax.set_title(title)
    ax.legend(fontsize=8)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--tier", choices=["test", "experiment"], default="experiment")
    args = parser.parse_args()

    if args.input is None:
        args.input = Path(f"stats/data/{args.tier}_runs.csv")
    output_dir = Path(f"stats/visuals_{args.tier}")

    df = pd.read_csv(args.input)

    has_modal = df["modal_set_agreement"].notna().any() if "modal_set_agreement" in df.columns else False

    if has_modal:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        plot_metric(ax1, df, "jaccard_all", "Jaccard similarity", "Median Jaccard (IQR)")
        plot_metric(ax2, df, "modal_set_agreement", "Modal-set agreement", "Agreement rate")
    else:
        fig, ax1 = plt.subplots(1, 1, figsize=(8, 5))
        plot_metric(ax1, df, "jaccard_all", "Jaccard similarity by model and temperature", "Median Jaccard (IQR)")

    fig.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "fig_5_2_jaccard.pdf", bbox_inches="tight")
    fig.savefig(output_dir / "fig_5_2_jaccard.png", bbox_inches="tight", dpi=150)
    print(f"Saved fig_5_2 to {output_dir}/")
    plt.close(fig)


if __name__ == "__main__":
    main()
