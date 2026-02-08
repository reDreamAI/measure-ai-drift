"""Evaluation metrics for rescripting stability experiments.

Implements the three-level evaluation framework from the thesis:
- Level 3.1: Cognitive Stability (plan consistency via Jaccard)
- Level 3.2: Output Consistency (semantic stability via BERTScore) - TODO
- Level 3.3: Plan-Output Alignment (intervention fit) - TODO
"""

from __future__ import annotations

import re
from itertools import combinations


PLAN_BLOCK_RE = re.compile(r"<plan>(.*?)</plan>", re.DOTALL | re.IGNORECASE)

# Valid strategy category IDs
VALID_CATEGORIES = {
    "empowerment",
    "safety",
    "cognitive_reframe",
    "emotional_regulation",
    "mastery",
    "social_support",
    "sensory_modulation",
    "gradual_exposure",
}


def extract_plan_strategies(plan_text: str) -> set[str]:
    """Extract strategy categories from a <plan>...</plan> block.

    Expects simple format: <plan>category1 / category2</plan>
    Returns only valid category IDs from the taxonomy.

    Args:
        plan_text: Raw model output containing a <plan> block.

    Returns:
        Set of valid strategy category IDs (e.g., {"mastery", "safety"}).
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
        >>> validate_plan_length({"empowerment", "safety"})
        True
        >>> validate_plan_length({"empowerment", "safety", "mastery"})
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
        >>> sets = [{"empowerment", "safety"}, {"empowerment", "mastery"}]
        >>> compute_pairwise_jaccard(sets)
        0.5  # |{empowerment}| / |{empowerment, safety, mastery}|
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
