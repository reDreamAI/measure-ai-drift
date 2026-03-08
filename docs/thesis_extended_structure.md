# Thesis: Table of Contents

**Measuring Drift in Therapeutic AI: A Stability-Based Evaluation of Sovereign LLMs in Nightmare Therapy**

Daniel Menzel, Institute of Cognitive Science, University of Osnabruck
Supervisors: Moritz Hartstang, Sebastian Musslick

> **Visualisation legend**
> [FIG] Conceptual diagram — logic, structure, or framework
> [GRAPH] Data figure — empirical results or distributions
> [Example] Worked instance — concrete case to build intuition

---

## Abstract

---

## 1 Introduction

   ### 1.1 Nightmare Disorder and Imagery Rehearsal Therapy
   - ~5% prevalence; strong comorbidity with PTSD and depression
   - IRT as evidence-based gold standard — rigid, phase-driven protocol
      - *Why IRT?* Its fixed structure makes it uniquely testable for protocol adherence
   - Rescripting as the cognitive core — narrative transformation as the key intervention
   - Clinician shortage as the practical motivation for scalable AI-assisted delivery
   - [FIG] *IRT five-stage overview — stages, clinical goals, where rescripting sits*

   ### 1.2 AI-Assisted Psychotherapy
   - Growing LLM deployment in mental health — from empathy tools to full CBT state
     machines — driven by scalability and access (Stade et al., 2024; NPJ MHR, 2024)
   - reDreamAI: consumer-facing IRT chatbot guiding users through all five protocol stages
      - Not a research prototype — a real deployment target where reliability is
        non-negotiable
   - **The problem this creates:** reDreamAI is not a general assistant — it is a
     *protocol-driven agent* bound to a manualized intervention
      - A general assistant has no therapeutic obligation; variability across sessions
        is fine — no single response is wrong
      - A protocol agent must make consistent strategic decisions across sessions and
        users — inconsistency is not stylistic variation, it is a clinical failure
      - *Why this matters for evaluation:* unlike rule-based chatbots whose behaviour
        can be reviewed once before deployment, an LLM agent must be evaluated
        repeatedly — each run is a new draw from the output distribution
      - *The deeper point:* stability is a necessary precondition for clinical
        deployment — not sufficient on its own, but without it, no claim about
        therapeutic quality is meaningful (see 2.2 for conceptual grounding)
   - EU AI Act and data sovereignty requirements push toward self-hosted EU-resident
     models → introduces the sovereign model constraint (detailed in 2.2)

   ### 1.3 The Evaluation Gap
   - Standard NLP benchmarks optimise for capability, not clinical reliability
   - No existing metrics for: intent stability, protocol adherence, strategic consistency
      - *The core problem:* a capable but inconsistent model is clinically unsafe —
        these two properties are not the same and are currently conflated
   - Prior therapeutic AI evaluation is largely qualitative, post-hoc, or single-session
   - The case for systematic, reproducible in silico clinical trials as a validation paradigm
   - [FIG] *Gap diagram — what capability benchmarks measure vs. what clinical
     reliability requires; the unmeasured space this thesis addresses*

   ### 1.4 Research Objectives
   - **RQ:** How consistent is LLM clinical reasoning across stochastic runs within
     a structured therapeutic protocol?
   - **Contribution 1:** A three-level hierarchical evaluation framework for therapeutic
     AI stability — plan consistency, output consistency, plan–output alignment
   - **Contribution 2:** Quantitative cross-model comparison across sovereign,
     proprietary, and open-weight model classes
   - **Scope:** IRT rescripting phase — isolated as the highest-stakes, most
     cognitively demanding intervention point
      - *Why isolated?* Eliminates stage-routing confounds; enables clean attribution
        of any measured instability to the therapist model

---

