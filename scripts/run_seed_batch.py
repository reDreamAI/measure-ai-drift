"""Run Mistral Large 3 seed experiment: same conditions as main experiment
(slice 2, T=0.075 and T=0.15, 20 trials) but with a fixed seed per trial.

Seed strategy: seed = trial_number (1-20), so each trial gets a deterministic
seed but different trials get different seeds. This tests whether fixing the
seed eliminates the variance we observed in the unseeded runs.

Output: experiments/runs/seed_batch/
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import yaml
from src.core import Conversation
from src.evaluation.metrics import (
    extract_plan_strategies,
    compute_validity_rate,
    compute_pairwise_jaccard,
    compute_modal_set_agreement,
    compute_pairwise_bertscore,
    compute_alignment,
)
from src.llm.provider import create_provider, load_config
from src.core.config_loader import load_strategy_taxonomy

MODEL = "mistral_large"
SLICE = 2
TEMPS = [0.0, 0.075, 0.15]
N_TRIALS = 20
BATCH_DIR = Path("experiments/runs/seed_batch")
FROZEN_HISTORIES = Path("data/synthetic/frozen_histories")
VIGNETTES = ["anxious", "avoidant", "cooperative", "resistant", "skeptic", "trauma"]


def find_slice_path(vignette: str, slice_num: int) -> Path | None:
    for d in FROZEN_HISTORIES.iterdir():
        if d.is_dir() and f"frozen_{vignette}_" in d.name:
            path = d / f"slice_{slice_num}.json"
            if path.exists():
                return path
    return None


async def run_seeded_trial(provider, messages, temperature, seed):
    """Single LLM call with seed."""
    output, usage = await provider.generate(
        messages, temperature=temperature, seed=seed
    )
    return output.strip(), usage


async def run_condition(vignette: str, temperature: float) -> dict:
    """Run 20 seeded trials for one vignette x temperature."""
    from datetime import datetime
    from src.stacks.evaluation_stack import EvaluationStack

    history_path = find_slice_path(vignette, SLICE)
    if not history_path:
        print(f"  SKIP: no slice {SLICE} for {vignette}")
        return {"error": f"no slice {SLICE}"}

    with open(history_path) as f:
        history_data = json.load(f)
    frozen_history = Conversation.from_dict(history_data)

    provider = create_provider(MODEL)

    # Build the fused prompt (same as EvaluationStack)
    stack = EvaluationStack(language="en", therapist_provider=provider, mode="fused")
    context = stack._build_history_context(frozen_history)
    fused_prompt = stack._fused_prompt

    # Create run directory
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = BATCH_DIR / f"{ts}_{MODEL}_{vignette}"
    run_dir.mkdir(parents=True, exist_ok=True)
    trials_dir = run_dir / "trials"
    trials_dir.mkdir(exist_ok=True)

    # Save frozen history
    with open(run_dir / "frozen_history.json", "w") as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False, default=str)

    # Save config
    config = {
        "model": MODEL,
        "vignette": vignette,
        "n_trials": N_TRIALS,
        "temperature": temperature,
        "slice": SLICE,
        "seed_strategy": "fixed_42",
        "language": "en",
        "mode": "fused",
        "timestamp": ts,
    }
    with open(run_dir / "config.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    # Run trials with seeds
    messages = [
        {"role": "system", "content": fused_prompt},
        {"role": "user", "content": context},
    ]

    results = []
    for trial_num in range(1, N_TRIALS + 1):
        seed = 42  # Same seed every trial: tests if seed = deterministic output
        output, usage = await run_seeded_trial(
            provider, messages, temperature, seed
        )

        plan, response = stack._parse_plan(output)
        strategies = list(extract_plan_strategies(plan))

        trial_data = {
            "temperature": temperature,
            "seed": seed,
            "plan": plan,
            "response": response,
            "plan_usage": usage,
            "response_usage": {},
            "strategies": strategies,
        }

        trial_path = trials_dir / f"trial_{trial_num:02d}.json"
        with open(trial_path, "w") as f:
            json.dump(trial_data, f, indent=2, ensure_ascii=False)

        results.append(trial_data)
        print(f"    trial {trial_num:2d}: seed={seed} strategies={strategies}")

    # Compute metrics
    strategy_sets = [set(r["strategies"]) for r in results]
    responses = [r["response"] for r in results]
    bertscore = compute_pairwise_bertscore(responses)
    taxonomy = load_strategy_taxonomy()
    alignment = await compute_alignment(
        strategy_sets, responses, taxonomy, experiment=True,
    )

    metrics = {
        "n_trials": N_TRIALS,
        "temperature": temperature,
        "slice": SLICE,
        "seed_strategy": "fixed_42",
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
    }

    with open(run_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    with open(run_dir / "judgments.json", "w") as f:
        json.dump(alignment["raw_judgments"], f, indent=2, ensure_ascii=False)

    print(f"  -> J={metrics['jaccard_all']:.3f} B={metrics['bertscore_f1']:.3f} A={metrics['alignment_mean']:.3f}")
    return metrics


async def main():
    print(f"Seed batch: {MODEL}, slice {SLICE}, temps {TEMPS}, {N_TRIALS} trials")
    print(f"Output: {BATCH_DIR}/")
    print(f"Seed strategy: fixed seed=42 for all trials")
    print("=" * 60)

    total = len(VIGNETTES) * len(TEMPS)
    done = 0
    failed = 0
    start = time.time()

    for vignette in VIGNETTES:
        for temp in TEMPS:
            done += 1
            print(f"\n[{done}/{total}] {vignette} T={temp}")
            try:
                await run_condition(vignette, temp)
            except Exception as e:
                failed += 1
                print(f"  FAILED: {e}")

    elapsed = time.time() - start
    m, s = divmod(int(elapsed), 60)
    print(f"\nDone: {done - failed}/{total} succeeded, {failed} failed in {m}m{s}s")


if __name__ == "__main__":
    asyncio.run(main())
