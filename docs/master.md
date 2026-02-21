# Measure-AI-Drift — Project Master Document

> Single source of truth for thesis scope, architecture, design decisions, and model selection.
> For chapter structure, see [thesis_outline.md](thesis_outline.md).
> For Claude Code working instructions, see [../CLAUDE.md](../CLAUDE.md).

---

## 1 Thesis Scope

**Title:** Measuring Drift in Therapeutic AI: A Stability-Based Evaluation of Sovereign LLMs in Nightmare Therapy

**Research question:** How consistent is LLM clinical reasoning across stochastic runs in a structured therapeutic protocol?

**Core idea:** LLMs used in therapy must produce stable, protocol-adherent responses — not just plausible ones. This thesis builds a three-level evaluation framework to measure that stability and applies it to compare an EU-sovereign therapy model against proprietary and open-weight baselines.

**Scope boundaries:**
- Isolated to the **rescripting phase** of Imagery Rehearsal Therapy (the cognitive core)
- Synthetic patients (BDI-profiled vignettes), not real clinical interactions
- **Fused mode** only (plan + response in a single CoT call) — chained mode was explored early on but fused is the production approach
- Stability measurement, not therapeutic efficacy

**What this thesis is NOT:**
- Not a clinical trial (no real patients)
- Not a benchmark paper (the framework is the contribution, not a leaderboard)
- Not about sovereignty per se — sovereignty motivates the choice of primary subject, but the evaluation framework applies to any LLM

---

## 2 Architecture

### 2.1 Two-Stack Design

The system separates dialogue creation from stability measurement:

**Generation Stack** (`src/stacks/generation_stack.py`):
Three-agent loop that produces synthetic therapy sessions.
- **Patient Agent** — simulates responses based on a BDI-profiled vignette
- **Router Agent** — classifies current IRT stage from conversation history
- **Therapist Agent** — generates stage-appropriate therapeutic responses
- Traverses the 5-stage IRT protocol: recording → rewriting → summary → rehearsal → final
- `save_frozen_history()` exports the full dialogue plus slices at rewriting-turn boundaries

**Evaluation Stack** (`src/stacks/evaluation_stack.py`):
Runs stability tests on frozen conversation histories.
- Bypasses the router — the rescripting prompt is injected directly (stage is known a priori)
- Fused CoT generation: `<plan>` block declares 1–2 strategies, then the therapeutic response follows
- Runs N independent trials per condition (default: 10)
- Computes three evaluation metrics per experiment run

### 2.2 Data Flow

```
Vignettes (6 JSON files)
    ↓
Generation Stack (Patient ↔ Router ↔ Therapist)
    ↓
Frozen Histories: frozen_{vignette}_{hash}/
    full.json, slice_1.json, slice_2.json, slice_3.json
    ↓
Evaluation Stack (rescripting prompt → Therapist LLM × 10 trials × 2 temperatures)
    ↓
Experiment Runs: {timestamp}_{model}_{vignette}/
    config.yaml, frozen_history.json, trials/, metrics.json, judgments.json
    ↓
Aggregation Pipeline
    ↓
Results: stability, semantic consistency, alignment scores
```

### 2.3 Frozen History Design

Frozen histories are deterministic evaluation entry points — every trial receives identical context.

Each vignette produces one folder with four files:
- `full.json` — complete dialogue (all stages)
- `slice_1.json` — prefix up to and including the 1st rewriting exchange
- `slice_2.json` — prefix up to and including the 2nd rewriting exchange
- `slice_3.json` — prefix up to and including the 3rd rewriting exchange

Slicing uses `slice_at_rewriting_turn(n)`, which cuts after the Nth therapist rewriting message. Patient messages have `stage=None` (only therapist messages carry stage tags), so this method correctly excludes post-slice patient responses.

> **Known bug:** `slice_at_stage(REWRITING)` leaks post-rewriting patient messages. Not used in production.

### 2.4 Key Components

| Component | Path | Purpose |
|-----------|------|---------|
| Agents | `src/agents/` | Patient, Therapist, Router implementations |
| Core models | `src/core/` | Conversation, Message, Stage/Language enums, config loading |
| LLM provider | `src/llm/provider.py` | Multi-provider abstraction (Groq, OpenAI, Scaleway, Gemini, OpenRouter) |
| Experiment runner | `src/evaluation/experiment.py` | Orchestrates a single experiment run |
| Sampler | `src/evaluation/sampler.py` | Multi-trial generation (serial/parallel) |
| Metrics | `src/evaluation/metrics.py` | Jaccard, BERTScore, validity rate, alignment |
| CLI | `src/cli.py` | All commands: generate, evaluate, aggregate, etc. |

### 2.5 Design Patterns