## 2 Background

   > *Reading guide:* each subsection establishes one conceptual prerequisite for
   > the methods. 2.1 defines what correct IRT delivery looks like → grounds the
   > evaluation target and Method 3 scoring. 2.2 names the clinical failure modes
   > → each maps to one evaluation method. 2.3 explains the mechanical source of
   > instability → justifies the experimental temperature conditions. 2.4 justifies
   > the chosen metrics → directly grounds Methods 1 and 2. 2.5 resolves the
   > conceptual tension the plan mechanism creates → must precede 3.5.

   ### 2.1 Imagery Rehearsal Therapy
   - *Role:* defines "correct" IRT delivery — the clinical standard the model is
     evaluated against
   - Five-stage protocol: recording → rewriting → summary → rehearsal → final
      - Each stage has defined purpose and bounded appropriate therapist behaviours
      - *→ 3.2:* dialogue generation traverses exactly these stages
   - Rescripting: patient rewrites the nightmare to reduce distress and restore agency
      - *→ 3.6:* the strategy taxonomy scope comes from the space of legitimate
        rescripting moves — no more, no less
   - Treatment fidelity instruments (ENACT, NIH BCC): define adherence gradations
     across absent / partial / implemented
      - *→ 3.7.3:* Method 3's ternary scoring is borrowed from this literature —
        not invented, clinically grounded
   - [Example] *Nightmare excerpt → rescripted version with strategy labels overlaid
     (cognitive_reframe, confrontation) — what a valid rescripting move looks like*

   ### 2.2 Large Language Models in Healthcare
   - *Role:* grounds the general vs. protocol distinction introduced in 1.2 in
     the clinical literature — and establishes stability as a precondition for
     deployment, not a byproduct of capability
   - **The general vs. protocol distinction — conceptual grounding:**
      - Treatment fidelity research (Webb et al., 2010; Waltz et al., 1993)
        formalises what it means for a therapist to deliver an intervention correctly:
        *adherence* (doing the prescribed things) and *competence* (doing them well)
      - Fidelity is only a meaningful concept when there is a protocol to adhere to —
        it is undefined for a general assistant
      - For rule-based chatbots, adherence is built in by construction — responses
        are pre-authored and reviewed once
      - For LLM-based protocol agents, adherence becomes *probabilistic* — it must
        be measured across runs, not assumed from a single review
      - *This thesis measures the stability precondition:* not whether the model
        delivers IRT correctly (no human baseline exists), but whether it delivers
        it *consistently* — which is required before fidelity can even be assessed
      - *→ 3.7:* each evaluation method measures one dimension of what consistency
        means for a stochastic protocol agent
   - Capability vs. reliability — the core gap:
      - A model can produce high-quality individual responses while being clinically
        unreliable across sessions — capability benchmarks cannot detect this
      - *→ 1.3:* this is the evaluation gap the framework addresses
   - Documented LLM failure modes in clinical settings: hallucination, strategy
     drift, stage confusion, persona inconsistency
      - Each maps to one evaluation method in 3.7
   - Regulatory framing: EU AI Act high-risk classification; Medical Device
     Regulation auditability and documentation requirements
      - *→ 3.8:* sovereign model selection is a legal constraint, not a preference
   - [FIG] *EU AI Act risk tier diagram — where autonomous therapeutic AI sits
     and what certification obligations follow*

   ### 2.3 Stochastic Behaviour in Language Models
   - *Role:* makes "drift" mechanistically concrete — explains where instability
     comes from at the model level
   - Temperature sampling: at T>0, token selection is probabilistic — small
     per-token variance compounds across a full therapeutic response
      - *→ 3.9:* T=0.0 is the deterministic ceiling; T=0.7 is the realistic
        clinical deployment range — both are grounded here
   - Clinical consequence: the same patient on two different days may receive
     strategically inconsistent care — this is not benign noise in a manualized protocol
   - Prior stability work targets factual consistency or output diversity —
     not therapeutic strategy stability or protocol adherence
      - *→ 1.3:* this gap in prior work is the direct justification for a
        domain-specific framework
   - [FIG] *Sampling diagram — same frozen history at T=0.0 vs. T=0.7 →
     diverging strategy distributions; intuition for why temperature is the
     primary experimental variable*

   ### 2.4 Evaluation Metrics for Text Generation
   - *Role:* justifies the specific metrics used in Methods 1 and 2 —
     and rules out the obvious alternatives
   - BLEU / ROUGE: surface token overlap — therapeutically equivalent paraphrases
     score near zero; lexically similar but strategically divergent responses score high
      - Ruled out: therapeutic paraphrasing is the norm; surface metrics
        penalise valid variation
   - BERTScore (Zhang et al., 2020): contextual embedding similarity —
     meaning equivalence independent of surface form
      - DeBERTa-XLarge-MNLI chosen: highest WMT16 human correlation (r = 0.778);
        NLI fine-tuning aligns with semantic equivalence over surface matching
      - *→ 3.7.2:* BERTScore F1 is the direct operationalisation of output
        consistency — this subsection is its full justification
   - LLM-as-judge: evaluates criteria no scalar metric can capture
     (e.g. "does this response implement a confrontation strategy?")
      - Known biases: self-preference, position bias, verbosity bias
      - *→ 3.7.3:* cross-model judging and deterministic decoding are the
        direct mitigations for the biases named here
   - [FIG] *ROUGE vs. BERTScore on a matched therapeutic sentence pair —
     where surface overlap fails and why embedding similarity is needed*

   ### 2.5 Chain-of-Thought and Plan Faithfulness
   - *Role:* resolves a conceptual tension the plan mechanism creates —
     must be understood before the plan is introduced in 3.5
   - CoT prompting (Wei et al., 2022): step-by-step generation before answering
     improves output structure and coherence
      - *→ 3.4:* the fused `<plan>` + response call is a CoT-style mechanism
   - The faithfulness problem: CoT explanations often do not reflect actual
     computation — post-hoc rationalisation of an answer reached by other means
     (Turpin et al., 2023; Lanham et al., 2023)
      - *The tension:* if `<plan>` is rationalisation, measuring plan consistency
        may not capture what the model actually decided
   - **Resolution — declared intent framing:** the `<plan>` block is not a
     window into model cognition; it is a structured, measurable output in its own right
      - If strategy declarations vary across runs, clinical responses will vary —
        this is true regardless of whether declarations reflect internal reasoning
      - *→ 3.5:* this framing is the conceptual foundation of the plan mechanism
   - [FIG] *Declared intent spectrum — from faithful CoT to post-hoc
     rationalisation; where declared intent sits and why measuring it is valid either way*

