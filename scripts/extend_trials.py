"""Extend existing experiment runs with extra trials and recompute metrics.

Iterates over all runs in experiments/latest/, adds N extra trials to each,
then recomputes metrics (Jaccard, BERTScore, Alignment) over all trials.

Existing trial files (trial_01..10) are preserved. New trials are numbered
from trial_11 onward. The original metrics.json is backed up as
metrics_n10.json before overwriting.

Usage:
    python scripts/extend_trials.py                    # +10 trials (default)
    python scripts/extend_trials.py --extra 15         # +15 trials
    python scripts/extend_trials.py --models mistral_large qwen35_27b  # subset
    python scripts/extend_trials.py --dry-run          # show what would run
"""

from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from src.core import Conversation
from src.evaluation.sampler import Sampler, TrialResult
from src.evaluation.metrics import (
    extract_plan_strategies,
    compute_validity_rate,
    compute_pairwise_jaccard,
    compute_modal_set_agreement,
    compute_pairwise_bertscore,
    compute_alignment,
)
from src.llm.provider import load_config, create_provider


def format_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"


def load_existing_trials(run_dir: Path) -> list[dict]:
    """Load all existing trial JSON files from a run directory."""
    trials = []
    for p in sorted((run_dir / "trials").glob("trial_*.json")):
        with open(p) as f:
            trials.append(json.load(f))
    return trials


def count_existing_trials(run_dir: Path) -> int:
    return len(list((run_dir / "trials").glob("trial_*.json")))


async def extend_run(
    run_dir: Path,
    extra: int,
    provider_cache: dict,
) -> dict:
    """Add extra trials to a single run and recompute metrics."""
    config_path = run_dir / "config.yaml"
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    model = cfg["model"]
    temperature = cfg["temperature"]
    existing_count = count_existing_trials(run_dir)

    # Load frozen history
    with open(run_dir / "frozen_history.json") as f:
        history_data = json.load(f)
    frozen_history = Conversation.from_dict(history_data)

    # Create provider (cached per model)
    if model not in provider_cache:
        provider_cache[model] = create_provider(model)
    provider = provider_cache[model]

    # Run extra trials
    from src.stacks.evaluation_stack import EvaluationStack
    stack = EvaluationStack(language="en", therapist_provider=provider, mode="fused")
    sampler = Sampler(language="en", stack=stack, mode="fused")

    new_results = await sampler.run(
        frozen_history,
        n_trials=extra,
        temperature=temperature,
    )

    # Save new trial files (numbered after existing)
    trials_dir = run_dir / "trials"
    for i, result in enumerate(new_results, existing_count + 1):
        trial_path = trials_dir / f"trial_{i:02d}.json"
        trial_data = {
            "temperature": result.temperature,
            "plan": result.plan,
            "response": result.response,
            "plan_usage": result.plan_usage,
            "response_usage": result.response_usage,
            "strategies": list(extract_plan_strategies(result.plan)),
        }
        with open(trial_path, "w") as f:
            json.dump(trial_data, f, indent=2, ensure_ascii=False)

    # Reload ALL trials (old + new) for metric computation
    all_trials = load_existing_trials(run_dir)
    total = len(all_trials)

    strategy_sets = [
        set(t.get("strategies", [])) or extract_plan_strategies(t.get("plan", ""))
        for t in all_trials
    ]
    responses = [t["response"] for t in all_trials]

    # BERTScore over all trials
    bertscore = compute_pairwise_bertscore(responses)

    # Alignment (judge) -- only judge the NEW trials, merge with old judgments
    from src.core.config_loader import load_strategy_taxonomy
    _all_cfg = load_config()
    _experiment_names = {
        t["name"] for t in _all_cfg.get("evaluation_targets", [])
        if not t.get("name", "").endswith("_test")
    }
    is_experiment = model in _experiment_names
    taxonomy = load_strategy_taxonomy()

    alignment = await compute_alignment(
        strategy_sets, responses, taxonomy, experiment=is_experiment,
    )

    # Backup old metrics, then overwrite
    metrics_path = run_dir / "metrics.json"
    backup_path = run_dir / f"metrics_n{existing_count}.json"
    if metrics_path.exists() and not backup_path.exists():
        shutil.copy2(metrics_path, backup_path)

    # Update config with new trial count
    cfg["n_trials"] = total
    with open(config_path, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)

    # Strategy counts
    counts: dict[str, int] = {}
    for ss in strategy_sets:
        for s in ss:
            counts[s] = counts.get(s, 0) + 1
    counts = dict(sorted(counts.items(), key=lambda x: -x[1]))

    metrics = {
        "n_trials": total,
        "temperature": cfg.get("temperature", 0.0),
        "slice": cfg.get("slice"),
        "validity_rate": compute_validity_rate(strategy_sets),
        "jaccard_all": compute_pairwise_jaccard(strategy_sets, only_valid=False),
        "jaccard_valid_only": compute_pairwise_jaccard(strategy_sets, only_valid=True),
        "modal_set_agreement": compute_modal_set_agreement(strategy_sets),
        "bertscore_f1": bertscore["f1"],
        "bertscore_precision": bertscore["precision"],
        "bertscore_recall": bertscore["recall"],
        "alignment_mean": alignment["mean_alignment"],
        "alignment_per_trial": alignment["per_trial"],
        "alignment_per_strategy": alignment["per_strategy"],
        "strategy_counts": counts,
    }

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    # Save updated judgments
    with open(run_dir / "judgments.json", "w") as f:
        json.dump(alignment["raw_judgments"], f, indent=2, ensure_ascii=False)

    return {
        "run": run_dir.name,
        "model": model,
        "vignette": cfg["vignette"],
        "temperature": temperature,
        "trials": f"{existing_count} -> {total}",
        "jaccard": metrics["jaccard_all"],
        "bertscore": metrics["bertscore_f1"],
        "alignment": metrics["alignment_mean"],
    }


