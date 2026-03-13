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

- [ ] Run full experiment (6 models x 6 vignettes x 3 slices x 10 trials x 2 temps = 2,160 trials)
- [ ] Judge validation: spot-check 10 random trials against Gemini judge scores
  - Read response + judge reasoning + score for each
  - Report agreement count (e.g., 10/10) in Methods
  - Include table in appendix
  - No Cohen's kappa needed: deterministic judge (t=0.0), cross-model (Gemini vs eval targets), reasoning traces published

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

## Writing (priority order)

- [ ] Ch3 Methods (11K draft, in progress)
- [ ] Ch4 Implementation (stub only)
- [ ] Ch2 Background (6.2K draft, in progress)
- [ ] Ch5 Results (skeleton, blocked on experiment)
- [ ] Ch6 Discussion (skeleton, blocked on experiment)
- [ ] Ch7 Conclusion (not started)