---

## 3 Methods

   ### 3.1 System Overview and Design Rationale
   - Two decoupled stacks: generation (dialogue creation) and evaluation (stability measurement)
      - *Why decoupled?* Evaluation must not be contaminated by generation-side
        randomness — reproducible entry points require frozen, pre-generated histories
   - End-to-end data flow:
     vignettes → generation → frozen histories → evaluation → aggregation
   - [FIG] *Full pipeline diagram — logical data flow across all stages, stack
     boundary marked, example artefact names at each step*

   ### 3.2 Dialogue Generation
   - Three-agent loop: Patient (BDI-profiled vignette), Router (stage classifier),
     Therapist (stage-appropriate response)
      - *Why three agents?* Mirrors clinical interaction structure; separates
        routing logic from therapeutic content generation
   - Six patient vignettes: anxious, avoidant, cooperative, resistant, skeptic, trauma
      - Cover the range of clinical presentation difficulty expected in IRT deployment
   - Full five-stage IRT traversal produces naturalistic conversation histories
     used as frozen evaluation entry points
   - [FIG] *Three-agent loop — single turn cycle with message passing*
   - [Example] *Resistant vignette excerpt — BDI profile and opening patient turn*

   ### 3.3 Frozen History Design
   - Conversations sliced at rewriting-turn boundaries: slice_1, slice_2, slice_3
   - Each slice is a deterministic, identical entry point across all trials
      - *Why frozen?* Any measured inconsistency is attributable solely to the
        model under evaluation — not to upstream context differences
   - Three slice depths test whether stability changes as therapeutic context accumulates
   - [FIG] *Slicing diagram — P/T turn sequence with cut points; which turns are
     in-context vs. excluded per slice*

   ### 3.4 Evaluation Stack
   - Router bypassed — rescripting prompt injected directly (stage known a priori)
      - *Why bypass?* Isolates the therapist model from stage-classification error
   - Fused CoT generation: `<plan>` block + response in a single model call
      - *Why fused?* Plan must condition the response tokens — a separate call
        would decouple intent from output
   - 10 independent trials per condition sample the stochastic output distribution
   - [FIG] *Evaluation stack — frozen history → injected prompt → fused generation*
   - [Example] *Raw model output: `<plan>` block and response side by side*

   ### 3.5 The Plan Mechanism
   - `<plan>` block declares 1–2 IRT strategies before the therapeutic response
   - Framed as **declared intent** — a structured output, not a reasoning trace
      - *Why?* Sidesteps the CoT faithfulness problem (see 2.5); makes the plan
        measurable regardless of whether it reflects true internal computation
   - Enables three independent uses: strategy-level consistency scoring (Method 1),
     plan–output alignment verification (Method 3), human-readable clinical oversight
   - Fixed strategy taxonomy constrains declarations to the therapeutic domain —
     prevents arbitrary strategies that cannot be clinically evaluated
   - [FIG] *Plan mechanism — `<plan>` block feeding into three downstream uses
     with declared-intent framing labelled*

   ### 3.6 Strategy Taxonomy Development
   - *Why fixed?* Enables discrete, comparable strategy sets — free-text plans
     cannot be aggregated into Jaccard similarity scores
   - Iterative revision driven by observed distribution failures:
      - v1 (8 categories): 87.7% mass on empowerment/mastery → unusable skew
      - v2 (merge to agency): 100% dominance → goal–mechanism conflation
      - v3 (mechanism-specific split): confrontation (external action) vs.
        self_empowerment (internal transformation)
   - Final 7 categories: confrontation, self_empowerment, safety, cognitive_reframe,
     emotional_regulation, social_support, sensory_modulation
   - Prompt-level steering encourages diversity across categories
   - [GRAPH] *Strategy frequency per taxonomy version (v1 → v3) — shows skew
     collapse and final distribution*
   - [FIG] *7-category taxonomy card — each category, definition, example phrase*

   ### 3.7 Evaluation Metrics
   - *Why three methods?* Each targets a distinct layer of the generation process —
     no single metric captures the full picture of clinical stability
      - Method 1: does the model make consistent therapeutic decisions? (planning layer)
      - Method 2: does the model produce consistent therapeutic responses? (output layer)
      - Method 3: does the model do what it says it will do? (alignment layer)
   - [FIG] *Three-level framework — plan → output → alignment; inputs and outputs
     of each method, with the clinical question each answers*

      #### 3.7.1 Method 1 — Cognitive Stability (Plan Consistency)
      - Pairwise Jaccard similarity over strategy sets from `<plan>` blocks
      - Validity rate as upstream quality gate — malformed plans excluded
      - *Why Jaccard?* Set similarity is appropriate for unordered strategy
        combinations; insensitive to labelling artefacts
      - [Example] *10 plan sets → pairwise Jaccard matrix → mean score;
        one high- and one low-consistency condition shown*

      #### 3.7.2 Method 2 — Output Consistency (Semantic Stability)
      - Pairwise BERTScore F1; mean over C(10,2) = 45 pairs per condition
      - DeBERTa-XLarge-MNLI: NLI fine-tuning + disentangled attention handles
        surface-form variation in therapeutic language (see 2.4)
      - [Example] *Two responses from the same condition → token alignment
        heatmap → F1; one high- and one low-similarity pair*

      #### 3.7.3 Method 3 — Plan–Output Alignment (Exploratory)
      - LLM judge (Gemini Pro, T=0.0); ternary scoring per declared strategy:
        0 = absent / 1 = partial / 2 = implemented
      - *Why ternary?* Borrowed from clinical fidelity literature (ENACT, NIH BCC);
        binary scoring loses partial implementation — clinically meaningful
      - *Why LLM judge?* Only approach capable of multi-strategy alignment with
        a reasoning trace; NLI cross-encoders ceiling at F1 ~0.55 on this task
      - Mitigations: cross-model judging, CoT justification, T=0.0, transparent rubric
      - Labelled exploratory: judge reliability is itself an open question
      - [Example] *Judge input + output — plan, response, ternary verdict with
        CoT justification; partial and absent case shown*

   ### 3.8 Model Selection
   - EU data sovereignty as primary criterion — self-hostability and EU data
     residency are legal constraints in the reDreamAI deployment context
   - **Primary subject:** Mistral Large — sovereign, frontier-class
   - **Proprietary ceiling:** Gemini 3.1 Pro — closed-weight frontier baseline;
     upper bound on what stability is achievable with current best models
   - **Open-weight comparisons:** Llama 3.3 70B, Qwen 3 32B, OLMo 3.1
      - Size-class diversity (32B–70B); provider diversity; sovereignty status varies
   - [FIG] *Model selection table — model, size, provider, sovereignty status,
     role in study*

   ### 3.9 Experimental Conditions
   - Full factorial: 6 vignettes × 3 slices × 10 trials × T∈{0.0, 0.7} × N models
   - T=0.0: deterministic baseline — theoretical upper bound on stability
   - T=0.7: stochastic condition — realistic clinical deployment range (see 2.3)
   - [FIG] *Condition matrix — factorial design as a grid; total run count labelled*