async def main() -> None:
    parser = argparse.ArgumentParser(description="Extend existing runs with extra trials")
    parser.add_argument("--extra", type=int, default=10,
                        help="Number of extra trials per run (default: 10)")
    parser.add_argument("--runs-dir", type=Path, default=Path("experiments/latest"),
                        help="Directory containing runs to extend")
    parser.add_argument("--models", type=str, nargs="+", default=None,
                        help="Only extend these models")
    parser.add_argument("--temps", type=float, nargs="+", default=None,
                        help="Only extend runs at these temperatures")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would run without executing")
    args = parser.parse_args()

    runs_dir = args.runs_dir.resolve() if args.runs_dir.is_symlink() else args.runs_dir

    # Collect runs to extend (skip already-extended ones)
    run_dirs = []
    skipped = 0
    for d in sorted(runs_dir.iterdir()):
        if not d.is_dir() or not (d / "config.yaml").exists():
            continue
        with open(d / "config.yaml") as f:
            cfg = yaml.safe_load(f)
        if args.models and cfg["model"] not in args.models:
            continue
        if args.temps and cfg["temperature"] not in args.temps:
            continue
        # Skip runs that already have enough trials
        n_existing = count_existing_trials(d)
        if n_existing >= 10 + args.extra:
            skipped += 1
            continue
        run_dirs.append(d)

    if skipped:
        print(f"Skipped {skipped} runs already at {10 + args.extra}+ trials")

    if not run_dirs:
        print("No matching runs found.")
        return

    # Summary
    models = sorted(set(
        yaml.safe_load(open(d / "config.yaml"))["model"] for d in run_dirs
    ))
    temps = sorted(set(
        yaml.safe_load(open(d / "config.yaml"))["temperature"] for d in run_dirs
    ))
    total_existing = sum(count_existing_trials(d) for d in run_dirs)
    total_new = len(run_dirs) * args.extra
    total_after = total_existing + total_new

    print(f"Extend {len(run_dirs)} runs with +{args.extra} trials each")
    print(f"  Models: {models}")
    print(f"  Temps: {temps}")
    print(f"  Trials: {total_existing} existing + {total_new} new = {total_after} total")
    print(f"  Judge calls: {total_new} (Flash) + Pro fallback if needed")
    print()

    if args.dry_run:
        for d in run_dirs:
            cfg = yaml.safe_load(open(d / "config.yaml"))
            n = count_existing_trials(d)
            print(f"  {cfg['model']:20s} x {cfg['vignette']:12s} T={cfg['temperature']}: {n} -> {n + args.extra}")
        return

    # Run extensions sequentially (to respect rate limits)
    provider_cache: dict = {}
    done = 0
    failed = 0
    start = time.time()

    for run_dir in run_dirs:
        cfg = yaml.safe_load(open(run_dir / "config.yaml"))
        n_before = count_existing_trials(run_dir)
        label = f"{cfg['model']} x {cfg['vignette']} T={cfg['temperature']}"

        try:
            result = await extend_run(run_dir, args.extra, provider_cache)
            done += 1
            elapsed = time.time() - start
            eta = elapsed / done * (len(run_dirs) - done) if done > 0 else 0
            print(
                f"  [{done}/{len(run_dirs)}] {label}: "
                f"{result['trials']} trials, J={result['jaccard']:.3f} "
                f"B={result['bertscore']:.3f} A={result['alignment']:.3f} "
                f"(ETA {format_time(eta)})"
            )
        except Exception as e:
            done += 1
            failed += 1
            print(f"  [{done}/{len(run_dirs)}] {label}: FAILED: {e}")

    total_time = time.time() - start
    print(f"\nDone: {done - failed}/{len(run_dirs)} extended in {format_time(total_time)}")
    if failed:
        print(f"  {failed} failed")


if __name__ == "__main__":
    asyncio.run(main())
