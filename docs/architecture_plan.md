LLM-THERAPY/
│
├── data/
│   ├── vignettes/                                  # Ground-truth patient profiles (JSON only)
│   │   ├── schema.json
│   │   ├── anxious.json
│   │   ├── avoidant.json
│   │   ├── cooperative.json
│   │   ├── resistant.json
│   │   ├── skeptic.json
│   │   └── trauma.json
│   │
│   ├── synthetic/                                  # Generated artifacts (JSON only)
│   │   ├── dialogues/                              # Full simulated therapy sessions (router + therapist)
│   │   │   ├── dialogue_0001.json
│   │   │   └── ...
│   │   ├── phase_annotations/                      # Stage detection outputs per dialogue
│   │   │   ├── dialogue_0001_phases.json           # psychoed / rescripting / rehearsal (+ spans/turns)
│   │   │   └── ...
│   │   └── frozen_histories/                       # Rescripting entry-point slices (evaluation inputs)
│   │       ├── vignette_anxious_caseA.json         # context up to rescripting boundary
│   │       └── ...
│   │
│   ├── prompts/                                    # YAML prompt library (no code)
│   │   ├── system/
│   │   │   ├── therapist_base.yaml                 # therapist persona + global rules
│   │   │   ├── patient_base.yaml                   # patient simulator persona
│   │   │   └── safety_guardrails.yaml
│   │   │
│   │   ├── router/
│   │   │   ├── router_system.yaml                  # router persona + routing policy
│   │   │   ├── stage_schema.yaml                   # allowed stages + constraints
│   │   │   └── stage_prompts/
│   │   │       ├── psychoeducation.yaml
│   │   │       ├── rescripting.yaml                # injected directly in evaluation (router model bypassed)
│   │   │       └── rehearsal.yaml
│   │   │
│   │   ├── irt/
│   │   │   ├── internal_plan.yaml                  # short <plan> (no CoT)
│   │   │   └── final_response.yaml                 # rescripting intervention output
│   │   │
│   │   └── evaluation/
│   │       ├── strategy_classification.yaml
│   │       ├── semantic_consistency.yaml
│   │       ├── plan_output_alignment.yaml
│   │       └── rubrics/
│   │           ├── irt_strategy_taxonomy.yaml
│   │           ├── alignment_labels.yaml
│   │           └── reporting_schema.yaml
│   │
│   └── results/                                    # Immutable outputs only (mirrors model groups)
│       ├── benchmark/
│       │   └── gemini3/                            # SOTA baseline
│       └── sovereign/
│           ├── mistral_small/
│           ├── llama/
│           └── qwen/
│
├── src/
│   ├── agents/                                     # Dialogue actors (therapy simulation)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── patient.py                              # BDI-driven patient simulator
│   │   ├── router.py                               # stage router (policy + selection logic)
│   │   └── therapist.py                            # therapist actor (model-backed)
│   │
│   ├── stacks/                                     # Two logical stacks (same codebase)
│   │   ├── generation_stack.py                     # full stack: router-model + therapist-model
│   │   └── evaluation_stack.py                     # rescripting-only: inject router stage prompt; bypass router model
│   │
│   ├── detection/                                  # Stage detection on synthetic dialogues
│   │   ├── stage_detector.py                       # detect rescripting spans/turns in transcripts
│   │   └── phase_schema.py                         # stage labels + validation helpers
│   │
│   ├── pipelines/
│   │   ├── data_generation/                        # Creates synthetic dialogues + frozen histories
│   │   │   ├── generate_dialogues.py               # runs generation_stack over vignettes
│   │   │   ├── annotate_phases.py                  # runs stage_detector over dialogues
│   │   │   └── build_frozen_histories.py           # slices context up to rescripting entry
│   │   │
│   │   ├── rescripting_eval/                       # Consumes frozen histories; evaluates rescripting only
│   │   │   ├── plan_sampler.py                     # multi-trial internal plans (t sweep, n trials)
│   │   │   ├── response_generator.py               # multi-trial rescripting outputs
│   │   │   ├── stability.py                        # Level 1: plan set consistency (e.g., mean Jaccard)
│   │   │   ├── semantic_consistency.py             # Level 2: output consistency (e.g., BERTScore F1)
│   │   │   └── alignment.py                        # Level 3: plan ↔ output alignment scoring
│   │   │
│   │   └── aggregation/
│   │       ├── trial_aggregator.py
│   │       └── experiment_summary.py
│   │
│   ├── models/                                     # Thin inference adapters
│   │   ├── base_model.py
│   │   ├── sovereign/
│   │   │   ├── mistral.py
│   │   │   ├── llama.py
│   │   │   └── qwen.py
│   │   └── benchmark/
│   │       └── gemini3.py
│   │
│   ├── config/                                     # YAML-only runtime configs
│   │   ├── models.yaml
│   │   ├── sampling.yaml
│   │   ├── evaluation.yaml
│   │   └── paths.yaml
│   │
│   ├── viz/                                        # Visualization + reporting
│   │   ├── plots.py
│   │   └── dashboards.py
│   │
│   └── utils/
│       ├── schema_validation.py
│       ├── reproducibility.py
│       ├── hashing.py
│       └── logging.py
│
├── experiments/                                   # Fully replayable runs
│   ├── exp_001_generate_synthetic_dataset/
│   │   ├── config_snapshot.yaml
│   │   ├── outputs/
│   │   │   ├── dialogues_index.json
│   │   │   ├── phase_annotations_index.json
│   │   │   └── frozen_histories_index.json
│   │   └── reports/
│   │       └── dataset_summary.json
│   │
│   ├── exp_010_rescripting_eval_mistral_vs_gemini3/
│   │   ├── config_snapshot.yaml
│   │   ├── inputs/
│   │   │   └── frozen_histories_manifest.json
│   │   ├── runs/
│   │   │   ├── RB-.../
│   │   │   │   ├── trial_01.json
│   │   │   │   └── ...
│   │   │   └── ...
│   │   ├── results/
│   │   │   ├── stability.json
│   │   │   ├── semantic_consistency.json
│   │   │   └── alignment.json
│   │   └── figures/
│   │       ├── stability_boxplot.png
│   │       ├── consistency_boxplot.png
│   │       └── alignment_heatmap.png
│   │
│   └── README.md
│
├── analysis/
│   ├── notebooks/
│   ├── figures/
│   ├── tables/
│   └── statistics.py
│
├── docs/
│   ├── architecture_plan.md
│   ├── Proposal_DMenzel_Measuring_Drift_in_Therapeutic_AI.md
│   ├── run_bundle_example.md
│   ├── evaluation_framework.md
│   ├── synthetic_data_protocol.md
│   └── regulatory_notes.md
│
└── old_version/                                  # Legacy architecture