---

## 4 Implementation

   > *Role:* translates Chapter 3 design decisions into concrete technical choices.
   > Each decision here is a consequence of a methods requirement.

   ### 4.1 Software Architecture
   - Python async pipeline; YAML config; Pydantic validation
      - *Why async?* 10 parallel trials per condition — sequential would be prohibitive
      - *Why YAML?* Every condition is a config parameter — reproducibility without
        code changes; full experiment defined declaratively
      - *Why Pydantic?* Malformed `<plan>` blocks must fail at parse time —
        silent propagation would corrupt downstream metrics
   - Provider abstraction via OpenRouter and Google
      - Enables model swap without changing evaluation logic — critical for
        cross-model comparison
   - [FIG] *Component diagram — modules, interfaces, provider abstraction layer*

   ### 4.2 Experiment Execution
   - Config → frozen history → parallel trials → output bundle
   - Artefacts per run: config.yaml, frozen_history.json, trials/,
     metrics.json, judgments.json
      - *Why this structure?* Frozen history is the only irreplaceable artefact;
        metrics and judgments are recomputable if evaluation logic changes
   - [Example] *Output directory tree for one complete experiment run*

   ### 4.3 Aggregation Pipeline
   - Collects all model × vignette × slice × temperature results into one
     analysis frame
   - Produces per-model, per-vignette, per-slice, per-temperature breakdowns
      - *→ 5.5:* cross-method correlation requires all three metric types aligned
        on the same condition index — this pipeline produces that alignment

