# Pipeline demo — a reproducible, shareable, self-showcasing analysis

<!-- After you push this to GitHub, this badge reflects the CI reproduction run.
     Replace OWNER/REPO with your repository. -->
<!-- [![reproduce](https://github.com/OWNER/REPO/actions/workflows/reproduce.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/reproduce.yml) -->

This is the reference example for the `reproducible-analysis` skill. It shows the
whole shape in miniature: a multi-step analysis pipeline whose declared outputs
regenerate from the raw input, checked by CI on a fresh clone, with a generated
showcase website.

## Layout

```text
pipeline-demo/
├── honyx.json        # lightweight manifest: inputs, steps, outputs + comparisons
├── run.sh            # orchestrator (runs the steps in order)
├── requirements.txt  # environment lock (stdlib only here)
├── data/
│   └── measurements.csv   # raw input (the only thing kept on the field in CI)
├── steps/
│   ├── 01_clean.py        # raw -> results/clean.csv
│   ├── 02_summarize.py    # clean -> results/summary.json  (the reported result)
│   └── 03_visualize.py    # summary -> results/chart.svg   (a regenerated plot)
├── results/          # reference outputs (committed; moved aside before re-run)
├── check.py          # compares regenerated outputs vs reference (numeric tolerance)
├── build_site.py     # builds site/index.html from the verified run
└── reproduce.yml     # -> copy to .github/workflows/reproduce.yml
```

## Run it locally

```bash
bash run.sh            # regenerate results/
python3 build_site.py  # regenerate the showcase into site/index.html
```

## Reproduce it the way CI does

The point is to re-run from the raw input **without** letting the pipeline see
the committed answer:

```bash
mv results reference-outputs     # keep only raw inputs on the field
bash run.sh                      # regenerate everything
python3 check.py results reference-outputs
```

A pass means `results/summary.json` regenerated within tolerance and the chart
was rebuilt. In a real repo this runs on every push (`reproduce.yml`), so the
green badge is asserted by a neutral machine, not by whoever authored the repo.

## What the badge does and does not mean

- ✅ The declared outputs regenerate from the declared raw inputs, in a
  reconstructed environment, on a clean machine.
- ❌ It does **not** mean the method is scientifically correct, nor that every
  step of the original process was captured. Those are best-effort and disclosed,
  not proven by CI.

## Notes carried from the design

- **Steps are explicit** so the site can show the process, the scripts, and the
  visualization — all generated from the verified run, so they never go stale.
- **The plot is compared as data, not bytes.** `summary.json` is compared with
  numeric tolerance; `chart.svg` only has to be regenerated (`exists`), because
  image bytes differ across machines for spurious rendering reasons.
- **Intermediates are regenerated, never trusted.** Only `data/` survives the
  "move reference aside" step, so a broken early step cannot hide behind a stale
  committed intermediate.
