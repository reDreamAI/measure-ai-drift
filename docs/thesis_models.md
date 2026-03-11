# Thesis Models

> Current LLM assignments from `src/config/models.yaml`.
> Provider policy: OpenRouter for everything, except Gemini via Google AI Studio (free credits).

---

## Two Modes

### Testing Mode (Free Tier)

For pipeline development and debugging. All models free on OpenRouter.

- Eval targets: Mistral Small 3.1 24B, Llama 3.3 70B
- Judge: GPT-oss-120B (T=0.0)
- Patient: Dolphin Mistral Venice 24B
- Router: Llama 3.3 70B
- Therapist: Llama 3.3 70B

### Full Experiment (Paid)

Switch by uncommenting the full evaluation_targets block in `models.yaml` and changing judge to `openrouter_gpt54`.

---

## Generation Stack (Supporting Roles)

Not evaluated. These serve infrastructure roles only.

- **Patient**: Dolphin Mistral 24B Venice Edition
  - Provider: OpenRouter (free)
  - Temperature: 0.7
  - Purpose: uncensored Mistral fine-tune for nightmare/trauma roleplay
  - Same model across both testing and full modes

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

### Primary Subject

- **Mistral Large 3**
  - Config key: `mistral_large`
  - Size: 675B MoE (41B active parameters per token)
  - Architecture: Mixture of Experts, deterministic routing at inference
  - Provider: OpenRouter
  - License: Apache 2.0
  - Context: 256K tokens
  - Role: EU-sovereign flagship. The model this thesis evaluates
  - Framing: does the EU flagship match proprietary frontier?

### Comparators by Size Class

**Small (24-32B)**

- **Mistral Small 3.2**
  - Config key: `mistral_small`
  - Size: 24B dense
  - Provider: OpenRouter
  - License: Apache 2.0
  - Angle: EU-origin, same Mistral family. Tests how far the small model falls behind the flagship

- **Qwen 3.5 27B**
  - Config key: `qwen35_27b`
  - Size: 27B dense
  - Provider: OpenRouter
  - License: Apache 2.0
  - Angle: current benchmark leader at this size class. 800K+ context. Replaces Qwen 3 32B

- **OLMo 3.1 32B Instruct**
  - Config key: `olmo3_32b`
  - Size: 32B dense
  - Provider: OpenRouter
  - License: Apache 2.0
  - Angle: fully open (weights + training data + code). Best provenance story for a thesis

**Mid (70B)**

- **Llama 3.3 70B**
  - Config key: `llama70b`
  - Size: 70B dense
  - Provider: OpenRouter
  - License: Meta (text-only, EU-legal)
  - Angle: original model from the efficacy study. Provides continuity with prior work

- **Mistral Medium 3.1**
  - Config key: `mistral_medium`
  - Size: undisclosed
  - Provider: OpenRouter
  - License: closed weights, API-only
  - Angle: EU-origin, Mistral vertical scaling between Small and Large

**Large (MoE, ~40B active)**

- **GLM-5**
  - Config key: `glm5`
  - Size: 744B MoE (40B active)
  - Provider: OpenRouter ($0.72/$2.30)
  - License: MIT
  - Angle: similar active parameter count to Mistral Large 3. Chinese origin (Zhipu AI). Trained on Huawei Ascend

- **DeepSeek V3.2**
  - Config key: `deepseek_v32`
  - Size: 671B MoE
  - Provider: OpenRouter ($0.25/$0.40)
  - License: MIT
  - Angle: similar MoE architecture to Mistral Large 3. Chinese origin. Cheapest large-class model

**Proprietary Ceiling**

- **Gemini 3.1 Pro**
  - Config key: `gemini31_pro`
  - Provider: Google AI Studio (free credits)
  - Angle: proprietary ceiling. Upgraded from 3.0 Preview (shut down Mar 9)

### Judge

- **GPT-5.4** (T=0.0) - full experiment
  - Provider: OpenRouter ($2.50/$15.00)
  - Purpose: scores plan-output alignment (Method 3). Native json_schema enforcement
  - No model-family overlap with any evaluation target

- **GPT-oss-120B** (T=0.0) - testing mode
  - Provider: OpenRouter (free)
  - Purpose: free judge for pipeline development

---

## Size Ladder

Primary subject at the top, comparators below:

- 744B MoE (40B active): **GLM-5**
- 675B MoE (41B active): **Mistral Large 3** (primary subject)
- 671B MoE: **DeepSeek V3.2**
- 70B: **Llama 3.3**
- undisclosed: **Mistral Medium 3.1**
- 32B: **OLMo 3.1**
- 27B: **Qwen 3.5**, **Mistral Small 3.2** (24B)
- Frontier: **Gemini 3.1 Pro** (proprietary ceiling)

MoE note: Mistral Large 3 uses 41B active parameters per token. MoE routing is deterministic at inference, so the architecture does not add stochastic variance to stability measurements. GLM-5 and DeepSeek V3.2 have similar MoE architectures, making them direct comparators at the architectural level.