---

## 5 Results

   ### 5.1 Plan Validity and Strategy Distribution
   - Validity rates across models and temperatures — quality gate check before
     any stability analysis
   - Strategy frequency distribution; expected vs. observed per vignette
   - [GRAPH] *Validity rate per model × temperature*
   - [GRAPH] *Strategy frequency heatmap — expected vs. observed per vignette*

   ### 5.2 Cognitive Stability — Method 1
   - Mean Jaccard scores by model, vignette, temperature, and slice
   - T=0.0 vs. T=0.7: how much does stochasticity cost in strategy stability?
   - [GRAPH] *Mean Jaccard per model × temperature*
   - [GRAPH] *Jaccard heatmap: vignette × slice for primary model (Mistral)*
   - [GRAPH] *Jaccard by slice depth (slice_1 → slice_3) — does context
     accumulation help or hurt stability?*

   ### 5.3 Output Consistency — Method 2
   - BERTScore F1 across all conditions
   - Does stable planning predict stable outputs, or are the two decoupled?
   - [GRAPH] *Mean BERTScore F1 per model × temperature*
   - [GRAPH] *Scatter: Jaccard vs. BERTScore F1 per condition —
     coupling or decoupling between planning and output stability*

   ### 5.4 Plan–Output Alignment — Method 3
   - Mean alignment scores by model and vignette
   - Which strategies are consistently implemented vs. consistently absent?
   - [GRAPH] *Mean alignment score per model*
   - [GRAPH] *Stacked bar: absent / partial / implemented per strategy category*
   - [GRAPH] *Alignment heatmap: vignette × strategy category*

   ### 5.5 Cross-Method Analysis
   - Correlations across all three evaluation levels — do the methods agree?
   - Divergence cases: high plan consistency with low output consistency
     (and vice versa) — what do these reveal about model behaviour?
   - Stability profiles per model across all three methods
   - Effect of conversation depth (slice_1 → slice_3)
   - [GRAPH] *Correlation matrix: Jaccard × BERTScore × Alignment*
   - [GRAPH] *Radar chart: per-model stability profile across all three methods*
   - [Example] *Annotated divergence case — Method 1 and Method 2 disagree;
     plan sets and response excerpts shown side by side*

