#!/usr/bin/env python3
"""Step 1 — clean the raw measurements into a tidy CSV.

Drops blank lines, trims whitespace, and removes rows whose value is missing or
non-numeric. Rows are sorted by (group, value) so the output is deterministic.
"""
from __future__ import annotations

import csv
import os

RAW = "data/measurements.csv"
OUT = "results/clean.csv"


def main() -> None:
    rows: list[tuple[str, float]] = []
    with open(RAW, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            group = (row.get("group") or "").strip()
            raw_value = (row.get("value") or "").strip()
            if not group or not raw_value:
                continue
            try:
                value = float(raw_value)
            except ValueError:
                continue
            rows.append((group, value))

    rows.sort()
    os.makedirs("results", exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["group", "value"])
        for group, value in rows:
            writer.writerow([group, repr(value)])
    print(f"wrote {OUT}: {len(rows)} rows")


if __name__ == "__main__":
    main()
