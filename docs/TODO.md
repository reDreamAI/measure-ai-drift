# TODO

## Now: pipeline smoke test

- [ ] Run test pipeline on existing frozen histories (test targets: Llama 70B, GPT-oss-120B)
- [ ] Re-evaluate strategy taxonomy distribution: v3 resolved the 87.7% empowerment skew, but verify current models do not collapse back into mastery/empowerment dominance
- [ ] Check plan validity rates and strategy spread across vignettes before committing to full run

## Pre-experiment (blocking full run)

- [ ] Test structured output compliance: all 6 eval targets must produce valid `<plan>` blocks
- [ ] Switch `models.yaml` from testing to experiment mode
- [ ] Link Zotero to `thesis/references.bib`
- [ ] Find Roleplay-doh citation (placeholder `??` in `docs/thesis_structure_dynamic.md` line 164)

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
- [ ] Strategy distribution heatmap figure (`??` in structure doc line 395)
