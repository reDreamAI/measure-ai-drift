"""Conversation and message models for therapy session management.

These models represent the core data structures for managing therapy
dialogue history, supporting both the generation stack (synthetic
dialogue creation) and evaluation stack (frozen history loading).
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.core.stages import Stage, Language


class Message(BaseModel):
    """A single message in a therapy conversation.
    
    Represents one turn in the dialogue, storing both the content and
    metadata about the message context (role, stage, language, timestamp).
    
    Attributes:
        content: The text content of the message
        role: The speaker role ("user" for patient, "assistant" for therapist)
        stage: The therapy stage when this message was generated
        language: The language of the message (ISO 639-1 code)
        timestamp: When the message was created
        
    Example:
        >>> msg = Message(
        ...     content="I keep having this nightmare about falling...",
        ...     role="user",
        ...     stage="recording"
        ... )
        >>> msg.role
        'user'
    """
    content: str
    role: str  # "user" (patient) or "assistant" (therapist)
    stage: str | None = None
    language: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    model_config = {"frozen": False, "extra": "ignore"}
    
    def to_api_format(self) -> dict[str, str]:
        """Convert to OpenAI-compatible message format.
        
        Returns:
            Dict with 'role' and 'content' keys suitable for LLM APIs
            
        Example:
            >>> msg = Message(content="Hello", role="user")
            >>> msg.to_api_format()
            {'role': 'user', 'content': 'Hello'}
        """
        return {"role": self.role, "content": self.content}
    
    def is_user_message(self) -> bool:
        """Check if this is a patient/user message."""
        return self.role == "user"
    
    def is_assistant_message(self) -> bool:
        """Check if this is a therapist/assistant message."""
        return self.role == "assistant"


class Conversation(BaseModel):
    """A complete therapy conversation with message history and stage tracking.
    
    Manages the full dialogue history for a therapy session, including
    stage transitions and language settings. Supports both:
    
    1. Generation stack: Building up conversation through patient-therapist
       interaction
    2. Evaluation stack: Loading frozen history up to a specific point
    
    Attributes:
        session_id: Unique identifier for this conversation session
        user_id: Optional identifier for the user/patient
        messages: Ordered list of messages in the conversation
        stages: List of stage values as the conversation progressed
        language: The language setting for this conversation
        
    Example:
        >>> conv = Conversation(session_id="abc-123")
        >>> conv.add_message("I had a nightmare", "user", stage="recording")
        >>> conv.add_message("Tell me about it", "assistant", stage="recording")
        >>> len(conv.messages)
        2
    """
    session_id: str
    user_id: str | None = None
    messages: list[Message] = Field(default_factory=list)
    stages: list[str] = Field(default_factory=list)
    language: str | None = None
    
    model_config = {"frozen": False, "extra": "ignore"}
    
    def add_message(
        self,
        content: str,
        role: str,
        stage: str | None = None,
        language: str | None = None,
    ) -> Message:
        """Add a new message to the conversation history.
        
        Args:
            content: The text content of the message
            role: Speaker role ("user" or "assistant")
            stage: Optional stage override (defaults to current stage)
            language: Optional language override (defaults to conversation language)
            
        Returns:
            The created Message instance
            
        Example:
            >>> conv = Conversation(session_id="test", language="en")
            >>> msg = conv.add_message("Hello", "user", stage="recording")
            >>> msg.language
            'en'
        """
        message = Message(
            content=content,
            role=role,
            stage=stage,
            language=language or self.language,
        )
        self.messages.append(message)
        return message
    
    def get_history_as_string(self, max_messages: int = 100) -> str:
        """Convert recent conversation history to string format for prompt context.
        
        Formats messages as "User: <content>" or "Assistant: <content>"
        for inclusion in prompts. Useful for routing and response generation.
        
        Args:
            max_messages: Maximum number of recent messages to include
            
        Returns:
            Formatted string with message history
            
        Example:
            >>> conv = Conversation(session_id="test")
            >>> conv.add_message("Hi", "user")
            >>> conv.add_message("Hello!", "assistant")
            >>> print(conv.get_history_as_string())
            User: Hi
            Assistant: Hello!
        """
        recent_messages = self.messages[-max_messages:] if self.messages else []
        history_lines = []
        
        for msg in recent_messages:
            role_label = "User" if msg.role == "user" else "Assistant"
            history_lines.append(f"{role_label}: {msg.content}")
        
        return "\n".join(history_lines)
    
    def get_messages_as_api_format(
        self,
        include_system: bool = False,
        system_prompt: str | None = None,
    ) -> list[dict[str, str]]:
        """Convert messages to OpenAI-compatible API format.
        
        Args:
            include_system: Whether to prepend a system message
            system_prompt: The system prompt content (required if include_system=True)
            
        Returns:
            List of message dicts with 'role' and 'content' keys
            
        Example:
            >>> conv = Conversation(session_id="test")
            >>> conv.add_message("Hi", "user")
            >>> conv.get_messages_as_api_format(
            ...     include_system=True,
            ...     system_prompt="You are a therapist."
            ... )
            [{'role': 'system', 'content': 'You are a therapist.'}, {'role': 'user', 'content': 'Hi'}]
        """
        messages = []
        
        if include_system and system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        for msg in self.messages:
            messages.append(msg.to_api_format())
        
        return messages
    
    def get_current_stage(self) -> Stage | None:
        """Get the current (most recent) stage of the conversation.
        
        Returns:
            The current Stage enum value, or None if no stages recorded
            
        Example:
            >>> conv = Conversation(session_id="test")
            >>> conv.stages = ["recording", "rewriting"]
            >>> conv.get_current_stage()
            <Stage.REWRITING: 'rewriting'>
        """
        if not self.stages:
            return None
        return Stage(self.stages[-1])
    
    def get_language(self) -> Language | None:
        """Get the conversation language as a Language enum.
        
        Returns:
            Language enum value, or None if not set
        """
        if not self.language:
            return None
        return Language(self.language)
    
    def count_rewriting_turns(self) -> int:
        """Count the number of therapist rewriting turns in the conversation.

        Only assistant messages with stage="rewriting" are counted,
        since patient responses carry stage=None.

        Returns:
            Number of rewriting therapist turns
        """
        return sum(
            1 for msg in self.messages
            if msg.stage == "rewriting" and msg.role == "assistant"
        )

    def slice_at_rewriting_turn(self, n: int) -> "Conversation":
        """Slice conversation after the Nth rewriting exchange.

        A rewriting exchange is a therapist message (stage=rewriting) followed
        by the patient response (stage=None). This creates evaluation entry
        points at different conversation depths within the rewriting stage.

        Args:
            n: 1-indexed rewriting turn to slice after

        Returns:
            New Conversation with messages up through the Nth rewriting exchange

        Raises:
            ValueError: If n is less than 1 or exceeds available rewriting turns
        """
        if n < 1:
            raise ValueError(f"n must be >= 1, got {n}")

        rewriting_count = 0
        cut_index = len(self.messages)  # default: include all

        for i, msg in enumerate(self.messages):
            if msg.stage == "rewriting" and msg.role == "assistant":
                rewriting_count += 1
                if rewriting_count == n:
                    # Include this therapist message + next message (patient response)
                    cut_index = i + 1
                    if i + 1 < len(self.messages) and self.messages[i + 1].stage is None:
                        cut_index = i + 2
                    break

        if rewriting_count < n:
            raise ValueError(
                f"Requested rewriting turn {n} but only {rewriting_count} found"
            )

        sliced_messages = [msg.model_copy() for msg in self.messages[:cut_index]]
        sliced_stages = list(dict.fromkeys(
            msg.stage for msg in sliced_messages if msg.stage
        ))

        return Conversation(
            session_id=self.session_id,
            user_id=self.user_id,
            messages=sliced_messages,
            stages=sliced_stages,
            language=self.language,
        )

    def slice_at_stage(self, target_stage: Stage | str) -> "Conversation":
        """Create a new conversation sliced up to and including the target stage.
        
        Useful for creating frozen histories for the evaluation stack. Returns
        all messages up to and including the last message at the target stage.
        
        Args:
            target_stage: The stage to slice at (inclusive)
            
        Returns:
            New Conversation with messages up to the target stage
            
        Example:
            >>> conv = Conversation(session_id="test")
            >>> conv.add_message("nightmare...", "user", stage="recording")
            >>> conv.add_message("let's modify it", "assistant", stage="rewriting")
            >>> conv.add_message("I imagine...", "user", stage="rewriting")
            >>> conv.stages = ["recording", "rewriting", "rewriting"]
            >>> sliced = conv.slice_at_stage(Stage.RECORDING)
            >>> len(sliced.messages)
            1
        """
        if isinstance(target_stage, str):
            target_stage = Stage(target_stage)
        
        target_value = target_stage.value
        
        # Find the last message index at or before the target stage
        cut_index = 0
        for i, msg in enumerate(self.messages):
            if msg.stage == target_value:
                cut_index = i + 1  # Include this message
            elif msg.stage and Stage(msg.stage) != target_stage:
                # Check if this stage comes after target
                try:
                    current_stage = Stage(msg.stage)
                    if not target_stage.can_transition_to(current_stage):
                        # This message is in a later stage, don't include
                        pass
                except ValueError:
                    pass
        
        # More accurate slicing: find messages up through target stage
        sliced_messages = []
        sliced_stages = []
        
        for msg in self.messages:
            if msg.stage:
                try:
                    msg_stage = Stage(msg.stage)
                    # Include if at or before target stage
                    from src.core.stages import get_stage_index
                    if get_stage_index(msg_stage) <= get_stage_index(target_stage):
                        sliced_messages.append(msg.model_copy())
                        if msg.stage not in sliced_stages or msg.stage == sliced_stages[-1] if sliced_stages else True:
                            if msg.stage not in sliced_stages:
                                sliced_stages.append(msg.stage)
                except ValueError:
                    # Unknown stage, include anyway
                    sliced_messages.append(msg.model_copy())
            else:
                # No stage metadata, include
                sliced_messages.append(msg.model_copy())
        
        return Conversation(
            session_id=self.session_id,
            user_id=self.user_id,
            messages=sliced_messages,
            stages=sliced_stages,
            language=self.language,
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize conversation to a dictionary.
        
        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Conversation":
        """Deserialize conversation from a dictionary.
        
        Args:
            data: Dictionary with conversation data
            
        Returns:
            Conversation instance
        """
        return cls.model_validate(data)
    
    def __len__(self) -> int:
        """Return the number of messages in the conversation."""
        return len(self.messages)
    
    def __bool__(self) -> bool:
        """Return True if the conversation has any messages."""
        return len(self.messages) > 0
