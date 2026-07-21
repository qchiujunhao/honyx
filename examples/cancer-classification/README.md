# Breast-cancer malignancy classification — reproducible ML example

<!-- After pushing to GitHub, this badge reflects the CI reproduction run.
     Replace OWNER/REPO. -->
<!-- [![reproduce](https://github.com/OWNER/REPO/actions/workflows/reproduce.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/reproduce.yml) -->

A realistic, dependency-heavy example for the `reproducible-analysis` skill: a
seeded scikit-learn classification pipeline whose reported metrics regenerate
from the raw input in a rebuilt environment, verified by CI on a fresh clone,
with a generated showcase.

**Question:** can tumor measurements separate malignant from benign, and how well?
**Result (seed 42):** test ROC AUC 0.995, accuracy 0.958, 5-fold CV ROC AUC
0.989 ± 0.010. Top features are the "worst"-region size/shape measurements.

## Layout

```text
cancer-classification/
├── honyx.json          # manifest: inputs, steps, outputs + comparisons
├── run.sh              # reconstructs a venv from pinned reqs, then runs steps
├── requirements.txt    # PINNED (numpy/pandas/scikit-learn/matplotlib), Python 3.11
├── export_data.py      # provenance: how data/cancer.csv was made (not in the pipeline)
├── data/cancer.csv     # raw input (the only file kept on the field in CI)
├── steps/
│   ├── 01_prepare.py       # raw -> seeded stratified train/test split
│   ├── 02_train_eval.py    # train seeded model -> results/metrics.json (+ roc, importances)
│   └── 03_visualize.py     # -> results/roc_curve.png, feature_importance.png
├── results/            # reference outputs (committed; moved aside in CI)
├── check.py            # verbatim skill asset — compares outputs
├── build_site.py       # showcase builder, ADAPTED to this analysis (metrics + PNGs)
└── reproduce.yml       # -> copy to .github/workflows/reproduce.yml
```

## Run locally

```bash
PYTHON=python3.11 bash run.sh   # builds .venv from pinned reqs, runs the pipeline
python3 build_site.py           # regenerate the showcase into site/index.html
```

## Reproduce it the CI way

```bash
mv results reference-outputs           # keep only the raw input
PYTHON=python3.11 bash run.sh           # fresh .venv, regenerate everything
python3 check.py results reference-outputs
```

A pass means `metrics.json` regenerated within `1e-6` and both plots were rebuilt.
On GitHub, `reproduce.yml` does this on every push (Python 3.11, ~seconds — well
within a free runner).

## What this example exercises (that the toy demo skipped)

- **Real dependencies + isolated environment reconstruction:** `run.sh` builds a
  fresh venv from a pinned `requirements.txt`, so the environment is part of what
  reproduces — not assumed to be on the machine.
- **Seeded stochasticity:** the split, model, and CV folds are all seeded, so the
  metrics are deterministic and comparable with numeric tolerance.
- **Compare data, not picture bytes:** `metrics.json` is compared with `1e-6`
  tolerance; the matplotlib PNGs are `exists`-only (their bytes differ across
  machines for rendering reasons).
- **An adapted showcase:** `build_site.py` is not the generic asset — it was
  rewritten for this analysis's outputs (a metrics table and embedded PNGs).

## What the badge does and does not mean

- ✅ The declared metrics regenerate from `data/cancer.csv` in a venv rebuilt from
  pinned requirements, on a clean machine.
- ❌ Not a claim that the model is clinically valid, that this seed/split is
  optimal, or that the whole modeling process was captured — those are disclosed,
  not proven by CI.
