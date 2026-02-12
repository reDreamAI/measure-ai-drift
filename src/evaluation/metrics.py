"""Evaluation metrics for rescripting stability experiments.

Implements the three-level evaluation framework from the thesis:
- Level 3.1: Cognitive Stability (plan consistency via Jaccard)
- Level 3.2: Output Consistency (semantic stability via BERTScore)
- Level 3.3: Plan-Output Alignment (intervention fit via LLM judge)
"""

from __future__ import annotations

import logging
import re
from itertools import combinations
from typing import Any

logger = logging.getLogger(__name__)


PLAN_BLOCK_RE = re.compile(r"<plan>(.*?)</plan>", re.DOTALL | re.IGNORECASE)

# Valid strategy category IDs
VALID_CATEGORIES = {
    "agency",
    "safety",
    "cognitive_reframe",
    "emotional_regulation",
    "social_support",
    "sensory_modulation",
}


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

    from bert_score import BERTScorer

    # Build all pairs
    refs = []
    cands = []
    for a, b in combinations(responses, 2):
        refs.append(a)
        cands.append(b)

    scorer = BERTScorer(model_type=model_type, lang="en")
    # Fix DeBERTa tokenizer overflow (model_max_length ≈ 10^30 overflows Rust backend).
    # All BERTScore models truncate at 510 tokens regardless.
    scorer._tokenizer.model_max_length = 512

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
        lines.append(f"- **{s['id']}** ({s['name']}): {s['description']}")
    return "\n".join(lines)


def _build_strategies_block(strategies: set[str], taxonomy: dict[str, Any]) -> str:
    """Format declared strategies with their descriptions for the judge."""
    lookup = {s["id"]: s for s in taxonomy.get("strategies", [])}
    lines = []
    for sid in sorted(strategies):
        info = lookup.get(sid)
        if info:
            lines.append(f"- **{sid}** ({info['name']}): {info['description']}")
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


async def compute_alignment(
    strategy_sets: list[set[str]],
    responses: list[str],
    taxonomy: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate plan-output alignment using an LLM judge.

    Implements Level 3.3 from the thesis: checks whether the therapist's
    response actually implements the strategies declared in its <plan>.
    Uses a ternary scale (0=absent, 1=partial, 2=implemented) normalised
    to 0.0-1.0 per trial.

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

    # Create judge provider (Gemini Flash at t=0.0 by default)
    judge = create_provider("judge")

    per_trial: list[float] = []
    raw_judgments: list[dict[str, Any]] = []
    strategy_scores: dict[str, list[int]] = {}

    for i, (strategies, response) in enumerate(zip(strategy_sets, responses)):
        if not strategies or not response or not response.strip():
            per_trial.append(0.0)
            raw_judgments.append({"trial": i + 1, "skipped": True, "reason": "empty strategies or response"})
            continue

        # Build user message
        strategies_block = _build_strategies_block(strategies, taxonomy)
        user_msg = user_template.replace("{strategies_block}", strategies_block).replace("{response}", response)

        try:
            raw_output, usage = await judge.generate(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg},
                ],
            )

            parsed = _parse_judgment(raw_output, strategies)

            # Per-trial alignment = mean score / 2 (normalised to 0-1)
            scores = [parsed[sid]["score"] for sid in strategies if sid in parsed]
            trial_alignment = (sum(scores) / (len(scores) * 2)) if scores else 0.0

            per_trial.append(trial_alignment)
            raw_judgments.append({
                "trial": i + 1,
                "raw_output": raw_output,
                "parsed": {sid: parsed[sid] for sid in strategies if sid in parsed},
                "trial_alignment": trial_alignment,
                "usage": usage,
            })

            # Accumulate per-strategy scores
            for sid in strategies:
                if sid in parsed:
                    strategy_scores.setdefault(sid, []).append(parsed[sid]["score"])

        except Exception as e:
            logger.warning("Judge call failed for trial %d: %s", i + 1, e)
            per_trial.append(0.0)
            raw_judgments.append({"trial": i + 1, "error": str(e)})

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
