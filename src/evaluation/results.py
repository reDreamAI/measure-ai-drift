"""Results aggregation for experiment analysis.

Aggregates metrics from individual experiment runs in experiments/runs/
and outputs consolidated results to data/synthetic/results/.

Output files:
    - stability.json: Jaccard similarity across models/vignettes
    - semantic_consistency.json: BERTScore metrics (Level 3.2, future)
    - alignment.json: Plan-output alignment (Level 3.3, future)
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.evaluation.experiment import load_experiment


def aggregate_experiments(
    runs_dir: str | Path = "experiments/runs",
) -> dict[str, Any]:
    """Scan experiment runs and aggregate metrics.

    Reads all completed experiment runs from the runs directory and
    consolidates their metrics into a summary suitable for analysis.

    Args:
        runs_dir: Directory containing experiment run folders

    Returns:
        Dictionary with aggregated metrics organized by model and vignette

    Example:
        >>> results = aggregate_experiments()
        >>> results["by_model"]["groq_llama"]["mean_jaccard"]
        0.72
    """
    runs_dir = Path(runs_dir)

    if not runs_dir.exists():
        return {"experiments": [], "by_model": {}, "by_vignette": {}}

    experiments = []
    by_model: dict[str, list[dict]] = {}
    by_vignette: dict[str, list[dict]] = {}

    # Scan all run directories
    for run_path in sorted(runs_dir.iterdir()):
        if not run_path.is_dir():
            continue

        metrics_file = run_path / "metrics.json"
        config_file = run_path / "config.yaml"

        if not metrics_file.exists() or not config_file.exists():
            continue

        try:
            exp_data = load_experiment(run_path)
            config = exp_data["config"]
            metrics = exp_data["metrics"]

            summary = {
                "run_id": run_path.name,
                "model": config.get("model", "unknown"),
                "vignette": config.get("vignette", "unknown"),
                "n_trials": metrics.get("n_trials", 0),
                "temperature": metrics.get("temperature", 0.0),
                "validity_rate": metrics.get("validity_rate", 0.0),
                "jaccard_all": metrics.get("jaccard_all", 0.0),
                "jaccard_valid": metrics.get("jaccard_valid_only", 0.0),
            }

            experiments.append(summary)

            # Group by model
            model = summary["model"]
            if model not in by_model:
                by_model[model] = []
            by_model[model].append(summary)

            # Group by vignette
            vignette = summary["vignette"]
            if vignette not in by_vignette:
                by_vignette[vignette] = []
            by_vignette[vignette].append(summary)

        except Exception:
            # Skip malformed experiments
            continue

    # Compute aggregate statistics
    model_stats = _compute_group_stats(by_model)
    vignette_stats = _compute_group_stats(by_vignette)

    return {
        "experiments": experiments,
        "by_model": model_stats,
        "by_vignette": vignette_stats,
        "total_experiments": len(experiments),
        "aggregated_at": datetime.now().isoformat(),
    }


def _compute_group_stats(grouped: dict[str, list[dict]]) -> dict[str, dict]:
    """Compute aggregate statistics for grouped experiments."""
    stats = {}

    for key, experiments in grouped.items():
        if not experiments:
            continue

        jaccard_values = [e["jaccard_valid"] for e in experiments]
        validity_values = [e["validity_rate"] for e in experiments]

        stats[key] = {
            "n_experiments": len(experiments),
            "total_trials": sum(e["n_trials"] for e in experiments),
            "mean_jaccard": sum(jaccard_values) / len(jaccard_values),
            "min_jaccard": min(jaccard_values),
            "max_jaccard": max(jaccard_values),
            "mean_validity": sum(validity_values) / len(validity_values),
        }

    return stats


def save_results(
    output_dir: str | Path = "data/synthetic/results",
    runs_dir: str | Path = "experiments/runs",
) -> Path:
    """Aggregate experiments and save results to output directory.

    Creates the results directory structure and saves aggregated metrics.
    Currently saves stability.json; semantic_consistency.json and
    alignment.json are placeholders for future implementation.

    Args:
        output_dir: Directory for results output
        runs_dir: Directory containing experiment runs

    Returns:
        Path to the saved stability.json file

    Example:
        >>> path = save_results()
        >>> print(path)
        data/synthetic/results/stability.json
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Aggregate all experiments
    results = aggregate_experiments(runs_dir)

    # Save stability results
    stability_path = output_dir / "stability.json"
    with open(stability_path, "w") as f:
        json.dump(results, f, indent=2)

    # Create placeholder files for future metrics
    _create_placeholder(
        output_dir / "semantic_consistency.json",
        "BERTScore semantic consistency metrics (Level 3.2)",
    )
    _create_placeholder(
        output_dir / "alignment.json",
        "Plan-output alignment metrics (Level 3.3)",
    )

    return stability_path


def _create_placeholder(path: Path, description: str) -> None:
    """Create a placeholder JSON file for future metrics."""
    if path.exists():
        return  # Don't overwrite existing data

    placeholder = {
        "status": "not_implemented",
        "description": description,
        "created_at": datetime.now().isoformat(),
    }

    with open(path, "w") as f:
        json.dump(placeholder, f, indent=2)
