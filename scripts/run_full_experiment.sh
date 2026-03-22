#!/usr/bin/env bash
# Run the full experiment with clean output.
# Usage: ./scripts/run_full_experiment.sh
#   or:  ./scripts/run_full_experiment.sh --trials 5 --temps 0.0 0.3

set -euo pipefail
cd "$(dirname "$0")/.."

# Activate venv and load env
source .venv/bin/activate
set -a; source .env; set +a

# Suppress noisy warnings from transformers/torch weight loading
export TRANSFORMERS_VERBOSITY=error
export TOKENIZERS_PARALLELISM=false
export PYTHONWARNINGS="ignore::FutureWarning,ignore::UserWarning"

# Default: full experiment
exec python scripts/run_experiment.py --no-therapy-temp "$@"