- **Async-first** — all LLM calls use `asyncio`
- **Config-driven** — models and prompts loaded from YAML; swap without code changes
- **Pydantic models** — type-safe data flow; `extra="ignore"` silently drops unknown JSON fields
- **Provider abstraction** — single `LLMProvider` class for all backends via OpenAI-compatible API
- **Frozen histories** — serialised conversation snapshots for deterministic evaluation

> For the full file tree, see [architecture_plan.md](architecture_plan.md).

---

## 3 Evaluation Framework

Three levels, each measuring a distinct property:

### 3.1 Method 1 — Cognitive Stability (Plan Consistency)

**Question:** Do stochastic runs produce the same therapeutic decisions?

**Metric:** Mean pairwise Jaccard similarity over strategy sets across C(10,2) = 45 trial pairs.

**Input:** Strategy sets extracted from `<plan>` blocks via `extract_plan_strategies()`.

**Quality gate:** Plan validity rate — percentage of trials where the `<plan>` block parses correctly.

### 3.2 Method 2 — Output Consistency (Semantic Stability)

**Question:** Do stochastic runs produce therapeutically equivalent responses?

**Metric:** Mean pairwise BERTScore F1 across 45 trial pairs.

**Embedding model:** DeBERTa-XLarge-MNLI (He et al., 2021) — ranked #1 of 130+ models on WMT16 human correlation (r = 0.778). NLI fine-tuning aligns with the semantic comparison task.

**Input:** Response texts only (plan blocks excluded).

> For model selection rationale, see [bertscore_model_selection.md](bertscore_model_selection.md).

### 3.3 Method 3 — Plan-Output Alignment (Exploratory)

**Question:** Does the model's response implement its declared therapeutic plan?

**Metric:** LLM judge (Gemini Flash, T=0.0) scores each declared strategy on a ternary scale:
- 0 = absent, 1 = partial, 2 = implemented

**Inputs:** Both the extracted strategies AND the response text, scored against the strategy taxonomy definitions.

**Mitigations:** Cross-model judging, CoT justification, deterministic decoding, transparent rubric.

> For the full rationale (including why NLI cross-encoders were rejected), see [alignment_approach_analysis.md](alignment_approach_analysis.md).

### Data Flow Between Methods

```
Trial output (plan + response)
    ├─→ extract_plan_strategies() ─→ strategy sets ─→ Method 1 (Jaccard)
    ├─→ response texts ─────────────────────────────→ Method 2 (BERTScore)
    └─→ strategies + response + taxonomy ───────────→ Method 3 (LLM judge)
```

---

## 4 The Plan Mechanism

The `<plan>` block is a **declared intent mechanism**, not an explanation of internal reasoning.

In fused mode, the model produces `<plan>strategy_1 / strategy_2</plan>` followed by its therapeutic response in a single call. The plan tokens condition the response tokens (CoT-style).

**What the plan enables:**
- Structured measurement of strategy-level consistency (Method 1)
- Alignment verification between intent and execution (Method 3)
- Clinical oversight (reviewable summary of intended approach)
- Taxonomic constraint (keeps responses within the IRT framework)

**What the plan does NOT claim:** faithfulness to internal reasoning. The CoT faithfulness debate (Turpin et al., 2023; Lanham et al., 2023) is acknowledged but sidestepped — the measurement framework works regardless of whether the plan reflects genuine reasoning.

> For the full analysis including fused vs. chained comparison, see [plan_mechanism_analysis.md](plan_mechanism_analysis.md). Note: that document was written during early exploration when chained mode showed higher empirical stability. The thesis uses fused mode because the plan conditioning the response tokens is the more natural CoT framing, and the chained comparison data predates the current 7-category taxonomy.

---

## 5 Strategy Taxonomy

7 categories describing concrete therapeutic **mechanisms** (not goals):

| Category | Mechanism |
|----------|-----------|
| confrontation | External action toward the threat (fight, challenge, resist) |
| self_empowerment | Internal transformation (grow stronger, gain abilities) |
| safety | Environment modification (safe spaces, protective elements) |
| cognitive_reframe | Meaning change (reinterpret threatening elements) |
| emotional_regulation | Calming (introduce comforting elements) |
| social_support | Adding allies (introduce helpful figures) |
| sensory_modulation | Sensory details (modify light, sound, texture) |

The taxonomy evolved through three iterations (8 → 6 → 7) to resolve a severe distribution skew where empowerment/mastery consumed 87.7% of all picks.

> For the full evolution history, see [strategy_taxonomy_evolution.md](strategy_taxonomy_evolution.md).

---

## 6 Model Selection

### 6.1 Sovereignty Scope

Sovereignty is relevant **only for the primary therapy model** — Mistral Small 3.2 on Scaleway. It is the EU-sovereign, self-hostable model being evaluated against baselines.

All other roles (patient, router, judge) and all other evaluation targets have **no sovereignty requirement**. The thesis question is: "does this sovereign model hold up against others?" — not "are all models sovereign?"

