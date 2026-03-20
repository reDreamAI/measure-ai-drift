"""Evaluation metrics for rescripting stability experiments.

Implements the three-level evaluation framework from the thesis:
- Level 3.1: Cognitive Stability (plan consistency via Jaccard)
- Level 3.2: Output Consistency (semantic stability via BERTScore)
- Level 3.3: Plan-Output Alignment (intervention fit via LLM judge)
"""

from __future__ import annotations

import asyncio
import logging
import re
from itertools import combinations
from typing import Any

logger = logging.getLogger(__name__)


PLAN_BLOCK_RE = re.compile(r"<plan>(.*?)</plan>", re.DOTALL | re.IGNORECASE)

def _load_valid_categories() -> set[str]:
    """Derive valid category IDs from the strategy taxonomy (single source of truth)."""
    from src.core.config_loader import load_strategy_taxonomy
    return {s["id"] for s in load_strategy_taxonomy().get("strategies", [])}


VALID_CATEGORIES = _load_valid_categories()


def extract_plan_strategies(plan_text: str) -> set[str]:
    """Extract strategy categories from a <plan>...</plan> block.

    Expects simple format: <plan>category1 / category2</plan>
    Returns only valid category IDs from the taxonomy.

    Args:
        plan_text: Raw model output containing a <plan> block.

    Returns:
        Set of valid strategy category IDs (e.g., {"agency", "safety"}).
    """
    match = PLAN_BLOCK_RE.search(plan_text or "")
    if not match:
        return set()

    block = match.group(1).strip()
    if not block:
        return set()

    # Split by " / " and normalize
    parts = [p.strip().lower() for p in block.split("/")]

    # Filter to valid categories only
    strategies = {p for p in parts if p in VALID_CATEGORIES}

    return strategies


def validate_plan_length(strategies: set[str], max_allowed: int = 2) -> bool:
    """Check if plan has valid number of strategies (1-2).
    
    Plans must have 1 or 2 strategies to be valid for thesis evaluation.
    
    Args:
        strategies: Set of extracted strategy bullets
        max_allowed: Maximum allowed strategies (default: 2)
        
    Returns:
        True if plan has valid number of strategies (1 <= n <= max_allowed)
        
    Example:
        >>> validate_plan_length({"agency", "safety"})
        True
        >>> validate_plan_length({"agency", "safety", "cognitive_reframe"})
        False
    """
    return 1 <= len(strategies) <= max_allowed


def compute_validity_rate(strategy_sets: list[set[str]], max_allowed: int = 2) -> float:
    """Compute fraction of plans that are valid (1-2 strategies).
    
    Useful for checking how well the model follows the 1-2 strategy constraint.
    
    Args:
        strategy_sets: List of strategy sets from multiple trials
        max_allowed: Maximum allowed strategies (default: 2)
        
    Returns:
        Fraction of valid plans (0.0-1.0)
        
    Example:
        >>> sets = [{"a", "b"}, {"c"}, {"d", "e", "f"}]  # 2 valid, 1 invalid
        >>> compute_validity_rate(sets)
        0.6666...
    """
    if not strategy_sets:
        return 0.0
    
    valid_count = sum(1 for s in strategy_sets if validate_plan_length(s, max_allowed))
    return valid_count / len(strategy_sets)


def compute_modal_set_agreement(strategy_sets: list[set[str]]) -> float:
    """Compute modal-set agreement: fraction of trials matching the most common strategy set.

    Complements Jaccard by measuring exact agreement rather than overlap.
    With discrete strategy picks (1-2 from 6), this is often more informative
    than mean pairwise Jaccard.

    Args:
        strategy_sets: List of strategy sets (one per trial).

    Returns:
        Fraction of trials matching the mode (0.0-1.0).

    Example:
        >>> sets = [{"a", "b"}, {"a", "b"}, {"a", "c"}]
        >>> compute_modal_set_agreement(sets)
        0.6666...
    """
    if not strategy_sets:
        return 0.0

    from collections import Counter
    # Convert sets to frozensets for hashing
    counts = Counter(frozenset(s) for s in strategy_sets)
    mode_count = counts.most_common(1)[0][1]
    return mode_count / len(strategy_sets)


