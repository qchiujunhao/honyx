#!/usr/bin/env bash
# Orchestrator template: run the pipeline steps in order from the package root.
# List every step here in the same order as honyx.json `steps`.
set -euo pipefail
cd "$(dirname "$0")"

# CI moves results/ aside before re-running, so recreate it here.
mkdir -p results

python3 steps/01_STEP.py
# python3 steps/02_STEP.py
# python3 steps/03_STEP.py
