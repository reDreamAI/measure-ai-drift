"""Analyse Mistral Large 3 stability as a function of conversation depth (slice).

Reads runs from experiments/runs/slice_batch/ where each vignette was evaluated
at 5 conversation depths (slices 1-5) and 2 temperatures (0.075, 0.15).

Outputs:
  - Console table with metrics per slice
  - Spearman correlation: depth vs each metric
  - Figure: line plots of Jaccard, BERTScore, Alignment by slice (one line per temp)
  - Per-vignette heatmap of Jaccard by slice

Usage:
    python stats/scripts/analyse_slice_depth.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from scipy import stats as sp

# ---------------------------------------------------------------------------
# Load runs
# ---------------------------------------------------------------------------

BATCH_DIR = Path("experiments/runs/slice_batch")


def load_slice_runs() -> pd.DataFrame:
    """Load all slice_batch runs, infer slice number from chronological order."""
    rows = []
    for run_dir in sorted(BATCH_DIR.iterdir()):
        if not run_dir.is_dir():
            continue
        config_path = run_dir / "config.yaml"
        metrics_path = run_dir / "metrics.json"
        history_path = run_dir / "frozen_history.json"
        if not config_path.exists() or not metrics_path.exists():
            continue

        with open(config_path) as f:
            cfg = yaml.safe_load(f)
        with open(metrics_path) as f:
            metrics = json.load(f)
        with open(history_path) as f:
            history = json.load(f)

        rows.append({
            "run_id": run_dir.name,
            "model": cfg["model"],
            "vignette": cfg["vignette"],
            "temperature": cfg["temperature"],
            "n_messages": len(history["messages"]),
            "jaccard": metrics.get("jaccard_all"),
            "bertscore_f1": metrics.get("bertscore_f1"),
            "alignment": metrics.get("alignment_mean"),
            "validity": metrics.get("validity_rate"),
            "modal_agreement": metrics.get("modal_set_agreement"),
        })

    df = pd.DataFrame(rows)

    # Infer slice number: within each (vignette, temperature) group,
    # rank by n_messages (ascending) to get slice 1-5
    df["slice"] = (
        df.groupby(["vignette", "temperature"])["n_messages"]
        .rank(method="dense")
        .astype(int)
    )

    return df.sort_values(["vignette", "temperature", "slice"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------

def print_summary(df: pd.DataFrame) -> None:
    """Print summary tables to console."""
    print("=" * 70)
    print("SLICE DEPTH ANALYSIS: Mistral Large 3")
    print(f"Runs: {len(df)} | Temps: {sorted(df['temperature'].unique())} | "
          f"Vignettes: {len(df['vignette'].unique())} | Slices: {sorted(df['slice'].unique())}")
    print("=" * 70)

    # Per-slice means (pooled across vignettes)
    print("\n--- Metrics by slice (pooled across vignettes) ---")
    for temp in sorted(df["temperature"].unique()):
        tdf = df[df["temperature"] == temp]
        print(f"\nT = {temp}")
        summary = tdf.groupby("slice").agg(
            n_msgs=("n_messages", "mean"),
            jaccard=("jaccard", "mean"),
            jaccard_sd=("jaccard", "std"),
            bertscore=("bertscore_f1", "mean"),
            alignment=("alignment", "mean"),
        ).round(3)
        summary["n_msgs"] = summary["n_msgs"].round(1)
        print(summary.to_string())

    # Spearman: slice vs metrics
    print("\n--- Spearman correlation: slice (depth) vs metrics ---")
    for temp in sorted(df["temperature"].unique()):
        tdf = df[df["temperature"] == temp]
        print(f"\nT = {temp}")
        for metric in ["jaccard", "bertscore_f1", "alignment"]:
            vals = tdf[metric].dropna()
            slices = tdf.loc[vals.index, "slice"]
            if len(vals) >= 3:
                rho, p = sp.spearmanr(slices, vals)
                sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
                print(f"  {metric:15s}: rho={rho:+.3f}, p={p:.4f} {sig}")

    # Pooled across both temps
    print("\nPooled (both temps):")
    for metric in ["jaccard", "bertscore_f1", "alignment"]:
        vals = df[metric].dropna()
        slices = df.loc[vals.index, "slice"]
        if len(vals) >= 3:
            rho, p = sp.spearmanr(slices, vals)
            sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
            print(f"  {metric:15s}: rho={rho:+.3f}, p={p:.4f} {sig}")

    # Per-vignette Jaccard table
    print("\n--- Jaccard by vignette and slice (T=0.075) ---")
    tdf = df[df["temperature"] == 0.075]
    pivot = tdf.pivot_table(index="vignette", columns="slice", values="jaccard")
    print(pivot.round(3).to_string())


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def plot_metrics_by_slice(df: pd.DataFrame, output_dir: Path) -> None:
    """Line plots: Jaccard, BERTScore, Alignment by slice, one line per temp."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    metrics = [("jaccard", "Jaccard"), ("bertscore_f1", "BERTScore F1"), ("alignment", "Alignment")]
    temp_colors = {0.075: "#2ca02c", 0.15: "#e8a830"}

    for ax, (col, label) in zip(axes, metrics):
        for temp in sorted(df["temperature"].unique()):
            tdf = df[df["temperature"] == temp]
            means = tdf.groupby("slice")[col].mean()
            sds = tdf.groupby("slice")[col].std()
            slices = means.index

            color = temp_colors.get(temp, "#888888")
            ax.plot(slices, means, marker="o", color=color, linewidth=2,
                    label=f"T={temp}")
            lower = np.clip(means - sds, 0, 1)
            upper = np.clip(means + sds, 0, 1)
            ax.fill_between(slices, lower, upper, alpha=0.1, color=color)

        ax.set_xlabel("Slice (conversation depth)")
        ax.set_ylabel(label)
        ax.set_xticks(sorted(df["slice"].unique()))
        ax.legend(fontsize=9)

        ax.set_ylim(0.5, 1.0)

    fig.suptitle("Mistral Large 3: stability by conversation depth", fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(output_dir / "fig_slice_depth_metrics.pdf", bbox_inches="tight")
    fig.savefig(output_dir / "fig_slice_depth_metrics.png", bbox_inches="tight", dpi=150)
    print(f"\nSaved fig_slice_depth_metrics to {output_dir}/")
    plt.close(fig)


def plot_vignette_heatmap(df: pd.DataFrame, output_dir: Path) -> None:
    """Heatmap: Jaccard by vignette x slice, one panel per temp."""
    temps = sorted(df["temperature"].unique())
    fig, axes = plt.subplots(1, len(temps), figsize=(6 * len(temps), 4))
    if len(temps) == 1:
        axes = [axes]

    for ax, temp in zip(axes, temps):
        tdf = df[df["temperature"] == temp]
        pivot = tdf.pivot_table(index="vignette", columns="slice", values="jaccard")
        pivot = pivot.reindex(sorted(pivot.index))

        im = ax.imshow(pivot.values, cmap="RdYlGn", vmin=0.4, vmax=1.0, aspect="auto")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels([f"S{c}" for c in pivot.columns])
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index, fontsize=9)
        ax.set_xlabel("Slice")
        ax.set_title(f"T = {temp}")

        # Annotate cells
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                val = pivot.values[i, j]
                if not np.isnan(val):
                    ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                            fontsize=8, color="black" if val > 0.6 else "white")

    fig.colorbar(im, ax=axes, shrink=0.8, label="Jaccard")
    fig.suptitle("Jaccard by vignette and conversation depth", fontsize=13)
    fig.savefig(output_dir / "fig_slice_depth_heatmap.pdf", bbox_inches="tight")
    fig.savefig(output_dir / "fig_slice_depth_heatmap.png", bbox_inches="tight", dpi=150)
    print(f"Saved fig_slice_depth_heatmap to {output_dir}/")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    df = load_slice_runs()
    if df.empty:
        print(f"No runs found in {BATCH_DIR}")
        return

    output_dir = Path("thesis/figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    print_summary(df)
    plot_metrics_by_slice(df, output_dir)
    plot_vignette_heatmap(df, output_dir)

    # Save raw data
    csv_path = Path("stats/data/slice_depth_runs.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    print(f"\nSaved data to {csv_path}")


if __name__ == "__main__":
    main()
