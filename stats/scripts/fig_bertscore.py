"""Figure 5.3: BERTScore F1 by model and temperature.

Line plot: x-axis = temperature, one line per model, y-axis = mean BERTScore F1
(shaded SD band).

Usage:
    python stats/scripts/fig_bertscore.py [--tier test|experiment]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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

    df = pd.read_csv(args.input)
    models = sorted(df["model"].unique())
    temps = sorted(df["temperature"].unique())

    fig, ax = plt.subplots(figsize=(8, 5))

    for model in models:
        mdf = df[df["model"] == model]
        means = []
        sds = []
        valid_temps = []

        for temp in temps:
            vals = mdf[mdf["temperature"] == temp]["bertscore_f1"].dropna()
            if vals.empty:
                continue
            valid_temps.append(temp)
            means.append(vals.mean())
            sds.append(vals.std() if len(vals) > 1 else 0)

        if not valid_temps:
            continue

        color = MODEL_COLORS.get(model, "#888888")
        means_arr = np.array(means)
        sds_arr = np.array(sds)
        ax.plot(valid_temps, means, marker="o", label=model, color=color, linewidth=2)
        ax.fill_between(valid_temps, means_arr - sds_arr, means_arr + sds_arr, alpha=0.15, color=color)

    ax.set_xlabel("Temperature")
    ax.set_ylabel("Mean BERTScore F1 (SD)")
    ax.set_ylim(0.5, 1.0)
    ax.set_title("BERTScore F1 by model and temperature")
    ax.legend(fontsize=8)

    fig.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "fig_5_3_bertscore.pdf", bbox_inches="tight")
    fig.savefig(output_dir / "fig_5_3_bertscore.png", bbox_inches="tight", dpi=150)
    print(f"Saved fig_5_3 to {output_dir}/")
    plt.close(fig)


if __name__ == "__main__":
    main()
