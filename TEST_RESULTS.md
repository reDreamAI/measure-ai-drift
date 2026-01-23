# Test Results - Model Configuration Update

**Date:** 2026-01-18  
**Changes:** Updated to Groq-based models (qwen3-32b for patient, llama-3.3-70b-versatile for therapist/router)

## Test Summary

### ✅ Unit Tests (11/11 passed)

```
tests/test_evaluation_pipeline.py::test_extract_plan_strategies_basic PASSED
tests/test_evaluation_pipeline.py::test_extract_plan_strategies_empty PASSED
tests/test_evaluation_pipeline.py::test_compute_pairwise_jaccard PASSED
tests/test_evaluation_pipeline.py::test_compute_pairwise_jaccard_single PASSED
tests/test_evaluation_pipeline.py::test_evaluation_stack_instantiation PASSED
tests/test_evaluation_pipeline.py::test_trial_result_structure PASSED
tests/test_evaluation_pipeline.py::test_validate_plan_length_valid PASSED
tests/test_evaluation_pipeline.py::test_validate_plan_length_invalid PASSED
tests/test_evaluation_pipeline.py::test_compute_validity_rate PASSED
tests/test_evaluation_pipeline.py::test_compute_validity_rate_all_valid PASSED
tests/test_evaluation_pipeline.py::test_compute_pairwise_jaccard_only_valid PASSED
```

**Duration:** 0.13s

### ✅ Configuration Tests (5/5 passed)

1. **Config file loading** - Successfully loaded and parsed models.yaml
2. **New model options** - Verified groq_qwen and groq_llama70b exist
3. **Active role assignments** - Confirmed correct default selections
4. **Model identifiers** - Verified exact model strings
5. **Provider structure** - All Groq-based providers configured correctly

### ✅ Stack Component Tests (7/7 passed)

1. **Vignette loading** - Found 6 vignettes (resistant, trauma, avoidant, anxious, skeptic, cooperative)
2. **PatientAgent** - Created with vignette data and dummy provider
3. **TherapistAgent** - Created with stage and language settings
4. **RouterAgent** - Created with valid stage list
5. **Conversation** - Message addition and stage tracking working
6. **EvaluationStack** - Instantiation with prompts loaded correctly
7. **Frozen history** - Conversation slicing at stages working

## Current Model Configuration

| Role | Provider | Model | Temp | Max Tokens |
|------|----------|-------|------|------------|
| Patient | Groq | `qwen/qwen3-32b` | 0.7 | 512 |
| Therapist | Groq | `llama-3.3-70b-versatile` | 0.0 | 1024 |
| Router | Groq | `llama-3.3-70b-versatile` | 0.0 | 32 |

**API Key Required:** `GROQ_API_KEY` (single key for all three roles)

## Available Vignettes

1. `resistant` - Marcus (high resistance)
2. `trauma` - (trauma-focused profile)
3. `avoidant` - (avoidant attachment)
4. `anxious` - (anxious attachment)
5. `skeptic` - (skeptical engagement)
6. `cooperative` - (cooperative engagement)

## Next Steps for Real LLM Testing

### 1. Set API Key
```bash
export GROQ_API_KEY=your_key_here
```

### 2. Test Provider Creation
```python
from src.llm.provider import create_provider

patient = create_provider("patient")      # qwen/qwen3-32b
therapist = create_provider("therapist")  # llama-3.3-70b-versatile
router = create_provider("router")        # llama-3.3-70b-versatile
```

### 3. Run Generation Stack (Full Dialogue)
```python
import asyncio
from src.stacks import GenerationStack

async def test_generation():
    stack = GenerationStack.from_vignette("cooperative", language="en")
    conversation = await stack.run(verbose=True)
    stack.save_dialogue("outputs/test_dialogue.json")

asyncio.run(test_generation())
```

### 4. Run Evaluation Stack (Multi-Trial)
```python
import asyncio
from src.core import Conversation
from src.stacks import EvaluationStack

async def test_evaluation():
    # Load or create a frozen history
    frozen_history = Conversation(session_id="test", language="en")
    # ... add messages up to rewriting stage
    
    stack = EvaluationStack(language="en")
    results = await stack.run_trials(
        frozen_history=frozen_history,
        n_trials=10,
        temperature=0.7
    )
    
    # Analyze results
    from src.evaluation import (
        extract_plan_strategies,
        compute_validity_rate,
        compute_pairwise_jaccard
    )
    
    strategy_sets = [extract_plan_strategies(r.plan) for r in results]
    validity = compute_validity_rate(strategy_sets)
    jaccard = compute_pairwise_jaccard(strategy_sets, only_valid=True)
    
    print(f"Validity rate: {validity:.2%}")
    print(f"Jaccard (valid only): {jaccard:.3f}")

asyncio.run(test_evaluation())
```

## Status

- ✅ Configuration updated
- ✅ All unit tests passing
- ✅ All component tests passing
- ⏸️ Real LLM testing pending (requires GROQ_API_KEY)

## Notes

- All tests run without API keys using dummy providers
- Real model testing requires `GROQ_API_KEY` environment variable
- Models can be swapped by changing `use:` value in models.yaml
- Previous model options (groq_kimi, groq_oss, etc.) remain available
