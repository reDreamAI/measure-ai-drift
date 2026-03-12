# SOTA LLMs - Living Reference (March 2026)

> **Purpose:** This file overrides Claude's training data on model availability and performance.
> LLM landscape changes faster than any training cutoff can track. Before recommending or configuring models, **always check live sources first** rather than relying on built-in knowledge.
>
> **Last verified:** 2026-03-11
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

## Recent News (March 2026)

### Releases in Last 2-4 Weeks

- **GPT-5.4** (Mar 5): Combines GPT-5.3-Codex coding strength with improved reasoning and computer use. 83% on GDPval (professional knowledge work). Replaces GPT-5.2 as frontier ceiling. Variants: GPT-5.4 Thinking, GPT-5.4 Pro. 1M context. $2.50/$15.00 per M tokens (cached input: $0.25/M)
- **Gemini 3.1 Flash Lite** (Mar 3): Cheapest Gemini model. $0.25/$1.50 per M tokens. 2.5x faster TTFT than 2.5 Flash. 86.9% GPQA Diamond
- **Gemini 3 Flash** (~Feb 2026): Default Gemini app model. Outperforms 2.5 Pro at 3x speed. $0.50/$3.00 per M tokens
- **DeepSeek V4** (early Mar): ~1T total / ~32B active MoE. 1M context. Native multimodal (vision + audio + text). Optimized for Huawei Ascend chips. Apache 2.0. Not EU-sovereign. Active EU GDPR issues persist
- **GPT-5.3-Codex** (Feb 24): 400K context. Industry-leading coding. $1.75/$14.00 per M tokens
- **Gemini 3.1 Pro** (Feb 19): Google's latest flagship. 77.1% ARC-AGI-2, 1M context, 65K output tokens. Gemini 3 Pro Preview shut down Mar 9
- **Qwen 3.5** (Feb 17-24): Full family released. 397B-A17B flagship MoE, 27B dense, 35B-A3B efficient MoE. Apache 2.0. Native multimodal
- **MiniMax M2.5** (Feb 12): 230B MoE, 10B active. Lightning Attention. 205K context. 80.2% SWE-Bench Verified. Modified MIT license. Chinese origin (Shanghai). Available on OpenRouter. Extremely cheap ($0.15/$1.20 per M tokens for standard variant)
- **GLM-5** (Feb 11): 744B MoE, 40B active, 256 experts. 205K context, 128K output. 77.8% SWE-bench, 92.7% AIME 2026. Trained entirely on Huawei Ascend (zero NVIDIA dependency). MIT license. Chinese origin (Zhipu AI / Z.ai). Available on OpenRouter
- **GPT-5.2** (Feb 2026): 400K context, 100% AIME 2025, hallucination rate 6.2%. Superseded by GPT-5.4
- **Kimi K2.5** (Jan 27): 1T MoE, 32B active, 384 experts. 256K context. Native multimodal (MoonViT 400M vision encoder). Agent swarm mode (up to 100 sub-agents). Modified MIT license. Chinese origin (Moonshot AI). Available on OpenRouter
- **Guide Labs Steerling-8B** (Feb 23): Every output token traceable to training data origins. Interesting for clinical interpretability arguments
- **Inception Mercury 2** (Feb 24): First reasoning diffusion LLM (dLLM). 1,000 tok/s. Not relevant for stability evaluation
- **NVIDIA Nemotron 3 Nano** (available): 3.2B active / 31.6B total, hybrid Mamba-Transformer MoE, 1M context. Nemotron 3 Super (~100B) and Ultra (~500B) expected H1 2026

### Mistral Ecosystem Updates

- **Mistral acquired Koyeb** (Feb 17): Paris-based cloud startup (ex-Scaleway founders). Signals full-stack EU-sovereign AI cloud ambitions
- **Mistral Compute** (announced Jun 2025) + Koyeb = building European inference infrastructure independent of US cloud
- **Ministral 3** (Dec 2025): 3B/8B/14B dense models, Apache 2.0. The 14B reasoning variant scores 85% on AIME '25
- **Devstral 2** (Dec 2025): 123B dense for coding, 256K context. Devstral Small 2: 24B, Apache 2.0

