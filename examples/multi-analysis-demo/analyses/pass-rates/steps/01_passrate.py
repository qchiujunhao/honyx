#!/usr/bin/env python3
"""Step 1 — compute the pass rate (score >= 60) per method."""
from __future__ import annotations

import csv
import json
from collections import defaultdict

RAW = "data/scores.csv"
OUT = "results/passrate.json"
THRESHOLD = 60.0


def main() -> None:
    passed: dict[str, int] = defaultdict(int)
    total: dict[str, int] = defaultdict(int)
    with open(RAW, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            method = (row.get("method") or "").strip()
            raw = (row.get("score") or "").strip()
            if not method or not raw:
                continue
            try:
                score = float(raw)
            except ValueError:
                continue
            total[method] += 1
            if score >= THRESHOLD:
                passed[method] += 1

    methods = [
        {"method": m, "n": total[m], "pass_rate": round(passed[m] / total[m], 6)}
        for m in sorted(total)
    ]
    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump({"threshold": THRESHOLD, "methods": methods}, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"wrote {OUT}: {len(methods)} methods")


if __name__ == "__main__":
    main()
