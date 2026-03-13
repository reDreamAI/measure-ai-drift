# Literature Grounding Citations

> Where each source fits in the thesis. Organized by chapter/section.
> Zotero keys in backticks. Sources marked **[ADD]** are not yet in Zotero.

---

## 1 Introduction

### 1.2 AI-Assisted Psychotherapy
- `DTKNEPHQ` Stade et al. (2024) "Large language models could change the future of behavioral healthcare." *npj Mental Health Research*.
  Use: foundational framing for LLM deployment in mental health. Roadmap paper, not specific methods.

### 1.3 The Evaluation Gap
- `B97RI7GA` Chiu et al. (2024) "A Computational Framework for Behavioral Assessment of LLM Therapists." *arXiv:2401.00820*.
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

- `34DFEBDG` Albanese et al. (2022) "Nightmare Rescripting: Using Imagery Techniques to Treat Sleep Disturbances in PTSD." *Frontiers in Psychiatry* 13:866144.
  Use: contains the empirical rescripting strategy breakdown (58% alternative endings, 23% positive images, 13% threat transformation, 10% lucidity cues, 8% distancing). Grounds our taxonomy in observed patient behavior. Cites Harb et al. as original source of the percentages.

### 2.2 Treatment Fidelity in LLM-Based Interventions
- `DTKNEPHQ` Stade et al. (2024) -- also cited in 1.2
  Use: capability vs reliability distinction. "Stability as precondition for deployment."

- `B97RI7GA` Chiu et al. (2024) BOLT -- also cited in 1.3
  Use: their 13 behavioral codes measure therapist action quality. Our framework measures action *consistency*. Direct methodological contrast.

### 2.4 Evaluation Metrics
- (BERTScore, LLM-as-judge references already handled in design docs)

---

## 3 Methods

### 3.2 Dialogue Generation (patient vignette design)
- `Z22JYAMU` Wang et al. (2024) "Roleplay-doh: Enabling domain-experts to create LLM-simulated patients." *arXiv:2407.00870* (EMNLP 2024).
  Use: cite for synthetic patient methodology. Their principle-adherence pipeline validates expert-driven vignette design. Our BDI-profiled vignettes follow a similar expert-grounded approach but without their iterative refinement loop (acknowledge as limitation).
  Note: fills the `??` placeholder in thesis_structure_dynamic.md line 164.

- `CQ94GEYA` Wang et al. (2024) "Patient-Ψ: Using Large Language Models to Simulate Patients for Training Mental Health Professionals." *arXiv:2405.19660*.
  Use: clinical grounding for patient vignette profiles. Their cognitive conceptualization diagrams (CBT belief structures) and 6 conversational styles (direct, resistant, expressive, minimal, deviating, agreeable) parallel our 6 vignette archetypes.

### 3.3 Frozen History Generation
- `WXMRG3JE` Cook et al. (2025) "Virtual patients using LLMs: Scalable, contextualized simulation of clinician-patient dialogue with feedback." *JMIR* 27, e68486.
  Use: validates LLM-to-LLM dialogue generation for clinical training. Their feedback mechanism parallels our frozen history approach (generate dialogue, then evaluate therapist output separately).

- `Q4SUNKHC` Chen et al. (2025) "Trustworthy AI Psychotherapy: Multi-agent LLM Workflow for Counseling." *arXiv:2508.11398*.
  Use: multi-agent therapeutic workflow where specialized agents handle distinct therapeutic functions. Relevant to our pipeline architecture (patient agent + therapist agent + judge).

- `BE9EV5EQ` Bi et al. (2025) "MAGI: Multi-agent Guided Interview for Psychiatric Assessment." *arXiv:2504.18260*.
  Use: structured multi-agent interview protocol. Their guided interview mechanism is analogous to our stage-based conversation flow (recording, exploring, rewriting).

### 3.4 Strategy Taxonomy

Our 6-category taxonomy (confrontation, self_empowerment, safety, cognitive_reframe, social_support, sensory_modulation) was built from two clinical foundations: Germain's mastery dimensions and Harb's empirical rescripting categories. Both classify what changes in a rescripted nightmare, but at different levels of abstraction. We chose *mechanism-level* categories (HOW the change works) rather than outcome-level (WHAT the dreamer achieves) because mechanism categories produce discrete, non-overlapping sets that Jaccard scoring requires.

**Clinical grounding (mastery dimensions):**

- `62ZMHBC3` Germain et al. (2004) "Increased Mastery Elements Associated With IRT for Nightmares." *Dreaming* 14(4), 195-206.
  Their Multidimensional Mastery Scale has 6 dimensions. The mapping to our taxonomy:
  - Physical Mastery (bodily action) maps to **confrontation** (action toward threat) and **self_empowerment** (dreamer transforms)
  - Social Mastery (enlisting help) maps to **social_support**
  - Environmental Mastery (changing surroundings) maps to **sensory_modulation** (sensory shift) and **safety** (barriers)
  - Emotional Mastery (internal calming) maps to **sensory_modulation** (merged with emotional_regulation in v4)
  - Mystical Mastery (supernatural transformation) maps to **cognitive_reframe** (element changes meaning) and **self_empowerment** (dreamer gains magical ability)
  - Avoidance (escape, withdrawal) -- deliberately excluded. See rationale below.

**Clinical grounding (empirical rescripting strategies):**

- `25UR8BHJ` Harb et al. (2012) "Combat-Related PTSD Nightmares and Imagery Rehearsal." *Journal of Traumatic Stress* 25, 511-518.
  5 rescripting categories coded by independent raters. The mapping:
  - Alternative endings (58%) maps to **confrontation** or **self_empowerment** (depends on how ending changes)
  - Positive image insertion (23%) maps to **sensory_modulation**
  - Threat transformation (13%) maps to **cognitive_reframe**
  - Reality markers (10%) -- excluded. Lucid dreaming cue, not a rescripting mechanism.
  - Distancing (8%) -- excluded. See avoidance rationale below.

**Why avoidance/distancing is excluded:**

- `25UR8BHJ` Harb et al. (2012) found that violence in rescripted dreams predicted *worse* treatment outcomes. Effective rescripting resolves the central nightmare theme rather than escaping it. Distancing was the least-used strategy (8%) and does not resolve the threat.
- `34DFEBDG` Albanese et al. (2022) (also cited in 2.1) reviews that IRT works by increasing mastery *over* the nightmare, not by avoiding it. Avoidance reinforces the fear memory rather than overwriting it.
- `FGA5H3ZD` Krakow & Zadra (2006) frame IRT as "changing the nightmare" not "leaving the nightmare." The five-stage protocol targets transformation, not withdrawal.

Our taxonomy captures all therapeutically desirable mechanisms from both scales. The uncovered dimensions (avoidance, reality markers) are either clinically counterproductive in single-turn rescripting or outside the scope of IRT.

- `34DFEBDG` Albanese et al. (2022) -- also cited in 2.1
  Use: empirical rescripting strategy breakdown grounds our taxonomy in observed patient behavior.

---

## Sources still missing

- AI therapist action-selection mechanism paper -- not yet identified. User recalls a paper defining how an LLM therapist should decide what therapeutic action to take.

## Verified wrong citations (do NOT use)

- "Gieselmann, Auer & Bohne (2022) Frontiers in Psychiatry" -- does not exist. Conflation of Albanese et al. (2022) and Gieselmann et al. (2019, Journal of Sleep Research). The rescripting categories come from Albanese/Harb, not Gieselmann.