### OpenAI GPT-4.1 Family (Still API-Available)

GPT-4.1 was released Apr 2025 and retired from ChatGPT Feb 13, 2026, but all three variants remain available via API and OpenRouter. The family was specifically optimized for instruction following and structured outputs.

- **GPT-4.1**: $2.00/$8.00 per M tokens. 1M context. Strong instruction following
- **GPT-4.1 mini**: $0.40/$1.60 per M tokens. 1M context. Mid-tier
- **GPT-4.1 nano**: $0.10/$0.40 per M tokens. 1M context. Cheapest quality OpenAI model

### EU Sovereignty Developments

- **OpenEuroLLM**: 37.4M EUR budget (20M from EU Digital Europe Programme). 20 European institutions. First versions mid-2026, final by 2028. Covers all 24 EU languages. AI Act compliant from the ground up
- **EU AI Act Article 53** enforcement begins Aug 2026: training data summaries mandatory for all GPAI providers
- **Mistral Large 3** remains the only frontier-class EU-sovereign open-weight model currently available

---

## EU Legality and Training Data Provenance

Legal usability and data provenance vary across models. Relevant for EU deployment and research transparency.

### EU Legality by Model

| Model | EU-Legal? | Training Data Transparency | Risk Notes |
|---|---|---|---|
| **Mistral Large 3** | Yes (EU company) | Undisclosed, but EU-origin likely compliant | Lowest risk. Apache 2.0, 675B MoE |
| **Mistral Small 3.2** | Yes (EU company) | Undisclosed, but EU-origin likely compliant | Low risk. Apache 2.0, 24B dense |
| **K2-V2 Instruct** | Yes (Apache 2.0) | **Fully open** - 12T tokens from TxT360, all mixtures published | Lowest risk. Best provenance story. No hosted inference |
| **OLMo 3.1 Instruct** | Yes (Apache 2.0) | **Fully open** - 9.3T token Dolma 3 corpus, all sources documented | Lowest risk. Allen AI nonprofit |
| **Qwen 3 / 3.5** | Yes if self-hosted (Apache 2.0) | High-level disclosure (36T tokens), but no detailed source list. No EU GDPR representative | Medium. Chinese origin, opaque data details |
| **Llama 3.3 70B** | Yes (text-only, EU ban is multimodal-only) | Undisclosed | Medium. US company, opaque data |
| **Llama 4 (all)** | **No** - entire family is multimodal, EU excluded from license | Undisclosed | capabilities low/ benchmarks faked | Blocked. Do not use |
| **DeepSeek R1/V3/V4** | Legally yes if self-hosted (MIT) | Undisclosed | High risk. Active GDPR enforcement across EU. Bad optics for therapy |
| **Gemma 3 27B** | Yes (open weights) | Undisclosed | Low-medium. Google has EU data processing agreements |
| **GLM-5** | Yes if self-hosted (MIT) | Undisclosed (28.5T tokens) | High risk. Chinese origin (Zhipu AI). No EU GDPR representative. Same risk profile as DeepSeek |
| **Kimi K2.5** | Yes if self-hosted (Modified MIT) | Undisclosed (15T tokens, multimodal) | High risk. Chinese origin (Moonshot AI). Native multimodal complicates EU licensing. Same risk profile as DeepSeek |
| **MiniMax M2.5** | Yes if self-hosted (Modified MIT) | Undisclosed | High risk. Chinese origin (MiniMax, Shanghai). No EU GDPR representative |
| **GPT-5 / 5.2 / 5.4** | Yes (API, OpenAI has EU DPA) | Closed | Low. Standard API use, no self-hosting |
| **GPT-oss-120B** | Yes (Apache 2.0) | Partially open | Low. OpenAI's first open-weight model |

### Key Regulations

