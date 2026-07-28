#!/usr/bin/env python3
"""Compare the two retained paths and state the shared conclusion."""
from __future__ import annotations

import json
from pathlib import Path

STRONG_AUC = 0.95


def read_json(path: str) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    paths = {
        "logistic_regression": read_json("results/logistic_metrics.json"),
        "random_forest": read_json("results/forest_metrics.json"),
    }
    selected = max(paths, key=lambda name: float(paths[name]["cv_roc_auc_mean"]))
    cv_values = [float(metrics["cv_roc_auc_mean"]) for metrics in paths.values()]
    test_values = [float(metrics["roc_auc"]) for metrics in paths.values()]
    stable = all(value >= STRONG_AUC for value in cv_values)

    comparison = {
        "comparison_basis": "highest mean five-fold training-set CV ROC AUC",
        "selected_path": selected,
        "strong_auc_threshold": STRONG_AUC,
        "both_paths_reach_threshold": stable,
        "cv_roc_auc_range": round(max(cv_values) - min(cv_values), 6),
        "test_roc_auc_range": round(max(test_values) - min(test_values), 6),
        "conclusion": (
            "Both model families support strong separation."
            if stable
            else "The separation conclusion depends on the model path."
        ),
        "paths": paths,
    }
    with open("results/comparison.json", "w", encoding="utf-8") as handle:
        json.dump(comparison, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print("comparison:", comparison["conclusion"], "selected:", selected)


if __name__ == "__main__":
    main()