def compute_pairwise_jaccard(
    sets: list[set[str]],
    only_valid: bool = False,
    max_allowed: int = 2,
) -> float:
    """Compute mean pairwise Jaccard similarity.
    
    Implements Level 3.1 (Cognitive Stability) from the thesis:
    Measures consistency of therapeutic strategies across stochastic trials.
    
    Args:
        sets: List of strategy sets (one per trial)
        only_valid: If True, exclude invalid plans (>2 strategies)
        max_allowed: Maximum strategies for validity check
        
    Returns:
        Mean Jaccard similarity across all pairs (0.0-1.0)
        
    Example:
        >>> sets = [{"agency", "safety"}, {"agency", "cognitive_reframe"}]
        >>> compute_pairwise_jaccard(sets)
        0.333...  # |{agency}| / |{agency, safety, cognitive_reframe}|
    """
    if only_valid:
        sets = [s for s in sets if validate_plan_length(s, max_allowed)]
    
    if len(sets) < 2:
        return 1.0

    scores: list[float] = []
    for a, b in combinations(sets, 2):
        if not a and not b:
            scores.append(1.0)
            continue
        union = a.union(b)
        if not union:
            scores.append(0.0)
            continue
        scores.append(len(a.intersection(b)) / len(union))

    return sum(scores) / len(scores) if scores else 0.0


_BERTSCORE_CACHE: dict[str, Any] = {}


def _get_bertscorer(model_type: str = "microsoft/deberta-xlarge-mnli") -> Any:
    """Return a cached BERTScorer instance (loads model only once per process)."""
    if model_type not in _BERTSCORE_CACHE:
        from bert_score import BERTScorer
        scorer = BERTScorer(model_type=model_type, lang="en")
        scorer._tokenizer.model_max_length = 512
        _BERTSCORE_CACHE[model_type] = scorer
    return _BERTSCORE_CACHE[model_type]


def compute_pairwise_bertscore(
    responses: list[str],
    model_type: str = "microsoft/deberta-xlarge-mnli",
) -> dict[str, float]:
    """Compute mean pairwise BERTScore across trial responses.

    Implements Level 3.2 (Output Consistency) from the thesis:
    Measures semantic similarity of therapist responses across trials.
    Uses DeBERTa-XLarge-MNLI (ranked #1 across 130+ models for correlation
    with human judgments). NLI fine-tuning makes it well-suited for
    comparing semantic equivalence of therapeutic responses.

    Args:
        responses: List of therapist response strings (one per trial)
        model_type: HuggingFace model for BERTScore

    Returns:
        Dict with mean precision, recall, and F1 scores

    Example:
        >>> responses = ["Let's modify the dream.", "Let's change the nightmare."]
        >>> scores = compute_pairwise_bertscore(responses)
        >>> scores["f1"]  # high similarity for semantically equivalent responses
    """
    # Filter empty responses (empty strings crash DeBERTa tokenizer)
    responses = [r for r in responses if r and r.strip()]

    if len(responses) < 2:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}

    # Build all pairs
    refs = []
    cands = []
    for a, b in combinations(responses, 2):
        refs.append(a)
        cands.append(b)

    scorer = _get_bertscorer(model_type)
    P, R, F1 = scorer.score(cands, refs)

    return {
        "precision": P.mean().item(),
        "recall": R.mean().item(),
        "f1": F1.mean().item(),
    }


# ---------------------------------------------------------------------------
# Level 3.3 — Plan-Output Alignment
# ---------------------------------------------------------------------------

