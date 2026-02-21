# Strategy Taxonomy Evolution

## Original taxonomy (8 categories)

The initial taxonomy used 8 IRT rescripting strategies:

| Category | Description |
|----------|-------------|
| empowerment | Increase sense of control and personal power |
| mastery | Gain skills or abilities to handle the situation |
| safety | Create safe spaces or protective elements |
| cognitive_reframe | Reinterpret threatening elements differently |
| emotional_regulation | Introduce calming or comforting elements |
| social_support | Introduce helpful figures or allies |
| sensory_modulation | Modify sensory details (light, sound, texture) |
| gradual_exposure | Gradually reduce intensity of threatening elements |

## Problem: severely skewed distribution

Across 1,272 strategy picks from all experiments:

```
empowerment:          50.0%
mastery:              37.7%
cognitive_reframe:     6.1%
safety:                5.3%
emotional_regulation:  1.0%
social_support:        0.0%
sensory_modulation:    0.0%
gradual_exposure:      0.0%
```

Two categories consumed 87.7% of all picks. Three categories were never selected.

### Root causes identified

1. **empowerment vs mastery overlap**: Both describe gaining control/capability in the dream. The model treats them as near-synonyms and alternates between them without meaningful clinical distinction.

2. **gradual_exposure inapplicable**: This is a multi-session technique (progressive desensitization over time). Single-turn rescripting cannot implement it, and the model correctly avoids it but gets no guidance toward alternatives.

3. **Plan prompts listed bare IDs**: The model saw `sensory_modulation` with no description and defaulted to familiar labels like `empowerment`.

## Revision 1: 8 → 6 categories (merge + drop)

**Decision**: Merge empowerment + mastery → `agency`. Drop `gradual_exposure`.

**Rationale**: Eliminating the overlap and the inapplicable category should concentrate valid picks and simplify analysis. Adding descriptions to prompts should help the model discover tail categories.

**Result** (n=5 per vignette, t=0.5, chained mode):

| Vignette | Strategies picked |
|----------|-------------------|
| anxious | agency (5/5), emotional_regulation (5/5) |
| trauma | agency (5/5), safety (5/5) |
| skeptic | agency (5/5), safety (5/5) |

Agency went from 87.7% (split across two) to **100%** of trials. The merge amplified the problem: one super-category now absorbs everything because "gain control, power, or capability" applies to every nightmare rescripting scenario.

Positive signal: `emotional_regulation` appeared (was 1% pre-revision), suggesting descriptions help.

## Revision 2: split agency → mechanism-specific categories

### Analysis

The core issue is that `agency` describes a therapeutic **goal** (feel more in control) rather than a specific **mechanism** of change. Every nightmare rescripting intervention serves agency in some way, making it a super-category that overlaps with everything.

The tail categories work better because they describe concrete mechanisms:
- cognitive_reframe: the mechanism is *reinterpretation*
- social_support: the mechanism is *introducing allies*
- sensory_modulation: the mechanism is *changing sensory details*

### Decision

Split `agency` into two mechanism-specific categories:

| Category | Description | Mechanism |
|----------|-------------|-----------|
| **confrontation** | Directly face, challenge, or overpower the threatening element | External action toward the threat |
| **self_empowerment** | Gain personal strength, abilities, or confidence within the dream | Internal change within the dreamer |

These are orthogonal:
- confrontation is about the dreamer's **action toward the threat** (fight, challenge, resist)
- self_empowerment is about the dreamer's **internal transformation** (grow stronger, gain abilities)

And distinct from the other categories:
- safety = environment modification (not confronting or self-changing)
- cognitive_reframe = meaning change (not action or transformation)
- emotional_regulation = calming (not strength or confrontation)
- social_support = adding allies (not self-focused)
- sensory_modulation = sensory details (not about power or action)

### Additional measures

Prompt-level steering added to encourage specificity:
- Instruction: "Choose the strategies most specifically suited to THIS patient's nightmare content"
- Diverse examples that demonstrate non-default category picks
- Categories listed with descriptions so the model understands each mechanism

### Final taxonomy (7 categories)

```
confrontation:        Directly face, challenge, or overpower the threatening element
self_empowerment:     Gain personal strength, abilities, or confidence within the dream
safety:               Create safe spaces or protective elements
cognitive_reframe:    Reinterpret threatening elements differently
emotional_regulation: Introduce calming or comforting elements
social_support:       Introduce helpful figures or allies
sensory_modulation:   Modify sensory details (light, sound, texture)
```

### Expected vignette-strategy mapping

| Vignette | Primary nightmare content | Expected strategies |
|----------|--------------------------|---------------------|
| anxious | Exam room flooding, walls closing in | emotional_regulation, sensory_modulation, cognitive_reframe |
| trauma | Trapped in dark room, footsteps approaching | safety, social_support, self_empowerment |
| skeptic | Server maze, being chased | confrontation, cognitive_reframe, sensory_modulation |
| avoidant | (varies) | safety, emotional_regulation |
| cooperative | (varies) | confrontation, self_empowerment |
| resistant | (varies) | cognitive_reframe, social_support |
