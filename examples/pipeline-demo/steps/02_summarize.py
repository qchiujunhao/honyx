#!/usr/bin/env python3
"""Step 2 — compute the per-group count and mean from the cleaned data."""
from __future__ import annotations

import csv
import json
from collections import defaultdict

IN = "results/clean.csv"
OUT = "results/summary.json"


def main() -> None:
    sums: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    with open(IN, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            group = row["group"]
            sums[group] += float(row["value"])
            counts[group] += 1

    groups = [
        {"group": group, "n": counts[group], "mean": round(sums[group] / counts[group], 6)}
        for group in sorted(counts)
    ]
    summary = {"question": "What is the mean value in each group?", "groups": groups}
    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"wrote {OUT}: {len(groups)} groups")


if __name__ == "__main__":
    main()
