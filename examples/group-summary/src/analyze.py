from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path


values_by_group: dict[str, list[float]] = defaultdict(list)
with Path("inputs/measurements.csv").open(newline="", encoding="utf-8") as handle:
    for row_number, row in enumerate(csv.DictReader(handle), start=2):
        group = (row.get("group") or "").strip()
        if not group:
            raise ValueError(f"row {row_number}: group must not be empty")
        try:
            value = float(row["value"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"row {row_number}: value must be numeric") from exc
        if not math.isfinite(value):
            raise ValueError(f"row {row_number}: value must be finite")
        values_by_group[group].append(value)

if not values_by_group:
    raise ValueError("input must contain at least one observation")

summary = {
    "groups": {
        group: {
            "count": len(values),
            "mean": sum(values) / len(values),
        }
        for group, values in sorted(values_by_group.items())
    },
    "total_observations": sum(len(values) for values in values_by_group.values()),
}

output = Path("results/summary.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

