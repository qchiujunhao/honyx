#!/usr/bin/env python3
"""Step 3 — render the ROC curve and feature-importance plots as PNGs.

The PNGs are presentation artifacts regenerated from the step-2 outputs;
reproduction is checked on metrics.json (data), not on the image bytes.
"""
from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


def main() -> None:
    roc = pd.read_csv("results/roc_points.csv")
    with open("results/metrics.json", encoding="utf-8") as handle:
        metrics = json.load(handle)
    importance = pd.read_json("results/feature_importance.json")

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(roc["fpr"], roc["tpr"], label=f"AUC = {metrics['roc_auc']:.3f}")
    ax.plot([0, 1], [0, 1], "--", color="gray")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title("ROC curve")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig("results/roc_curve.png", dpi=110)
    plt.close(fig)

    top = importance.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(top["feature"], top["importance"], color="#4c78a8")
    ax.set_xlabel("Importance")
    ax.set_title("Top 10 feature importances")
    fig.tight_layout()
    fig.savefig("results/feature_importance.png", dpi=110)
    plt.close(fig)
    print("wrote results/roc_curve.png, results/feature_importance.png")


if __name__ == "__main__":
    main()
