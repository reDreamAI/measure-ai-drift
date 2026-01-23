"""Base agent class for LLM-powered therapy agents.

Provides common functionality for all agents including:
- LLM provider integration
- System prompt management
- Message formatting
- Response generation
"""

from abc import ABC, abstractmethod
from typing import Any

from src.core import Conversation, Message
from src.llm.provider import LLMProvider, create_provider


class BaseAgent(ABC):
    """Abstract base class for all therapy simulation agents.
    
    Provides common infrastructure for LLM-based agents including
    provider management, message formatting, and response generation.
    
    Subclasses must implement:
        - get_system_prompt(): Return the current system prompt
        - get_role(): Return the agent's role identifier
    
    Attributes:
        provider: The LLMProvider instance for API calls
        name: Human-readable name for the agent
        
    Example:
        >>> class MyAgent(BaseAgent):
        ...     def get_system_prompt(self) -> str:
        ...         return "You are a helpful assistant."
        ...     def get_role(self) -> str:
        ...         return "assistant"
        >>> agent = MyAgent(role="therapist")
        >>> response, usage = await agent.generate("Hello!")
    """
    
    def __init__(
        self,
        role: str | None = None,
        provider: LLMProvider | None = None,
        name: str | None = None,
    ) -> None:
        """Initialize the agent with an LLM provider.
        
        Args:
            role: Role identifier for provider factory (e.g., "therapist", "patient")
                  If provider is given, this is ignored for provider creation.
            provider: Optional pre-configured LLMProvider instance.
                     If not provided, one is created using the role.
            name: Human-readable name for the agent (defaults to role)
            
        Raises:
            ValueError: If neither role nor provider is specified
        """
        if provider is None and role is None:
            raise ValueError("Either 'role' or 'provider' must be specified")
        
        self.provider = provider if provider else create_provider(role)
        self.name = name or role or "Agent"
        self._role = role
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the current system prompt for this agent.
        
        Subclasses must implement this to provide context-appropriate
        system prompts (e.g., based on therapy stage, patient profile, etc.)
        
        Returns:
            The system prompt string
        """
        pass
    
    @abstractmethod
    def get_role(self) -> str:
        """Return the agent's role identifier.
        
        Returns:
            Role string (e.g., "therapist", "patient", "router")
        """
        pass
    
    def format_messages(
        self,
        conversation: Conversation | None = None,
        user_message: str | None = None,
    ) -> list[dict[str, str]]:
        """Format messages for the LLM API call.
        
        Constructs the message list with:
        1. System prompt
        2. Conversation history (if provided)
        3. Current user message (if provided)
        
        Args:
            conversation: Optional conversation with history
            user_message: Optional new user message to append
            
        Returns:
            List of message dicts with 'role' and 'content' keys
        """
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        
        if conversation:
            for msg in conversation.messages:
                messages.append(msg.to_api_format())
        
        if user_message:
            messages.append({"role": "user", "content": user_message})
        
        return messages
    
    async def generate(
        self,
        user_message: str | None = None,
        conversation: Conversation | None = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any]]:
        """Generate a response from the agent.
        
        Args:
            user_message: Optional user message to respond to
            conversation: Optional conversation context
            **kwargs: Additional parameters for the LLM provider
            
        Returns:
            Tuple of (response_content, usage_dict)
        """
        messages = self.format_messages(conversation, user_message)
        return await self.provider.generate(messages, **kwargs)
    
    async def generate_with_history(
        self,
        history_string: str,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any]]:
        """Generate a response using a pre-formatted history string.
        
        Useful for routing where the history is formatted as a transcript.
        
        Args:
            history_string: Pre-formatted conversation history
            **kwargs: Additional parameters for the LLM provider
            
        Returns:
            Tuple of (response_content, usage_dict)
        """
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": history_string},
        ]
        return await self.provider.generate(messages, **kwargs)
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name={self.name!r}, provider={self.provider!r})"
