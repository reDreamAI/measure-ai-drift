"""Configuration and prompt loading utilities.

This module provides functions to load YAML configuration files and prompts
from the data/prompts/ directory structure.
"""

import json
import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# Base paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROMPTS_DIR = DATA_DIR / "prompts"
VIGNETTES_DIR = PROMPTS_DIR / "patients" / "vignettes"
CONFIG_DIR = PROJECT_ROOT / "src" / "config"


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML file and return its contents as a dictionary.
    
    Args:
        path: Path to the YAML file (absolute or relative to project root)
        
    Returns:
        Parsed YAML content as dictionary
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        yaml.YAMLError: If the file contains invalid YAML
    """
    path = Path(path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_json(path: str | Path) -> dict[str, Any]:
    """Load a JSON file and return its contents as a dictionary.
    
    Args:
        path: Path to the JSON file (absolute or relative to project root)
        
    Returns:
        Parsed JSON content as dictionary
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    path = Path(path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_routing_prompt() -> dict[str, Any]:
    """Load the router system prompt configuration.
    
    Returns:
        Dictionary containing:
            - system_prompt: The routing instruction prompt
            - valid_stages: List of valid stage values
            - default_stage: Fallback stage value
    """
    return load_yaml(PROMPTS_DIR / "router" / "routing.yaml")


def load_stage_prompt(stage: str, language: str = "en") -> str:
    """Load a stage-specific therapist prompt.
    
    Args:
        stage: Stage name (recording, rewriting, summary, rehearsal, final)
        language: Language code ("en" or "de")
        
    Returns:
        The stage prompt text for the specified language
        
    Raises:
        FileNotFoundError: If the stage prompt file doesn't exist
        KeyError: If the language is not found in the prompt file
    """
    prompt_file = PROMPTS_DIR / "router" / "stage_prompts" / f"{stage}.yaml"
    prompt_data = load_yaml(prompt_file)
    
    if language not in prompt_data:
        available = [k for k in prompt_data.keys() if k in ("en", "de")]
        raise KeyError(
            f"Language '{language}' not found in {stage}.yaml. "
            f"Available: {available}"
        )
    
    return prompt_data[language]


def load_all_stage_prompts(language: str = "en") -> dict[str, str]:
    """Load all stage prompts for a given language.
    
    Args:
        language: Language code ("en" or "de")
        
    Returns:
        Dictionary mapping stage names to their prompts
    """
    stages = ["recording", "rewriting", "summary", "rehearsal", "final"]
    return {stage: load_stage_prompt(stage, language) for stage in stages}


def load_patient_prompt() -> dict[str, Any]:
    """Load the patient simulator base prompt configuration.
    
    Returns:
        Dictionary containing:
            - system_prompt: Base patient simulation instructions
            - vignette_format: Template for formatting vignette data
            - intro_messages: Language-specific intro messages
    """
    return load_yaml(PROMPTS_DIR / "patients" / "patient_prompt.yaml")


def load_vignette(vignette_name: str) -> dict[str, Any]:
    """Load a patient vignette by name.
    
    Args:
        vignette_name: Name of the vignette file (without .json extension)
        
    Returns:
        Vignette data dictionary containing patient profile
        
    Raises:
        FileNotFoundError: If the vignette doesn't exist
    """
    vignette_file = VIGNETTES_DIR / f"{vignette_name}.json"
    return load_json(vignette_file)


def list_vignettes() -> list[str]:
    """List all available vignette names.
    
    Returns:
        List of vignette names (without .json extension)
    """
    if not VIGNETTES_DIR.exists():
        return []
    
    return [f.stem for f in VIGNETTES_DIR.glob("*.json")]


def format_vignette_for_prompt(vignette: dict[str, Any]) -> str:
    """Format a vignette dictionary into a prompt-ready string.
    
    Uses the vignette_format template from patient_prompt.yaml to ensure
    consistency between prompt definition and actual formatting.
    
    Args:
        vignette: Vignette data dictionary
        
    Returns:
        Formatted string suitable for inclusion in a system prompt
    """
    patient_config = load_patient_prompt()
    template = patient_config.get("vignette_format", "")
    
    if not template:
        # Fallback to basic formatting if template is missing
        nightmare = vignette.get("nightmare", {})
        return f"""## Current Patient Profile
Name: {vignette.get('name', 'Unknown')}
Age: {vignette.get('age', 'Unknown')}
Gender: {vignette.get('gender', 'Unknown')}

Background: {vignette.get('background', 'Not specified')}

Nightmare:
- Content: {nightmare.get('content', 'Not specified')}
- Frequency: {nightmare.get('frequency', 'Unknown')}
- Duration: {nightmare.get('duration', 'Unknown')}
- Impact: {nightmare.get('impact', 'Unknown')}

Personality: {', '.join(vignette.get('personality_traits', []))}
Resistance Level: {vignette.get('resistance_level', 'Unknown')}
Resistance Behaviors: {', '.join(vignette.get('resistance_behaviors', []))}
Engagement Triggers: {', '.join(vignette.get('engagement_triggers', []))}"""
    
    # Format using template
    nightmare = vignette.get("nightmare", {})
    
    # Build format dictionary for safe substitution
    format_dict = {
        "name": vignette.get("name", "Unknown"),
        "age": vignette.get("age", "Unknown"),
        "gender": vignette.get("gender", "Unknown"),
        "background": vignette.get("background", "Not specified"),
        "nightmare.content": nightmare.get("content", "Not specified"),
        "nightmare.frequency": nightmare.get("frequency", "Unknown"),
        "nightmare.duration": nightmare.get("duration", "Unknown"),
        "nightmare.impact": nightmare.get("impact", "Unknown"),
        "personality_traits": ", ".join(vignette.get("personality_traits", [])),
        "resistance_level": vignette.get("resistance_level", "Unknown"),
        "resistance_behaviors": ", ".join(vignette.get("resistance_behaviors", [])),
        "engagement_triggers": ", ".join(vignette.get("engagement_triggers", [])),
    }
    
    # Use simple string replacement (safer than format())
    result = template
    for key, value in format_dict.items():
        result = result.replace(f"{{{key}}}", str(value))
    
    return result


def get_intro_message(language: str = "en") -> str:
    """Get the session intro message for the specified language.
    
    Args:
        language: Language code ("en" or "de")
        
    Returns:
        Intro message string
    """
    patient_config = load_patient_prompt()
    intro_messages = patient_config.get("intro_messages", {})
    
    if language not in intro_messages:
        language = "en"  # Fallback to English
    
    return intro_messages.get(language, "").strip()


def load_strategy_taxonomy() -> dict[str, Any]:
    """Load the IRT strategy taxonomy for plan classification.
    
    Returns:
        Dictionary containing:
            - strategies: List of strategy definitions with id, name, description, keywords
            - validation: Validation rules (min/max strategies allowed)
            - notes: Clinical rationale for constraints
    """
    return load_yaml(PROMPTS_DIR / "evaluation" / "strategy_taxonomy.yaml")


def load_internal_plan_prompt() -> dict[str, Any]:
    """Load the internal plan generation prompt configuration.
    
    Returns:
        Dictionary containing:
            - system_prompt: Prompt for generating <plan> blocks
            - example_en: English example output
            - example_de: German example output
    """
    return load_yaml(PROMPTS_DIR / "evaluation" / "internal_plan.yaml")
