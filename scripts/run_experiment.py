"""Run the full experiment: all evaluation targets x all vignettes x slice_2.

Usage:
    python scripts/run_experiment.py [--trials 10] [--temperature 0.7] [--slice 2]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from src.core import Conversation
from src.evaluation import ExperimentRun
from src.llm.provider import load_config, create_provider


FROZEN_HISTORIES = Path("data/synthetic/frozen_histories")
VIGNETTES = ["anxious", "avoidant", "cooperative", "resistant", "skeptic", "trauma"]


def find_slice_path(vignette: str, slice_num: int) -> Path | None:
    """Find the slice file for a vignette."""
    for d in FROZEN_HISTORIES.iterdir():
        if d.is_dir() and f"frozen_{vignette}_" in d.name:
            path = d / f"slice_{slice_num}.json"
            if path.exists():
                return path
    return None


async def run_single(
    model_name: str,
    vignette: str,
    history_path: Path,
    n_trials: int,
    temperature: float,
) -> dict:
    """Run one experiment (model x vignette) and return summary."""
    with open(history_path) as f:
        history_data = json.load(f)

    frozen_history = Conversation.from_dict(history_data)
    provider = create_provider(model_name)

    experiment = ExperimentRun(
        frozen_history=frozen_history,
        model_name=model_name,
        vignette_name=vignette,
    ).setup()

    start = time.time()
    await experiment.run(
        n_trials=n_trials,
        temperature=temperature,
        language="en",
        mode="fused",
        therapist_provider=provider,
    )
    elapsed = time.time() - start

    # Read back metrics
    with open(experiment.path / "metrics.json") as f:
        metrics = json.load(f)

    return {
        "model": model_name,
        "vignette": vignette,
        "jaccard": metrics["jaccard_all"],
        "bertscore": metrics["bertscore_f1"],
        "alignment": metrics["alignment_mean"],
        "path": str(experiment.path),
        "elapsed": round(elapsed, 1),
    }


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run full experiment")
    parser.add_argument("--trials", "-n", type=int, default=10)
    parser.add_argument("--temperature", "-t", type=float, default=0.7)
    parser.add_argument("--slice", "-s", type=int, default=2)
    args = parser.parse_args()

    config = load_config()
    targets = [
        t["name"]
        for t in config.get("evaluation_targets", [])
        if not t["name"].endswith("_test")
    ]

    print(f"Experiment: {len(targets)} models x {len(VIGNETTES)} vignettes x slice_{args.slice}")
    print(f"  Models: {targets}")
    print(f"  Trials: {args.trials}, Temperature: {args.temperature}")
    print(f"  Total runs: {len(targets) * len(VIGNETTES)}")
    print()

    results = []
    total = len(targets) * len(VIGNETTES)
    done = 0

    for model in targets:
        for vignette in VIGNETTES:
            history_path = find_slice_path(vignette, args.slice)
            if history_path is None:
                print(f"  SKIP {model} x {vignette}: no slice_{args.slice} found")
                continue

            done += 1
            print(f"  [{done}/{total}] {model} x {vignette} ...", end=" ", flush=True)

            try:
                result = await run_single(
                    model, vignette, history_path, args.trials, args.temperature,
                )
                results.append(result)
                print(
                    f"J={result['jaccard']:.3f} B={result['bertscore']:.3f} "
                    f"A={result['alignment']:.3f} ({result['elapsed']}s)"
                )
            except Exception as e:
                print(f"FAILED: {e}")
                results.append({
                    "model": model,
                    "vignette": vignette,
                    "error": str(e),
                })

    # Summary
    print(f"\nCompleted {len([r for r in results if 'error' not in r])}/{total} runs")
    if results:
        successful = [r for r in results if "jaccard" in r]
        if successful:
            avg_j = sum(r["jaccard"] for r in successful) / len(successful)
            avg_b = sum(r["bertscore"] for r in successful) / len(successful)
            print(f"Mean Jaccard: {avg_j:.3f}, Mean BERTScore: {avg_b:.3f}")


if __name__ == "__main__":
    asyncio.run(main())