- **EU AI Act Article 53**: All GPAI providers must publish training data summaries and demonstrate copyright compliance (enforcement from Aug 2026)
- **Llama 4 EU ban**: Meta excluded EU from all multimodal Llama models due to AI Act concerns. Text-only Llama 3.3 is unaffected
- **DeepSeek**: Italian, German, and Belgian DPAs have launched investigations. Multiple EU countries restricting deployment in early 2026

---

## EU-Sovereign Options (Self-Hostable in EU)

| Model | Params | Provider | Notes |
|---|---|---|---|
| **Mistral Large 3** | 675B (41B active, MoE) | OpenRouter / Mistral API / Scaleway | Released Dec 2025. Apache 2.0. 256K context |
| **Mistral Medium 3.1** | undisclosed | OpenRouter / Mistral API | EU-origin, closed weights. Mistral vertical scaling |
| **Mistral Small 3.2** | 24B dense | Scaleway (EU) | Apache 2.0 |
| **Ministral 3 14B** | 14B dense | Mistral API | Apache 2.0. Reasoning variant: 85% AIME '25. Edge deployment |
| **OpenEuroLLM** | TBD | EU consortium | First versions mid-2026. 24 EU languages |

**Sovereignty narrative strengthened** by Mistral's Feb 2026 Koyeb acquisition (EU cloud infrastructure) and Mistral Compute platform. Mistral is building a full-stack EU-sovereign AI cloud.

---

## Best Non-Reasoning Instruct Models (Mid-to-Large)

Non-reasoning, instruction-following models in the mid-to-large size range.

### Tier 1: Fully Open (weights + training data + code)

Best for academic defensibility. You can cite exactly what these were trained on.

| Model | Size | Origin | Performance | License |
|---|---|---|---|---|
| **K2-V2 Instruct** | 70B dense | MBZUAI (UAE) / LLM360 | Rivals Qwen 2.5 72B, approaches Qwen 3 235B. Strong on GPQA-Diamond. No hosted inference | Fully open (LLM360) |
| **OLMo 3.1 32B Instruct** | 32B | Allen AI (US nonprofit) | Competitive with Qwen 3 32B, beats Gemma 3 and Llama 3.1 at scale. 5+ point gains over OLMo 3.0 on AIME/IFEval | Apache 2.0 |

### Tier 2: EU-Origin (sovereignty + Apache 2.0, opaque training data)

| Model | Size | Origin | Performance | License |
|---|---|---|---|---|
| **Mistral Large 3** | 675B MoE (41B active) | Mistral (France) | #2 open model on LMArena. Strong multilingual, 256K context | Apache 2.0 |
| **Mistral Small 3.2** | 24B dense | Mistral (France) | Comparable to 70B models on many tasks despite 24B size | Apache 2.0 |

### Tier 3: Open Weights (good license, opaque data, non-EU origin)

| Model | Size | Origin | Performance | License |
|---|---|---|---|---|
| **Qwen 3.5 27B** | 27B dense | Alibaba (China) | NEW (Feb 2026). 800K+ context. Successor to Qwen 3 32B | Apache 2.0 |
| **Qwen 3.5 35B-A3B** | 35B (3B active, MoE) | Alibaba (China) | NEW (Feb 2026). Exceeds 1M context on 32GB VRAM. Extremely efficient | Apache 2.0 |
| **GLM-5** | 744B MoE (40B active) | Zhipu AI / Z.ai (China) | NEW (Feb 2026). 205K context, 128K output. 77.8% SWE-bench, 92.7% AIME 2026. Trained on Huawei Ascend. On OpenRouter | MIT |
| **Kimi K2.5** | 1T MoE (32B active) | Moonshot AI (China) | NEW (Jan 2026). 256K context. Native multimodal. Agent swarm mode. On OpenRouter | Modified MIT |
| **MiniMax M2.5** | 230B MoE (10B active) | MiniMax (China) | NEW (Feb 2026). 205K context. Lightning Attention. 80.2% SWE-bench. Extremely cheap. On OpenRouter | Modified MIT |
| **Qwen 3 32B** | 32B dense | Alibaba (China) | Benchmark leader at 32B. Hybrid thinking modes. Superseded by Qwen 3.5 27B | Apache 2.0 |
| **Gemma 3 27B** | 27B | Google (US) | Same size class as Mistral Small. Good comparator | Open |
| **Llama 3.3 70B** | 70B | Meta (US) | Text-only = EU-legal. Reliable 70B baseline | Meta license |
| **GPT-oss-120B** | 120B | OpenAI (US) | Apache 2.0. OpenAI's first open-weight model. Strong reasoning | Apache 2.0 |