# Matches lines like: "agency: reasoning text | score: 2"
_JUDGMENT_LINE_RE = re.compile(
    r"^(\w+):\s*(.+?)\s*\|\s*score:\s*([012])\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def _build_taxonomy_block(taxonomy: dict[str, Any]) -> str:
    """Format strategy definitions for the judge prompt."""
    lines = []
    for s in taxonomy.get("strategies", []):
        lines.append(f"- **{s['id']}**: {s['description']}")
    return "\n".join(lines)


def _build_strategies_block(strategies: set[str], taxonomy: dict[str, Any]) -> str:
    """Format declared strategies with their descriptions for the judge."""
    lookup = {s["id"]: s for s in taxonomy.get("strategies", [])}
    lines = []
    for sid in sorted(strategies):
        info = lookup.get(sid)
        if info:
            lines.append(f"- **{sid}**: {info['description']}")
        else:
            lines.append(f"- **{sid}**")
    return "\n".join(lines)


def _parse_judgment(raw: str, expected: set[str]) -> dict[str, dict[str, Any]]:
    """Parse judge output into per-strategy scores.

    Returns dict mapping strategy_id -> {"reasoning": str, "score": int}.
    Missing or unparseable strategies default to score 0.
    """
    parsed: dict[str, dict[str, Any]] = {}
    for match in _JUDGMENT_LINE_RE.finditer(raw):
        sid = match.group(1).lower()
        reasoning = match.group(2).strip()
        score = int(match.group(3))
        parsed[sid] = {"reasoning": reasoning, "score": score}

    # Fill missing strategies with score 0
    for sid in expected:
        if sid not in parsed:
            logger.warning("Judge did not score strategy '%s' — defaulting to 0", sid)
            parsed[sid] = {"reasoning": "not scored by judge", "score": 0}

    return parsed


# Semaphore to limit concurrent judge calls (Gemini free tier: 25 RPM)
_JUDGE_SEMAPHORE: asyncio.Semaphore | None = None

def _get_judge_semaphore(max_concurrent: int = 5) -> asyncio.Semaphore:
    """Get or create the judge semaphore (lazy init for the current event loop)."""
    global _JUDGE_SEMAPHORE
    if _JUDGE_SEMAPHORE is None:
        _JUDGE_SEMAPHORE = asyncio.Semaphore(max_concurrent)
    return _JUDGE_SEMAPHORE


async def _judge_single_trial(
    judge: Any,
    system_prompt: str,
    user_msg: str,
    strategies: set[str],
    trial_index: int,
    timeout_seconds: int = 120,
    max_retries: int = 3,
) -> tuple[float, dict[str, Any], dict[str, list[int]]]:
    """Judge one trial with a timeout, semaphore, and retry on 429. Returns (score, judgment_dict, strategy_scores)."""
    sem = _get_judge_semaphore()

    for attempt in range(max_retries + 1):
        try:
            async with sem:
                raw_output, usage = await asyncio.wait_for(
                    judge.generate([
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg},
                    ]),
                    timeout=timeout_seconds,
                )

            parsed = _parse_judgment(raw_output, strategies)
            scores = [parsed[sid]["score"] for sid in strategies if sid in parsed]
            trial_alignment = (sum(scores) / (len(scores) * 2)) if scores else 0.0

            strat_scores: dict[str, list[int]] = {}
            for sid in strategies:
                if sid in parsed:
                    strat_scores.setdefault(sid, []).append(parsed[sid]["score"])

            judgment = {
                "trial": trial_index,
                "raw_output": raw_output,
                "parsed": {sid: parsed[sid] for sid in strategies if sid in parsed},
                "trial_alignment": trial_alignment,
                "usage": usage,
            }
            return trial_alignment, judgment, strat_scores

        except asyncio.TimeoutError:
            logger.warning("Judge call timed out for trial %d after %ds", trial_index, timeout_seconds)
            return 0.0, {"trial": trial_index, "error": f"timeout after {timeout_seconds}s"}, {}
        except Exception as e:
            err_str = str(e)
            if "429" in err_str and attempt < max_retries:
                wait = 15 * (attempt + 1)
                logger.info("Judge 429 for trial %d, retry %d/%d in %ds", trial_index, attempt + 1, max_retries, wait)
                await asyncio.sleep(wait)
                continue
            logger.warning("Judge call failed for trial %d: %s", trial_index, e)
            return 0.0, {"trial": trial_index, "error": err_str}, {}


