#!/usr/bin/env python3
"""Step 2 — train a seeded model, evaluate it, and write the reported metrics.

Scaling and the forest live in one pipeline so cross-validation refits the
scaler inside each fold (no leakage). Everything is seeded and single-threaded
so the metrics are deterministic.
"""
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
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SEED = 42


def main() -> None:
    train = pd.read_csv("results/train.csv")
    test = pd.read_csv("results/test.csv")
    x_train, y_train = train.drop(columns=["target"]), train["target"]
    x_test, y_test = test.drop(columns=["target"]), test["target"]

    model = make_pipeline(
        StandardScaler(),
        RandomForestClassifier(n_estimators=200, random_state=SEED, n_jobs=1),
    )
    model.fit(x_train, y_train)
    proba = model.predict_proba(x_test)[:, 1]
    pred = (proba >= 0.5).astype(int)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    cv_scores = cross_val_score(model, x_train, y_train, cv=cv, scoring="roc_auc", n_jobs=1)

    metrics = {
        "model": "StandardScaler + RandomForest(n_estimators=200)",
        "seed": SEED,
        "n_train": int(len(y_train)),
        "n_test": int(len(y_test)),
        "accuracy": round(float(accuracy_score(y_test, pred)), 6),
        "precision": round(float(precision_score(y_test, pred)), 6),
        "recall": round(float(recall_score(y_test, pred)), 6),
        "f1": round(float(f1_score(y_test, pred)), 6),
        "roc_auc": round(float(roc_auc_score(y_test, proba)), 6),
        "cv_roc_auc_mean": round(float(cv_scores.mean()), 6),
        "cv_roc_auc_std": round(float(cv_scores.std()), 6),
    }
    with open("results/metrics.json", "w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2, sort_keys=True)
        handle.write("\n")

    fpr, tpr, _ = roc_curve(y_test, proba)
    pd.DataFrame({"fpr": fpr, "tpr": tpr}).to_csv("results/roc_points.csv", index=False)

    forest = model.named_steps["randomforestclassifier"]
    importance = (
        pd.DataFrame({"feature": x_train.columns, "importance": forest.feature_importances_})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )
    importance.to_json("results/feature_importance.json", orient="records", indent=2)
    print("metrics:", metrics)


if __name__ == "__main__":
    main()
