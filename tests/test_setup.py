#!/usr/bin/env python3
"""
Basic setup verification script - similar to old test_basic.py

Tests:
- Module imports
- Configuration loading
- API key availability
- Provider instantiation
- Quick LLM connectivity (optional)

Usage:
    python tests/test_setup.py
    python tests/test_setup.py --quick    # Skip API calls
    python tests/test_setup.py --full     # Include API calls
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent to path
_PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Load .env file from project root
_ENV_FILE = _PROJECT_ROOT / ".env"
if _ENV_FILE.exists():
    load_dotenv(_ENV_FILE)
else:
    load_dotenv()

console = Console()


def test_imports():
    """Test that all core modules can be imported."""
    console.print("\n[cyan]Test 1: Module Imports[/cyan]")
    
    try:
        # Core modules
        from src.core import Stage, Language, Message, Conversation
        from src.core import load_vignette, load_stage_prompt, load_routing_prompt
        
        # Agent modules
        from src.agents import BaseAgent, PatientAgent, TherapistAgent, RouterAgent
        
        # Stack modules
        from src.stacks import GenerationStack, EvaluationStack
        
        # LLM provider
        from src.llm.provider import LLMProvider, create_provider, load_config
        
        # Evaluation
        from src.evaluation import compute_pairwise_jaccard, compute_validity_rate
        
        console.print("  ✓ All core modules imported successfully", style="green")
        return True
        
    except ImportError as e:
        console.print(f"  ✗ Import error: {e}", style="red")
        return False


def test_config():
    """Test configuration loading."""
    console.print("\n[cyan]Test 2: Configuration Loading[/cyan]")
    
    try:
        from src.llm.provider import load_config
        from src.core import load_vignette
        
        # Load models config
        config = load_config()
        assert 'roles' in config, "Missing 'roles' in config"
        assert 'model_options' in config, "Missing 'model_options' in config"
        
        # Check roles are defined
        expected_roles = ['patient', 'therapist', 'router']
        for role in expected_roles:
            assert role in config['roles'], f"Missing role: {role}"
        
        console.print(f"  ✓ Models config loaded: {len(config['roles'])} roles", style="green")
        
        # Load a vignette
        vignette = load_vignette('cooperative')
        assert 'name' in vignette, "Missing 'name' in vignette"
        assert 'nightmare' in vignette, "Missing 'nightmare' in vignette"
        
        console.print(f"  ✓ Vignette loaded: {vignette['name']}", style="green")
        return True
        
    except Exception as e:
        console.print(f"  ✗ Config test error: {e}", style="red")
        return False


def test_available_vignettes():
    """Test that vignettes are available."""
    console.print("\n[cyan]Test 3: Available Vignettes[/cyan]")
    
    try:
        from pathlib import Path
        
        vignettes_dir = Path("data/prompts/patients/vignettes")
        vignettes = list(vignettes_dir.glob("*.json"))
        
        expected_vignettes = ['cooperative', 'anxious', 'resistant', 'trauma', 'avoidant', 'skeptic']
        found = []
        
        for v in expected_vignettes:
            vignette_file = vignettes_dir / f"{v}.json"
            if vignette_file.exists():
                found.append(v)
        
        console.print(f"  ✓ Found {len(found)}/{len(expected_vignettes)} vignettes", style="green")
        
        if len(found) < len(expected_vignettes):
            missing = set(expected_vignettes) - set(found)
            console.print(f"  ⚠ Missing: {', '.join(missing)}", style="yellow")
        
        return len(found) > 0
        
    except Exception as e:
        console.print(f"  ✗ Vignette test error: {e}", style="red")
        return False


def test_api_keys():
    """Test API key availability (doesn't make calls)."""
    console.print("\n[cyan]Test 4: API Key Availability[/cyan]")
    
    try:
        # Check for common API keys
        keys_to_check = {
            'GROQ_API_KEY': 'Groq (default for patient/therapist)',
            'OPENAI_API_KEY': 'OpenAI (optional)',
            'GEMINI_API_KEY': 'Gemini (optional)',
        }
        
        found_keys = []
        missing_keys = []
        
        for key, description in keys_to_check.items():
            if os.getenv(key):
                found_keys.append(f"{key} ({description})")
                console.print(f"  ✓ {key} found", style="green")
            else:
                missing_keys.append(f"{key} ({description})")
                console.print(f"  ✗ {key} not found", style="yellow")
        
        if not found_keys:
            console.print("  ⚠ No API keys found. Set them in .env file", style="yellow")
            return False
        
        return True
        
    except Exception as e:
        console.print(f"  ✗ API key test error: {e}", style="red")
        return False


def test_provider_creation():
    """Test that providers can be instantiated."""
    console.print("\n[cyan]Test 5: Provider Instantiation[/cyan]")
    
    try:
        from src.llm.provider import create_provider
        
        roles = ['patient', 'therapist', 'router']
        created = []
        
        for role in roles:
            try:
                provider = create_provider(role)
                created.append(role)
                console.print(f"  ✓ {role.capitalize()} provider created", style="green")
            except Exception as e:
                console.print(f"  ✗ {role.capitalize()} provider failed: {e}", style="red")
        
        return len(created) == len(roles)
        
    except Exception as e:
        console.print(f"  ✗ Provider creation error: {e}", style="red")
        return False


async def test_quick_llm_call():
    """Test a quick LLM call (optional, requires API key)."""
    console.print("\n[cyan]Test 6: Quick LLM Call (Optional)[/cyan]")
    
    try:
        from src.llm.provider import create_provider
        
        # Try with therapist provider (usually Groq)
        provider = create_provider('therapist')
        
        # Make a minimal call
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'test successful' and nothing else."}
        ]
        
        content, usage = await provider.generate(messages, max_tokens=20)
        
        console.print(f"  ✓ LLM responded: {content[:50]}...", style="green")
        console.print(f"  ✓ Tokens used: {usage.get('total_tokens', 'unknown')}", style="green")
        return True
        
    except Exception as e:
        console.print(f"  ✗ LLM call failed: {e}", style="yellow")
        console.print("  ℹ This is optional - check API key if needed", style="dim")
        return False


