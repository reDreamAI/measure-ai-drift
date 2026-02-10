"""Tests for evaluation pipeline metrics."""

from src.evaluation.metrics import (
    compute_pairwise_jaccard,
    compute_validity_rate,
    extract_plan_strategies,
    validate_plan_length,
)


def test_extract_plan_strategies():
    assert extract_plan_strategies("<plan>mastery / safety</plan>") == {"mastery", "safety"}
    assert extract_plan_strategies("<plan>empowerment</plan>") == {"empowerment"}
    assert extract_plan_strategies("<plan>invalid / mastery</plan>") == {"mastery"}
    assert extract_plan_strategies("No plan here.") == set()


def test_validate_plan_length():
    assert validate_plan_length({"empowerment"}) is True
    assert validate_plan_length({"empowerment", "safety"}) is True
    assert validate_plan_length(set()) is False
    assert validate_plan_length({"a", "b", "c"}) is False


def test_compute_validity_rate():
    sets = [
        {"empowerment"},           # valid
        {"empowerment", "safety"}, # valid
        {"a", "b", "c"},           # invalid
        set(),                     # invalid
    ]
    assert compute_validity_rate(sets) == 0.5


def test_compute_pairwise_jaccard():
    sets = [
        {"empowerment", "safety"},
        {"empowerment", "mastery"},
        {"empowerment", "safety"},
    ]
    score = compute_pairwise_jaccard(sets)
    assert 0.5 < score < 0.8  # approximate check


def test_compute_pairwise_jaccard_single():
    assert compute_pairwise_jaccard([{"empowerment"}]) == 1.0
