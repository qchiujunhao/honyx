#!/usr/bin/env python3
"""Step 1 — load the raw data and make a seeded, stratified train/test split."""
from __future__ import annotations

import pandas as pd
from sklearn.model_selection import train_test_split

RAW = "data/cancer.csv"
SEED = 42
TEST_SIZE = 0.25


def main() -> None:
    df = pd.read_csv(RAW)
    features = df.drop(columns=["target"])
    target = df["target"]
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=TEST_SIZE, random_state=SEED, stratify=target
    )
    train = x_train.assign(target=y_train)
    test = x_test.assign(target=y_test)
    train.to_csv("results/train.csv", index=False)
    test.to_csv("results/test.csv", index=False)
    print(f"train {train.shape} test {test.shape}")


if __name__ == "__main__":
    main()
