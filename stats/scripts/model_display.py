"""Shared model display names and colors for all figures."""

# Internal name -> display name for figures and tables
MODEL_NAMES = {
    # Mistral EU-sovereign
    "mistral_small4": "Mistral Small 4 (119B)",
    "mistral_large": "Mistral Large 3 (675B)",
    "mistral_small32": "Mistral Small 3.2 (24B)",
    # Qwen family
    "qwen35_122b": "Qwen 3.5 122B",
    "qwen35_397b": "Qwen 3.5 397B",
    "qwen35_27b": "Qwen 3.5 27B",
    # Dense comparators
    "olmo3_32b": "OLMo 3.1 32B",
    "llama70b": "Llama 3.3 70B",
    # Proprietary
    "gpt54": "GPT-5.4",
    "sonnet46": "Claude Sonnet 4.6",
    # Test
    "llama70b_test": "Llama 70B (test)",
    "gpt_oss_test": "GPT-oss 120B (test)",
}

MODEL_COLORS = {
    # Mistral EU-sovereign (reds)
    "mistral_small4": "#e63946",
    "mistral_large": "#9b2226",
    "mistral_small32": "#d4756b",
    # Qwen family (yellows/ambers)
    "qwen35_122b": "#e9c46a",
    "qwen35_397b": "#c8961e",
    "qwen35_27b": "#f4d08f",
    # Dense comparators
    "olmo3_32b": "#f4a261",
    "llama70b": "#2a9d8f",
    # Proprietary ceiling
    "gpt54": "#457b9d",
    "sonnet46": "#6a0dad",
    # Test
    "llama70b_test": "#a8dadc",
    "gpt_oss_test": "#6d6875",
}


def display_name(internal_name: str) -> str:
    """Get display name for a model, fallback to internal name."""
    return MODEL_NAMES.get(internal_name, internal_name)
