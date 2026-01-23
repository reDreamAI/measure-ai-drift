"""Therapist agent for generating stage-appropriate therapeutic responses.

The TherapistAgent selects and applies the appropriate system prompt
based on the current therapy stage and language setting.
"""

from typing import Any

from src.agents.base import BaseAgent
from src.core import (
    Conversation,
    Stage,
    load_stage_prompt,
    get_intro_message,
)
from src.llm.provider import LLMProvider


class TherapistAgent(BaseAgent):
    """Agent that generates therapeutic responses based on current stage.
    
    The therapist agent adapts its behavior to the current stage of
    Imagery Rehearsal Therapy:
    - Recording: Elicit nightmare details using Socratic method
    - Rewriting: Guide rescripting with open questions
    - Summary: Generate structured dream summaries
    - Rehearsal: Explain the practice process
    - Final: Provide warm session closing
    
    Attributes:
        stage: Current therapy stage
        language: Session language ("en" or "de")
        
    Example:
        >>> therapist = TherapistAgent(stage=Stage.RECORDING)
        >>> response, usage = await therapist.generate(
        ...     user_message="I had a nightmare about falling.",
        ...     conversation=conv,
        ... )
    """
    
    def __init__(
        self,
        stage: Stage | str = Stage.RECORDING,
        language: str = "en",
        provider: LLMProvider | None = None,
    ) -> None:
        """Initialize the therapist agent.
        
        Args:
            stage: Initial therapy stage
            language: Session language ("en" or "de")
            provider: Optional pre-configured LLMProvider
        """
        super().__init__(role="therapist", provider=provider, name="Therapist")
        self._stage = Stage(stage) if isinstance(stage, str) else stage
        self.language = language
    
    @property
    def stage(self) -> Stage:
        """Current therapy stage."""
        return self._stage
    
    @stage.setter
    def stage(self, value: Stage | str) -> None:
        """Set the current therapy stage."""
        self._stage = Stage(value) if isinstance(value, str) else value
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the current stage and language.
        
        Returns:
            Stage-specific system prompt
        """
        return load_stage_prompt(self._stage.value, self.language)
    
    def get_role(self) -> str:
        """Return the agent's role identifier."""
        return "therapist"
    
    def get_intro_message(self) -> str:
        """Get the session introduction message.
        
        Returns:
            Intro message in the current language
        """
        return get_intro_message(self.language)
    
    def format_messages(
        self,
        conversation: Conversation | None = None,
        user_message: str | None = None,
    ) -> list[dict[str, str]]:
        """Format messages with intro message prepended to history.
        
        Overrides base implementation to include the session intro
        at the start of the conversation context.
        
        Args:
            conversation: Optional conversation with history
            user_message: Optional new user message
            
        Returns:
            List of message dicts for the LLM API
        """
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        
        # Build context with intro message
        intro = self.get_intro_message()
        history_parts = [f"AI: {intro}"]
        
        if conversation:
            history_parts.append(conversation.get_history_as_string())
        
        if user_message:
            history_parts.append(f"User: {user_message}")
        
        # Combine into user message (history + current message)
        full_context = "\n\nConversation history:\n" + "\n".join(history_parts)
        messages.append({"role": "user", "content": full_context})
        
        return messages
    
    async def generate(
        self,
        user_message: str | None = None,
        conversation: Conversation | None = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any]]:
        """Generate a therapeutic response.
        
        Args:
            user_message: Patient message to respond to
            conversation: Conversation context
            **kwargs: Additional LLM parameters
            
        Returns:
            Tuple of (response_content, usage_dict)
        """
        messages = self.format_messages(conversation, user_message)
        return await self.provider.generate(messages, **kwargs)
    
    def update_stage(self, new_stage: Stage | str) -> None:
        """Update the therapist's current stage.
        
        Args:
            new_stage: The new therapy stage
        """
        self.stage = new_stage
    
    def __repr__(self) -> str:
        """String representation of the therapist agent."""
        return (
            f"TherapistAgent(stage={self._stage.value!r}, "
            f"language={self.language!r})"
        )
