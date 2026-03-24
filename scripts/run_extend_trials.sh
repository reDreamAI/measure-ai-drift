#!/usr/bin/env bash
# Extend existing experiment runs with extra trials (default +10).
# Saves backup of old metrics as metrics_n10.json per run.
#
# Usage: caffeinate -i ./scripts/run_extend_trials.sh
#        caffeinate -i ./scripts/run_extend_trials.sh --extra 15
#        caffeinate -i ./scripts/run_extend_trials.sh --models mistral_large qwen35_27b
#        caffeinate -i ./scripts/run_extend_trials.sh --dry-run

set -euo pipefail
cd "$(dirname "$0")/.."

source .venv/bin/activate
set -a; source .env; set +a

export TRANSFORMERS_VERBOSITY=error
export TOKENIZERS_PARALLELISM=false
export PYTHONWARNINGS="ignore::FutureWarning,ignore::UserWarning"

exec python scripts/extend_trials.py "$@"
