"""Router agent for stage classification and transition management.

The RouterAgent determines appropriate therapy stage transitions
based on conversation content, with guardrails to ensure proper
protocol adherence.
"""

import logging
from typing import Any

from src.agents.base import BaseAgent
from src.core import Conversation, Stage, load_routing_prompt
from src.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


class RouterAgent(BaseAgent):
    """Agent that classifies conversation stage and manages transitions.
    
    The router agent:
    - Analyzes conversation history to determine current stage
    - Applies guardrails to prevent stage skipping
    - Ensures summary and rehearsal occur before final stage
    
    The guardrails enforce the IRT protocol:
    - Cannot skip to FINAL without SUMMARY
    - Cannot skip to FINAL without REHEARSAL
    
    Attributes:
        valid_stages: List of valid stage values
        default_stage: Fallback stage when parsing fails
        
    Example:
        >>> router = RouterAgent()
        >>> stage = await router.determine_stage(conversation)
        >>> print(stage)  # Stage.RECORDING
    """
    
    def __init__(
        self,
        provider: LLMProvider | None = None,
    ) -> None:
        """Initialize the router agent.
        
        Args:
            provider: Optional pre-configured LLMProvider
        """
        super().__init__(role="router", provider=provider, name="Router")
        self._config = load_routing_prompt()
        self.valid_stages = self._config.get("valid_stages", [
            "recording", "rewriting", "summary", "rehearsal", "final"
        ])
        self.default_stage = self._config.get("default_stage", "recording")
    
    def get_system_prompt(self) -> str:
        """Get the routing system prompt.
        
        Returns:
            System prompt for stage classification
        """
        return self._config.get("system_prompt", "")
    
    def get_role(self) -> str:
        """Return the agent's role identifier."""
        return "router"
    
    def _format_transcript(self, conversation: Conversation) -> str:
        """Format conversation history as a transcript for routing.
        
        Args:
            conversation: The conversation to format
            
        Returns:
            Formatted transcript string
        """
        history = conversation.get_history_as_string()
        return f"<transcript>\n{history}\n</transcript>\n\nClassification:"
    
    def _parse_stage(
        self,
        response: str,
        conversation: Conversation,
    ) -> Stage:
        """Parse the LLM response into a Stage enum.
        
        Args:
            response: Raw LLM response
            conversation: Current conversation for fallback
            
        Returns:
            Parsed Stage enum value
        """
        stage_str = response.strip().lower()
        
        try:
            return Stage(stage_str)
        except ValueError:
            logger.warning(f"Invalid stage '{stage_str}', using fallback")
            
            # Fallback to last known stage or default
            if conversation.stages:
                return Stage(conversation.stages[-1])
            return Stage(self.default_stage)
    
    def _apply_guardrails(
        self,
        proposed_stage: Stage,
        conversation: Conversation,
    ) -> Stage:
        """Apply guardrails to prevent invalid stage transitions.
        
        Enforces the IRT protocol by ensuring:
        - Summary must occur before final
        - Rehearsal must occur before final
        
        Args:
            proposed_stage: Stage proposed by the LLM
            conversation: Current conversation with stage history
            
        Returns:
            Validated stage (may differ from proposed if guardrails trigger)
        """
        if proposed_stage != Stage.FINAL:
            return proposed_stage
        
        # Guardrails for FINAL stage
        previous_stages = set(conversation.stages)
        
        # Guard rail 1: Must have summary before final
        if Stage.SUMMARY.value not in previous_stages:
            logger.info(
                "Guardrail: Redirecting to SUMMARY (no summary generated yet)"
            )
            return Stage.SUMMARY
        
        # Guard rail 2: Must have rehearsal before final
        if Stage.REHEARSAL.value not in previous_stages:
            logger.info(
                "Guardrail: Redirecting to REHEARSAL (no rehearsal yet)"
            )
            return Stage.REHEARSAL
        
        return proposed_stage
    
    async def determine_stage(
        self,
        conversation: Conversation,
        **kwargs: Any,
    ) -> Stage:
        """Determine the appropriate stage for the conversation.
        
        Analyzes the conversation history and applies guardrails
        to determine the correct therapy stage.
        
        Args:
            conversation: Current conversation with history
            **kwargs: Additional LLM parameters
            
        Returns:
            The determined Stage enum value
        """
        # Format conversation as transcript
        transcript = self._format_transcript(conversation)
        
        # Get LLM classification
        response, usage = await self.generate_with_history(transcript, **kwargs)
        
        logger.debug(f"Router raw response: {response!r}")
        
        # Parse and validate
        proposed_stage = self._parse_stage(response, conversation)
        
        # Apply guardrails
        final_stage = self._apply_guardrails(proposed_stage, conversation)
        
        logger.info(
            f"Stage determination: proposed={proposed_stage.value}, "
            f"final={final_stage.value}"
        )
        
        return final_stage
    
    async def classify_and_update(
        self,
        conversation: Conversation,
        **kwargs: Any,
    ) -> Stage:
        """Determine stage and update conversation's stage history.
        
        Convenience method that determines the stage and appends it
        to the conversation's stages list.
        
        Args:
            conversation: Current conversation (will be modified)
            **kwargs: Additional LLM parameters
            
        Returns:
            The determined Stage enum value
        """
        stage = await self.determine_stage(conversation, **kwargs)
        conversation.stages.append(stage.value)
        return stage
    
    def __repr__(self) -> str:
        """String representation of the router agent."""
        return f"RouterAgent(valid_stages={self.valid_stages})"
