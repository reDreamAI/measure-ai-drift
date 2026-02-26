# Thesis Models

> Current LLM assignments from `src/config/models.yaml`.
> For a visual overview, run `python visual_scripts/visualize_models.py` (outputs to `visualizations/`).

---

## Generation Stack (Supporting Roles)

Not evaluated. These serve infrastructure roles only.

- **Patient**: Dolphin Mistral 24B Venice
  - Provider: OpenRouter (free)
  - Temperature: 0.7
  - Purpose: uncensored Mistral fine-tune for nightmare/trauma roleplay

- **Therapist** (generation only): Llama 3.3 70B Versatile
  - Provider: Groq
  - Temperature: 0.0
  - Purpose: generates stage-appropriate therapeutic responses

- **Router**: Llama 3.3 70B Versatile
  - Provider: Groq
  - Temperature: 0.0
  - Purpose: classifies IRT stage from conversation history

---

## Evaluation Stack

### Primary Subject

- **Mistral Large 3**
  - Config key: `mistral_large`
  - Size: 675B MoE (41B active parameters per token)
  - Architecture: Mixture of Experts, deterministic routing at inference
  - Provider: Mistral API (OpenRouter fallback)
  - License: Apache 2.0
  - Context: 256K tokens
  - Role: EU-sovereign flagship. The model this thesis evaluates
  - Framing: does the EU flagship match proprietary frontier?

### Comparators by Size Class

**Small (24-32B)**

- **Mistral Small 3.2**
  - Config key: `mistral_small`
  - Size: 24B dense
  - Provider: Scaleway
  - License: Apache 2.0
  - Angle: EU-origin, same Mistral family. Tests how far the small model falls behind the flagship
  - Status: configured

- **Qwen 3 32B**
  - Config key: `qwen3_32b`
  - Size: 32B dense
  - Provider: Groq
  - License: Apache 2.0
  - Angle: benchmark leader at this size class. Chinese origin, opaque training data
  - Status: planned

- **OLMo 3.1 32B Instruct**
  - Config key: `olmo3_32b`
  - Size: 32B dense
  - Provider: OpenRouter (DeepInfra)
  - License: Apache 2.0
  - Angle: fully open (weights + training data + code). Best provenance story for a thesis
  - Status: planned

**Mid (70B + Mistral scaling)**

- **Llama 3.3 70B**
  - Config key: `llama70b`
  - Size: 70B dense
  - Provider: Groq / OpenRouter (free)
  - License: Meta (text-only, EU-legal)
  - Angle: original model from the efficacy study. Provides continuity with prior work
  - Status: configured

- **Mistral Medium 3**
  - Config key: `mistral_medium`
  - Size: undisclosed
  - Provider: Mistral API (OpenRouter fallback)
  - License: closed weights, API-only
  - Angle: EU-origin, Mistral vertical scaling between Small and Large
  - Status: planned

**Proprietary Ceiling**

- **Gemini 3 Pro**
  - Config key: `gemini3_pro`
  - Provider: Google AI Studio
  - Angle: proprietary ceiling with free credits. Upgrade to 3.1 Pro when released
  - Status: planned

- **Gemini 2.5 Flash**
  - Config key: `gemini_flash`
  - Provider: Google AI Studio
  - Angle: fast, cheap. Pipeline testing, may stay as lightweight proprietary reference
  - Status: configured

### Judge

- **Gemini 2.5 Flash** (T=0.0)
  - Provider: Google AI Studio
  - Purpose: scores plan-output alignment (Method 3)

---

## Size Ladder

Primary subject at the top, comparators below:

- 675B MoE (41B active): **Mistral Large 3** (primary subject)
- 70B: Llama 3.3
- undisclosed: Mistral Medium 3
- 32B: Qwen 3, OLMo 3.1
- 24B: Mistral Small 3.2
- Frontier: Gemini 3 Pro (proprietary ceiling)

MoE note: 41B active parameters per token. MoE routing is deterministic at inference, so the architecture does not add stochastic variance to stability measurements.
