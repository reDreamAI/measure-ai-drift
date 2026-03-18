"""Run the full experiment: all evaluation targets x all vignettes x temperature scale.

Temperatures run in parallel for each model x vignette combination.
Optionally includes a therapy_temp run per model (vendor-recommended clinical temperature).

Usage:
    python scripts/run_experiment.py [--trials 10] [--slice 2]
    python scripts/run_experiment.py --temps 0.0 0.5 1.0   # custom subset
    python scripts/run_experiment.py --no-therapy-temp      # skip therapy_temp runs
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
DEFAULT_TEMPS = [0.0, 0.25, 0.5, 0.7, 1.0]

# Models with strict rate limits that cannot run temps in parallel
RATE_LIMITED_MODELS = {"trinity_large"}


def load_therapy_temps(config: dict) -> dict[str, float]:
    """Load therapy_temp values from models.yaml evaluation_targets."""
    temps = {}
    for t in config.get("evaluation_targets", []):
        if "therapy_temp" in t:
            temps[t["name"]] = t["therapy_temp"]
    return temps


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
    """Run one experiment (model x vignette x temperature) and return summary."""
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
        "temperature": temperature,
        "jaccard": metrics["jaccard_all"],
        "bertscore": metrics["bertscore_f1"],
        "alignment": metrics["alignment_mean"],
        "path": str(experiment.path),
        "elapsed": round(elapsed, 1),
    }


async def run_temps_parallel(
    model_name: str,
    vignette: str,
    history_path: Path,
    n_trials: int,
    temps: list[float],
) -> list[dict]:
    """Run all temperatures for one model x vignette in parallel."""
    tasks = [
        run_single(model_name, vignette, history_path, n_trials, temp)
        for temp in temps
    ]
    raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    results = []
    for temp, result in zip(temps, raw_results):
        if isinstance(result, Exception):
            results.append({
                "model": model_name,
                "vignette": vignette,
                "temperature": temp,
                "error": str(result),
            })
        else:
            results.append(result)
    return results


def print_result(r: dict) -> None:
    """Print a single run result."""
    if "error" in r:
        print(f"    T={r['temperature']}: FAILED: {r['error']}")
    else:
        print(
            f"    T={r['temperature']}: "
            f"J={r['jaccard']:.3f} B={r['bertscore']:.3f} "
            f"A={r['alignment']:.3f} ({r['elapsed']}s)"
        )


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run full experiment")
    parser.add_argument("--trials", "-n", type=int, default=10)
    parser.add_argument("--temps", type=float, nargs="+", default=DEFAULT_TEMPS,
                        help="Temperature scale (default: 0.0 0.25 0.5 0.75 1.0)")
    parser.add_argument("--slice", "-s", type=int, default=2)
    parser.add_argument("--no-therapy-temp", action="store_true",
                        help="Skip the extra therapy_temp run per model")
    args = parser.parse_args()

    temps = sorted(args.temps)

    config = load_config()
    targets = [
        t["name"]
        for t in config.get("evaluation_targets", [])
        if not t["name"].endswith("_test")
    ]
    therapy_temps = load_therapy_temps(config)

    # Determine which therapy_temps actually add a new data point
    # (skip if the therapy_temp already matches one of the scale temps)
    extra_therapy = {}
    if not args.no_therapy_temp:
        for model in targets:
            tt = therapy_temps.get(model)
            if tt is not None and tt not in temps:
                extra_therapy[model] = tt

    combos = len(targets) * len(VIGNETTES)
    scale_runs = combos * len(temps)
    extra_runs = len(extra_therapy) * len(VIGNETTES)
    total = scale_runs + extra_runs

    print(f"Experiment: {len(targets)} models x {len(VIGNETTES)} vignettes x {len(temps)} temps x slice_{args.slice}")
    print(f"  Models: {targets}")
    print(f"  Scale temps: {temps} (parallel per model x vignette)")
    if extra_therapy:
        print(f"  Extra therapy_temp runs: {extra_therapy}")
    print(f"  Trials per run: {args.trials}")
    print(f"  Total runs: {total} ({total * args.trials} trials)")
    print()

    results = []
    done_combos = 0

    for model in targets:
        # Build the temperature list for this model: scale + optional therapy_temp
        model_temps = list(temps)
        has_extra = model in extra_therapy
        if has_extra:
            model_temps = sorted(set(model_temps + [extra_therapy[model]]))

        for vignette in VIGNETTES:
            history_path = find_slice_path(vignette, args.slice)
            if history_path is None:
                print(f"  SKIP {model} x {vignette}: no slice_{args.slice} found")
                continue

            done_combos += 1
            sequential = model in RATE_LIMITED_MODELS
            mode_label = "sequential, rate-limited" if sequential else "parallel"
            extra_label = f" +rec {extra_therapy[model]}" if has_extra else ""
            print(f"  [{done_combos}/{combos}] {model} x {vignette} x {len(model_temps)} temps ({mode_label}{extra_label}) ...", flush=True)

            start = time.time()
            if sequential:
                batch = []
                for temp in model_temps:
                    try:
                        result = await run_single(model, vignette, history_path, args.trials, temp)
                        batch.append(result)
                    except Exception as e:
                        batch.append({"model": model, "vignette": vignette, "temperature": temp, "error": str(e)})
            else:
                batch = await run_temps_parallel(
                    model, vignette, history_path, args.trials, model_temps,
                )
            batch_elapsed = time.time() - start

            for r in batch:
                results.append(r)
                print_result(r)

            print(f"    batch wall-clock: {batch_elapsed:.0f}s")

    # Summary
    successful = [r for r in results if "jaccard" in r]
    print(f"\nCompleted {len(successful)}/{total} runs")
    if successful:
        avg_j = sum(r["jaccard"] for r in successful) / len(successful)
        avg_b = sum(r["bertscore"] for r in successful) / len(successful)
        print(f"Mean Jaccard: {avg_j:.3f}, Mean BERTScore: {avg_b:.3f}")

        # Per-temperature summary
        all_temps_seen = sorted(set(r["temperature"] for r in successful))
        for temp in all_temps_seen:
            temp_runs = [r for r in successful if r["temperature"] == temp]
            t_j = sum(r["jaccard"] for r in temp_runs) / len(temp_runs)
            t_b = sum(r["bertscore"] for r in temp_runs) / len(temp_runs)
            marker = ""
            rec_models = [m for m, t in extra_therapy.items() if t == temp]
            if rec_models:
                marker = f" (rec for: {', '.join(rec_models)})"
            print(f"  T={temp}: J={t_j:.3f} B={t_b:.3f} ({len(temp_runs)} runs){marker}")


if __name__ == "__main__":
    asyncio.run(main())
