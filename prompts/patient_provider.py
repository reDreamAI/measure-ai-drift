"""Custom Promptfoo provider that uses the real PatientAgent pipeline.

This provider calls the exact same code path as the CLI:
- Loads vignettes from data/prompts/patients/vignettes/*.json
- Builds the system prompt via PatientAgent.get_system_prompt()
- Uses the LLM provider configured in src/config/models.yaml
- Inverts roles via PatientAgent.format_messages()

Promptfoo calls call_api(prompt, options, context) and expects
a dict with 'output' (str) back.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env before importing anything that reads env vars
from dotenv import load_dotenv
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    load_dotenv(env_file)

from src.agents.patient import PatientAgent
from src.core.config_loader import get_intro_message


def call_api(prompt, options, context):
    """Promptfoo entry point. Called once per test case.

    Args:
        prompt: The rendered prompt string (we ignore this since we
                build our own via PatientAgent)
        options: Provider config from promptfoo.yaml
        context: Contains 'vars' from the test case

    Returns:
        dict with 'output' (str) and optionally 'tokenUsage'
    """
    test_vars = context.get("vars", {})
    vignette_name = test_vars.get("vignette_name", "cooperative")
    therapist_message = test_vars.get("therapist_message", "Tell me about your nightmare.")
    language = test_vars.get("language", "en")

    try:
        response, usage = asyncio.run(
            _generate_patient_response(vignette_name, therapist_message, language)
        )
        return {
            "output": response,
            "tokenUsage": {
                "total": usage.get("total_tokens", 0),
                "prompt": usage.get("prompt_tokens", 0),
                "completion": usage.get("completion_tokens", 0),
            },
        }
    except Exception as e:
        return {"error": str(e)}


async def _generate_patient_response(
    vignette_name: str,
    therapist_message: str,
    language: str = "en",
) -> tuple:
    """Run the real PatientAgent pipeline for a single turn.

    Creates a PatientAgent from the vignette, builds the message
    history with the therapist's intro + the test message, and
    returns the patient's response.
    """
    patient = PatientAgent.from_vignette(vignette_name, language=language)

    # Build messages the same way the generation stack does:
    # system prompt + intro (as user) + therapist message (as user)
    messages = patient.format_messages(user_message=therapist_message)

    # Call the LLM through the existing provider
    response, usage = await patient.provider.generate(messages)
    return response, usage
