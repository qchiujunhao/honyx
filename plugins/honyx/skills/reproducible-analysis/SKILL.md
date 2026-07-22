---
name: reproducible-analysis
description: Turn a finished analysis into a GitHub repo that is reproducible, shareable, and self-showcasing — the final pipeline regenerates its declared outputs from raw inputs, a fresh CI clone verifies it, and a generated site shows the steps, scripts, and result visualizations. Use when a user asks to make an analysis reproducible, reusable, shareable, publishable to GitHub, or ready to hand off; when an analysis is reaching completion and should leave a portable pipeline rather than a conversational answer; or when reviewing such a package.
---

# Reproducible Analysis

Treat reproducibility as a completion condition. Capture the **final result
pipeline** — not the exploration or dead ends — as a repo that regenerates its
outputs from raw inputs, is shared as a normal GitHub repository, and showcases
its own process. Verification is asserted by a neutral CI run, never by you.

This skill bundles scaffolding in `assets/`, but the pieces play different roles —
do not treat them all as generic:

- **`check.py` — copy verbatim; never rewrite it.** It is the trusted verifier and
  the one genuinely generic script: it compares only by the `compare` type declared
  in `honyx.json` and knows nothing about your data's shape. Verification must not
  be author-improvised, so this file is fixed on purpose.
- **`reproduce.yml` — copy verbatim.** The CI workflow is analysis-independent.
- **`honyx.json` and `run.sh` — fill in from `honyx.template.json` and
  `assets/run.sh`.** These are templates, not drop-ins.
- **`build_site.py` — a starting-point *example*, not a generic tool.** It is pure
  presentation with no verification role, and it is written for one specific result
  shape (`{"groups":[{"group","n","mean"}]}` + `chart.svg`). Adapt it to your own
  outputs, or replace it with a static-site tool (Quarto, MkDocs). Do not copy it
  and assume it fits.

`examples/pipeline-demo/` is a full worked demonstration — read it to see the shape.

## Pick the operation

- **Active analysis** → allow free exploration, then run *Finalize*.
- **Existing package** → run *Reproduce it the CI way* before editing.
- **Failed reproduction** → repair only the reported gap, then re-run.

Read `references/package-contract.md` before creating or editing `honyx.json`.
Read `references/verification-policy.md` before trusting any reproduction claim.
Use `references/review-prompts.md` for the completeness audit and repair.

## Finalize

1. Name the scientific question and the findings actually being reported.
2. Identify the **true raw inputs**. Never declare current outputs, caches,
   notebook state, or the old workspace as inputs.
3. Extract the final result-affecting method and split it into **ordered steps**
   (e.g. clean → transform → analyze → visualize). Each step is one script that
   reads declared inputs or a prior step's output and writes its own output.
4. Write a non-interactive orchestrator (`run.sh` or `Makefile`) that runs the
   steps in order from the package root. It must recreate the results directory
   (`mkdir -p results`) because CI moves the reference aside before re-running.
5. **Freeze the environment** while it is still live, and reconstruct it in
   **isolation** — not into whatever interpreter happens to be active. Pin exact
   versions into `requirements.txt` (or `environment.yml`) and pin the
   interpreter. Have `run.sh` build a fresh **venv** from those pins and run the
   steps through it, so the environment is part of what reproduces. See
   `examples/cancer-classification/` for the venv pattern.
6. Declare the pipeline in `honyx.json`: `inputs`, ordered `steps`, and
   `outputs` with a comparison per output (`numeric` + tolerance for data,
   `exists` for regenerated plots, `exact` only for truly byte-stable files).
7. Generate results with `bash run.sh`, then build the showcase from those
   outputs (never by hand). Adapt `assets/build_site.py` to your result shape or
   use a static-site tool; whatever you produce, `reproduce.yml` runs it as
   `build_site.py`. Show the statistics your analysis actually reports, not only
   what the demo template happened to render.
8. Handle data by size: small data lives in `data/`; large data is fetched from a
   declared URL and checked against a recorded hash — never committed to git.
9. Set up sharing and CI: install `reproduce.yml` at
   `.github/workflows/reproduce.yml`, add the CI badge to `README.md`, **commit
   `results/`** (CI moves it aside as the reference — the workflow fails without
   it), and add a `.gitignore` for `reference-outputs/` and `site/` (regenerated).

## Reproduce it the CI way

The verdict comes from re-running with only the raw inputs on the field, so the
pipeline cannot reuse a committed answer:

```bash
mv results reference-outputs     # keep only raw inputs
bash run.sh                      # regenerate every intermediate and output
python3 check.py results reference-outputs
```

On GitHub this is exactly what `reproduce.yml` does on every push: a blank runner
checks out only what is committed, rebuilds the environment, moves the reference
aside, re-runs, compares, and publishes the site. A green badge is the runner's
assertion, not yours.

## Multiple analyses in one session

A session may leave several results worth reporting. First classify them, because
they need different shapes:

- **Separate questions** (e.g. answered Q1, Q2, Q3) → **one self-contained package
  per question**, laid out under `analyses/<slug>/`. Each keeps its own
  `honyx.json`, steps, `results/`, `check.py`, and `build_site.py`, and reproduces
  independently. Use the multi-analysis scaffolding: `assets/reproduce-multi.yml`
  (a matrix job verifies each analysis on its own) and `assets/build_index.py`
  (a landing page linking every analysis's showcase into one repo website). List
  each analysis in the workflow matrix.
- **Alternative paths for the *same* question** (tried several models/parameters
  and want them side by side) → **one package with a comparison step**, not many
  packages. The comparison is a declared output; the showcase presents the paths
  together.

Either way, still capture only the paths actually worth reporting. Exploration
and dead ends stay dropped — do not package every branch that was tried.

## Match verification to the runner's resources

Free GitHub runners are limited (~2–4 vCPU, ~7–16 GB RAM, ~14 GB disk, no GPU,
6 h/job). Choose a tier and **state it in the badge/README**:

- Fits a free runner → CI reproduces the **full** analysis.
- Too big → CI reproduces a **declared representative subset** end-to-end (real
  code, small slice) and the badge says "subset"; run the full pipeline on a
  self-hosted or larger runner with the same workflow.

A green check on a slice must never read as full reproduction.

## Audit for completeness before claiming done

CI proves that *what was captured* reproduces. It cannot prove *nothing was left
in the conversation*. Run the adversarial audit in `references/review-prompts.md`
to hunt for undeclared filtering, result-dependent thresholds, manual or visual
decisions, missing-value handling, and hidden caches. Fix what you find; disclose
in `README.md` whatever remains uncovered. Do not grant reproduction status from
this review — only CI does that.

## Report evidence precisely

- **Reproduces (CI):** the fresh-clone run regenerated the declared outputs from
  raw inputs — say whether on full data or a subset.
- Never collapse this into "fully reproducible," and never claim scientific
  correctness from computational regeneration alone.
