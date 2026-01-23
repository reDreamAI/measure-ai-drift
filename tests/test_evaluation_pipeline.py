"""Mock-based tests for evaluation pipeline structure."""

from __future__ import annotations

from src.evaluation.metrics import (
    compute_pairwise_jaccard,
    compute_validity_rate,
    extract_plan_strategies,
    validate_plan_length,
)
from src.stacks.evaluation_stack import EvaluationStack, TrialResult


class DummyProvider:
    """Minimal provider stub for evaluation stack tests."""

    async def generate(self, messages, **kwargs):
        return "stub", {}


def test_extract_plan_strategies_basic() -> None:
    plan_text = """
<plan>
- Empowerment / agency
- Safety / containment
- Sensory modulation / imagery change
</plan>
"""
    strategies = extract_plan_strategies(plan_text)
    assert "empowerment / agency" in strategies
    assert "safety / containment" in strategies
    assert "sensory modulation / imagery change" in strategies
    assert len(strategies) == 3


def test_extract_plan_strategies_empty() -> None:
    strategies = extract_plan_strategies("No plan here.")
    assert strategies == set()


def test_compute_pairwise_jaccard() -> None:
    sets = [
        {"empowerment", "safety", "sensory"},
        {"empowerment", "safety", "mastery"},
        {"empowerment", "safety", "sensory"},
    ]
    score = compute_pairwise_jaccard(sets)
    # Pairwise Jaccard scores: (2/4, 1.0, 2/4) -> avg = 2/3
    assert abs(score - (2 / 3)) < 1e-6


def test_compute_pairwise_jaccard_single() -> None:
    assert compute_pairwise_jaccard([{"empowerment"}]) == 1.0


def test_evaluation_stack_instantiation() -> None:
    stack = EvaluationStack(language="en", therapist_provider=DummyProvider())
    assert stack.language == "en"
    assert isinstance(stack._plan_prompt, str)
    assert isinstance(stack._stage_prompt, str)


def test_trial_result_structure() -> None:
    result = TrialResult(
        temperature=0.7,
        plan="<plan>- Example</plan>",
        response="Response text",
        plan_usage={"total_tokens": 10},
        response_usage={"total_tokens": 20},
    )
    assert result.temperature == 0.7
    assert "plan" in result.plan
    assert "Response" in result.response


def test_validate_plan_length_valid() -> None:
    """Test validation accepts 1-2 strategies."""
    assert validate_plan_length({"empowerment"}) is True
    assert validate_plan_length({"empowerment", "safety"}) is True


def test_validate_plan_length_invalid() -> None:
    """Test validation rejects 0 or 3+ strategies."""
    assert validate_plan_length(set()) is False
    assert validate_plan_length({"empowerment", "safety", "mastery"}) is False
    assert validate_plan_length({"a", "b", "c", "d"}) is False


def test_compute_validity_rate() -> None:
    """Test validity rate computation."""
    sets = [
        {"empowerment"},  # Valid (1 strategy)
        {"empowerment", "safety"},  # Valid (2 strategies)
        {"a", "b", "c"},  # Invalid (3 strategies)
        set(),  # Invalid (0 strategies)
    ]
    rate = compute_validity_rate(sets)
    assert rate == 0.5  # 2 out of 4 are valid


def test_compute_validity_rate_all_valid() -> None:
    """Test validity rate with all valid plans."""
    sets = [
        {"empowerment"},
        {"safety", "mastery"},
        {"cognitive_reframe"},
    ]
    rate = compute_validity_rate(sets)
    assert rate == 1.0


def test_compute_pairwise_jaccard_only_valid() -> None:
    """Test Jaccard with only_valid flag."""
    sets = [
        {"empowerment", "safety"},  # Valid
        {"empowerment", "mastery"},  # Valid
        {"a", "b", "c"},  # Invalid (will be excluded)
    ]
    # Without only_valid flag
    score_all = compute_pairwise_jaccard(sets, only_valid=False)
    assert score_all > 0.0
    
    # With only_valid flag (should exclude the 3-strategy set)
    score_valid = compute_pairwise_jaccard(sets, only_valid=True)
    assert score_valid > 0.0
    assert score_valid >= score_all  # Valid-only should be >= all (fewer outliers)
