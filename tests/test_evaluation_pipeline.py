"""Tests for evaluation pipeline metrics."""

from src.evaluation.metrics import (
    compute_pairwise_jaccard,
    compute_validity_rate,
    extract_plan_strategies,
    validate_plan_length,
)


def test_extract_plan_strategies():
    assert extract_plan_strategies("<plan>confrontation / safety</plan>") == {"confrontation", "safety"}
    assert extract_plan_strategies("<plan>cognitive_reframe</plan>") == {"cognitive_reframe"}
    assert extract_plan_strategies("<plan>invalid / self_empowerment</plan>") == {"self_empowerment"}
    assert extract_plan_strategies("No plan here.") == set()


def test_validate_plan_length():
    assert validate_plan_length({"confrontation"}) is True
    assert validate_plan_length({"confrontation", "safety"}) is True
    assert validate_plan_length(set()) is False
    assert validate_plan_length({"a", "b", "c"}) is False


def test_compute_validity_rate():
    sets = [
        {"confrontation"},           # valid
        {"self_empowerment", "safety"}, # valid
        {"a", "b", "c"},           # invalid
        set(),                     # invalid
    ]
    assert compute_validity_rate(sets) == 0.5


def test_compute_pairwise_jaccard():
    sets = [
        {"confrontation", "safety"},
        {"confrontation", "cognitive_reframe"},
        {"confrontation", "safety"},
    ]
    score = compute_pairwise_jaccard(sets)
    assert 0.5 < score < 0.8  # approximate check


def test_compute_pairwise_jaccard_single():
    assert compute_pairwise_jaccard([{"confrontation"}]) == 1.0
