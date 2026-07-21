#!/usr/bin/env bash
# Orchestrator: reconstruct an isolated environment from pinned requirements,
# then run the pipeline steps in order from the package root.
set -euo pipefail
cd "$(dirname "$0")"

# CI moves results/ aside before re-running, so recreate it here.
mkdir -p results

# Reconstruct the environment in an isolated venv from pinned requirements.
# Override the base interpreter with PYTHON=... (must be Python 3.11).
BASE_PYTHON="${PYTHON:-python3}"
if [ ! -x .venv/bin/python ]; then
  "$BASE_PYTHON" -m venv .venv
  .venv/bin/python -m pip install --quiet --upgrade pip
  .venv/bin/python -m pip install --quiet -r requirements.txt
fi
PY=.venv/bin/python

"$PY" steps/01_prepare.py
"$PY" steps/02_train_eval.py
"$PY" steps/03_visualize.py
