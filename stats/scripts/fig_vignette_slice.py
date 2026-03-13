"""Figure 5.4: Vignette difficulty by temperature (and slice depth if available).

Two heatmaps side by side: T=0.0 (left) and T=0.7 (right), model x vignette.
If only one temperature exists, single heatmap.
If slice data is available, adds a third panel with slice depth lines.

Usage:
    python stats/scripts/fig_vignette_slice.py [--tier test|experiment]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def make_heatmap(ax, df, models, vignettes, title):
    """Draw a model x vignette heatmap on the given axis."""
    pivot = df.groupby(["model", "vignette"])["jaccard_all"].median().unstack(fill_value=np.nan)
    pivot = pivot.reindex(index=models, columns=vignettes)

    sns.heatmap(
        pivot,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn",
        vmin=0,
        vmax=1,
        ax=ax,
        cbar_kws={"label": "Median Jaccard"},
    )
    ax.set_title(title)
    ax.set_ylabel("")


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
    vignettes = sorted(df["vignette"].unique())
    temps = sorted(df["temperature"].unique())
    has_slices = "slice" in df.columns and df["slice"].notna().any()

    # Determine layout
    n_panels = len(temps) + (1 if has_slices else 0)
    fig, axes = plt.subplots(1, n_panels, figsize=(6 * n_panels, max(4, len(models) * 0.8 + 1)))
    if n_panels == 1:
        axes = [axes]

    # One heatmap per temperature
    for i, temp in enumerate(temps):
        temp_df = df[df["temperature"] == temp]
        make_heatmap(axes[i], temp_df, models, vignettes, f"T = {temp}")

    # Slice depth panel (if available)
    if has_slices:
        ax_slice = axes[-1]
        for model in models:
            model_data = df[df["model"] == model]
            slice_medians = model_data.groupby("slice")["jaccard_all"].median()
            ax_slice.plot(slice_medians.index, slice_medians.values, marker="o", label=model)

        ax_slice.set_xlabel("Slice depth")
        ax_slice.set_ylabel("Median Jaccard")
        ax_slice.set_title("Stability by conversation depth")
        ax_slice.legend(fontsize=8)
        ax_slice.set_ylim(0, 1.1)

    fig.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "fig_5_4_vignette_slice.pdf", bbox_inches="tight")
    fig.savefig(output_dir / "fig_5_4_vignette_slice.png", bbox_inches="tight", dpi=150)
    print(f"Saved fig_5_4 to {output_dir}/")
    plt.close(fig)


if __name__ == "__main__":
    main()
