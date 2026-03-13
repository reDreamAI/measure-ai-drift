"""Figure 5.3: BERTScore F1 by model and temperature.

Grouped bar chart: x-axis = models, two bars per model (t=0.0, t=0.7),
y-axis = mean BERTScore F1 (error bars = SD).

Usage:
    python stats/scripts/fig_bertscore.py [--input stats/data/all_runs.csv]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--tier", choices=["test", "experiment"], default="experiment")
    args = parser.parse_args()

    if args.input is None:
        args.input = Path(f"stats/data/{args.tier}_runs.csv")
    output_dir = Path(f"stats/visuals_{args.tier}")

    df = pd.read_csv(args.input)
    models = sorted(df["model"].unique())
    temps = sorted(df["temperature"].unique())
    n_models = len(models)
    bar_width = 0.35
    x = np.arange(n_models)

    colors = ["#264653", "#e9c46a"]

    fig, ax = plt.subplots(figsize=(8, 5))

    for i, temp in enumerate(temps):
        subset = df[df["temperature"] == temp]
        means = []
        sds = []
        for model in models:
            vals = subset[subset["model"] == model]["bertscore_f1"].dropna()
            means.append(vals.mean() if not vals.empty else 0)
            sds.append(vals.std() if len(vals) > 1 else 0)

        offset = (i - (len(temps) - 1) / 2) * bar_width
        ax.bar(
            x + offset,
            means,
            bar_width,
            yerr=sds,
            label=f"T={temp}",
            color=colors[i % len(colors)],
            edgecolor="white",
            capsize=3,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Mean BERTScore F1 (SD)")
    ax.set_ylim(0.5, 1.0)
    ax.set_title("BERTScore F1 by model and temperature")
    ax.legend(fontsize=9)

    fig.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "fig_5_3_bertscore.pdf", bbox_inches="tight")
    fig.savefig(output_dir / "fig_5_3_bertscore.png", bbox_inches="tight", dpi=150)
    print(f"Saved fig_5_3 to {output_dir}/")
    plt.close(fig)


if __name__ == "__main__":
    main()
