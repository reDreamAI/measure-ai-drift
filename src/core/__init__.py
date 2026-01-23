"""Core data models for the therapy LLM simulation system.

This module provides the fundamental data structures used across both
the generation stack (synthetic dialogue creation) and evaluation stack
(rescripting stability measurement).

Exports:
    - Stage: Enum representing IRT therapy stages
    - Language: Enum for supported languages
    - Message: Single conversation message with metadata
    - Conversation: Full conversation with message history and stage tracking
    - Config loading utilities for prompts and vignettes
"""

from src.core.stages import Stage, Language
from src.core.conversation import Message, Conversation
from src.core.config_loader import (
    load_yaml,
    load_json,
    load_routing_prompt,
    load_stage_prompt,
    load_all_stage_prompts,
    load_patient_prompt,
    load_vignette,
    list_vignettes,
    format_vignette_for_prompt,
    get_intro_message,
    load_strategy_taxonomy,
    load_internal_plan_prompt,
)

__all__ = [
    # Data models
    "Stage",
    "Language",
    "Message",
    "Conversation",
    # Config loading
    "load_yaml",
    "load_json",
    "load_routing_prompt",
    "load_stage_prompt",
    "load_all_stage_prompts",
    "load_patient_prompt",
    "load_vignette",
    "list_vignettes",
    "format_vignette_for_prompt",
    "get_intro_message",
    "load_strategy_taxonomy",
    "load_internal_plan_prompt",
]
