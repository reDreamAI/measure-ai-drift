# Thesis TODO

Thesis-specific tasks. For pipeline and source grounding, see [TODO.md](TODO.md).

---

## Blocking: before writing can finish

- [x] Run full experiment (6,000 trials: 10 models x 6 vignettes x 5 temps x 20 trials). Data in stats/data/experiment_runs.csv
- [ ] Judge validation: spot-check ~50 trials, compute Cohen's kappa. Blocks 3.5.3 final wording and 5.4
- [ ] Verify remaining therapy_temp sources (see [grounded/temperature_sources.md](grounded/temperature_sources.md)). Blocks 3.7

## Stats and figures (stats/)

- [x] Run `aggregate.py`, `descriptives.py`, `tests.py` on real N=20 data
- [x] Generate all result figures (fig scripts in stats/scripts/)
- [ ] Check alignment ceiling effect. If alignment stays near 1.0, downgrade Method 3 from comparative metric to validation check (affects 5.4 and 6.1)
- [ ] Review all figures before including in thesis

## Conceptual diagrams (still needed)

- [ ] Fig 1.1: IRT five-stage overview (stages, clinical goals, where rescripting sits)
- [ ] Fig 1.2: Gap diagram (capability benchmarks vs. clinical reliability)
- [x] Fig 3.1-3.3: all generated, in `thesis/figures/`

## Figure placement plan

### Ch1 Introduction (conceptual, not yet drawn)
- [ ] **Fig 1.1** in 1.1: IRT five-stage overview (stages, clinical goals, where rescripting sits)
- [ ] **Fig 1.2** in 1.3: Gap diagram (capability benchmarks vs. clinical reliability)

### Ch3 Methodology (generated, in `thesis/figures/`)
- [ ] **Fig 3.1** in 3.1 System Overview: two-stack pipeline (`fig_3_1_pipeline.pdf`)
- [ ] **Fig 3.2** in 3.4 Evaluation Stack: frozen history fan-out to trials (`fig_3_3_eval_stack.pdf`)
- [ ] **Fig 3.3** in 3.7 Evaluation Metrics: three-level measurement framework (`fig_3_2_measurement.pdf`)

### Ch5 Results -- main text (5 figures, in `stats/visuals_experiment/`)
- [ ] **Fig 5.1** in 5.2 Plan Consistency: Jaccard 3-panel by family (`fig_5_2_jaccard.pdf`) -- headline result
- [ ] **Fig 5.2** in 5.2 Plan Consistency: modal-set agreement (`fig_5_2b_modal_agreement.pdf`) -- exact-match complement
- [ ] **Fig 5.3** in 5.4 Alignment: plan-output alignment by temperature + per model (`fig_5_6_alignment.pdf`)
- [ ] **Fig 5.4** in 5.5 Cross-Method: strategy vs. semantic consistency scatter (`fig_5_5_correlations.pdf`)
- [ ] **Fig 5.5** in 5.6 Secondary: slice depth stability, Mistral Large 3 (`fig_slice_depth_metrics.pdf`)

### Ch6 Discussion
- [ ] **Fig 6.1** in 6.5 Framework Reflections: seed comparison (`fig_seed_comparison.pdf`) -- seed does not help

### Appendix D: Supplementary Results
- [ ] **Fig D.1**: strategy distribution by model (`fig_5_1_strategy_distribution.pdf`)
- [ ] **Fig D.2**: BERTScore 3-panel by family (`fig_5_3_bertscore.pdf`) -- limited sensitivity, see analysis finding 6
- [ ] **Fig D.3**: vignette heatmaps per temperature (`fig_5_4_vignette_slice.pdf`)
- [ ] **Fig D.4**: per-temperature correlation panels (`fig_5_6_correlations_by_temp.pdf`)
- [ ] **Fig D.5**: slice depth heatmap (`fig_slice_depth_heatmap.pdf`)
- [ ] **Fig D.6**: plan validity rate (`fig_A1_validity.pdf`)

## Writing: chapters (priority order)