def test_agent_creation():
    """Test that agents can be instantiated."""
    console.print("\n[cyan]Test 7: Agent Instantiation[/cyan]")
    
    try:
        from src.agents import PatientAgent, TherapistAgent, RouterAgent
        from src.core import load_vignette, Language
        
        # Create agents with dummy providers to avoid API calls
        class DummyProvider:
            async def generate(self, messages, **kwargs):
                return "Test response", {"total_tokens": 0}
        
        dummy = DummyProvider()
        
        # Patient agent
        vignette = load_vignette('cooperative')
        patient = PatientAgent(vignette=vignette, language='en', provider=dummy)
        console.print("  ✓ PatientAgent created", style="green")
        
        # Therapist agent
        therapist = TherapistAgent(language='en', provider=dummy)
        console.print("  ✓ TherapistAgent created", style="green")
        
        # Router agent
        router = RouterAgent(provider=dummy)
        console.print("  ✓ RouterAgent created", style="green")
        
        return True
        
    except Exception as e:
        console.print(f"  ✗ Agent creation error: {e}", style="red")
        return False


def print_summary(results: dict, mode: str):
    """Print test summary."""
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    console.print("\n" + "=" * 60)
    
    # Create results table
    table = Table(title="Test Results Summary", show_header=True)
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="bold")
    
    for test_name, passed_test in results.items():
        status = "[green]✓ PASS[/green]" if passed_test else "[red]✗ FAIL[/red]"
        table.add_row(test_name, status)
    
    console.print(table)
    console.print("=" * 60)
    
    # Overall status
    if passed == total:
        console.print(
            Panel(
                f"[bold green]All {total} tests passed![/bold green]\n\n"
                "Your setup is ready to use.\n\n"
                "Next steps:\n"
                "1. Ensure .env file has your GROQ_API_KEY\n"
                "2. Run: python3 -m src generate\n"
                "3. Or: ./run generate",
                title="✅ Setup Complete",
                border_style="green"
            )
        )
    else:
        failed = total - passed
        console.print(
            Panel(
                f"[bold yellow]{failed}/{total} tests failed[/bold yellow]\n\n"
                "Please check the errors above and:\n"
                "1. Verify .env file exists with API keys\n"
                "2. Run: pip install -r requirements.txt\n"
                "3. Check that all files are in place",
                title="⚠ Setup Issues",
                border_style="yellow"
            )
        )
    
    console.print(f"\nMode: {mode.upper()}")


def main():
    """Run all tests."""
    # Parse arguments
    mode = "quick"  # Default mode
    if len(sys.argv) > 1:
        if sys.argv[1] == "--full":
            mode = "full"
        elif sys.argv[1] == "--quick":
            mode = "quick"
    
    console.print(
        Panel(
            "[bold]Measure AI Drift - Setup Verification[/bold]\n\n"
            f"Mode: {mode.upper()}\n"
            "Similar to old test_basic.py but for new architecture",
            title="Setup Test",
            border_style="blue"
        )
    )
    
    # Run tests
    results = {}
    
    # Always run these
    results["1. Module Imports"] = test_imports()
    results["2. Configuration"] = test_config()
    results["3. Vignettes"] = test_available_vignettes()
    results["4. API Keys"] = test_api_keys()
    results["5. Provider Creation"] = test_provider_creation()
    results["7. Agent Creation"] = test_agent_creation()
    
    # Optional: Full mode includes API call
    if mode == "full":
        results["6. Quick LLM Call"] = asyncio.run(test_quick_llm_call())
    
    # Print summary
    print_summary(results, mode)
    
    # Exit code
    all_passed = all(results.values())
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
