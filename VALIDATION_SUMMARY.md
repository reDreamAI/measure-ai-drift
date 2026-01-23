# Strategy Taxonomy and Plan Validation

## Implementation Complete

### 1. Strategy Taxonomy (Single Source of Truth)

**File:** `data/prompts/evaluation/strategy_taxonomy.yaml`

8 IRT strategy categories with structured metadata:
- `id`: Machine-readable identifier
- `name`: Human-readable category name
- `description`: Clinical definition
- `keywords`: Terms for automated classification (future use)

**Validation Rules:**
```yaml
validation:
  min_strategies: 1
  max_strategies: 2  # ENFORCED: Only 1-2 strategies allowed
  allow_testing_more: true  # Can test 3+ but flagged as invalid
```

### 2. Updated Plan Prompt Constraint

**File:** `data/prompts/evaluation/internal_plan.yaml`

**Changed:**
- ~~"2-5 bullet points"~~ → **"1-2 bullet points"**
- Added: "You MUST select exactly 1 or 2 strategies"
- Added: "Plans with more than 2 strategies are invalid and will be rejected"
- Updated examples to show exactly 2 strategies

### 3. Validation Functions

**File:** `src/evaluation/metrics.py`

```python
validate_plan_length(strategies, max_allowed=2) -> bool
    # Returns True if 1 <= len(strategies) <= 2
    
compute_validity_rate(strategy_sets, max_allowed=2) -> float
    # Returns fraction of valid plans (0.0-1.0)
    
compute_pairwise_jaccard(sets, only_valid=False, max_allowed=2) -> float
    # Now supports only_valid flag to exclude invalid plans
```

### 4. Config Loader Extensions

**File:** `src/core/config_loader.py`

Added:
```python
load_strategy_taxonomy() -> dict
    # Loads the 8-category taxonomy + validation rules
    
load_internal_plan_prompt() -> dict
    # Loads plan generation prompt + examples
```

### 5. Test Coverage

**File:** `tests/test_evaluation_pipeline.py`

11 tests, all passing:
- ✓ Plan strategy extraction
- ✓ Jaccard computation
- ✓ Plan length validation (1-2 valid, 0 or 3+ invalid)
- ✓ Validity rate computation
- ✓ Jaccard with only_valid flag
- ✓ EvaluationStack instantiation
- ✓ TrialResult dataclass

## Usage

```python
from src.evaluation import (
    extract_plan_strategies,
    validate_plan_length,
    compute_validity_rate,
    compute_pairwise_jaccard,
)

# Extract strategies from plan
plan_text = "<plan>- Empowerment\n- Safety</plan>"
strategies = extract_plan_strategies(plan_text)

# Validate plan length
is_valid = validate_plan_length(strategies)  # True (2 strategies)

# Compute validity rate across trials
trial_plans = [{"empowerment"}, {"safety", "mastery"}, {"a", "b", "c"}]
validity = compute_validity_rate(trial_plans)  # 0.67 (2/3 valid)

# Compute Jaccard (Level 3.1 metric)
jaccard = compute_pairwise_jaccard(trial_plans, only_valid=True)
```

## What This Enables

1. **Enforce 1-2 strategy constraint** - thesis requirement
2. **Quality control** - flag models that generate too many strategies
3. **Valid-only metrics** - exclude invalid plans from stability analysis
4. **Single source of truth** - all 8 categories defined once in YAML

## Testing

```bash
pytest -v tests/test_evaluation_pipeline.py
# 11 passed in 0.14s
```

## Next Steps

Ready for thesis evaluation:
- ✅ Strategy taxonomy defined
- ✅ Plan validation working
- ✅ Jaccard metric implemented
- ✅ 1-2 strategy constraint enforced

Can now run multi-trial experiments and measure cognitive stability!