- [x] **Ch3 Methods** -- full draft. Needs: diagrams inserted, model table finalized after LLM selection
- [x] **Ch4 Implementation** -- full draft. Needs: dirtree package for directory listing
- [x] **Ch2 Background** -- full draft. Needs: diagrams, ROUGE vs BERTScore example, 2.3 prior-work citations
- [x] **Ch1 Introduction** -- full draft. Needs: two conceptual diagrams
- [ ] **Ch5 Results** -- skeleton exists. Blocked on experiment data
- [ ] **Ch6 Discussion** -- skeleton exists. Blocked on results. Include: BERTScore limitation (insensitive to plan-level instability, see [analysis.md](analysis.md) finding 6)
- [ ] **Ch7 Conclusion** -- not started. Blocked on discussion

## Writing: appendices

- [ ] **A: Strategy Taxonomy** -- category definitions, examples, v1-v4 revision history. Material exists in citations.md and strategy_taxonomy_evolution.md
- [ ] **B: Prompts** -- system prompt, judge rubric, vignette profiles. Extract from src/
- [ ] **C: Architecture Diagrams** -- three-agent dialogue loop (patient, router, therapist message flow during frozen history generation), expanded pipeline diagram
- [ ] **D: Supplementary Results** -- full per-condition tables. Blocked on experiment

## Source grounding (thesis-relevant subset)

- [ ] Find AI therapist action-selection mechanism paper (from TODO.md, relevant for 2.2)
- [ ] Add min-p / dynamic truncation citation for future work (Nguyen et al., 2025, ICLR). Relevant for 7.3
- [ ] Verify all Zotero entries match references.bib (51 entries exported, may have grown)

### Missing bib entries (block compilation of Ch2-4)

- [x] **BERTScore**: Zhang et al. (2020), ICLR. Zotero `PUYCKUYY`, added to references.bib
- [x] **DeBERTa**: He et al. (2021), ICLR. Zotero `8MQC2H2V`, added to references.bib
- [x] **Renze (2024)**: EMNLP Findings. Zotero `96K5MF6A`, added to references.bib
- [x] **Liu and Tsai (2026)**: arXiv:2603.11082v1. Zotero `32QZTBPH`, added to references.bib
- [ ] **Google Gemini 3 Developer Guide (2026)**: https://ai.google.dev/gemini-api/docs/text-generation. Add to Zotero as web source. Grounds the T=1.0 requirement for judge
- [ ] **2.3 prior-work citations**: find specific citations for factual consistency, output diversity, and benchmark reproducibility studies

### Temperature source verification (block Ch3 3.8 finalisation)

- [x] **Mistral Small 3.2 T=0.15**: HF generation_config.json [VERIFIED]
- [ ] **Mistral Large 3 T=0.15**: query Mistral `/models` endpoint for `mistral-large-2512` default. Currently assumed same as Small 3.2
- [ ] **Mistral Small 4 T=0.15**: query Mistral `/models` endpoint for `mistral-small-2603` default. Currently assumed same family
- [x] **Qwen 3.5 T=0.6**: HF generation_config.json [VERIFIED]
- [x] **OLMo 3.1 T=0.6**: HF generation_config.json [VERIFIED]
- [ ] **Llama 3.3 T=0.6**: HF repo is gated (401). Check with gated access or llama-recipes repo
- [ ] **GPT-5.4 T=0.7**: OpenAI API docs returned 403. Check authenticated or test empirically
- [x] **Sonnet 4.6 T=0.7**: Anthropic API docs [VERIFIED]
- [ ] **OpenAI reintroduced temperature with GPT-5.2**: need source (blog post, API changelog, or docs). Grounds why GPT-5.4 non-thinking accepts temperature
- [ ] **Anthropic character training**: source for Sonnet 4.6 safety-aware interaction claim (anthropic.com/research/claude-character)

## Polish (after all chapters drafted)

- [ ] Style pass: check against [STYLE.md](STYLE.md) (no em-dashes, no semicolons, active voice)
- [ ] Cross-reference pass: verify all forward/backward references (e.g., "grounded in 2.1", "discussed in 6.4")
- [ ] Word count check: bachelor thesis target ~15-20K words
- [ ] Abstract (write last)
