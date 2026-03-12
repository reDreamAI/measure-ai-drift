"""Multi-trial sampler for rescripting stability experiments.

Orchestrates running multiple trials against frozen histories and
collecting results for metric computation.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from src.core import Conversation
from src.stacks.evaluation_stack import EvaluationStack


@dataclass
class TrialResult:
    """Single evaluation trial output."""

    temperature: float
    plan: str
    response: str
    plan_usage: dict[str, Any] = field(default_factory=dict)
    response_usage: dict[str, Any] = field(default_factory=dict)


class Sampler:
    """Run multiple rescripting trials for stability analysis.

    Wraps EvaluationStack to handle multi-trial orchestration,
    including temperature sweeps and parallel execution.

    Example:
        >>> sampler = Sampler(language="en")
        >>> results = await sampler.run(frozen_history, n_trials=10, temperature=0.7)
        >>> # Or sweep multiple temperatures:
        >>> results = await sampler.sweep(frozen_history, temperatures=[0.3, 0.7, 1.0], trials_per=5)
    """

    def __init__(
        self,
        language: str = "en",
        stack: EvaluationStack | None = None,
        mode: str = "split",
    ) -> None:
        self.language = language
        self._stack = stack or EvaluationStack(language=language, mode=mode)

    async def run_single(
        self,
        frozen_history: Conversation,
        temperature: float,
        max_retries: int = 1,
    ) -> TrialResult:
        """Run a single trial with retry on transient errors (e.g. 429)."""
        for attempt in range(max_retries + 1):
            try:
                plan, response, plan_usage, response_usage = (
                    await self._stack.run_trial(frozen_history, temperature)
                )
                return TrialResult(
                    temperature=temperature,
                    plan=plan,
                    response=response,
                    plan_usage=plan_usage,
                    response_usage=response_usage,
                )
            except Exception as e:
                if attempt < max_retries and ("429" in str(e) or "rate" in str(e).lower()):
                    wait = 2 ** attempt * 5
                    print(f"  ↻ Rate limited, retrying in {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    raise

    async def run(
        self,
        frozen_history: Conversation,
        n_trials: int,
        temperature: float,
        parallel: bool = False,
    ) -> list[TrialResult]:
        """Run multiple trials at a single temperature.

        Args:
            frozen_history: Conversation history to use as input
            n_trials: Number of trials to run
            temperature: Sampling temperature
            parallel: If True, run trials concurrently

        Returns:
            List of TrialResult objects
        """
        if parallel:
            tasks = [
                self.run_single(frozen_history, temperature)
                for _ in range(n_trials)
            ]
            return await asyncio.gather(*tasks)

        results = []
        for _ in range(n_trials):
            results.append(await self.run_single(frozen_history, temperature))
        return results

    async def sweep(
        self,
        frozen_history: Conversation,
        temperatures: list[float],
        trials_per: int,
        parallel: bool = False,
    ) -> dict[float, list[TrialResult]]:
        """Run trials across multiple temperatures.

        Args:
            frozen_history: Conversation history to use as input
            temperatures: List of temperatures to test
            trials_per: Number of trials per temperature
            parallel: If True, run trials concurrently within each temperature

        Returns:
            Dict mapping temperature -> list of TrialResults
        """
        results = {}
        for temp in temperatures:
            results[temp] = await self.run(
                frozen_history, trials_per, temp, parallel=parallel
            )
        return results
