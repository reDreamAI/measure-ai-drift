# SOTA LLMs - Living Reference (February 2026)

> **Purpose:** This file overrides Claude's training data on model availability and performance.
> LLM landscape changes faster than any training cutoff can track. Before recommending or configuring models, **always check live sources first** rather than relying on built-in knowledge.
>
> **Last verified:** 2026-02-23
>
> **Live sources to check before any model decision:**
> - [Artificial Analysis Leaderboard](https://artificialanalysis.ai/leaderboards/models) - intelligence, speed, price rankings
> - [OpenRouter Models](https://openrouter.ai/models) - available models, pricing, free tier
> - [OpenRouter Rankings](https://openrouter.ai/rankings) - community usage rankings
> - [LM Arena](https://lmarena.ai/) - head-to-head human preference rankings

---

## How to Use This File

1. **Before any model selection discussion**, fetch the live sources above
2. **Cross-check** this file against live data, as it may already be outdated
3. **Update this file** whenever new information is confirmed
4. **Flag staleness**: if `Last verified` is more than 2 weeks old, re-research before trusting the content below

---

## EU Legality and Training Data Provenance

For a therapy thesis, both legal usability and data provenance matter. Models with opaque training data are harder to defend academically.

### EU Legality by Model

| Model | EU-Legal? | Training Data Transparency | Risk Notes |
|---|---|---|---|
| **Mistral Small 3.2** | Yes (EU company) | Undisclosed, but EU-origin likely compliant | Low risk. Small-class comparator |
| **Mistral Large 3** | Yes (EU company) | Undisclosed, but EU-origin likely compliant | Lowest risk. Primary therapy subject. Apache 2.0, 675B MoE |
| **K2-V2 Instruct** | Yes (Apache 2.0) | **Fully open** - 12T tokens from TxT360, all mixtures published | Lowest risk. Best provenance story |
| **OLMo 3.1 Instruct** | Yes (Apache 2.0) | **Fully open** - 9.3T token Dolma 3 corpus, all sources documented | Lowest risk. Allen AI nonprofit |
| **Qwen 3 / 3.5** | Yes if self-hosted (Apache 2.0) | High-level disclosure (36T tokens), but no detailed source list. No EU GDPR representative | Medium. Chinese origin, opaque data details |
| **Llama 3.3 70B** | Yes (text-only, EU ban is multimodal-only) | Undisclosed | Medium. US company, opaque data |
| **Llama 4 (all)** | **No** - entire family is multimodal, EU excluded from license | Undisclosed | Blocked. Do not use |
| **DeepSeek R1/V3** | Legally yes if self-hosted (MIT) | Undisclosed | High risk. Active GDPR enforcement across EU. Bad optics for therapy |
| **Gemma 3 27B** | Yes (open weights) | Undisclosed | Low-medium. Google has EU data processing agreements |
| **GPT-5** | Yes (API, OpenAI has EU DPA) | Closed | Low. Standard API use, no self-hosting |

### Key Regulations

- **EU AI Act Article 53**: All GPAI providers must publish training data summaries and demonstrate copyright compliance (enforcement from Aug 2026)
- **Llama 4 EU ban**: Meta excluded EU from all multimodal Llama models due to AI Act concerns. Text-only Llama 3.3 is unaffected
- **DeepSeek**: Italian, German, and Belgian DPAs have launched investigations. Multiple EU countries restricting deployment in early 2026

---

## EU-Sovereign Options (Self-Hostable in EU)

| Model | Params | Provider | Notes |
|---|---|---|---|
| **Mistral Small 3.2** | 24B dense | Scaleway (EU) | Small-class comparator. Apache 2.0 |
| **Mistral Large 3** | 675B (41B active, MoE) | Mistral API / self-host | Current primary therapy subject. Released Dec 2025. Apache 2.0. Top EU-origin model. 256K context. Multi-GPU required |
| **Mistral Medium 3** | - | Mistral API | Check if released, may sit between Small and Large |
| **OpenEuroLLM** | TBD | EU consortium | First versions expected mid-2026. Covers all 24 EU languages |

**Key point for thesis:** sovereignty only matters for the primary therapy model (Mistral Large 3 via Mistral API). Other roles and eval targets have no sovereignty requirement.

---

## Best Non-Reasoning Instruct Models (Mid-to-Large)

These are the most relevant models for our evaluation targets: non-reasoning, instruction-following, mid-to-large size.

### Tier 1: Fully Open (weights + training data + code)

Best for academic defensibility. You can cite exactly what these were trained on.

| Model | Size | Origin | Performance | License |
|---|---|---|---|---|
| **K2-V2 Instruct** | 70B dense | MBZUAI (UAE) / LLM360 | Rivals Qwen 2.5 72B, approaches Qwen 3 235B. Strong on GPQA-Diamond | Fully open (LLM360) |
| **OLMo 3.1 32B Instruct** | 32B | Allen AI (US nonprofit) | Competitive with Qwen 3 32B, beats Gemma 3 and Llama 3.1 at scale | Apache 2.0 |

### Tier 2: EU-Origin (sovereignty + Apache 2.0, opaque training data)

| Model | Size | Origin | Performance | License |
|---|---|---|---|---|
| **Mistral Large 3** | 675B MoE (41B active) | Mistral (France) | Our primary subject. Top EU model. Strong multilingual, 256K context | Apache 2.0 |
| **Mistral Small 3.2** | 24B dense | Mistral (France) | Small-class comparator. Punches above weight but not frontier-class | Apache 2.0 |

### Tier 3: Open Weights (good license, opaque data, non-EU origin)

| Model | Size | Origin | Performance | License |
|---|---|---|---|---|
| **Qwen 3 32B** | 32B | Alibaba (China) | Strongest benchmarks at 32B. Hybrid thinking modes | Apache 2.0 |
| **Qwen 3.5** | Various | Alibaba (China) | Released Feb 2026. Latest iteration, multimodal + agentic | Apache 2.0 |
| **Gemma 3 27B** | 27B | Google (US) | Same size class as Mistral Small. Good comparator | Open |
| **Llama 3.3 70B** | 70B | Meta (US) | Text-only = EU-legal. Mature, widely deployed, GPT-4 level | Meta license |

---

## Frontier Closed Models (Feb 2026)

| Model | Provider | Tier | Notes |
|---|---|---|---|
| **Gemini 3.1 Pro** | Google | Top | Highest on Artificial Analysis intelligence index |
| **Claude Opus 4.6** | Anthropic | Top | Top reasoning performance |
| **GPT-5.2** | OpenAI | Top | Latest OpenAI flagship |
| **Claude Sonnet 4.6** | Anthropic | High | Strong reasoning, faster than Opus |
| **GPT-5** | OpenAI | High | Previous flagship, still strong |

---

## Free Models on OpenRouter (Feb 2026)

Rate limits: 50 req/day without credits, 1000/day with $10+ deposit, typically 20 RPM.

| Model | Params | RPM | Notes |
|---|---|---|---|
| **Llama 3.3 70B** | 70B | 20 | GPT-4 level, reliable baseline |
| **Gemma 3 27B** | 27B | 20 | Good size-class comparator for Mistral Small |
| **Mistral Small 3.1** | 24B | 20 | Slightly older than our 3.2 comparator |
| **DeepSeek R1** | 671B MoE | 20 | Strong reasoning, but Chinese-origin (high EU risk) |
| **NVIDIA Nemotron Nano 9B v2** | 9B | 20 | Fast, good for testing |
| **Dolphin Mistral Venice 24B** | 24B | 8 | Uncensored Mistral fine-tune. Current patient model |
| **Arcee Trinity Large** | 400B MoE (13B active) | 20 | Previous patient model |

---

## Project-Specific Model Assignments

> Cross-reference with `src/config/models.yaml` for actual configuration.

**Primary therapy subject (being evaluated):** Mistral Large 3 via Mistral API

**Evaluation targets (compared against primary):**
- Small benchmark: Qwen 3 32B (Groq, benchmark leader at size class) - planned
- Small provenance: OLMo 3.1 32B Instruct (OpenRouter/DeepInfra, fully open) - planned
- Mid open: Llama 3.3 70B (Groq, original efficacy study model) - configured
- Mid EU: Mistral Medium 3 (Mistral API, closed weights) - planned
- Small EU: Mistral Small 3.2 24B (Scaleway, Apache 2.0) - configured
- Proprietary ceiling: Gemini 3 Pro (Google, free credits). Upgrade to 3.1 Pro when available - planned
- Testing: Gemini 2.5 Flash (configured, lightweight proprietary reference)

**Supporting roles (not being evaluated):**
- Patient: Dolphin Mistral Venice 24B (OpenRouter, free)
- Router: Gemini 2.5 Flash
- Judge: GPT-5 / Claude (TBD)

---

## Staleness Checklist

When updating this file, verify:
- [ ] Are the "free on OpenRouter" models still free?
- [ ] Have any new Mistral models been released?
- [ ] Has OpenEuroLLM shipped anything yet?
- [ ] Are the frontier model rankings still accurate?
- [ ] Have rate limits or pricing changed?
- [ ] Any new open-weight models in the 24-32B range (direct comparators for Mistral Small)?
- [ ] Is K2-V2 / OLMo 3.1 available on any hosted provider (OpenRouter, etc.)?
- [ ] Has Qwen 3.5 been benchmarked against K2-V2 and OLMo 3?
