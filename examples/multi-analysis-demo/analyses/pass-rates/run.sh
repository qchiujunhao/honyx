#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# CI moves results/ aside before re-running, so recreate it here.
mkdir -p results

python3 steps/01_passrate.py
python3 steps/02_visualize.py
