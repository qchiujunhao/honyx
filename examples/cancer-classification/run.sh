#!/usr/bin/env bash
# Orchestrator: reconstruct the resolved environment, then run the shared
# preparation, both final model paths, their comparison, and visualization.
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p results

BASE_PYTHON="${PYTHON:-python3}"
rm -rf .venv
"$BASE_PYTHON" -m venv .venv
.venv/bin/python -m pip install --quiet --disable-pip-version-check -r requirements.txt
PY=.venv/bin/python

"$PY" steps/01_prepare.py
"$PY" steps/02_logistic.py
"$PY" steps/03_forest.py
"$PY" steps/04_compare.py
"$PY" steps/05_visualize.py
