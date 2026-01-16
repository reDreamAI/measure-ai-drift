#!/usr/bin/env python3
"""
Key sanity checks for all providers (Scaleway/Mistral, Groq, OpenAI, Gemini).

Runs lightweight model-list calls to confirm credentials without full sims.
Outputs a compact, colorized table of status/results.
"""

import asyncio
import os
import sys
from typing import Tuple

import rich
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.config import scaleway_config, groq_config, openai_config, judge_config

console = Console()


async def check_mistral_scaleway() -> Tuple[str, str]:
    if not scaleway_config.api_key:
        return ("missing", "SCALEWAY_API_KEY not set")
    try:
        os.environ["OPENAI_API_BASE"] = scaleway_config.server_url
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=scaleway_config.api_key, base_url=scaleway_config.server_url)
        resp = await client.models.list()
        names = [m.id for m in getattr(resp, "data", [])] if hasattr(resp, "data") else []
        return ("ok", f"{', '.join(names[:3]) or 'no models'}")
    except Exception as e:
        return ("fail", str(e))


async def check_groq() -> Tuple[str, str]:
    if not groq_config.api_key:
        return ("missing", "GROQ_API_KEY not set")
    try:
        from groq import AsyncGroq

        client = AsyncGroq(api_key=groq_config.api_key)
        resp = await client.models.list()
        names = [m.id for m in getattr(resp, "data", [])] if hasattr(resp, "data") else []
        return ("ok", f"{', '.join(names[:3]) or 'no models'}")
    except Exception as e:
        return ("fail", str(e))


async def check_openai() -> Tuple[str, str]:
    if not openai_config.api_key:
        return ("missing", "OPENAI_API_KEY not set")
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=openai_config.api_key)
        resp = await client.models.list()
        names = [m.id for m in getattr(resp, "data", [])] if hasattr(resp, "data") else []
        return ("ok", f"{', '.join(names[:3]) or 'no models'}")
    except Exception as e:
        return ("fail", str(e))


async def check_gemini() -> Tuple[str, str]:
    key = judge_config.developer_key
    if not key:
        return ("missing", "GEMINI_API_KEY / G_DEVELOPER_KEY / GOOGLE_API_KEY not set")
    try:
        import google.generativeai as genai

        genai.configure(api_key=key)
        models = [m.name for m in genai.list_models()]
        return ("ok", f"{', '.join(models[:3]) or 'no models'}")
    except Exception as e:
        return ("fail", str(e))


async def main():
    tasks = [
        ("Scaleway/Mistral", check_mistral_scaleway()),
        ("Groq", check_groq()),
        ("OpenAI", check_openai()),
        ("Gemini", check_gemini()),
    ]

    results = await asyncio.gather(*[t[1] for t in tasks])

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Provider", style="bold")
    table.add_column("Status", style="bold")
    table.add_column("Details")

    for (name, _), (status, detail) in zip(tasks, results):
        if status == "ok":
            status_text = "[green]OK[/green]"
        elif status == "missing":
            status_text = "[yellow]MISSING[/yellow]"
        else:
            status_text = "[red]FAIL[/red]"
        table.add_row(name, status_text, detail)

    console.print(Panel(table, title="Key Check", border_style="cyan"))


if __name__ == "__main__":
    # Ensure we run from project root
    sys.path.append(os.path.dirname(__file__))
    asyncio.run(main())

