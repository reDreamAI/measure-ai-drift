"""
Central list of model options for the reDream Thesis stack.

Full menu (choose per role):
- Therapist (sovereign): Scaleway Mistral (router: mistral-nemo-instruct-2407, chat: mistral-small-latest)
- Therapist (benchmark/alt): Groq openai/gpt-oss-120, OpenAI gpt-4o-2024-08-06
- Patient: Groq kimi-k2, Vertex Claude Sonnet 4.5
- Judge: Gemini 3 Pro Preview (fallback: Gemini 2.5 Pro) via GEMINI_API_KEY / G_DEVELOPER_KEY or Vertex SA
"""

# Therapist options
THERAPIST_MODELS = {
    "mistral_sovereign": {
        "router": "mistral-nemo-instruct-2407",
        "chat": "mistral-small-latest",
        "provider": "scaleway",
    },
    "groq_oss": {
        "model": "openai/gpt-oss-120",
        "provider": "groq",
    },
    "openai_gpt4o": {
        "model": "gpt-4o-2024-08-06",
        "provider": "openai",
    },
}

# Patient options
PATIENT_MODELS = {
    "groq_kimi": {"model": "moonshotai/kimi-k2-instruct-0905", "provider": "groq"},
    "vertex_claude": {"model": "claude-sonnet-4.5", "provider": "vertex"},
}

# Judge options
JUDGE_MODELS = {
    "gemini": {"model": "gemini-3-pro-preview", "fallback": "gemini-2.5-pro", "provider": "google-ai"},
}

# Suggested defaults for current stack
DEFAULT_SELECTION = {
    "therapist": "groq_oss",
    "patient": "groq_kimi",
    "judge": "gemini",
}


def model_overview() -> dict:
    """Return a structured overview for logging or debugging."""
    return {
        "therapist": THERAPIST_MODELS,
        "patient": PATIENT_MODELS,
        "judge": JUDGE_MODELS,
        "defaults": DEFAULT_SELECTION,
    }

