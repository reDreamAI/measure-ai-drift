# Concrete Run Bundle Specification

This document defines the **exact, concrete run bundle** used in this project. It is intended as an **implementation-grade reference** for building, executing, and extending the architecture.

---

## Run Bundle: Definition

A **run bundle** is a deterministic specification of *one rescripting evaluation case*.

It binds together:

- one frozen clinical context,
- one fixed therapeutic stage constraint,
- one set of planning/execution instructions,
- one normative evaluation definition,
- one sampling regime.

Everything outside this bundle is **upstream data generation** or **downstream aggregation**.

---

## 1. Run Bundle Identifier

Each run bundle MUST be addressable by a stable identifier.

Example:

```
run_bundle_id: RB-ANX-CASEA-RESCRIPT
```

Derived from:

- vignette ID
- synthetic dialogue instance
- rescripting entry point

---

## 2. Frozen Clinical Context (Input)

**File**

```
data/synthetic/frozen_histories/vignette_anxious_caseA.json
```

**Properties**

- JSON only
- Contains:
  - patient utterances
  - therapist utterances
  - system messages
- Ends **immediately before** first rescripting intervention
- Immutable once created

This file is the **sole semantic input** shared across all models and trials.

---

## 3. Stage Constraint (Router Policy Injection)

**File**

```
prompts/router/stage_prompts/rescripting.yaml
```

**Role**

- Encodes the router policy for the *rescripting* phase
- Defines:
  - allowed therapist actions
  - forbidden transitions (e.g. psychoeducation)
  - therapeutic intent boundaries

**Important**

- Router *model* is NOT executed
- Router *policy* is enforced via prompt injection

---

## 4. Cognitive Instruction Set

### 4.1 Internal Planning Instruction

**File**

```
prompts/irt/internal_plan.yaml
```

**Purpose**

- Elicit a short therapeutic strategy declaration
- No chain-of-thought
- Output is a `<plan>` artifact

**Output Artifact**

```
<plan>
  STRATEGY_LABEL
</plan>
```

---

### 4.2 Final Rescripting Instruction

**File**

```
prompts/irt/final_response.yaml
```

**Purpose**

- Generate the actual therapeutic rescripting intervention
- Executed after plan generation

**Output Artifact**

```
THERAPIST_RESPONSE_TEXT
```

---

## 5. Normative Evaluation Semantics

These files define **how outputs are interpreted and scored**.

### 5.1 Strategy Taxonomy

**File**

```
prompts/evaluation/rubrics/irt_strategy_taxonomy.yaml
```

Defines:

- finite set of allowed IRT strategies
- mapping from textual plans to categories

---

### 5.2 Alignment Labels

**File**

```
prompts/evaluation/rubrics/alignment_labels.yaml
```

Defines:

- valid plan–output alignment states
- e.g. `aligned / partially_aligned / misaligned`

---

### 5.3 Reporting Schema

**File**

```
prompts/evaluation/rubrics/reporting_schema.yaml
```

Defines:

- expected JSON structure of evaluation outputs
- required fields for aggregation and visualisation

---

## 6. Sampling & Execution Parameters

Loaded from configuration files:

```
config/sampling.yaml
config/evaluation.yaml
config/models.yaml
```

Typical contents:

- number of trials (e.g. n = 10)
- temperature schedule (e.g. t ∈ {0.0, 0.7})
- model under test (e.g. `mistral_small`, `gemini3`)

These parameters probe **stochastic stability** without changing task semantics.

---

## 7. Execution Contract

A run bundle execution MUST:

1. Load frozen history
2. Inject rescripting stage prompt
3. Execute internal plan generation (multi-trial)
4. Execute final response generation (multi-trial)
5. Store raw plans and outputs per trial
6. Apply evaluation semantics

No step may alter upstream artifacts.

---

## 8. Output Artifacts (Per Run Bundle)

Stored under:

```
experiments/<experiment_id>/runs/<run_bundle_id>/
```

Contents:

```
trial_01.json
trial_02.json
...
```

Each trial contains:

- frozen history hash
- plan text
- response text
- model + sampling metadata

---

## 9. Aggregated Metrics (Derived)

Computed *from* run bundle outputs:

- Plan stability (Level 1)
- Semantic output consistency (Level 2)
- Plan–output alignment (Level 3)

Stored separately in experiment-level results.

---

## 10. Non-Goals (Explicit)

A run bundle does NOT include:

- vignette generation
- router model inference
- cross-bundle aggregation
- statistical testing

Those belong to other layers by design.

\
