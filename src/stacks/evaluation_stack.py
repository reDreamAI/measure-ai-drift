"""Evaluation stack for rescripting-only analysis.

The EvaluationStack bypasses the router and injects the rescripting stage
prompt directly. It generates plan + response pairs from frozen histories.

Supports two modes:
- "fused" (default): Single LLM call where plan conditions the response (CoT-style)
- "chained": Two LLM calls; plan generated first, then injected into response prompt
"""

from __future__ import annotations

import re
from typing import Any

from src.core import (
    Conversation, Stage, get_intro_message, load_stage_prompt, load_yaml,
    load_strategy_taxonomy, build_categories_block,
)
from src.llm.provider import LLMProvider, create_provider

# Match <plan>...</plan> (closed) or <plan>...<blank line> (unclosed fallback)
_PLAN_CLOSED_RE = re.compile(r"<plan>(.*?)</plan>", re.DOTALL | re.IGNORECASE)
# Handles \n\n, \n \n, \n\t\n etc. — models sometimes pad blank lines with whitespace
_PLAN_OPEN_RE = re.compile(r"<plan>(.*?)(?:\s*\n\s*\n|\Z)", re.DOTALL | re.IGNORECASE)
# Fallback: model uses strategy names as tag, e.g. <cognitive_reframe / safety>
_STRATEGY_TAG_RE = re.compile(r"<([a-z_]+(?:\s*/\s*[a-z_]+)*)>", re.IGNORECASE)


class EvaluationStack:
    """Generate rescripting plan + response from frozen histories."""

    def __init__(
        self,
        language: str = "en",
        therapist_provider: LLMProvider | None = None,
        plan_prompt_path: str = "data/prompts/evaluation/internal_plan.yaml",
        mode: str = "fused",
    ) -> None:
        self.language = language
        self.mode = mode
        self.therapist_provider = therapist_provider or create_provider("therapist")

        # Single source of truth: build category list from taxonomy
        taxonomy = load_strategy_taxonomy()
        categories = build_categories_block(taxonomy)

        if mode == "fused":
            fused_path = "data/prompts/evaluation/fused_plan_response.yaml"
            raw = load_yaml(fused_path).get("system_prompt", "")
            self._fused_prompt = raw.replace("{categories_block}", categories)
        else:
            # chained: need both plan prompt and stage prompt
            raw = load_yaml(plan_prompt_path).get("system_prompt", "")
            self._plan_prompt = raw.replace("{categories_block}", categories)
            self._stage_prompt = load_stage_prompt(Stage.REWRITING.value, language)

    def _build_history_context(self, conversation: Conversation) -> str:
        """Build a prompt context from frozen history."""
        intro = get_intro_message(self.language)
        history = conversation.get_history_as_string()
        history_parts = [f"AI: {intro}", history] if history else [f"AI: {intro}"]
        return "\n\nConversation history:\n" + "\n".join(history_parts)

    @staticmethod
    def _parse_plan(output: str) -> tuple[str, str]:
        """Extract <plan> block and remaining response from raw output."""
        match = _PLAN_CLOSED_RE.search(output)
        if not match:
            match = _PLAN_OPEN_RE.search(output)
        if match:
            # Take only the first line of plan content (categories only, no sentences)
            plan_raw = match.group(1).strip().split("\n")[0].strip()
            plan = f"<plan>{plan_raw}</plan>"
            response = output[match.end():].strip()
            return plan, response

        # Fallback: model used strategies as tag name, e.g. <cognitive_reframe / safety>
        from src.evaluation.metrics import VALID_CATEGORIES
        tag_match = _STRATEGY_TAG_RE.search(output)
        if tag_match:
            parts = [p.strip().lower() for p in tag_match.group(1).split("/")]
            if all(p in VALID_CATEGORIES for p in parts):
                plan_raw = " / ".join(parts)
                plan = f"<plan>{plan_raw}</plan>"
                response = output[tag_match.end():].strip()
                response = re.sub(r"^</\w+>\s*", "", response)
                return plan, response

        # Fallback: bare strategy names on first line (no tags at all)
        # Also handles "plan\nstrategy / strategy\n</plan>" (missing < on opening tag)
        lines = output.strip().split("\n")
        first_line = lines[0].strip()
        if first_line.lower() in ("plan", "plan:") and len(lines) > 1:
            first_line = lines[1].strip()
        # Strip any stray tags/quotes
        first_line = re.sub(r"[<>\"\']", "", first_line).strip()
        parts = [p.strip().lower() for p in first_line.split("/")]
        if 1 <= len(parts) <= 2 and all(p in VALID_CATEGORIES for p in parts):
            plan_raw = " / ".join(parts)
            plan = f"<plan>{plan_raw}</plan>"
            rest = "\n".join(output.strip().split("\n")[1:]).strip()
            # Strip trailing </plan> if present
            rest = re.sub(r"</plan>\s*$", "", rest).strip()
            return plan, rest

        return "", output.strip()

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
        return await self._run_chained(frozen_history, temperature)

    async def _run_chained(
        self,
        frozen_history: Conversation,
        temperature: float,
    ) -> tuple[str, str, dict[str, Any], dict[str, Any]]:
        """Two LLM calls: plan generated first, then injected into response prompt."""
        context = self._build_history_context(frozen_history)

        # Step 1: Generate plan
        plan_messages = [
            {"role": "system", "content": self._plan_prompt},
            {"role": "user", "content": context},
        ]
        plan, plan_usage = await self.therapist_provider.generate(
            plan_messages, temperature=temperature
        )
        plan = plan.strip()

        # Step 2: Generate response, conditioned on the plan
        response_messages = [
            {"role": "system", "content": self._stage_prompt
                + f"\n\nYour therapeutic plan for this response: {plan}"},
            {"role": "user", "content": context},
        ]
        response, response_usage = await self.therapist_provider.generate(
            response_messages, temperature=temperature
        )

        return plan, response.strip(), plan_usage, response_usage

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

        plan, response = self._parse_plan(output.strip())
        return plan, response, usage, {}
