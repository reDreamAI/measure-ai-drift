# Patient Agent Implementation Summary

## ✅ YAML-Driven Architecture (Good Practice)

The patient simulation system now follows **single source of truth** principles:

### 1. **Patient Prompt YAML** (`data/prompts/patients/patient_prompt.yaml`)
**Purpose**: Complete configuration for patient simulator behavior

**Structure**:
```yaml
system_prompt: |
  # Base simulation instructions
  
vignette_format: |
  # Template for formatting vignette data
  ## Current Patient Profile
  Name: {name}
  Age: {age}
  ...
  
intro_messages:
  en: "Session intro in English"
  de: "Session intro in German"
```

**Benefits**:
- ✅ All prompt text in one place
- ✅ Non-code prompt iteration
- ✅ Template ensures consistent formatting
- ✅ Language-specific intros centralized

### 2. **Patient Vignettes** (`data/prompts/patients/vignettes/*.json`)
**Purpose**: Stable baseline patient profiles

**Structure**:
```json
{
  "type": "anxious",
  "name": "Maya",
  "age": 24,
  "nightmare": {...},
  "personality_traits": [...],
  "resistance_behaviors": [...],
  "sample_responses": [...]
}
```

**Status**: Fixed data, provides stable baselines for:
- Dialogue generation
- Model evaluation
- Reproducible experiments

### 3. **PatientAgent** (`src/agents/patient.py`)
**Purpose**: Orchestrates YAML + vignette into LLM prompts

**Key Methods**:
```python
get_system_prompt() -> str
    # Combines:
    # 1. Base prompt (from YAML)
    # 2. Language injection
    # 3. Formatted vignette (using YAML template)
    # 4. Sample responses
```

**Data Flow**:
```
patient_prompt.yaml ──┐
                      ├──> format_vignette_for_prompt()
vignettes/anxious.json ┘         │
                                 ↓
                        PatientAgent.get_system_prompt()
                                 │
                                 ↓
                           Full LLM Prompt
```

## Key Design Decisions

### ✅ Chosen: YAML Template-Driven Formatting
- **Benefit**: Change prompt structure without code changes
- **Implementation**: `vignette_format` template with `{placeholder}` syntax
- **Fallback**: Hardcoded format if YAML template missing

### ✅ Chosen: Intro Messages in patient_prompt.yaml
- **Current State**: Therapist intros stored in patient YAML
- **Rationale**: Single source until therapist_base.yaml is reintroduced
- **Future**: May move to therapist YAML when created

### ✅ Chosen: Language Injection in System Prompt
- **Implementation**: Explicit language instruction added to prompt
- **Benefit**: LLM knows target language explicitly
- **Format**: "## Language\nRespond in English (en)."

## Testing Results

```
✓ Vignette formatting uses YAML template
✓ Language injection working (en/de)
✓ Sample responses included
✓ Intro messages loaded from YAML
✓ No linter errors
✓ All 6 vignettes loadable
```

## File Structure

```
data/prompts/
├── patients/
│   ├── patient_prompt.yaml         # YAML-driven config (80 lines)
│   └── vignettes/                  # Stable baseline data
│       ├── anxious.json
│       ├── avoidant.json
│       ├── cooperative.json
│       ├── resistant.json
│       ├── skeptic.json
│       └── trauma.json
└── router/
    ├── routing.yaml
    └── stage_prompts/
        ├── recording.yaml
        ├── rewriting.yaml
        ├── summary.yaml
        ├── rehearsal.yaml
        └── final.yaml

src/agents/
├── base.py                         # BaseAgent ABC
├── patient.py                      # PatientAgent (YAML-driven)
├── therapist.py                    # TherapistAgent
└── router.py                       # RouterAgent

src/core/
├── config_loader.py                # YAML loading + formatting
├── conversation.py                 # Message, Conversation models
└── stages.py                       # Stage enum
```

## Benefits of This Approach

1. **Maintainability**: Prompt changes don't require code changes
2. **Consistency**: Template ensures uniform vignette formatting
3. **Flexibility**: Easy to add new vignette fields
4. **Testability**: Configuration separate from logic
5. **Reproducibility**: Vignettes are fixed baselines

## Next Steps (Optional)

- [ ] Add schema validation for vignette JSON
- [ ] Create `therapist_base.yaml` for therapist-specific config
- [ ] Move intro_messages to therapist YAML when created
- [ ] Add vignette versioning for baseline tracking
