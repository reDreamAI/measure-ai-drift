# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Measure-AI-Drift is a thesis project that evaluates LLM stability in therapeutic contexts, specifically focusing on Imagery Rehearsal Therapy (IRT) simulations. It measures stochastic drift and consistency across multiple LLM systems. The primary subject is Mistral Small 3.2 (24B), an EU-sovereign, self-hostable model. Sovereignty is relevant only for this one therapy model being evaluated, not for any supporting roles (patient, router, judge) or other evaluation targets.

## Commands

### CLI Entry Points
```bash
python3 -m src <command>        # Main CLI method
./run <command>                 # Wrapper script
uv run python -m src <command>  # With uv isolation
```

### Available Commands
```bash
# Generate synthetic dialogues
generate -v <vignette> -t <turns> -o <output> --verbose
generate -v <vignette> --freeze   # Also create frozen history slices

# Run rescripting stability tests
evaluate -i <history.json> -n <trials> -t <temperature> --mode fused|chained

# Aggregate results across experiment runs
aggregate -r <runs_dir> -o <output_dir>

# Configuration checks
keys --quick          # Check config only (no API calls)
keys                  # Full API connectivity test

# Inventory
list-vignettes        # Show available patient profiles
list-models --verbose # Show all model options

# Testing
test-setup --quick    # Verify config (default)
test-setup --full     # Include API tests
```

### Testing
```bash
pytest tests/                              # Full test suite
pytest tests/test_setup.py -v              # Verbose setup tests
python3 -m src test-setup --full           # With API connectivity
```

### Dependencies
```bash
pip install -r requirements.txt   # Direct pip
uv sync                           # Using uv
cd promptfoo && npm install        # For promptfoo testing (separate folder)
```

## Project Knowledge Base

For thesis scope, architecture, model selection, and design decisions, see **[docs/master.md](docs/master.md)**, the single source of truth. It links to detailed docs for specific topics (taxonomy evolution, BERTScore model selection, etc.).

## Architecture

### Two-Stack Design

**Generation Stack** (`src/stacks/generation_stack.py`):
Creates synthetic therapy dialogues through agent interaction:
- Patient Agent → Simulates patient responses based on vignette data
- Router Agent → Determines current IRT stage from conversation
- Therapist Agent → Responds therapeutically at the appropriate stage
- Follows 5-stage IRT protocol: `recording` → `rewriting` → `summary` → `rehearsal` → `final`
- `save_frozen_history()` exports a folder with the full dialogue plus slices at each rewriting turn boundary

**Evaluation Stack** (`src/stacks/evaluation_stack.py`):
Measures rescripting stability using frozen histories:
- Takes a frozen dialogue (full or sliced) as input
- Runs multiple trials at a given temperature on the same history
- Supports "fused" (single CoT call) and "chained" (plan → response) modes
- Measures consistency via Jaccard similarity, BERTScore, validity rate, and plan-response alignment

### Data Flow

```
generate --freeze → frozen_histories/frozen_{vignette}_{id}/
                        full.json + slice_1..N.json
    ↓
evaluate -i slice_N.json → experiments/runs/{timestamp}_{model}_{vignette}/
                               config.yaml, frozen_history.json, trials/, metrics.json, judgments.json
    ↓
aggregate → data/synthetic/results/
```

### Key Components

- `src/agents/` - Agent implementations (BaseAgent, patient, therapist, router)
- `src/core/` - Data models (Conversation, Message, Stage enums, config loading, strategy taxonomy)
- `src/llm/provider.py` - Multi-provider LLM abstraction (Groq, OpenAI, Scaleway, Gemini, OpenRouter)
- `src/evaluation/experiment.py` - Experiment runner with structured output
- `src/evaluation/sampler.py` - Multi-trial sampling with parallel execution
- `src/evaluation/metrics.py` - Jaccard similarity, BERTScore, validity rate, alignment (LLM judge)
- `data/prompts/` - YAML/JSON prompts and vignettes (6 patient profiles)

### Configuration

- `src/config/models.yaml` - Provider endpoints, model options, active role assignments
- `src/config/experiment.yaml` - Sampling parameters, metrics, output paths
- `.env` - API keys (git-ignored)

### Design Patterns

- **Async-First**: All LLM calls use asyncio
- **Config-Driven**: Models and prompts loaded from YAML (swap without code changes)
- **Pydantic Models**: Type-safe data validation throughout (`extra="ignore"` allows forward-compatible JSON)
- **Provider Abstraction**: Single code path for all LLM backends
- **Frozen Histories**: Evaluation uses serialized conversation snapshots for deterministic testing

### Known Issues

- `Conversation.slice_at_stage(REWRITING)` includes post-rewriting patient messages that have `stage=None`. Not currently called in production. `slice_at_rewriting_turn()` is used instead.

## Model Selection (Training Data Override)

LLM landscape moves faster than any training cutoff. **Do not rely on built-in knowledge for model recommendations.** Before any model-related discussion, check [docs/SOTA_LLMs.md](docs/SOTA_LLMs.md) first, then verify against live sources listed there (Artificial Analysis, OpenRouter, LM Arena). Update the file when new information is confirmed.

## Rules for Claude Code

- **Never commit directly**: Do not run `git commit`. Instead, stage files with `git add` and propose a commit message for the user to run themselves.
- **Preserve old_versions/**: Do not delete the `old_versions/` folder during cleanup - it contains reference implementations.
- **Markdown style**: Follow [docs/STYLE.md](docs/STYLE.md) for all `.md` files. Key rules: no em-dashes, no `--`, no semicolons (except citations), active voice, plain words, short paragraphs.
