# Pipeline Architecture

This document provides visual documentation of the Measure-AI-Drift pipeline using Mermaid diagrams. The system comprises a **Generation Stack** that produces synthetic therapy dialogues and an **Evaluation Stack** that measures rescripting stability across repeated trials. All diagrams render natively on GitHub.

---

## 1. System Overview

The two stacks operate sequentially: generation produces dialogues and frozen histories, evaluation consumes frozen histories and produces multi-level metrics. Configuration files drive both stacks, and all LLM calls flow through a single provider abstraction.

```mermaid
flowchart TB
    subgraph config["Configuration Layer"]
        models["models.yaml\n(providers, model options, roles)"]
        experiment["experiment.yaml\n(sampling, metrics, paths)"]
        env[".env\n(API keys)"]
        taxonomy["strategy_taxonomy.yaml\n(7 IRT strategy categories)"]
    end

    subgraph gen["Generation Stack"]
        direction TB
        vignette["Vignette JSON\n(patient profile)"] --> agents["Create Agents\nPatient + Router + Therapist"]
        agents --> loop["Dialogue Loop\n(3 LLM calls/turn)"]
        loop --> dialogue["Full Dialogue JSON"]
        loop --> frozen["Frozen Histories\n(full + rewriting slices)"]
    end

    subgraph eval["Evaluation Stack"]
        direction TB
        load["Load Frozen History"] --> trials["Run N Trials\n(fused or chained mode)"]
        trials --> metrics["Compute 3-Level Metrics"]
        metrics --> results["Metrics + Judgments JSON"]
    end

    config --> gen
    config --> eval
    frozen -->|"input"| load

    dialogue --> out_dial["data/synthetic/dialogues/"]
    frozen --> out_frozen["data/synthetic/frozen_histories/"]
    results --> out_runs["experiments/runs/{id}/"]

    style config fill:#f0f4ff,stroke:#4a6fa5
    style gen fill:#f0fff0,stroke:#2d8a4e
    style eval fill:#fff8f0,stroke:#c47a2a
```

---

## 2. Generation Stack

A single dialogue generation traces from CLI invocation through three cooperating agents to saved output artifacts. Each turn involves three LLM calls: patient generates a message, router classifies the IRT stage, and therapist responds with a stage-appropriate prompt. The patient agent uses **role inversion** (therapist messages become `"user"` in its context) so the LLM produces patient-style responses.

```mermaid
flowchart TB
    cli["CLI: generate\n-v vignette -l language\n-t max-turns --freeze"]

    subgraph load["Load Configuration"]
        m_yaml["models.yaml\n(provider endpoints, role assignments)"]
        v_json["vignettes/{name}.json\n(patient profile)"]
        p_prompt["patient_prompt.yaml"]
        r_prompt["routing.yaml"]
        s_prompts["stage_prompts/\n(recording, rewriting,\nsummary, rehearsal, final)"]
    end

    subgraph agents["Create Agents"]
        patient["PatientAgent\n.from_vignette()"]
        router["RouterAgent\n(T=0.0)"]
        therapist["TherapistAgent\n.update_stage()"]
    end

    subgraph genloop["Generation Loop (per turn)"]
        direction TB
        p_msg["PatientAgent.generate()\n(LLM call, role-inverted context)"]
        r_stage["RouterAgent.determine_stage()\n(LLM call, T=0.0)"]
        guard["Apply Guardrails\n(enforce stage ordering:\nno skip to FINAL w/o\nSUMMARY + REHEARSAL)"]
        t_resp["TherapistAgent.generate()\n(LLM call, stage-specific prompt)"]
        check{"stage == FINAL\nor turns >= max?"}

        p_msg --> r_stage --> guard --> t_resp --> check
        check -->|No| p_msg
    end

    subgraph save["Save Outputs"]
        full["save_dialogue()\n-> dialogues/{vignette}_{id}.json"]
        freeze{"--freeze\nflag?"}
        slice["save_frozen_history()\n-> frozen_{vignette}_{id}/\nfull.json + slice_1..N.json"]
    end

    cli --> load --> agents --> genloop
    check -->|Yes| save
    freeze -->|Yes| slice
    full --> freeze

    note_stages["5-stage IRT protocol:\nRECORDING -> REWRITING ->\nSUMMARY -> REHEARSAL -> FINAL"]

    style genloop fill:#f0fff0,stroke:#2d8a4e
    style load fill:#f0f4ff,stroke:#4a6fa5
    style agents fill:#fff8f0,stroke:#c47a2a
    style note_stages fill:#fffff0,stroke:#999,stroke-dasharray: 5 5
```

---

## 3. Evaluation Stack

Evaluation loads a frozen history (a full dialogue or a rewriting-stage slice) and runs N independent trials, each producing a plan and therapeutic response. Two modes are supported: **fused** (single LLM call with CoT-style `<plan>` block) and **chained** (separate plan then response calls). After all trials complete, three levels of metrics are computed, including an LLM judge call for plan-output alignment.

