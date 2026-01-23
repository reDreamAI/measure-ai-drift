"""Evaluation stack for rescripting-only analysis.

The EvaluationStack bypasses the router and injects the rescripting stage
prompt directly. It is used with frozen histories to generate:
1) An internal <plan>
2) A rescripting response
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.core import Conversation, Stage, get_intro_message, load_stage_prompt, load_yaml
from src.llm.provider import LLMProvider, create_provider


@dataclass
class TrialResult:
    """Single evaluation trial output."""

    temperature: float
    plan: str
    response: str
    plan_usage: dict[str, Any]
    response_usage: dict[str, Any]


class EvaluationStack:
    """Run rescripting-only trials against frozen histories."""

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

    async def _generate_plan(
        self,
        frozen_history: Conversation,
        temperature: float,
    ) -> tuple[str, dict[str, Any]]:
        messages = [
            {"role": "system", "content": self._plan_prompt},
            {"role": "user", "content": self._build_history_context(frozen_history)},
        ]
        return await self.therapist_provider.generate(
            messages,
            temperature=temperature,
        )

    async def _generate_response(
        self,
        frozen_history: Conversation,
        temperature: float,
    ) -> tuple[str, dict[str, Any]]:
        messages = [
            {"role": "system", "content": self._stage_prompt},
            {"role": "user", "content": self._build_history_context(frozen_history)},
        ]
        return await self.therapist_provider.generate(
            messages,
            temperature=temperature,
        )

    async def run_trial(
        self,
        frozen_history: Conversation,
        temperature: float,
    ) -> TrialResult:
        """Run a single rescripting trial."""
        plan, plan_usage = await self._generate_plan(frozen_history, temperature)
        response, response_usage = await self._generate_response(frozen_history, temperature)
        return TrialResult(
            temperature=temperature,
            plan=plan.strip(),
            response=response.strip(),
            plan_usage=plan_usage,
            response_usage=response_usage,
        )

    async def run_trials(
        self,
        frozen_history: Conversation,
        n_trials: int,
        temperature: float,
    ) -> list[TrialResult]:
        """Run multiple trials for a single temperature."""
        results: list[TrialResult] = []
        for _ in range(n_trials):
            results.append(await self.run_trial(frozen_history, temperature))
        return results
