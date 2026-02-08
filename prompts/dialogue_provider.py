"""Custom Promptfoo provider that runs a full dialogue via GenerationStack.

Returns the complete conversation as a JSON string for dialogue-level
evaluation. Uses the exact same code path as:

    python -m src generate --vignette <name> --max-turns <n>

Promptfoo calls call_api(prompt, options, context) and expects
a dict with 'output' (str) back. The output is a JSON object
containing messages, stages visited, completion status, etc.
JavaScript assertions in promptfoo-dialogue.yaml parse this JSON
to evaluate dialogue quality.
"""

import asyncio
import json
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

from src.stacks import GenerationStack


def call_api(prompt, options, context):
    """Promptfoo entry point. Called once per test case.

    Args:
        prompt: The rendered prompt string (ignored — we run the full stack)
        options: Provider config from promptfoo-dialogue.yaml
        context: Contains 'vars' from the test case

    Returns:
        dict with 'output' (JSON string of the full dialogue)
    """
    test_vars = context.get("vars", {})
    vignette_name = test_vars.get("vignette_name", "cooperative")
    language = test_vars.get("language", "en")
    max_turns = int(test_vars.get("max_turns", 16))

    try:
        result = asyncio.run(
            _run_dialogue(vignette_name, language, max_turns)
        )
        return {
            "output": json.dumps(result),
            "tokenUsage": {
                "total": result.get("total_tokens", 0),
            },
        }
    except Exception as e:
        return {"error": str(e)}


async def _run_dialogue(vignette_name, language, max_turns):
    """Run a full dialogue via GenerationStack (same as CLI).

    Returns a dict with messages, stages, and metadata that
    JavaScript assertions can parse and evaluate.
    """
    stack = GenerationStack.from_vignette(
        vignette_name=vignette_name,
        language=language,
        max_turns=max_turns,
    )

    conversation = await stack.run(verbose=False)

    messages = []
    for msg in conversation.messages:
        messages.append({
            "role": msg.role,
            "content": msg.content,
            "stage": msg.stage,
        })

    return {
        "messages": messages,
        "stages_visited": list(dict.fromkeys(conversation.stages)),
        "completed": stack._is_complete,
        "total_turns": stack._turn_count,
        "vignette": vignette_name,
    }
