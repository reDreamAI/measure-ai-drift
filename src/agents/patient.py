"""Patient agent for simulating realistic therapy patient behavior.

The PatientAgent uses vignette data to simulate patient responses
with appropriate personality traits, resistance behaviors, and
engagement patterns.
"""

from typing import Any

from src.agents.base import BaseAgent
from src.core import (
    Conversation,
    Message,
    load_patient_prompt,
    load_vignette,
    format_vignette_for_prompt,
    get_intro_message,
)
from src.llm.provider import LLMProvider


class PatientAgent(BaseAgent):
    """Agent that simulates a therapy patient based on vignette data.
    
    The patient agent uses a vignette profile to generate realistic
    patient responses that reflect:
    - The patient's nightmare content
    - Personality traits and communication style
    - Resistance behaviors and engagement patterns
    - Gradual progress through the therapy session
    
    Attributes:
        vignette: The patient profile data
        vignette_name: Name of the loaded vignette
        language: Current session language
        
    Example:
        >>> patient = PatientAgent.from_vignette("anxious")
        >>> response, usage = await patient.generate(
        ...     user_message="Tell me about your nightmare."
        ... )
    """
    
    def __init__(
        self,
        vignette: dict[str, Any],
        vignette_name: str = "unknown",
        language: str = "en",
        provider: LLMProvider | None = None,
    ) -> None:
        """Initialize the patient agent with vignette data.
        
        Args:
            vignette: Patient profile dictionary from vignette file
            vignette_name: Name identifier for the vignette
            language: Session language ("en" or "de")
            provider: Optional pre-configured LLMProvider
        """
        super().__init__(role="patient", provider=provider, name=vignette.get("name", "Patient"))
        self.vignette = vignette
        self.vignette_name = vignette_name
        self.language = language
        self._base_prompt = load_patient_prompt()
    
    @classmethod
    def from_vignette(
        cls,
        vignette_name: str,
        language: str = "en",
        provider: LLMProvider | None = None,
    ) -> "PatientAgent":
        """Create a patient agent from a vignette file.
        
        Args:
            vignette_name: Name of the vignette (without .json extension)
            language: Session language ("en" or "de")
            provider: Optional pre-configured LLMProvider
            
        Returns:
            Configured PatientAgent instance
            
        Example:
            >>> patient = PatientAgent.from_vignette("cooperative")
        """
        vignette = load_vignette(vignette_name)
        return cls(
            vignette=vignette,
            vignette_name=vignette_name,
            language=language,
            provider=provider,
        )
    
    def get_system_prompt(self) -> str:
        """Build the full system prompt with vignette data.
        
        Combines the base patient simulation prompt with the
        formatted vignette data for realistic patient behavior.
        Uses the vignette_format template from patient_prompt.yaml
        for consistent formatting.
        
        Returns:
            Complete system prompt string
        """
        base_prompt = self._base_prompt.get("system_prompt", "")
        vignette_context = format_vignette_for_prompt(self.vignette)
        
        # Add language instruction
        language_note = f"\n\n## Language\nRespond in {'German (de)' if self.language == 'de' else 'English (en)'}."
        
        # Add sample responses as behavioral guidance
        sample_responses = self.vignette.get("sample_responses", [])
        sample_text = ""
        if sample_responses:
            sample_text = "\n\n## How You Talk\n"
            sample_text += "Aim for this register and length. Some of your messages can be even shorter (a single sentence, or just 'yeah', 'I guess', 'I don't know'):\n"
            for response in sample_responses:
                sample_text += f"- \"{response}\"\n"
        
        return f"{base_prompt}{language_note}\n\n{vignette_context}{sample_text}"
    
    def get_role(self) -> str:
        """Return the agent's role identifier."""
        return "patient"

    def format_messages(
        self,
        conversation: Conversation | None = None,
        user_message: str | None = None,
    ) -> list[dict[str, str]]:
        """Format messages with inverted roles for patient perspective.

        From the patient's perspective:
        - Therapist messages appear as "user" (what we respond to)
        - Patient's own messages appear as "assistant" (what we said)

        This ensures the LLM understands it should generate patient
        responses, not therapist responses.

        Args:
            conversation: Optional conversation with history
            user_message: Optional new therapist message to respond to

        Returns:
            List of message dicts for the LLM API with inverted roles
        """
        messages = [{"role": "system", "content": self.get_system_prompt()}]

        # Start with therapist's intro message as the first "user" message
        intro = get_intro_message(self.language)
        messages.append({"role": "user", "content": intro})

        if conversation:
            for msg in conversation.messages:
                # Invert roles: patient (user) -> assistant, therapist (assistant) -> user
                if msg.role == "user":
                    # Patient's message becomes assistant (our previous response)
                    messages.append({"role": "assistant", "content": msg.content})
                else:
                    # Therapist's message becomes user (what we respond to)
                    messages.append({"role": "user", "content": msg.content})

        if user_message:
            # New therapist message to respond to
            messages.append({"role": "user", "content": user_message})

        return messages

    def get_initial_message(self) -> str:
        """Get the patient's initial nightmare description.
        
        Returns a natural opening message based on the vignette's
        nightmare content and personality traits. Converts third-person
        vignette descriptions to first-person speech.
        
        Returns:
            Initial message to start the therapy session
        """
        nightmare = self.vignette.get("nightmare", {})
        content = nightmare.get("content", "I've been having bad dreams...")
        
        # Convert third-person vignette content to first-person fragment
        # Take just the first sentence/clause for brevity
        first_part = content.split(".")[0].strip()
        # Common third-person to first-person replacements
        first_part = first_part.replace(" her ", " my ").replace(" his ", " my ")
        first_part = first_part.replace(" she ", " I ").replace(" he ", " I ")
        first_part = first_part.replace("Her ", "My ").replace("His ", "My ")
        first_part = first_part.replace("She ", "I ").replace("He ", "I ")
        
        # Craft an opening based on personality
        traits = self.vignette.get("personality_traits", [])
        
        if "worried" in traits or "anxious" in traits:
            opener = "I've been having these bad dreams. "
        elif "resistant" in traits or "dismissive" in traits:
            opener = "I don't really know why I'm here but "
        elif "cooperative" in traits or "engaged" in traits:
            opener = "I'd like to tell you about a recurring dream I've been having. "
        else:
            opener = "I've been having this nightmare. "
        
        # Keep the initial description brief to allow therapist to probe
        return f"{opener}It's about {first_part.lower()}."
    
    def get_nightmare_content(self) -> str:
        """Get the full nightmare content from the vignette.
        
        Returns:
            The nightmare content string
        """
        return self.vignette.get("nightmare", {}).get("content", "")
    
    def get_resistance_level(self) -> str:
        """Get the patient's resistance level.
        
        Returns:
            Resistance level string (e.g., "low", "moderate", "high")
        """
        return self.vignette.get("resistance_level", "moderate")
    
    def __repr__(self) -> str:
        """String representation of the patient agent."""
        return (
            f"PatientAgent(name={self.name!r}, "
            f"vignette={self.vignette_name!r}, "
            f"resistance={self.get_resistance_level()!r})"
        )
