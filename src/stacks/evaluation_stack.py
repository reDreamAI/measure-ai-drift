"""Evaluation stack for rescripting-only analysis.

The EvaluationStack bypasses the router and injects the rescripting stage
prompt directly. It generates plan + response pairs from frozen histories.
"""

from __future__ import annotations

from typing import Any

from src.core import Conversation, Stage, get_intro_message, load_stage_prompt, load_yaml
from src.llm.provider import LLMProvider, create_provider


class EvaluationStack:
    """Generate rescripting plan + response from frozen histories."""

    def __init__(
        self,
        language: str = "en",
        therapist_provider: LLMProvider | None = None,
        plan_prompt_path: str = "data/prompts/evaluation/internal_plan.yaml",
    ) -> None:
        self.language = language
        self.therapist_provider = therapist_provider or create_provider("therapist")
        self._plan_prompt = load_yaml(plan_prompt_path).get("system_prompt", "")
        self._stage_prompt = load_stage_prompt(Stage.REWRITING.value, language)

    def _build_history_context(self, conversation: Conversation) -> str:
        """Build a prompt context from frozen history."""
        intro = get_intro_message(self.language)
        history = conversation.get_history_as_string()
        history_parts = [f"AI: {intro}", history] if history else [f"AI: {intro}"]
        return "\n\nConversation history:\n" + "\n".join(history_parts)

    async def run_trial(
        self,
        frozen_history: Conversation,
        temperature: float,
    ) -> tuple[str, str, dict[str, Any], dict[str, Any]]:
        """Run a single rescripting trial.

        Args:
            frozen_history: Conversation up to rewriting stage
            temperature: Sampling temperature

        Returns:
            Tuple of (plan, response, plan_usage, response_usage)
        """
        context = self._build_history_context(frozen_history)

        # Generate plan
        plan_messages = [
            {"role": "system", "content": self._plan_prompt},
            {"role": "user", "content": context},
        ]
        plan, plan_usage = await self.therapist_provider.generate(
            plan_messages, temperature=temperature
        )

        # Generate response
        response_messages = [
            {"role": "system", "content": self._stage_prompt},
            {"role": "user", "content": context},
        ]
        response, response_usage = await self.therapist_provider.generate(
            response_messages, temperature=temperature
        )

        return plan.strip(), response.strip(), plan_usage, response_usage
