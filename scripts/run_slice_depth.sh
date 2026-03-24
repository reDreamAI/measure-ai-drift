#!/usr/bin/env bash
# Run Mistral Large 3 across slices 1-5 for slice depth analysis.
# Saves into experiments/runs/slice_batch/
#
# Usage: caffeinate -i ./scripts/run_slice_depth.sh

set -euo pipefail
cd "$(dirname "$0")/.."

source .venv/bin/activate
set -a; source .env; set +a

export TRANSFORMERS_VERBOSITY=error
export TOKENIZERS_PARALLELISM=false
export PYTHONWARNINGS="ignore::FutureWarning,ignore::UserWarning"

BATCH_DIR="experiments/runs/slice_batch"
mkdir -p "$BATCH_DIR"

for slice in 1 3 4 5; do
    echo ""
    echo "========== SLICE $slice / 5 =========="
    python scripts/run_experiment.py \
        --no-therapy-temp \
        --trials 20 \
        --temps 0.075 0.15 \
        --models mistral_large \
        --slice "$slice" \
        --batch-dir "$BATCH_DIR"
done

echo ""
echo "Done. Runs in $BATCH_DIR: $(ls "$BATCH_DIR" | wc -l)"
