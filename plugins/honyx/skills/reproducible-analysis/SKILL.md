---
name: reproducible-analysis
description: Turn a finished analysis into a GitHub repo that is reproducible, shareable, and self-showcasing — the final pipeline regenerates its declared outputs from raw inputs, a fresh CI clone verifies it, and a generated site shows the steps, scripts, and result visualizations. Use when a user asks to make an analysis reproducible, reusable, shareable, publishable to GitHub, or ready to hand off; when an analysis is reaching completion and should leave a portable pipeline rather than a conversational answer; or when reviewing such a package.
---

# Reproducible Analysis

Treat reproducibility as a completion condition. Capture the **final result
pipeline** — not the exploration or dead ends — as a repo that regenerates its
outputs from raw inputs, is shared as a normal GitHub repository, and showcases
its own process. Verification is asserted by a neutral CI run, never by you.

This skill bundles the reusable scaffolding in `assets/`: copy `check.py`,
`build_site.py`, and `reproduce.yml` verbatim into the user's package, and start
`honyx.json` and `run.sh` from `honyx.template.json` and `assets/run.sh`. These
are generic and analysis-independent. `examples/pipeline-demo/` in this repo is a
full worked demonstration of the finished result — read it to see the shape, but
scaffold new packages from `assets/`.

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
5. **Freeze the environment** while it is still live: pin dependencies into
   `requirements.txt` (or `environment.yml`). Record the interpreter version.
6. Declare the pipeline in `honyx.json`: `inputs`, ordered `steps`, and
   `outputs` with a comparison per output (`numeric` + tolerance for data,
   `exists` for regenerated plots, `exact` only for truly byte-stable files).
7. Generate results and the showcase from a real run: `bash run.sh` then
   `python3 build_site.py`. The site must be built from outputs, never by hand.
8. Handle data by size: small data lives in `data/`; large data is fetched from a
   declared URL and checked against a recorded hash — never committed to git.
9. Install `reproduce.yml` at `.github/workflows/reproduce.yml` and add the CI
   badge to `README.md`.

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