---

## Frontier Closed Models (March 2026)

| Model | Provider | Tier | Notes |
|---|---|---|---|
| **GPT-5.4** | OpenAI | Top | (Mar 5). $2.50/$15.00. 1M context. 83% GDPval |
| **Gemini 3.1 Pro** | Google | Top | (Feb 19). 77.1% ARC-AGI-2, 1M context, 65K output. Thinking mode |
| **Claude Opus 4.6** | Anthropic | Top | Top reasoning performance. 1M context (beta). 128K output |
| **Claude Sonnet 4.6** | Anthropic | Top | Strong reasoning, faster than Opus. Best value at frontier tier |
| **GPT-5.2** | OpenAI | High | 400K context, 100% AIME 2025. Superseded by GPT-5.4 |
| **GPT-5** | OpenAI | High | Previous flagship, still strong |

---

## Free Models on OpenRouter (March 2026)

Rate limits: 20 RPM, 200 req/day without credits, higher with credits.

| Model | Params | Notes |
|---|---|---|
| **Llama 3.3 70B** | 70B | GPT-4 level, reliable baseline |
| **DeepSeek R1** | 671B MoE | Strong reasoning, Chinese-origin (high EU risk) |
| **DeepSeek V3** | 671B MoE | General purpose, same risk as R1 |
| **Qwen3 Coder 480B** | 480B MoE | Strongest free coding model, 262K context |
| **Mistral Small 3.1** | 24B | Slightly older than 3.2 |
| **Gemma 3 27B** | 27B | Google, open weights, 27B class |
| **NVIDIA Nemotron Nano 9B v2** | 9B | Fast, good for testing |
| **GLM-5** | 744B MoE (40B active) | Frontier-class open-weight. MIT license. Chinese-origin (high EU risk) |
| **MiniMax M2.5** | 230B MoE (10B active) | Extremely cheap. Modified MIT. Chinese-origin (high EU risk) |
| **Dolphin Mistral Venice 24B** | 24B | Uncensored Mistral fine-tune. Venice-hosted |

---

## Models to Watch

| Model | Why | Timeline |
|---|---|---|
| **DeepSeek V4** | ~1T MoE, ~32B active. Apache 2.0. Native multimodal | Released early Mar 2026, not yet on hosted API |
| **DeepSeek V3.2 structured output** | Currently json_object only, no json_schema | Ongoing |
| **NVIDIA Nemotron 3 Super/Ultra** | ~100B / ~500B. Hybrid Mamba-Transformer MoE | H1 2026 |
| **OpenEuroLLM** | EU institutional sovereign LLM | Mid-2026 |
| **K2-V2 hosted inference** | 70B fully open, no hosted inference yet | No timeline |
| **Guide Labs Steerling-8B** | Every output token traceable to training data origins. Interesting for interpretability | Available now, 8B only |

---

## Staleness Checklist

When updating this file, verify:
- [ ] Are the "free on OpenRouter" models still free?
- [ ] Have any new Mistral models been released?
- [ ] Has OpenEuroLLM shipped anything yet?
- [ ] Are the frontier model rankings still accurate?
- [ ] Have rate limits or pricing changed?
- [ ] Any new open-weight models in the 24-32B range?
- [ ] Is K2-V2 available on any hosted provider?
- [ ] Has DeepSeek V4 landed on hosted APIs?
- [ ] Any new EU-sovereign options beyond Mistral?
