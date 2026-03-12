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
- [ ] Link Zotero to `thesis/references.bib`
- [x] Find Roleplay-doh citation (Wang et al., 2024, EMNLP)
- [ ] Add BOLT (Chiu et al., 2024) and Albanese et al. (2022) to Zotero
- [ ] Identify "mystical mastery" IRT rescripting taxonomy paper
- [ ] Identify therapist vignette/taxonomy paper

## Experiment

- [ ] Run full experiment (6 models x 6 vignettes x 3 slices x 10 trials x 2 temps = 2,160 trials)
- [ ] Judge validation: manually annotate ~50 trials, compute Cohen's kappa against Gemini

## Writing (priority order)

- [ ] Ch3 Methods (11K draft, in progress)
- [ ] Ch4 Implementation (stub only)
- [ ] Ch2 Background (6.2K draft, in progress)
- [ ] Ch5 Results (skeleton, blocked on experiment)
- [ ] Ch6 Discussion (skeleton, blocked on experiment)
- [ ] Ch7 Conclusion (not started)