```mermaid
flowchart TB
    cli["CLI: evaluate\n-i history.json -n trials\n-t temperature -m mode"]

    load["Load frozen_history.json\n-> Conversation object"]

    setup["ExperimentRun.setup()\n- Create run directory\n- Save frozen_history copy\n- Save config.yaml"]

    mode{"Mode?"}

    subgraph fused["Fused Mode (per trial)"]
        f_call["Single LLM call\n(fused_plan_response.yaml)\nCoT: plan + response together"]
        f_parse["Parse output:\nregex &lt;plan&gt;...&lt;/plan&gt;\nsplit plan from response"]
        f_call --> f_parse
    end

    subgraph chained["Chained Mode (per trial)"]
        c_plan["LLM Call 1: Generate Plan\n(internal_plan.yaml)\nOutput: &lt;plan&gt;cat1 / cat2&lt;/plan&gt;"]
        c_resp["LLM Call 2: Generate Response\n(stage prompt + plan injected)\nConditioned on plan output"]
        c_plan --> c_resp
    end

    save_trial["Save trial_{n}.json\n(plan, response, usage, strategies)"]

    repeat{"n < N trials?"}

    subgraph metrics["Metrics Computation"]
        direction TB
        extract["extract_plan_strategies()\nregex + VALID_CATEGORIES filter\n(strategy_taxonomy.yaml)"]

        subgraph l31["Level 3.1: Cognitive Stability"]
            validity["compute_validity_rate()\n(1 &lt;= strategies &lt;= 2)"]
            jaccard["compute_pairwise_jaccard()\n(set overlap across trials)"]
        end

        subgraph l32["Level 3.2: Output Consistency"]
            bert["compute_pairwise_bertscore()\n(DeBERTa-XLarge-MNLI, local)"]
        end

        subgraph l33["Level 3.3: Plan-Output Alignment"]
            judge["compute_alignment()\nLLM judge (Gemini Flash, T=0.0)\nalignment_judge.yaml prompt\nENACT ternary: 0/1/2"]
        end

        extract --> l31
        extract --> l32
        extract --> l33
    end

    save_out["Save Results:\nmetrics.json + judgments.json\n-> experiments/runs/{id}/"]

    cli --> load --> setup --> mode
    mode -->|"fused"| fused --> save_trial
    mode -->|"chained"| chained --> save_trial
    save_trial --> repeat
    repeat -->|"Yes"| mode
    repeat -->|"No, all done"| metrics --> save_out

    style metrics fill:#fff8f0,stroke:#c47a2a
    style fused fill:#f0f4ff,stroke:#4a6fa5
    style chained fill:#f0f4ff,stroke:#4a6fa5
    style l31 fill:#fafafa,stroke:#888
    style l32 fill:#fafafa,stroke:#888
    style l33 fill:#fafafa,stroke:#888
```

---

## 4. Configuration & Data Flow

This diagram maps every configuration file to the components that consume it, and every component to the output artifacts it produces. The strategy taxonomy is a single source of truth: it is interpolated into LLM prompts (via `build_categories_block()`), used for plan extraction validation, and injected into the alignment judge prompt.

```mermaid
flowchart LR
    subgraph inputs["Configuration Inputs"]
        direction TB
        env[".env\n(API keys per provider)"]
        models["models.yaml\n(providers, model_options,\nrole assignments)"]
        exp_cfg["experiment.yaml\n(n_trials, temperatures,\nmetric selection, paths)"]
        tax["strategy_taxonomy.yaml\n(7 categories + rules:\nmin=1, max=2)"]
        vignettes["vignettes/*.json\n(6 patient profiles:\ncooperative, anxious, trauma,\navoidant, resistant, skeptic)"]
        stage_p["stage_prompts/*.yaml\n(per-stage therapist behavior)"]
        routing["routing.yaml\n(stage classification rules)"]
        patient_p["patient_prompt.yaml\n(patient simulation rules)"]
        judge_p["alignment_judge.yaml\n(judge system + user templates)"]
        plan_p["internal_plan.yaml\nfused_plan_response.yaml\n(evaluation prompt templates)"]
    end

    subgraph components["System Components"]
        direction TB
        provider["LLMProvider\n(create_provider(role))\nOpenAI-compatible abstraction"]
        pat_agent["PatientAgent"]
        ther_agent["TherapistAgent"]
        rout_agent["RouterAgent"]
        eval_stack["EvaluationStack\n(fused / chained)"]
        judge_comp["Alignment Judge\n(compute_alignment)"]
        metric_comp["Metrics Engine\n(Jaccard, BERTScore)"]
        exp_run["ExperimentRun\n(.setup() + .run())"]
    end

    subgraph outputs["Output Artifacts"]
        direction TB
        dial_out["data/synthetic/dialogues/\n(full dialogue JSONs)"]
        frozen_out["data/synthetic/frozen_histories/\n(full + rewriting slices per vignette)"]
        cfg_out["experiments/runs/{id}/config.yaml\n(experiment parameters)"]
        fh_out["experiments/runs/{id}/frozen_history.json\n(input copy)"]
        trial_out["experiments/runs/{id}/trials/trial_*.json\n(plan + response + usage)"]
        metrics_out["experiments/runs/{id}/metrics.json\n(3-level evaluation results)"]
        judge_out["experiments/runs/{id}/judgments.json\n(raw judge LLM outputs)"]
    end

    env --> provider
    models --> provider
    models --> pat_agent
    models --> ther_agent
    models --> rout_agent

    vignettes --> pat_agent
    patient_p --> pat_agent
    routing --> rout_agent
    stage_p --> ther_agent

    exp_cfg --> exp_run
    tax --> eval_stack
    tax --> metric_comp
    tax --> judge_comp
    plan_p --> eval_stack
    judge_p --> judge_comp

    provider --> pat_agent
    provider --> ther_agent
    provider --> rout_agent
    provider --> eval_stack
    provider --> judge_comp

    pat_agent --> dial_out
    ther_agent --> dial_out
    dial_out --> frozen_out

    exp_run --> cfg_out
    exp_run --> fh_out
    eval_stack --> trial_out
    metric_comp --> metrics_out
    judge_comp --> judge_out

    style inputs fill:#f0f4ff,stroke:#4a6fa5
    style components fill:#f0fff0,stroke:#2d8a4e
    style outputs fill:#fff8f0,stroke:#c47a2a
```