async def compute_alignment(
    strategy_sets: list[set[str]],
    responses: list[str],
    taxonomy: dict[str, Any],
    experiment: bool = False,
) -> dict[str, Any]:
    """Evaluate plan-output alignment using an LLM judge.

    Implements Level 3.3 from the thesis: checks whether the therapist's
    response actually implements the strategies declared in its <plan>.
    Uses a ternary scale (0=absent, 1=partial, 2=implemented) normalised
    to 0.0-1.0 per trial.

    Judge calls run in parallel with a per-call timeout (120s).

    Args:
        strategy_sets: List of strategy sets (one per trial).
        responses: List of therapist response strings (one per trial).
        taxonomy: Loaded strategy_taxonomy.yaml dict.

    Returns:
        Dict with keys: mean_alignment, per_trial, per_strategy, raw_judgments.
    """
    from src.core.config_loader import load_yaml, PROMPTS_DIR
    from src.llm.provider import create_provider

    # Load judge prompt template
    prompt_data = load_yaml(PROMPTS_DIR / "evaluation" / "alignment_judge.yaml")
    system_template = prompt_data["system_prompt"]
    user_template = prompt_data["user_template"]

    # Build taxonomy block (shared across all trials)
    taxonomy_block = _build_taxonomy_block(taxonomy)
    system_prompt = system_template.replace("{taxonomy_block}", taxonomy_block)

    # Create judge provider: flash-lite for testing, pro for experiment
    judge = create_provider("judge", experiment=experiment)

    # Build tasks for all trials
    tasks = []
    skip_indices: dict[int, dict] = {}

    for i, (strategies, response) in enumerate(zip(strategy_sets, responses)):
        if not strategies or not response or not response.strip():
            skip_indices[i] = {"trial": i + 1, "skipped": True, "reason": "empty strategies or response"}
            continue

        strategies_block = _build_strategies_block(strategies, taxonomy)
        user_msg = user_template.replace("{strategies_block}", strategies_block).replace("{response}", response)
        tasks.append((i, _judge_single_trial(judge, system_prompt, user_msg, strategies, i + 1)))

    # Run all judge calls in parallel
    results_map: dict[int, tuple[float, dict, dict]] = {}
    if tasks:
        gathered = await asyncio.gather(*(t[1] for t in tasks))
        for (idx, _), result in zip(tasks, gathered):
            results_map[idx] = result

    # Reassemble in order
    per_trial: list[float] = []
    raw_judgments: list[dict[str, Any]] = []
    strategy_scores: dict[str, list[int]] = {}

    for i in range(len(strategy_sets)):
        if i in skip_indices:
            per_trial.append(0.0)
            raw_judgments.append(skip_indices[i])
        elif i in results_map:
            score, judgment, strat_scores = results_map[i]
            per_trial.append(score)
            raw_judgments.append(judgment)
            for sid, scores_list in strat_scores.items():
                strategy_scores.setdefault(sid, []).extend(scores_list)

    # Aggregate
    mean_alignment = sum(per_trial) / len(per_trial) if per_trial else 0.0
    per_strategy = {
        sid: sum(scores) / (len(scores) * 2) if scores else 0.0
        for sid, scores in strategy_scores.items()
    }

    return {
        "mean_alignment": mean_alignment,
        "per_trial": per_trial,
        "per_strategy": per_strategy,
        "raw_judgments": raw_judgments,
    }
