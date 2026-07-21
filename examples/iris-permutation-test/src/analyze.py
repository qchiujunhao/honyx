"""Fixed-seed permutation test for petal-length differences among Iris species."""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path


INPUT_PATH = Path("inputs/bezdek-iris.data")
OUTPUT_PATH = Path("results/analysis.json")
EXPECTED_LABELS = (
    "Iris-setosa",
    "Iris-versicolor",
    "Iris-virginica",
)
PERMUTATIONS = 20_000
RANDOM_SEED = 1936


def read_records(path: Path) -> tuple[list[float], list[str]]:
    """Read all complete nonempty records without collapsing observations."""
    values: list[float] = []
    labels: list[str] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            line_number = reader.line_num
            if not row:
                continue
            if len(row) != 5:
                raise ValueError(
                    f"line {line_number}: expected 5 fields, observed {len(row)}"
                )
            try:
                measurements = [float(value) for value in row[:4]]
            except ValueError as exc:
                raise ValueError(
                    f"line {line_number}: all four measurements must be numeric"
                ) from exc
            if not all(math.isfinite(value) for value in measurements):
                raise ValueError(f"line {line_number}: measurements must be finite")
            label = row[4].strip()
            if label not in EXPECTED_LABELS:
                raise ValueError(f"line {line_number}: unexpected species label {label!r}")
            values.append(measurements[2])
            labels.append(label)

    if not values:
        raise ValueError("input contains no observations")
    missing = sorted(set(EXPECTED_LABELS) - set(labels))
    if missing:
        raise ValueError(f"input is missing expected groups: {', '.join(missing)}")
    return values, labels


def group_values(values: list[float], labels: list[str]) -> dict[str, list[float]]:
    groups: dict[str, list[float]] = defaultdict(list)
    for value, label in zip(values, labels, strict=True):
        groups[label].append(value)
    return dict(groups)


def anova_components(
    values: list[float], labels: list[str]
) -> dict[str, float | int]:
    groups = group_values(values, labels)
    observation_count = len(values)
    group_count = len(groups)
    grand_mean = statistics.fmean(values)
    group_means = {
        label: statistics.fmean(group) for label, group in groups.items()
    }
    ss_between = sum(
        len(groups[label]) * (group_means[label] - grand_mean) ** 2
        for label in groups
    )
    ss_within = sum(
        sum((value - group_means[label]) ** 2 for value in groups[label])
        for label in groups
    )
    df_between = group_count - 1
    df_within = observation_count - group_count
    if df_between <= 0 or df_within <= 0 or ss_within <= 0:
        raise ValueError("ANOVA statistic is undefined for the declared input")
    f_statistic = (ss_between / df_between) / (ss_within / df_within)
    ss_total = ss_between + ss_within
    return {
        "df_between": df_between,
        "df_within": df_within,
        "f_statistic": f_statistic,
        "ss_between": ss_between,
        "ss_within": ss_within,
        "ss_total": ss_total,
        "eta_squared": ss_between / ss_total,
    }


def summarize_groups(
    values: list[float], labels: list[str]
) -> dict[str, dict[str, float | int]]:
    groups = group_values(values, labels)
    return {
        label.removeprefix("Iris-"): {
            "count": len(group),
            "maximum_cm": max(group),
            "mean_cm": statistics.fmean(group),
            "minimum_cm": min(group),
            "sample_sd_cm": statistics.stdev(group),
        }
        for label, group in sorted(groups.items())
    }


def permutation_test(
    values: list[float], labels: list[str], observed_f: float
) -> tuple[int, float]:
    generator = random.Random(RANDOM_SEED)
    permuted_labels = labels.copy()
    exceedances = 0
    for _ in range(PERMUTATIONS):
        generator.shuffle(permuted_labels)
        permuted_f = float(anova_components(values, permuted_labels)["f_statistic"])
        if permuted_f >= observed_f:
            exceedances += 1
    p_value = (1 + exceedances) / (1 + PERMUTATIONS)
    return exceedances, p_value


def main() -> None:
    values, labels = read_records(INPUT_PATH)
    observed = anova_components(values, labels)
    observed_f = float(observed["f_statistic"])
    exceedances, p_value = permutation_test(values, labels, observed_f)
    result = {
        "analysis": {
            **observed,
            "group_count": len(set(labels)),
            "observation_count": len(values),
        },
        "group_summaries": summarize_groups(values, labels),
        "permutation_test": {
            "exceedances": exceedances,
            "permutations": PERMUTATIONS,
            "p_value": p_value,
            "random_seed": RANDOM_SEED,
            "tail_rule": "permuted_f_greater_than_or_equal_to_observed_f",
        },
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

