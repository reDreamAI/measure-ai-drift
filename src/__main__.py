"""Main entry point for the measure-ai-drift CLI.

Enables running the package as a module:
    python -m src <command>
"""

from pathlib import Path

# Load .env before importing CLI (which imports providers)
from dotenv import load_dotenv
_PROJECT_ROOT = Path(__file__).parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"
if _ENV_FILE.exists():
    load_dotenv(_ENV_FILE)
else:
    load_dotenv()

from src.cli import main

if __name__ == "__main__":
    main()
