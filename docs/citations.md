# Literature Grounding Citations

> Where each source fits in the thesis. Organized by chapter/section.
> Zotero keys in backticks. Sources marked **[ADD]** are not yet in Zotero.

---

## 1 Introduction

### 1.2 AI-Assisted Psychotherapy
- `DTKNEPHQ` Stade et al. (2024) "Large language models could change the future of behavioral healthcare." *npj Mental Health Research*.
  Use: foundational framing for LLM deployment in mental health. Roadmap paper, not specific methods.

### 1.3 The Evaluation Gap
- **[ADD]** Chiu et al. (2024) "A Computational Framework for Behavioral Assessment of LLM Therapists." *arXiv:2401.00820*. DOI: 10.48550/arXiv.2401.00820
  Use: closest prior work. BOLT measures behavioral *quality* (13 behavioral codes from MI coding). We measure behavioral *stability*. Cite to differentiate: they ask "does the LLM do the right thing?", we ask "does it do the *same* thing?"
  Note: 13 behavioral codes (reflections, questions, solutions), not 13 therapy approaches. Unpublished preprint.

---

## 2 Background

### 2.1 Imagery Rehearsal Therapy
- `FGA5H3ZD` Krakow & Zadra (2006) "Clinical management of chronic nightmares: IRT." *Behavioral Sleep Medicine* 4(1), 45-70.
  Use: primary IRT reference. Five-stage protocol, "change the nightmare any way you wish." Deliberately open-ended rescripting.

- `YIAHJLNY` Krakow et al. (2001) "IRT for chronic nightmares in sexual assault survivors." *JAMA* 286(5), 537-545.
  Use: landmark RCT establishing IRT as evidence-based. 114 participants, significant reduction in nightmare frequency and PTSD severity.

- `IYVNR3FA` Krakow et al. (1995) "Imagery rehearsal treatment for chronic nightmares." *Behaviour Research and Therapy* 33(7), 837-843.
  Use: early IRT work. Cite for historical grounding if needed.

- `34M7Y3F8` Morgenthaler et al. (2018) "Position paper for the treatment of nightmare disorder." *Journal of Clinical Sleep Medicine* 14(6), 1041-1055.
  Use: clinical consensus on IRT as recommended treatment. Strengthens "gold standard" claim.

- `S43I93ZQ` Forbes et al. (2001) "IRT in combat veterans." *Journal of Traumatic Stress* 14(2), 433-442.
  Use: IRT generalizability beyond sexual assault populations. Optional cite.

- **[ADD]** Albanese et al. (2022) "Nightmare Rescripting: Using Imagery Techniques to Treat Sleep Disturbances in PTSD." *Frontiers in Psychiatry* 13:866144. DOI: 10.3389/fpsyt.2022.866144
  Use: contains the empirical rescripting strategy breakdown (58% alternative endings, 23% positive images, 13% threat transformation, 10% lucidity cues, 8% distancing). Grounds our taxonomy in observed patient behavior. Cites Harb et al. as original source of the percentages.

### 2.2 Treatment Fidelity in LLM-Based Interventions
- `DTKNEPHQ` Stade et al. (2024) -- also cited in 1.2
  Use: capability vs reliability distinction. "Stability as precondition for deployment."

- **[ADD]** Chiu et al. (2024) BOLT -- also cited in 1.3
  Use: their 13 behavioral codes measure therapist action quality. Our framework measures action *consistency*. Direct methodological contrast.

### 2.4 Evaluation Metrics
- (BERTScore, LLM-as-judge references already handled in design docs)

---

## 3 Methods

### 3.2 Dialogue Generation (vignette design)
- `Z22JYAMU` Wang et al. (2024) "Roleplay-doh: Enabling domain-experts to create LLM-simulated patients." *arXiv:2407.00870* (EMNLP 2024).
  Use: cite for synthetic patient methodology. Their principle-adherence pipeline validates expert-driven vignette design. Our BDI-profiled vignettes follow a similar expert-grounded approach but without their iterative refinement loop (acknowledge as limitation).
  Note: fills the `??` placeholder in thesis_structure_dynamic.md line 164.

### 3.4 Strategy Taxonomy
- **[ADD]** Albanese et al. (2022) -- also cited in 2.1
  Use: our 6-category taxonomy maps to *mechanism* rather than *observed patient behavior*. Cite Albanese's empirical categories to show the clinical grounding, then explain why we chose mechanism-level categories (Jaccard scoring requires discrete, non-overlapping sets).

---

## Sources to add to Zotero

1. Chiu et al. (2024) BOLT. arXiv:2401.00820. DOI: 10.48550/arXiv.2401.00820
2. Albanese et al. (2022) Nightmare Rescripting. Frontiers in Psychiatry 13:866144. DOI: 10.3389/fpsyt.2022.866144

## Sources still missing (user may have seen)

- IRT rescripting taxonomy with "mystical mastery" category -- not found in Zotero or web search. User to identify.
- Therapist vignette/taxonomy paper -- not found. User to identify.

## Verified wrong citations (do NOT use)

- "Gieselmann, Auer & Bohne (2022) Frontiers in Psychiatry" -- does not exist. Conflation of Albanese et al. (2022) and Gieselmann et al. (2019, Journal of Sleep Research). The rescripting categories come from Albanese/Harb, not Gieselmann.
