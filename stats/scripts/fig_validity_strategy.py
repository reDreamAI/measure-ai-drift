"""Figure 5.1: Validity rate and strategy distribution per model.

Left subplot: bar chart of validity rate per model.
Right subplot: stacked bar chart of strategy frequency per model.

Usage:
    python stats/scripts/fig_validity_strategy.py [--input stats/data/all_runs.csv]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
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

STRATEGY_COLORS = {
    "confrontation": "#e63946",
    "self_empowerment": "#457b9d",
    "safety": "#2a9d8f",
    "cognitive_reframe": "#e9c46a",
    "social_support": "#f4a261",
    "sensory_modulation": "#264653",
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

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left: validity rate per model
    validity = df.groupby("model")["validity_rate"].mean().reindex(models)
    ax1.bar(range(len(models)), validity.values, color="#457b9d", edgecolor="white")
    ax1.set_xticks(range(len(models)))
    ax1.set_xticklabels(models, rotation=45, ha="right", fontsize=9)
    ax1.set_ylabel("Validity rate")
    ax1.set_ylim(0, 1.05)
    ax1.set_title("Plan validity rate")
    ax1.axhline(y=1.0, color="gray", linestyle="--", alpha=0.5)

    # Right: stacked strategy distribution per model
    strat_cols = [f"n_{cat}" for cat in STRATEGY_CATEGORIES]
    available = [c for c in strat_cols if c in df.columns]
    strat_data = df.groupby("model")[available].sum().reindex(models)

    # Normalize to percentages
    row_totals = strat_data.sum(axis=1)
    strat_pct = strat_data.div(row_totals, axis=0) * 100

    bottom = np.zeros(len(models))
    for col in available:
        cat = col.replace("n_", "")
        values = strat_pct[col].values
        ax2.bar(
            range(len(models)),
            values,
            bottom=bottom,
            label=cat,
            color=STRATEGY_COLORS.get(cat, "#888888"),
            edgecolor="white",
            linewidth=0.5,
        )
        bottom += values

    ax2.set_xticks(range(len(models)))
    ax2.set_xticklabels(models, rotation=45, ha="right", fontsize=9)
    ax2.set_ylabel("Strategy share (%)")
    ax2.set_title("Strategy distribution")
    ax2.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)

    fig.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "fig_5_1_validity_strategy.pdf", bbox_inches="tight")
    fig.savefig(output_dir / "fig_5_1_validity_strategy.png", bbox_inches="tight", dpi=150)
    print(f"Saved fig_5_1 to {output_dir}/")
    plt.close(fig)


if __name__ == "__main__":
    main()
