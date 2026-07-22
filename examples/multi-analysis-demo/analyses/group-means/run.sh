#!/usr/bin/env bash
# Orchestrator: run the pipeline steps in order from the package root.
set -euo pipefail
cd "$(dirname "$0")"

# CI moves results/ aside before re-running, so recreate it here.
mkdir -p results

python3 steps/01_clean.py
python3 steps/02_summarize.py
python3 steps/03_visualize.py
