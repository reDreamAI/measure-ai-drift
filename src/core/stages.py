"""Stage and language enumerations for IRT therapy sessions.

The IRT (Imagery Rehearsal Therapy) process follows a structured flow
through distinct stages:

    recording → rewriting → summary → rehearsal → final

Stage Mapping to Thesis:
    - RECORDING: Psychoeducation phase (nightmare elicitation)
    - REWRITING: Rescripting phase (evaluation target) - where imagery is modified
    - SUMMARY: Rescripting phase (evaluation target) - consolidation
    - REHEARSAL: Practice phase for the rescripted imagery
    - FINAL: Session closing and wrap-up
"""

from enum import Enum


class Stage(str, Enum):
    """Therapy session stages following the IRT protocol.
    
    The Stage enum inherits from str to allow easy serialization and
    comparison with string values (e.g., Stage.RECORDING == "recording").
    
    Attributes:
        RECORDING: Initial stage for nightmare description and elicitation
        REWRITING: Core rescripting stage where nightmare imagery is modified
        SUMMARY: Summary generation after rescripting
        REHEARSAL: Practice instructions for the new imagery
        FINAL: Session conclusion and closing
        
    Example:
        >>> stage = Stage.REWRITING
        >>> stage.value
        'rewriting'
        >>> stage == "rewriting"
        True
        >>> Stage("recording")
        <Stage.RECORDING: 'recording'>
    """
    RECORDING = "recording"
    REWRITING = "rewriting"
    SUMMARY = "summary"
    REHEARSAL = "rehearsal"
    FINAL = "final"
    
    @classmethod
    def from_string(cls, value: str) -> "Stage":
        """Parse a string value into a Stage enum.
        
        Args:
            value: String stage name (case-insensitive)
            
        Returns:
            Corresponding Stage enum member
            
        Raises:
            ValueError: If value doesn't match any stage
            
        Example:
            >>> Stage.from_string("REWRITING")
            <Stage.REWRITING: 'rewriting'>
            >>> Stage.from_string("recording")
            <Stage.RECORDING: 'recording'>
        """
        normalized = value.lower().strip()
        try:
            return cls(normalized)
        except ValueError:
            valid = [s.value for s in cls]
            raise ValueError(
                f"Invalid stage '{value}'. Valid stages: {valid}"
            ) from None
    
    def is_rescripting_stage(self) -> bool:
        """Check if this stage is part of the rescripting evaluation target.
        
        The rescripting stages (REWRITING and SUMMARY) are the primary
        targets for stability evaluation in the thesis.
        
        Returns:
            True if this is REWRITING or SUMMARY stage
            
        Example:
            >>> Stage.REWRITING.is_rescripting_stage()
            True
            >>> Stage.RECORDING.is_rescripting_stage()
            False
        """
        return self in (Stage.REWRITING, Stage.SUMMARY)
    
    def can_transition_to(self, next_stage: "Stage") -> bool:
        """Check if a transition to the next stage is valid.
        
        Enforces the IRT protocol stage ordering. Valid transitions:
            - recording → rewriting
            - rewriting → summary
            - summary → rehearsal
            - rehearsal → final
        
        Note: Same-stage transitions are always allowed (staying in stage).
        
        Args:
            next_stage: The proposed next stage
            
        Returns:
            True if the transition is valid
            
        Example:
            >>> Stage.RECORDING.can_transition_to(Stage.REWRITING)
            True
            >>> Stage.RECORDING.can_transition_to(Stage.FINAL)
            False
        """
        if self == next_stage:
            return True  # Staying in same stage is always valid
            
        transitions = {
            Stage.RECORDING: Stage.REWRITING,
            Stage.REWRITING: Stage.SUMMARY,
            Stage.SUMMARY: Stage.REHEARSAL,
            Stage.REHEARSAL: Stage.FINAL,
        }
        
        return transitions.get(self) == next_stage


class Language(str, Enum):
    """Supported languages for therapy sessions.
    
    The system supports bilingual operation (German/English) to accommodate
    different patient populations. Language affects:
        - System prompts loaded for the therapist agent
        - Routing prompts
        - Session introductions
    
    Attributes:
        ENGLISH: English language (en)
        GERMAN: German language (de)
        
    Example:
        >>> lang = Language.GERMAN
        >>> lang.value
        'de'
        >>> Language("en")
        <Language.ENGLISH: 'en'>
    """
    ENGLISH = "en"
    GERMAN = "de"
    
    @classmethod
    def from_string(cls, value: str) -> "Language":
        """Parse a string value into a Language enum.
        
        Args:
            value: Language code or name (case-insensitive)
            
        Returns:
            Corresponding Language enum member
            
        Raises:
            ValueError: If value doesn't match any language
            
        Example:
            >>> Language.from_string("EN")
            <Language.ENGLISH: 'en'>
            >>> Language.from_string("german")
            <Language.GERMAN: 'de'>
        """
        normalized = value.lower().strip()
        
        # Handle full language names
        name_mapping = {
            "english": "en",
            "german": "de",
            "deutsch": "de",
        }
        
        if normalized in name_mapping:
            normalized = name_mapping[normalized]
        
        try:
            return cls(normalized)
        except ValueError:
            valid = [f"{l.value} ({l.name.lower()})" for l in cls]
            raise ValueError(
                f"Invalid language '{value}'. Valid languages: {valid}"
            ) from None


# Stage flow order for reference
STAGE_ORDER: list[Stage] = [
    Stage.RECORDING,
    Stage.REWRITING,
    Stage.SUMMARY,
    Stage.REHEARSAL,
    Stage.FINAL,
]


def get_stage_index(stage: Stage) -> int:
    """Get the numerical index of a stage in the IRT flow.
    
    Args:
        stage: The stage to look up
        
    Returns:
        Zero-based index in the stage flow
        
    Example:
        >>> get_stage_index(Stage.REWRITING)
        1
    """
    return STAGE_ORDER.index(stage)
