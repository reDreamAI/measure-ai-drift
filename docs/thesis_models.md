# Thesis Models

> Current LLM assignments from `src/config/models.yaml`.
> Provider policy: OpenRouter for everything, except Gemini via Google AI Studio (free credits).

---

## Two Modes

### Testing (Free Tier)

For pipeline development and debugging.

- Eval targets: Llama 3.3 70B (OpenRouter free), GPT-oss-120B (OpenRouter free)
- Judge: Gemini 3.1 Flash Lite (Google AI Studio, T=0.0)
- Patient: Dolphin Mistral Venice 24B (OpenRouter free, only uncensored option, always same)
- Router: Llama 3.3 70B (OpenRouter free)
- Therapist: Llama 3.3 70B (OpenRouter free)
- Mistral Small removed from testing: shares Venice provider rate limit with patient

### Experiment (Full Run)

Switch by uncommenting the experiment evaluation_targets block in `models.yaml` and changing judge to `gemini31_pro`.

---

## Generation Stack (Supporting Roles)

Not evaluated. These serve infrastructure roles only.

- **Patient**: Dolphin Mistral 24B Venice Edition
  - Provider: OpenRouter (free)
  - Temperature: 0.7
  - Purpose: uncensored Mistral fine-tune for nightmare/trauma roleplay
  - Same model across both modes

- **Therapist** (generation only): Llama 3.3 70B Instruct
  - Provider: OpenRouter
  - Temperature: 0.0
  - Purpose: generates stage-appropriate therapeutic responses

- **Router**: Llama 3.3 70B Instruct
  - Provider: OpenRouter
  - Temperature: 0.0
  - Purpose: classifies IRT stage from conversation history

---

## Evaluation Stack

All evaluation targets run in non-thinking mode for fair comparison.

### Primary Subject

- **Mistral Large 3**
  - Config key: `mistral_large`
  - Size: 675B MoE (41B active parameters per token)
  - Architecture: Mixture of Experts, deterministic routing at inference
  - Provider: OpenRouter
  - License: Apache 2.0
  - Context: 256K tokens
  - Thinking: no (native non-thinking)
  - Role: EU-sovereign flagship. The model this thesis evaluates
  - Framing: does the EU flagship match proprietary frontier?

### Comparators by Size Class

**Small (24-32B dense)**

- **Qwen 3.5 27B**
  - Config key: `qwen35_27b`
  - Size: 27B dense
  - Provider: OpenRouter
  - License: Apache 2.0
  - Thinking: hybrid, disabled via `reasoning.effort: none`
  - Angle: current benchmark leader at this size class. 800K+ context

- **OLMo 3.1 32B Instruct**
  - Config key: `olmo3_32b`
  - Size: 32B dense
  - Provider: OpenRouter
  - License: Apache 2.0
  - Thinking: no (native non-thinking)
  - Angle: fully open (weights + training data + code). Best provenance story for a thesis

**Mid (70B dense)**

- **Llama 3.3 70B**
  - Config key: `llama70b`
  - Size: 70B dense
  - Provider: OpenRouter
  - License: Meta (text-only, EU-legal)
  - Thinking: no (native non-thinking)
  - Angle: original model from the efficacy study. Provides continuity with prior work

**Large (MoE)**

- **DeepSeek V3.2**
  - Config key: `deepseek_v32`
  - Size: 671B MoE
  - Provider: OpenRouter ($0.25/$0.40)
  - License: MIT
  - Thinking: no (V3 line is non-reasoning)
  - Angle: similar MoE architecture to Mistral Large 3. Chinese origin. Direct architectural comparator

**Proprietary Ceiling**

- **GPT-5.4**
  - Config key: `gpt54`
  - Provider: OpenRouter ($2.50/$15.00)
  - Thinking: no (separate `gpt-5.4-thinking` model exists)
  - Angle: proprietary ceiling. Non-thinking variant ensures fair comparison with all other targets

### Dropped (available if needed)

- **Mistral Small 3.2** (24B) - redundant with Qwen/OLMo at small class
- **Mistral Medium 3.1** (undisclosed) - closed weights, weak thesis story
- **GLM-5** (744B MoE, 40B active) - third MoE adds little over DeepSeek

### Judge

- **Gemini 3.1 Pro** (T=0.0) - experiment
  - Provider: Google AI Studio (free credits)
  - Purpose: scores plan-output alignment (Method 3)
  - Thinking enabled: aids judgment accuracy for ternary scoring
  - max_tokens: 4096 (extra budget for thinking overhead)
  - No model-family overlap with any evaluation target

- **Gemini 3.1 Flash Lite** (T=0.0) - testing
  - Provider: Google AI Studio (free)
  - Purpose: free judge for pipeline development. Same Gemini family as experiment judge

---

## Size Ladder

- 675B MoE (41B active): **Mistral Large 3** (primary subject)
- 671B MoE: **DeepSeek V3.2**
- 70B dense: **Llama 3.3**
- 32B dense: **OLMo 3.1**
- 27B dense: **Qwen 3.5**
- Frontier: **GPT-5.4** (proprietary ceiling)

MoE note: Mistral Large 3 uses 41B active parameters per token. MoE routing is deterministic at inference, so the architecture does not add stochastic variance to stability measurements. DeepSeek V3.2 has a similar MoE architecture, making it the direct architectural comparator.
