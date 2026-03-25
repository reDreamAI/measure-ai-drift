#!/usr/bin/env bash
# Run seed batch experiment for Mistral Large 3
set -euo pipefail
cd "$(dirname "$0")/.."

source .venv/bin/activate
source .env 2>/dev/null || true

export TOKENIZERS_PARALLELISM=false
export TRANSFORMERS_NO_ADVISORY_WARNINGS=1

python scripts/run_seed_batch.py "$@"
