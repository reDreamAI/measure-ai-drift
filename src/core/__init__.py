"""Core data models for the therapy LLM simulation system.

This module provides the fundamental data structures used across both
the generation stack (synthetic dialogue creation) and evaluation stack
(rescripting stability measurement).

Exports:
    - Stage: Enum representing IRT therapy stages
    - Language: Enum for supported languages
    - Message: Single conversation message with metadata
    - Conversation: Full conversation with message history and stage tracking
"""

from src.core.stages import Stage, Language
from src.core.conversation import Message, Conversation

__all__ = [
    "Stage",
    "Language",
    "Message",
    "Conversation",
]
