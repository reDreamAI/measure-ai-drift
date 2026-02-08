"""Command-line interface for measure-ai-drift.

Provides commands to:
- Generate synthetic therapy dialogues
- Run evaluation experiments
- Check API keys
- List available resources
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Find project root (where .env file should be)
# Works regardless of where the script is called from
_PROJECT_ROOT = Path(__file__).parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"

# Load environment variables from .env file
# Try project root first, then current directory
if _ENV_FILE.exists():
    load_dotenv(_ENV_FILE)
else:
    load_dotenv()  # Falls back to cwd

console = Console()


def cmd_generate(args: argparse.Namespace) -> int:
    """Run the Generation Stack to create synthetic dialogues."""
    from src.stacks import GenerationStack
    from datetime import datetime

    # Auto-generate output filename if not provided
    output_path = args.output
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/synthetic/dialogues/dialogue_{args.vignette}_{timestamp}.json"

    freeze_info = " + frozen history" if args.freeze else ""
    console.print(Panel(
        f"[bold]Generation Stack[/bold]\n"
        f"Vignette: {args.vignette}\n"
        f"Language: {args.language}\n"
        f"Max turns: {args.max_turns}\n"
        f"Output: {output_path}{freeze_info}",
        title="Starting Dialogue Generation",
        border_style="blue"
    ))

    async def _run():
        try:
            stack = GenerationStack.from_vignette(
                vignette_name=args.vignette,
                language=args.language,
                max_turns=args.max_turns,
            )

            conversation = await stack.run(verbose=args.verbose)

            # Always save (either to specified path or auto-generated)
            save_path = Path(output_path)
            stack.save_dialogue(save_path, include_metadata=True)
            console.print(f"\n[green]✓[/green] Dialogue saved to: {save_path}")

            # Optionally create frozen history
            if args.freeze:
                frozen_dir = Path("data/synthetic/frozen_histories")
                frozen_path = stack.save_frozen_history(frozen_dir)
                console.print(f"[green]✓[/green] Frozen history saved to: {frozen_path}")

            # Print summary
            summary = stack.get_conversation_summary()
            table = Table(title="Session Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            for key, value in summary.items():
                table.add_row(key, str(value))

            console.print(table)

            return 0

        except FileNotFoundError as e:
            console.print(f"[red]✗ Error:[/red] {e}")
            console.print("\nUse 'python -m src list-vignettes' to see available vignettes")
            return 1
        except Exception as e:
            console.print(f"[red]✗ Error:[/red] {e}")
            import traceback
            if args.verbose:
                traceback.print_exc()
            return 1

    return asyncio.run(_run())


def cmd_evaluate(args: argparse.Namespace) -> int:
    """Run the Evaluation Stack for multi-trial experiments."""
    from src.core import Conversation
    from src.evaluation import (
        ExperimentRun,
        extract_plan_strategies,
        compute_validity_rate,
        compute_pairwise_jaccard,
    )
    from src.llm.provider import load_config
    import re

    # Infer vignette from filename if not provided
    vignette = getattr(args, 'vignette', None)
    if not vignette:
        match = re.search(r'dialogue_(\w+)_\d+', Path(args.history).stem)
        vignette = match.group(1) if match else "unknown"

    # Get model name from config
    config = load_config()
    model_key = config.get("roles", {}).get("therapist", {}).get("use", "unknown")

    console.print(Panel(
        f"[bold]Evaluation Experiment[/bold]\n"
        f"History: {args.history}\n"
        f"Model: {model_key}\n"
        f"Vignette: {vignette}\n"
        f"Trials: {args.trials}\n"
        f"Temperature: {args.temperature}",
        title="Starting Evaluation",
        border_style="green"
    ))

    async def _run():
        try:
            # Load frozen history
            with open(args.history, 'r') as f:
                history_data = json.load(f)

            if 'messages' not in history_data:
                console.print("[yellow]Warning:[/yellow] Expected conversation format with 'messages' key")
                return 1

            frozen_history = Conversation.from_dict(history_data)
            console.print(f"[cyan]→[/cyan] Loaded history: {len(frozen_history.messages)} messages")

            # Create and run experiment
            experiment = ExperimentRun(
                frozen_history=frozen_history,
                model_name=model_key,
                vignette_name=vignette,
            ).setup()

            with console.status(f"[bold green]Running {args.trials} trials..."):
                results = await experiment.run(
                    n_trials=args.trials,
                    temperature=args.temperature,
                    language=args.language,
                )

            console.print(f"[green]✓[/green] Completed {len(results)} trials")

            # Compute metrics for display
            strategy_sets = [extract_plan_strategies(r.plan) for r in results]
            validity = compute_validity_rate(strategy_sets)
            jaccard_all = compute_pairwise_jaccard(strategy_sets, only_valid=False)
            jaccard_valid = compute_pairwise_jaccard(strategy_sets, only_valid=True)

            # Display metrics
            table = Table(title="Evaluation Metrics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Trials", str(len(results)))
            table.add_row("Temperature", f"{args.temperature:.2f}")
            table.add_row("Validity Rate", f"{validity:.1%}")
            table.add_row("Jaccard (all)", f"{jaccard_all:.3f}")
            table.add_row("Jaccard (valid only)", f"{jaccard_valid:.3f}")

            console.print(table)

            # Show strategy distribution
            strategy_counts: dict[str, int] = {}
            for strategies in strategy_sets:
                for s in strategies:
                    strategy_counts[s] = strategy_counts.get(s, 0) + 1
            if strategy_counts:
                sorted_strategies = sorted(strategy_counts.items(), key=lambda x: -x[1])
                strategies_str = ", ".join(f"{s}: {c}/{len(results)}" for s, c in sorted_strategies)
                console.print(f"\n[cyan]Strategies:[/cyan] {strategies_str}")

            console.print(f"\n[green]✓[/green] Experiment saved to: {experiment.path}")

            return 0

        except FileNotFoundError:
            console.print(f"[red]✗ Error:[/red] History file not found: {args.history}")
            return 1
        except Exception as e:
            console.print(f"[red]✗ Error:[/red] {e}")
            import traceback
            if args.verbose:
                traceback.print_exc()
            return 1

    return asyncio.run(_run())


def cmd_keys(args: argparse.Namespace) -> int:
    """Check API key configuration and test provider connections."""
    from src.llm.provider import load_config, create_provider
    
    console.print(Panel("Testing API Key Configuration", border_style="cyan"))
    
    async def test_provider(role: str, config: dict) -> tuple[str, str, str]:
        """Test a single provider."""
        try:
            provider = create_provider(role)
            
            # Try a minimal generation call
            test_messages = [
                {"role": "system", "content": "You are a test assistant."},
                {"role": "user", "content": "Say 'OK' if you can read this."}
            ]
            
            response, usage = await provider.generate(test_messages, max_tokens=10)
            
            return (
                role,
                "[green]✓ OK[/green]",
                f"{provider.config.provider}/{provider.config.model} ({usage.get('total_tokens', 0)} tokens)"
            )
            
        except ValueError as e:
            if "API key" in str(e):
                return (role, "[yellow]⚠ NO KEY[/yellow]", str(e))
            return (role, "[red]✗ ERROR[/red]", str(e))
        except Exception as e:
            return (role, "[red]✗ ERROR[/red]", str(e)[:80])
    
    async def _run():
        try:
            config = load_config()
            roles = list(config.get('roles', {}).keys())
            
            console.print(f"Testing {len(roles)} configured roles...\n")
            
            # Test each role
            results = await asyncio.gather(*[
                test_provider(role, config) for role in roles
            ], return_exceptions=True)
            
            # Display results
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Role", style="bold cyan")
            table.add_column("Status", style="bold")
            table.add_column("Details")
            
            for result in results:
                if isinstance(result, Exception):
                    table.add_row("error", "[red]✗ ERROR[/red]", str(result))
                else:
                    table.add_row(*result)
            
            console.print(table)
            
            # Check environment variables
            console.print("\n[bold]Environment Variables:[/bold]")
            env_vars = ['GROQ_API_KEY', 'OPENAI_API_KEY', 'SCALEWAY_API_KEY', 'GOOGLE_AI_STUDIO_API_KEY', 'OPENROUTER_API_KEY']
            for var in env_vars:
                status = "✓ Set" if os.environ.get(var) else "✗ Not set"
                color = "green" if os.environ.get(var) else "yellow"
                console.print(f"  {var}: [{color}]{status}[/{color}]")
            
            return 0
            
        except Exception as e:
            console.print(f"[red]✗ Error:[/red] {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    if args.quick:
        # Quick check without API calls
        from src.llm.provider import load_config
        
        config = load_config()
        console.print("[green]✓[/green] Config file loaded successfully")
        
        table = Table(title="Configured Roles")
        table.add_column("Role", style="cyan")
        table.add_column("Provider", style="green")
        table.add_column("Model")
        
        for role, role_config in config.get('roles', {}).items():
            use_key = role_config.get('use', 'unknown')
            if role in config.get('model_options', {}):
                model_def = config['model_options'][role].get(use_key, {})
                provider = model_def.get('provider', 'unknown')
                model = model_def.get('model', 'unknown')
            else:
                provider = 'unknown'
                model = 'unknown'
            
            table.add_row(role, provider, model)
        
        console.print(table)
        return 0
    
    return asyncio.run(_run())


def cmd_list_vignettes(args: argparse.Namespace) -> int:
    """List available patient vignettes."""
    from src.core import list_vignettes, load_vignette
    
    vignettes = list_vignettes()
    
    if not vignettes:
        console.print("[yellow]No vignettes found[/yellow]")
        return 1
    
    table = Table(title=f"Available Vignettes ({len(vignettes)})")
    table.add_column("Name", style="cyan")
    table.add_column("Patient", style="green")
    table.add_column("Resistance", style="yellow")
    table.add_column("Traits")
    
    for vignette_name in sorted(vignettes):
        try:
            data = load_vignette(vignette_name)
            name = data.get('name', 'Unknown')
            resistance = data.get('resistance_level', 'Unknown')
            traits = ', '.join(data.get('personality_traits', [])[:3])
            
            table.add_row(vignette_name, name, resistance, traits)
        except Exception as e:
            table.add_row(vignette_name, "[red]Error[/red]", str(e)[:20], "")
    
    console.print(table)
    return 0


def cmd_list_models(args: argparse.Namespace) -> int:
    """List configured models and active selections."""
    from src.llm.provider import load_config

    config = load_config()
    roles = config.get("roles", {})
    model_options = config.get("model_options", {})

    # Active roles table
    table = Table(title="Active Model Configuration")
    table.add_column("Role", style="bold cyan")
    table.add_column("Selection", style="green")
    table.add_column("Temperature", style="yellow")
    table.add_column("Max Tokens", style="blue")

    for role, role_config in roles.items():
        table.add_row(
            role,
            role_config.get("use", "direct"),
            f"{role_config.get('temperature', 0.0):.1f}",
            str(role_config.get("max_tokens", 1024))
        )

    console.print(table)

    # Model options per role
    if args.verbose:
        for role in ['patient', 'therapist', 'router', 'judge']:
            if role not in model_options:
                continue

            console.print(f"\n[bold]{role.upper()} Options:[/bold]")
            active_key = roles.get(role, {}).get("use", "")

            for option_name, option_config in model_options[role].items():
                provider = option_config.get('provider', 'unknown')
                model = option_config.get('model', 'unknown')
                notes = option_config.get('notes', '')

                active = " [green]← ACTIVE[/green]" if active_key == option_name else ""
                console.print(f"  • {option_name}: {provider}/{model}{active}")
                if notes:
                    console.print(f"    {notes}")

    return 0


def cmd_test_setup(args: argparse.Namespace) -> int:
    """Run setup verification tests (like old test_basic.py)."""
    import subprocess
    
    # Determine mode
    mode = "full" if args.full else "quick"
    
    console.print(Panel(
        f"[bold]Running Setup Tests[/bold]\n"
        f"Mode: {mode}\n\n"
        "This will verify your project setup similar to old test_basic.py",
        title="Test Setup",
        border_style="blue"
    ))
    
    # Run the test script
    cmd = [sys.executable, "tests/test_setup.py", f"--{mode}"]
    result = subprocess.run(cmd)
    
    return result.returncode


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='python -m src',
        description='Measure AI Drift - Therapy Simulation & Evaluation'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate synthetic therapy dialogues')
    gen_parser.add_argument('--vignette', '-v', default='cooperative', help='Vignette name (default: cooperative)')
    gen_parser.add_argument('--language', '-l', default='en', choices=['en', 'de'], help='Session language')
    gen_parser.add_argument('--max-turns', '-t', type=int, default=20, help='Maximum dialogue turns (default: 20)')
    gen_parser.add_argument('--output', '-o', help='Output file path (JSON, default: auto-generated in data/synthetic/dialogues/)')
    gen_parser.add_argument('--freeze', '-f', action='store_true', help='Also create frozen history at REWRITING stage')
    gen_parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    
    # Evaluate command
    eval_parser = subparsers.add_parser('evaluate', help='Run evaluation experiments')
    eval_parser.add_argument('--history', '-i', required=True, help='Path to frozen history JSON')
    eval_parser.add_argument('--trials', '-n', type=int, default=10, help='Number of trials')
    eval_parser.add_argument('--temperature', '-t', type=float, default=0.7, help='Sampling temperature')
    eval_parser.add_argument('--language', '-l', default='en', choices=['en', 'de'], help='Session language')
    eval_parser.add_argument('--vignette', '-v', help='Vignette name (auto-detected from filename if omitted)')
    eval_parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    
    # Keys command
    keys_parser = subparsers.add_parser('keys', help='Check API key configuration')
    keys_parser.add_argument('--quick', '-q', action='store_true', help='Quick check without API calls')
    
    # List commands
    subparsers.add_parser('list-vignettes', help='List available patient vignettes')
    
    models_parser = subparsers.add_parser('list-models', help='Show model configuration')
    models_parser.add_argument('--verbose', '-v', action='store_true', help='Show all model options')
    
    # Test setup command
    test_parser = subparsers.add_parser('test-setup', help='Verify project setup (like old test_basic.py)')
    test_parser.add_argument('--full', action='store_true', help='Include API call tests')
    test_parser.add_argument('--quick', action='store_true', help='Skip API call tests (default)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Dispatch to command handler
    commands = {
        'generate': cmd_generate,
        'evaluate': cmd_evaluate,
        'keys': cmd_keys,
        'list-vignettes': cmd_list_vignettes,
        'list-models': cmd_list_models,
        'test-setup': cmd_test_setup,
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        console.print(f"[red]Unknown command:[/red] {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
