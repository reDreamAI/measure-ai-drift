#!/bin/bash
# Phase 1: Baseline model comparison
# 6 vignettes x 3 models x 2 temperatures = 36 runs, 10 trials each, fused mode, slice_3
set -e

FROZEN_DIR="data/synthetic/frozen_histories"
VIGNETTES=(anxious avoidant cooperative resistant skeptic trauma)
MODELS=(llama70b mistral_small gemini_flash)
TEMPS=(0.0 0.7)
TRIALS=10
SLICE=slice_3

# Find the frozen folder for each vignette
find_frozen() {
    local vignette=$1
    local dir=$(ls -d ${FROZEN_DIR}/frozen_${vignette}_* 2>/dev/null | head -1)
    echo "${dir}/${SLICE}.json"
}

total=$((${#VIGNETTES[@]} * ${#MODELS[@]} * ${#TEMPS[@]}))
count=0

for vignette in "${VIGNETTES[@]}"; do
    history=$(find_frozen "$vignette")
    if [ ! -f "$history" ]; then
        echo "SKIP: No ${SLICE}.json for ${vignette}"
        continue
    fi

    for model in "${MODELS[@]}"; do
        for temp in "${TEMPS[@]}"; do
            count=$((count + 1))
            echo ""
            echo "=========================================="
            echo "[$count/$total] ${model} / ${vignette} / t=${temp}"
            echo "=========================================="

            uv run python -m src evaluate \
                --history "$history" \
                --model "$model" \
                --trials $TRIALS \
                --temperature "$temp" \
                --mode fused \
                --vignette "$vignette"

            echo "Completed: ${model} / ${vignette} / t=${temp}"
        done
    done
done

echo ""
echo "Phase 1 complete: $count/$total runs"
