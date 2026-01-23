LLM-THERAPY/
│
├── data/
│   ├── synthetic/                                  # Generated artifacts (JSON only)
│   │   ├── dialogues/                              # Full simulated therapy sessions
│   │   │   ├── dialogue_0001.json
│   │   │   └── ...
│   │   ├── frozen_histories/                       # Rescripting entry-point slices
│   │   │   ├── vignette_anxious_caseA.json
│   │   │   └── ...
│   │   └── results/                                # Metrics outputs (JSON only)
│   │       ├── stability.json
│   │       ├── semantic_consistency.json
│   │       └── alignment.json
│   │
│   ├── prompts/                                    # YAML prompt library
│   │   ├── patients/                               # Patient simulator + vignettes
│   │   │   ├── patient_prompt.yaml
│   │   │   └── vignettes/
│   │   │       ├── schema.json
│   │   │       ├── anxious.json
│   │   │       ├── avoidant.json
│   │   │       ├── cooperative.json
│   │   │       ├── resistant.json
│   │   │       ├── skeptic.json
│   │   │       └── trauma.json
│   │   │
│   │   ├── router/
│   │   │   ├── routing.yaml                         # Router prompt
│   │   │   └── stage_prompts/                       # Stage system prompts
│   │   │       ├── recording.yaml
│   │   │       ├── rewriting.yaml
│   │   │       ├── summary.yaml
│   │   │       ├── rehearsal.yaml
│   │   │       └── final.yaml
│   │   │
│   │   └── evaluation/
│   │       ├── internal_plan.yaml                   # Short <plan> generation
│   │       └── strategy_taxonomy.yaml               # IRT strategy categories
│   │
│   └── results/                                    # Immutable outputs (model groups)
│       ├── benchmark/
│       │   └── gemini3/
│       └── sovereign/
│           ├── mistral_small/
│           ├── llama/
│           └── qwen/
│
├── src/
│   ├── agents/                                     # Dialogue actors (therapy simulation)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── patient.py
│   │   ├── router.py
│   │   └── therapist.py
│   │
│   ├── stacks/
│   │   ├── generation_stack.py                     # Full IRT flow
│   │   └── evaluation_stack.py                     # Rescripting-only (router bypassed)
│   │
│   ├── evaluation/                                 # Thesis evaluation (simplified)
│   │   ├── __init__.py
│   │   ├── sampler.py                              # Multi-trial generation
│   │   └── metrics.py                              # Jaccard, BERTScore, alignment
│   │
│   ├── llm/                                        # Config-driven LLM provider
│   │   ├── __init__.py
│   │   └── provider.py
│   │
│   ├── core/                                       # Shared data models
│   │   ├── __init__.py
│   │   ├── conversation.py
│   │   ├── stages.py
│   │   └── config_loader.py
│   │
│   └── config/                                     # Runtime configs
│       ├── models.yaml
│       └── experiment.yaml
│
├── experiments/
│   └── runs/
│       └── {timestamp}_{model}_{vignette}/
│           ├── config.yaml
│           ├── frozen_history.json
│           ├── trials/
│           │   ├── trial_01_plan.json
│           │   ├── trial_01_response.json
│           │   └── ...
│           └── metrics.json
│
├── analysis/ # DON'T TOUCH YET
│   ├── notebooks/
│   ├── figures/
│   ├── tables/
│   └── statistics.py
│
├── docs/
│   ├── architecture_plan.md
│   ├── thesis_proposal.md
│   ├── run_bundle_example.md
│   ├── evaluation_framework.md
│   ├── synthetic_data_protocol.md
│   └── regulatory_notes.md
│
├── tests/
│   └── key_test.py
│
└── old_versions/                                  # Legacy architectures
