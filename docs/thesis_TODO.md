# Thesis TODO

Thesis-specific tasks. For pipeline and source grounding, see [TODO.md](TODO.md).

---

## Blocking: before writing can finish

- [ ] Run full experiment (2,160 trials). Blocks Ch5, Ch6, Ch7
- [ ] Judge validation: spot-check ~50 trials, compute Cohen's kappa. Blocks 3.5.3 final wording and 5.4
- [ ] Verify remaining therapy_temp sources (see [grounded/temperature_sources.md](grounded/temperature_sources.md)). Blocks 3.7

## Stats and figures (stats/)

- [ ] Run `aggregate.py` on real experiment data (currently tested on smoke data only)
- [ ] Run `descriptives.py` and `tests.py` on real data
- [ ] Generate all five result figures (fig scripts exist, need real data)
- [ ] Check alignment ceiling effect. If alignment stays at 1.0, downgrade Method 3 from comparative metric to validation check (affects 5.4 and 6.1)
- [ ] Review all figures before including in thesis

## Conceptual diagrams (draw, not code)

These go into Ch1-3. Generated diagrams are in `thesis/figures/`.

- [ ] 1.1: IRT five-stage overview (stages, clinical goals, where rescripting sits)
- [ ] 1.3: Gap diagram (capability benchmarks vs. clinical reliability)
- [x] 3.1: Two-stack pipeline (`fig_3_1_pipeline`)
- [x] 3.3: Frozen history and measurement design (`fig_3_3_eval_stack`)
- [x] 3.5: Three-level evaluation framework (`fig_3_2_measurement`)

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
