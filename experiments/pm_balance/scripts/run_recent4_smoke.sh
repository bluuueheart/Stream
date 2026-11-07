#!/usr/bin/env bash
# One real OVO question; validates runtime only, never a benchmark score.
set -euo pipefail
cd "$(dirname "$0")/../../.."
: "${MODEL_PATH:?Set MODEL_PATH to the local Qwen3-VL-8B-Instruct directory}"
: "${RESULT_DIR:?Set RESULT_DIR to a new, unused output directory}"
if [[ -e "$RESULT_DIR" ]]; then
  echo "Refusing to reuse result directory: $RESULT_DIR" >&2
  exit 1
fi
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-GPU-bb163038-9f05-12e3-dc3c-ead2ac87a033}"
export HF_HUB_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-4}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-4}"
export FORCE_QWENVL_VIDEO_READER="${FORCE_QWENVL_VIDEO_READER:-torchvision}"
export PYTHONFAULTHANDLER=1
# Limit CPU affinity too: FFmpeg may ignore BLAS/OpenMP thread limits.
cpu_list=$(.venv-qwen3/bin/python -c 'import os; print(",".join(map(str, sorted(os.sched_getaffinity(0))[:8])))')
taskset -c "$cpu_list" .venv-qwen3/bin/python SimpleStream/main_experiments/eval_qwen3vl_ovo.py \
  --model_path "$MODEL_PATH" \
  --anno_path experiments/pm_balance/data/smoke/annotations.json \
  --chunked_dir experiments/pm_balance/data/smoke/chunked_videos \
  --result_dir "$RESULT_DIR" \
  --recent_frames_only 4 --chunk_duration 1.0 --fps 1.0 --max_qa_tokens 256
