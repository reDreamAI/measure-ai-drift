# Patient Agent Quick Reference

## Usage

### Create from Vignette
```python
from src.agents import PatientAgent

# Create patient agent for English session
patient = PatientAgent.from_vignette("anxious", language="en")

# Create patient agent for German session
patient_de = PatientAgent.from_vignette("cooperative", language="de")
```

### Generate Responses
```python
# Get initial nightmare description
initial_msg = patient.get_initial_message()
# → "I'm not sure where to start... I've been having these awful dreams. 
#    It's about being in an exam room where the questions keep changing..."

# Generate response to therapist
from src.core import Conversation
conv = Conversation(session_id="test-123", language="en")
response, usage = await patient.generate(
    user_message="Tell me more about the exam room.",
    conversation=conv
)
```

## Available Vignettes (Stable Baselines)

| Name | Type | Resistance | Key Traits |
|------|------|------------|------------|
| Anna | cooperative | low | Open, engaged, trusting |
| Maya | anxious | moderate | Worried, catastrophizing, needs reassurance |
| Sam | trauma | moderate | Guarded, hypervigilant, trust issues |
| Jordan | avoidant | high | Minimizing, dismissive, deflecting |
| Marcus | resistant | high | Skeptical, argumentative, defensive |
| Lara | skeptic | high | Questioning, analytical, doubting |

## Configuration (YAML-Driven)

All configuration is in `data/prompts/patients/patient_prompt.yaml`:

```yaml
system_prompt: |
  # Base patient simulation instructions
  
vignette_format: |
  # Template for vignette data
  ## Current Patient Profile
  Name: {name}
  Age: {age}
  ...
  
intro_messages:
  en: "English session intro"
  de: "German session intro"
```

### Modifying Prompts

**To change patient behavior:**
1. Edit `patient_prompt.yaml` → `system_prompt` section
2. No code changes needed

**To change vignette formatting:**
1. Edit `patient_prompt.yaml` → `vignette_format` section
2. Use `{placeholder}` for vignette fields

**To add new vignette fields:**
1. Add to vignette JSON
2. Add `{new_field}` to `vignette_format`
3. No code changes needed

## Implementation Details

### System Prompt Construction

```python
# What PatientAgent.get_system_prompt() does:
1. Load base_prompt from patient_prompt.yaml
2. Add language instruction: "## Language\nRespond in English (en)."
3. Format vignette using vignette_format template
4. Append sample_responses from vignette
5. Return complete prompt
```

### Data Flow

```
patient_prompt.yaml (YAML config)
        +
vignettes/anxious.json (Stable baseline)
        ↓
PatientAgent.get_system_prompt()
        ↓
LLM Provider
        ↓
Realistic patient response
```

## Best Practices

✅ **DO**:
- Keep vignettes as stable baselines for reproducibility
- Iterate on `patient_prompt.yaml` for behavior tuning
- Use vignette `sample_responses` for realistic variety

❌ **DON'T**:
- Modify vignette JSON unless creating new baseline
- Hardcode prompt text in Python code
- Skip language specification

## Testing

```python
# Quick test without API keys
from src.core import load_vignette, format_vignette_for_prompt

vignette = load_vignette('anxious')
formatted = format_vignette_for_prompt(vignette)
print(formatted)  # See formatted vignette
```