---

## 6 Discussion

   ### 6.1 Interpreting the Three-Level Framework
   - What the three methods together reveal that no single method could show alone
   - Cases where the levels align vs. diverge — and what each divergence type means
   - The framework as a diagnostic tool: which layer is the source of instability?
   - [FIG] *Stability failure taxonomy — which divergence pattern indicates which
     type of clinical risk*

   ### 6.2 Cross-Model Comparison
   - Mistral Large vs. GPT-class and open-weight peers across all three methods
   - Does self-hostability come at a stability cost? — the sovereignty tradeoff
   - Size-class effects: does more parameters mean more stability?
   - [GRAPH] *Summary: all models × all three metrics × both temperatures —
     the central comparative result*

   ### 6.3 Temperature and Clinical Deployment
   - Greedy decoding as an upper-bound baseline — theoretical best case
   - Stochastic drift patterns: which models degrade most under T=0.7?
   - Practical deployment recommendations: when is T=0.7 acceptable?
   - [GRAPH] *Delta chart: T=0.7 minus T=0.0 per model — the stochastic cost*

   ### 6.4 Vignette-Dependent Behaviour
   - Which patient profiles challenge model consistency most: resistant, trauma
   - Strategy selection patterns across clinical presentations — are some
     strategies inherently harder to maintain consistently?
   - Implications for deployment: not all patient profiles are equally safe
   - [GRAPH] *Per-vignette stability ranking across all three methods*

   ### 6.5 Evaluation Framework Reflections
   - What the taxonomy design choices reveal — and what they constrain
   - What declared intent can and cannot claim about model cognition
   - Generalisability: can this framework apply to CBT, DBT, other manualized protocols?
   - [FIG] *Generalisation sketch — framework mapped onto a second structured
     protocol (e.g. CBT thought records) to show reusability*

   ### 6.6 Toward In Silico Clinical Trials
   - This framework as a reusable, reproducible validation template
   - What stability testing can certify — and what it cannot replace
   - The remaining gap: from benchmark stability to demonstrated clinical safety
   - [FIG] *Positioning diagram — where this framework sits in a full clinical
     validation pipeline; what it certifies and what remains open*

---

## 7 Conclusion

   ### 7.1 Summary of Findings
   - Key results across all three evaluation levels
   - Direct answer to the research question: how consistent are sovereign LLMs
     in a structured therapeutic protocol — and what does that mean clinically?

   ### 7.2 Limitations
   - Scope: single protocol, single phase (IRT rescripting only)
   - Simulation: synthetic patients differ from real clinical interaction in
     ways that cannot be fully controlled
   - Method 3 is exploratory — judge reliability is unverified and should
     not be treated as ground truth
   - Fixed taxonomy constrains the measurable strategy space — unmeasured
     strategies may show different stability patterns

   ### 7.3 Future Work
   - Full IRT protocol evaluation — beyond the rescripting phase
   - Extension to other manualized therapies (CBT, DBT, PE)
   - Longitudinal drift: does stability degrade across model version updates?
   - Multi-language evaluation — German therapeutic context for reDreamAI
   - Clinical validation: human therapist ratings as external ground truth
   - RAG-based guardrail integration for safety and alignment

---

## References
...

---

## Appendices

   ### A Strategy Taxonomy
   - Full 7-category definitions with revision history (8 → 6 → 7)
   - [FIG] *Taxonomy card — all 7 categories, definitions, example phrases*

   ### B Prompts
   - Fused plan+response system prompt
   - Alignment judge prompt and scoring rubric
   - Patient vignette profiles (all six)

   ### C Architecture Diagrams
   - Full pipeline diagram (high-resolution)
   - Three-level evaluation framework (high-resolution)
   - Three-agent loop (high-resolution)

   ### D Supplementary Results
   - Full per-condition metric tables (Jaccard, BERTScore, Alignment)