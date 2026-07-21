#!/usr/bin/env python3
"""Provenance for data/cancer.csv — NOT part of the reproducible pipeline.

The declared raw input is data/cancer.csv. This script records where it came
from (scikit-learn's bundled breast-cancer dataset) and regenerates it from
source if needed. The pipeline itself never runs this.
"""
from __future__ import annotations

import os

from sklearn.datasets import load_breast_cancer


def main() -> None:
    frame = load_breast_cancer(as_frame=True).frame  # 30 features + 'target'
    os.makedirs("data", exist_ok=True)
    frame.to_csv("data/cancer.csv", index=False)
    print(f"wrote data/cancer.csv {frame.shape}")


if __name__ == "__main__":
    main()
