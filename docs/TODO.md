# TODO

## Done: pipeline smoke test (2026-03-12)

- [x] Run test pipeline on frozen histories: 12/12 completed (llama70b + gpt-oss x 6 vignettes, T=0.7, slice_2, 10 trials each)
- [x] Taxonomy v3 validated: all 7 categories appeared, no empowerment/mastery dominance
- [x] 100% plan validity across all runs
- [x] Strategy spread healthy: sensory_modulation, cognitive_reframe, safety, self_empowerment, confrontation all well-represented; emotional_regulation and social_support rarest
- [x] Llama less consistent than GPT-oss (mean Jaccard ~0.57 vs ~0.78), resistant vignette hardest for both

## Done: compliance testing and taxonomy v4 (2026-03-12)

- [x] Structured output compliance: 6/6 eval targets produce valid `<plan>` blocks (OLMo needed parser fallback for non-standard tag formats)
- [x] Taxonomy v4: merged emotional_regulation into sensory_modulation (7 → 6 categories). emotional_regulation was picked 1/120 trials (0.4%). Sharpened cognitive_reframe vs self_empowerment boundary.
- [x] All eval targets in single `evaluation_targets` list (no more comment-swapping)

## Pre-experiment (blocking full run)
- [x] Link Zotero to `thesis/references.bib` (51 BibLaTeX entries exported)
- [x] Find Roleplay-doh citation (Wang et al., 2024, EMNLP)
- [x] Identify "mystical mastery" IRT rescripting taxonomy paper
  - Germain et al. (2004). *Dreaming*, 14(4), 195-206. DOI: 10.1037/1053-0797.14.4.195
  - Multidimensional Mastery Scale (MMS): Physical, Social, Environmental, Emotional, Mystical, Avoidance
  - Also found: Harb et al. (2012). *J Traumatic Stress*, 25, 511-518. DOI: 10.1002/jts.21748
  - 5 rescripting categories: alternative endings, positive image insertion, threat transformation, reality markers, distancing
- [x] Patient vignette taxonomy: N/A, vignettes are original (grounded in Roleplay-doh + Patient-Ψ)
- [x] Add papers to Zotero: Germain (2004), Harb (2012), Chiu/BOLT (2024), Albanese (2022), Patient-Ψ (2024)
- [ ] Identify AI therapist action-selection mechanism paper (user recalls but not yet found)
- [x] Refine taxonomy v4 against clinical precedent (Germain MMS + Harb rescripting categories)
  - Mapped all MMS dimensions and Harb categories to our 6 categories
  - No gaps in therapeutically desirable mechanisms
  - Avoidance/distancing excluded (Harb: violence in rescripts predicts worse outcomes)
  - Reality markers excluded (lucid dreaming cue, not rescripting mechanism)
  - Documented in citations.md section 3.4

## Experiment

- [ ] Run full experiment (8 models x 6 vignettes x 5 temps x 10 trials = 2,400 trials + therapy_temp extra runs)
- [ ] Judge validation: spot-check 10 random trials against Gemini judge scores
  - Read response + judge reasoning + score for each
  - Report agreement count (e.g., 10/10) in Methods
  - Include table in appendix
  - Judge now at T=1.0 (Gemini 3 requirement), consistency from structured rubric

## Source verification (docs/grounded/temperature_sources.md)

- [ ] **Mistral Large 3 therapy_temp (0.15):** Query Mistral `/models` endpoint for `mistral-large-2512` actual default. Or check La Plateforme model card
- [ ] **Llama 3.3 70B therapy_temp (0.6):** Check `generation_config.json` with gated HuggingFace access, or verify via llama-recipes repo
- [ ] **GPT-5.4 therapy_temp (0.7):** Check OpenAI API reference while authenticated, or test empirically
- [ ] **Gemini judge T=1.0:** Add all three sources to Zotero:
  - Google AI for Developers (2026). Gemini 3 Developer Guide (primary)
  - Liu & Tsai (2026). arXiv:2603.11082v1 (Gemini 3.1 Pro as LLM judge precedent)
  - Renze (2024). EMNLP Findings. "The Effect of Sampling Temperature on Problem Solving in LLMs"
- [ ] **Claude Sonnet 4.6:** Add sources to Zotero:
  - Anthropic (2026). "Claude's Character" (anthropic.com/research/claude-character)
  - Anthropic (2026). Claude Sonnet 4.6 announcement (anthropic.com/news/claude-sonnet-4-6)
  - Anthropic (2026). Claude API Documentation (platform.claude.com/docs)
- [ ] **Model temperature sources:** Add to Zotero:
  - DeepSeek API Documentation (api-docs.deepseek.com/quick_start/parameter_settings)
  - HuggingFace generation_config.json files for: Qwen 3.5, OLMo 3.1, Trinity Large

## Statistics and visualization (see docs/statistics.md)

- [ ] `stats/scripts/aggregate.py` -- runs -> single CSV (test on March 12 smoke data first)
- [ ] `stats/scripts/descriptives.py` -- medians/IQR for Jaccard, means/SD for BERTScore
- [ ] `stats/scripts/tests.py` -- Wilcoxon (temp), Kruskal-Wallis (models, exploratory), Spearman (Jaccard vs BERTScore)
- [ ] Figure scripts (5 figures, alignment only if variance appears):
  - [ ] `fig_validity_strategy.py` -- Fig 5.1: validity bars + strategy stacked bars
  - [ ] `fig_jaccard.py` -- Fig 5.2: Jaccard + modal-set by model x temperature (headline)
  - [ ] `fig_bertscore.py` -- Fig 5.3: BERTScore F1 by model x temperature
  - [ ] `fig_vignette_slice.py` -- Fig 5.4: vignette heatmap + slice depth
  - [ ] `fig_correlations.py` -- Fig 5.5: Jaccard vs BERTScore scatter
- [ ] Review figures with user before including in thesis

## Future work notes (for Ch6 Discussion / Ch7 Conclusion)

- [ ] **Dynamic truncation for safety**: Cite Nguyen et al. (2025), "Turning Up the Heat: Min-p Sampling for Creative and Coherent LLM Outputs," ICLR 2025 Oral (arXiv:2407.01082). Min-p sampling scales the truncation threshold based on the top token's probability, outperforming standard top-p in balancing quality and diversity at higher temperatures. Relevant for therapeutic interventions where slight narrative variance (creativity) is needed without risking hallucinatory or unsafe outputs. Add to Zotero.

## Writing (priority order)

- [ ] Ch3 Methods (11K draft, in progress)
- [ ] Ch4 Implementation (stub only)
- [ ] Ch2 Background (6.2K draft, in progress)
- [ ] Ch5 Results (skeleton, blocked on experiment)
- [ ] Ch6 Discussion (skeleton, blocked on experiment)
- [ ] Ch7 Conclusion (not started)