### 6.2 Evaluation Targets (Therapist Role)

These are the models being compared on the three evaluation metrics:

| Model | Size | Provider | Role in comparison | Config status |
|-------|------|----------|--------------------|---------------|
| **Mistral Small 3.2** | 24B | Scaleway | Primary subject (EU-sovereign) | configured |
| **Llama 3.3 70B** | 70B | Groq / OpenRouter (free) | Open-weight, larger size class | configured |
| **GPT-5** | frontier | OpenAI | Proprietary ceiling baseline | planned |
| **Qwen 3 32B** | 32B | Groq | Open-weight, similar size class | planned |
| **Gemma 3 27B** | 27B | OpenRouter (free) | Open-weight, similar size class | planned |

Selection rationale: size-class diversity (24B / 27-32B / 70B / frontier), provider diversity, sovereignty status for primary subject.

> **Note:** `models.yaml` currently defines three `evaluation_models` entries (Mistral Small, Llama 70B, and Gemini 2.5 Flash for testing). GPT-5, Qwen 32B, and Gemma 27B need to be added before running the full experiment matrix.

### 6.3 Supporting Roles

These models are NOT being evaluated — they serve infrastructure roles:

| Role | Current model | Purpose |
|------|--------------|---------|
| **Patient** | Arcee Trinity Large Preview (OpenRouter, free) | Simulates patient responses; good roleplay capability. Planned switch to Dolphin Mistral Venice 24B (uncensored, better for nightmare/trauma content) |
| **Router** | Mistral Nemo / Llama 70B | Classifies IRT stage during generation |
| **Judge** | Gemini Flash (T=0.0) | Scores plan-output alignment (Method 3) |

### 6.4 Providers

| Provider | Base URL | Used for |
|----------|----------|----------|
| Scaleway | `api.scaleway.ai/v1` | Mistral Small 3.2 (sovereign) |
| Groq | `api.groq.com/openai/v1` | Llama 70B, Qwen 32B |
| OpenAI | `api.openai.com/v1` | GPT-5 |
| OpenRouter | `openrouter.ai/api/v1` | Patient (Venice), Gemma 27B, free-tier eval models |
| Gemini | `generativelanguage.googleapis.com/v1beta/openai/` | Judge (Gemini Flash) |

### 6.5 OpenRouter Free Tier Constraints

Free models (`:free` suffix) have rate limits:
- **50 req/day** without credits; **1000 req/day** with $10+ credits purchased
- **20 RPM** (some Venice-hosted models: 8 RPM)
- Per experiment: 6 vignettes × 3 slices × 10 trials = 180 calls per temperature → 360 calls per model for both T=0.0 and T=0.7

---

## 7 Experimental Design

### 7.1 Conditions

| Dimension | Values |
|-----------|--------|
| Vignettes | anxious, avoidant, cooperative, resistant, skeptic, trauma |
| Slices | slice_1, slice_2, slice_3 |
| Trials per condition | 10 |
| Temperatures | T=0.0 (deterministic), T=0.7 (stochastic) |
| Models | 5 evaluation targets (see §6.2) |

Total per model: 6 × 3 × 10 × 2 = **360 trials**
Total across all models: 360 × 5 = **1,800 trials**

### 7.2 Output Structure

Each experiment run produces:
```
experiments/runs/{timestamp}_{model}_{vignette}/
    config.yaml          — run parameters
    frozen_history.json   — input conversation
    trials/
        trial_01.json ... trial_10.json  — plan + response + usage + strategies
    metrics.json          — Jaccard, BERTScore, validity, alignment
    judgments.json         — raw LLM judge outputs with reasoning
```

### 7.3 Configuration Files

- `src/config/models.yaml` — provider endpoints, model options, active role assignments, evaluation targets
- `src/config/experiment.yaml` — trial count, temperatures, tag formats, metric selection, output paths

---

## 8 Document Index

| Document | Content |
|----------|---------|
| [thesis_outline.md](thesis_outline.md) | Chapter and subchapter structure with keypoints |
| [thesis_proposal.md](thesis_proposal.md) | Original research proposal (Jan 2026) |
| [architecture_plan.md](architecture_plan.md) | Full project file tree |
| [strategy_taxonomy_evolution.md](strategy_taxonomy_evolution.md) | Taxonomy journey: 8 → 6 → 7 categories |
| [plan_mechanism_analysis.md](plan_mechanism_analysis.md) | Plan as declared intent; fused vs. chained comparison |
| [alignment_approach_analysis.md](alignment_approach_analysis.md) | LLM judge vs. NLI rationale; ternary scoring design |
| [bertscore_model_selection.md](bertscore_model_selection.md) | DeBERTa-XLarge-MNLI selection rationale |
| [pipeline_flowcharts.md](pipeline_flowcharts.md) | Mermaid diagrams of full architecture |
