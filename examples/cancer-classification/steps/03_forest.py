#!/usr/bin/env python3
"""Path B — seeded random forest on the shared split."""
from __future__ import annotations

import json

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score

SEED = 42


def main() -> None:
    train = pd.read_csv("results/train.csv")
    test = pd.read_csv("results/test.csv")
    x_train, y_train = train.drop(columns=["target"]), train["target"]
    x_test, y_test = test.drop(columns=["target"]), test["target"]

    model = RandomForestClassifier(n_estimators=200, random_state=SEED, n_jobs=1)
    model.fit(x_train, y_train)
    probability = model.predict_proba(x_test)[:, 1]
    prediction = (probability >= 0.5).astype(int)

    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    cv_scores = cross_val_score(
        model, x_train, y_train, cv=folds, scoring="roc_auc", n_jobs=1
    )
    metrics = {
        "path": "random_forest",
        "positive_class": "benign",
        "seed": SEED,
        "n_train": int(len(y_train)),
        "n_test": int(len(y_test)),
        "accuracy": round(float(accuracy_score(y_test, prediction)), 6),
        "precision": round(float(precision_score(y_test, prediction)), 6),
        "recall": round(float(recall_score(y_test, prediction)), 6),
        "f1": round(float(f1_score(y_test, prediction)), 6),
        "roc_auc": round(float(roc_auc_score(y_test, probability)), 6),
        "cv_roc_auc_mean": round(float(cv_scores.mean()), 6),
        "cv_roc_auc_std": round(float(cv_scores.std()), 6),
    }
    with open("results/forest_metrics.json", "w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2, sort_keys=True)
        handle.write("\n")

    false_positive, true_positive, _ = roc_curve(y_test, probability)
    roc = [
        {"false_positive_rate": round(float(x), 10), "true_positive_rate": round(float(y), 10)}
        for x, y in zip(false_positive, true_positive)
    ]
    with open("results/forest_roc.json", "w", encoding="utf-8") as handle:
        json.dump(roc, handle, indent=2)
        handle.write("\n")

    drivers = sorted(
        (
            {
                "feature": feature,
                "importance": round(float(value), 10),
            }
            for feature, value in zip(x_train.columns, model.feature_importances_)
        ),
        key=lambda row: (-row["importance"], row["feature"]),
    )
    with open("results/forest_importance.json", "w", encoding="utf-8") as handle:
        json.dump(drivers, handle, indent=2)
        handle.write("\n")

    print("forest metrics:", metrics)


if __name__ == "__main__":
    main()
