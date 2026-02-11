"""Evaluation stack for rescripting-only analysis.

The EvaluationStack bypasses the router and injects the rescripting stage
prompt directly. It generates plan + response pairs from frozen histories.

Supports two modes:
- "split" (default): Two separate LLM calls for plan and response (independent)
- "fused": Single LLM call where plan conditions the response (CoT-style)
"""

from __future__ import annotations

import re
from typing import Any

from src.core import Conversation, Stage, get_intro_message, load_stage_prompt, load_yaml
from src.llm.provider import LLMProvider, create_provider

# Match <plan>...</plan> (closed) or <plan>...\n\n (unclosed, ends at first blank line)
_PLAN_CLOSED_RE = re.compile(r"<plan>(.*?)</plan>", re.DOTALL | re.IGNORECASE)
_PLAN_OPEN_RE = re.compile(r"<plan>(.*?)(?:\n\n|\Z)", re.DOTALL | re.IGNORECASE)


class EvaluationStack:
    """Generate rescripting plan + response from frozen histories."""

    def __init__(
        self,
        language: str = "en",
        therapist_provider: LLMProvider | None = None,
        plan_prompt_path: str = "data/prompts/evaluation/internal_plan.yaml",
        mode: str = "split",
    ) -> None:
        self.language = language
        self.mode = mode
        self.therapist_provider = therapist_provider or create_provider("therapist")

        if mode == "fused":
            fused_path = "data/prompts/evaluation/fused_plan_response.yaml"
            self._fused_prompt = load_yaml(fused_path).get("system_prompt", "")
        else:
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
        if self.mode == "fused":
            return await self._run_fused(frozen_history, temperature)
        return await self._run_split(frozen_history, temperature)

    async def _run_split(
        self,
        frozen_history: Conversation,
        temperature: float,
    ) -> tuple[str, str, dict[str, Any], dict[str, Any]]:
        """Two separate LLM calls: plan and response are independent."""
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

    async def _run_fused(
        self,
        frozen_history: Conversation,
        temperature: float,
    ) -> tuple[str, str, dict[str, Any], dict[str, Any]]:
        """Single LLM call: plan conditions the response (CoT-style)."""
        context = self._build_history_context(frozen_history)

        messages = [
            {"role": "system", "content": self._fused_prompt},
            {"role": "user", "content": context},
        ]
        output, usage = await self.therapist_provider.generate(
            messages, temperature=temperature
        )
        output = output.strip()

        # Parse: extract <plan> block, everything after is the response
        match = _PLAN_CLOSED_RE.search(output)
        if not match:
            match = _PLAN_OPEN_RE.search(output)
        if match:
            plan = f"<plan>{match.group(1).strip()}</plan>"
            response = output[match.end():].strip()
        else:
            plan = ""
            response = output

        return plan, response, usage, {}
