#!/usr/bin/env python3
"""
API key sanity checks for all configured providers.

Tests provider connectivity and API key validity using the new
src.llm.provider system.

Usage:
    python tests/key_test.py
    # or
    python -m src keys
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Tuple

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Load .env file from project root
_PROJECT_ROOT = Path(__file__).parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"
if _ENV_FILE.exists():
    load_dotenv(_ENV_FILE)
else:
    load_dotenv()

from src.llm.provider import load_config, create_provider

console = Console()


async def check_provider(role: str, config: dict) -> Tuple[str, str, str]:
    """Test a single provider by making a minimal API call.
    
    Args:
        role: Role name (e.g., 'patient', 'therapist', 'router')
        config: Full config dictionary
        
    Returns:
        Tuple of (role, status, details)
    """
    try:
        # Get provider info
        role_config = config['roles'][role]
        use_key = role_config.get('use', '')
        
        if role in config.get('model_options', {}):
            model_def = config['model_options'][role].get(use_key, {})
            provider_name = model_def.get('provider', 'unknown')
            model_name = model_def.get('model', 'unknown')
        else:
            provider_name = 'unknown'
            model_name = 'unknown'
        
        # Create provider (this checks API key)
        provider = create_provider(role)
        
        # Try a minimal test call
        test_messages = [
            {"role": "system", "content": "Test"},
            {"role": "user", "content": "Say OK"}
        ]
        
        response, usage = await provider.generate(
            test_messages,
            max_tokens=5,
            temperature=0.0
        )
        
        tokens = usage.get('total_tokens', 0)
        return (
            role,
            "[green]✓ OK[/green]",
            f"{provider_name}/{model_name} ({tokens} tokens)"
        )
        
    except ValueError as e:
        error_msg = str(e)
        if "API key" in error_msg or "api_key" in error_msg.lower():
            return (role, "[yellow]⚠ NO KEY[/yellow]", error_msg[:80])
        return (role, "[red]✗ ERROR[/red]", error_msg[:80])
    except ImportError as e:
        return (role, "[red]✗ MISSING PACKAGE[/red]", str(e)[:80])
    except Exception as e:
        return (role, "[red]✗ ERROR[/red]", str(e)[:80])


async def main():
    """Run API key checks for all configured providers."""
    console.print(Panel(
        "Testing API Key Configuration\n"
        "This will make minimal API calls to verify connectivity",
        title="API Key Checker",
        border_style="cyan"
    ))
    
    try:
        # Load configuration
        config = load_config()
        roles = list(config.get('roles', {}).keys())
        
        console.print(f"\n[cyan]→[/cyan] Testing {len(roles)} configured roles...\n")
        
        # Test each role in parallel
        results = await asyncio.gather(*[
            check_provider(role, config) for role in roles
        ], return_exceptions=True)
        
        # Display results table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Role", style="bold cyan")
        table.add_column("Status", style="bold")
        table.add_column("Details")
        
        for result in results:
            if isinstance(result, Exception):
                table.add_row("error", "[red]✗ EXCEPTION[/red]", str(result)[:80])
            else:
                table.add_row(*result)
        
        console.print(table)
        
        # Show environment variables status
        console.print("\n[bold]Environment Variables:[/bold]")
        env_vars = [
            'GROQ_API_KEY',
            'OPENAI_API_KEY',
            'OPENROUTER_API_KEY',
            'SCALEWAY_API_KEY',
            'GEMINI_API_KEY',
            'G_DEVELOPER_KEY',
        ]
        
        for var in env_vars:
            is_set = bool(os.environ.get(var))
            status = "✓ Set" if is_set else "✗ Not set"
            color = "green" if is_set else "dim"
            console.print(f"  {var:25} [{color}]{status}[/{color}]")
        
        console.print("\n[dim]Tip: Set API keys in your environment or .env file[/dim]")
        
    except FileNotFoundError as e:
        console.print(f"[red]✗ Error:[/red] Config file not found: {e}")
        return 1
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


