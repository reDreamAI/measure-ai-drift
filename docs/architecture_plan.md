measure-ai-drift/
│
├── data/
│   ├── synthetic/                                  # Generated artifacts (JSON only)
│   │   ├── dialogues/                              # Full simulated therapy sessions
│   │   │   ├── dialogue_cooperative_20260210.json
│   │   │   └── ...
│   │   ├── frozen_histories/                       # Evaluation entry-point slices
│   │   │   ├── frozen_anxious_a1b2c3d4/
│   │   │   │   ├── full.json                       # Complete dialogue (all stages)
│   │   │   │   ├── slice_1.json                    # Up to 1st rewriting exchange
│   │   │   │   ├── slice_2.json                    # Up to 2nd rewriting exchange
│   │   │   │   └── slice_3.json                    # Up to 3rd rewriting exchange
│   │   │   └── ...
│   │   └── results/                                # Aggregated outputs
│   │
│   ├── prompts/                                    # YAML prompt library
│   │   ├── patients/                               # Patient simulator + vignettes
│   │   │   ├── patient_prompt.yaml
│   │   │   └── vignettes/
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
│   │       ├── internal_plan.yaml                   # Plan-only prompt (chained mode)
│   │       ├── fused_plan_response.yaml             # CoT plan+response prompt (fused mode)
│   │       ├── alignment_judge.yaml                 # LLM judge prompt (Level 3.3)
│   │       └── strategy_taxonomy.yaml               # 7 IRT strategy categories
│   │
│   └── ...
│
├── src/
│   ├── cli.py                                       # CLI entry point (all commands)
│   │
│   ├── agents/                                      # Dialogue actors (therapy simulation)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── patient.py
│   │   ├── router.py
│   │   └── therapist.py
│   │
│   ├── stacks/
│   │   ├── generation_stack.py                      # Full IRT flow + frozen history export
│   │   └── evaluation_stack.py                      # Rescripting-only (fused / chained)
│   │
│   ├── evaluation/                                  # Experiment execution + metrics
│   │   ├── __init__.py
│   │   ├── experiment.py                            # ExperimentRun: structured output runner
│   │   ├── sampler.py                               # Multi-trial generation (serial/parallel)
│   │   ├── metrics.py                               # Jaccard, BERTScore, validity, alignment
│   │   └── results.py                               # Cross-experiment aggregation
│   │
│   ├── llm/                                         # Config-driven LLM provider
│   │   ├── __init__.py
│   │   └── provider.py
│   │
│   ├── core/                                        # Shared data models
│   │   ├── __init__.py
│   │   ├── conversation.py                          # Conversation, Message, slicing methods
│   │   ├── stages.py                                # Stage enum, Language enum
│   │   └── config_loader.py                         # YAML/JSON loaders, taxonomy, prompts
│   │
│   └── config/                                      # Runtime configs
│       ├── models.yaml
│       └── experiment.yaml
│
├── experiments/
│   └── runs/
│       └── {timestamp}_{model}_{vignette}/
│           ├── config.yaml
│           ├── frozen_history.json
│           ├── trials/
│           │   ├── trial_01.json                    # plan + response + usage + strategies
│           │   ├── trial_02.json
│           │   └── ...
│           ├── metrics.json                         # 3-level evaluation results
│           └── judgments.json                        # Raw LLM judge outputs
│
├── analysis/                                        # Post-experiment analysis (future)
│   ├── notebooks/
│   ├── figures/
│   └── tables/
│
├── docs/
│   ├── architecture_plan.md                         # This file
│   ├── thesis_proposal.md                           # Research objectives and methodology
│   ├── alignment_approach_analysis.md               # LLM judge vs NLI rationale
│   ├── bertscore_model_selection.md                 # DeBERTa-XLarge-MNLI justification
│   ├── plan_mechanism_analysis.md                   # Plan as declared intent, fused vs chained
│   ├── strategy_taxonomy_evolution.md               # 8 → 6 → 7 category journey
│   └── pipeline_flowcharts.md                       # Mermaid diagrams of full architecture
│
├── tests/
│   ├── test_setup.py                                # Config and connectivity verification
│   └── test_evaluation_pipeline.py                  # Metrics and pipeline tests
│
└── old_versions/                                    # Legacy architectures (do not delete)
