---
name: reproducible-analysis
description: Turn a completed analysis into a GitHub repository whose final analysis paths can be rerun, compared with committed reference results, and presented as a generated website. Use when a user asks to make an analysis reproducible, reusable, shareable, publishable, ready for GitHub Pages, or transferable to another person or coding agent; when an analysis is ending and should leave an executable result rather than only a conversational answer; or when reviewing or repairing such a package.
---

# Reproducible Analysis

Package the **final reported analysis**, not the agent's exploration. Leave a
normal repository that a person or another coding agent can understand, rerun,
check, and show through GitHub Pages.

Use the fixed v0 conventions in `references/package-contract.md`.

## Use the bundled pieces

- Copy `assets/check.py` unchanged. It performs the declared output comparisons.
- Adapt `assets/run.sh` into the one canonical command for environment setup and
  every final analysis step.
- Fill in `assets/honyx.template.json`.
- Adapt `assets/build_site.py` to the analysis's actual results. It is an example,
  not a generic renderer.
- Use `assets/reproduce.yml` for one analysis.
- Use `assets/reproduce-multi.yml` and `assets/build_index.py` for several
  independent analyses in one repository.

## Finalize

1. State the scientific question and the findings that will be reported.
2. Identify the true raw inputs. Do not treat outputs, caches, notebook state, or
   the exploratory workspace as inputs.
3. Retain only result-affecting paths that belong in the final report. Convert
   manual or interactive actions into scripts or disclose them.
4. Put final operations into ordered scripts under `steps/`. Let multiple scripts
   read a shared earlier result when the final method branches.
5. Make `run.sh` recreate `results/`, reconstruct the declared environment, and
   run every step non-interactively from the package root. For Python, freeze the
   full resolved environment in `requirements.txt`; the bundled `run.sh` shows the
   isolated-venv pattern. Adapt it for another runtime instead of adding a new
   framework.
6. Declare raw inputs, ordered steps, produced files, and reported outputs in
   `honyx.json`. Compare deterministic JSON numerically, stable text exactly, and
   rendered figures by non-empty existence while separately comparing their
   backing data.
7. Run `bash run.sh` to create the reference `results/`, then adapt
   `build_site.py` to show the question, result, final paths, scripts, and
   visualizations. Generate the site from results; never maintain result values
   separately in HTML.
8. Write a self-contained `README.md` with the question, method choices,
   assumptions, limitations, result meaning, rerun command, and precise CI claim.
9. Commit `results/`, `check.py`, the environment lock, and the workflow at
   `.github/workflows/reproduce.yml`. Ignore `.venv/` and `site/`.

## Choose one repository shape

- **One question, one final path:** create one package at the repository root.
- **Several independent questions:** create one self-contained package per
  question under `analyses/<slug>/`. The multi-analysis workflow discovers and
  checks every manifest before `build_index.py` publishes the combined site.
- **One question, several defensible final paths:** keep one package. Represent
  the branches as steps after shared preparation, add a comparison step, declare
  every branch result plus the comparison as outputs, and show them side by side.

Do not package every attempted branch. Keep only paths the final report presents.

## Check it locally

Move the committed reference outside the package, rerun, compare, and build the
same site CI will publish:

```bash
reference_root="$(mktemp -d)"
mv results "$reference_root/results"
bash run.sh
python3 check.py results "$reference_root/results"
python3 build_site.py
```

Run the completeness audit in `references/review-prompts.md` before claiming
done. Repair only concrete gaps; never change the scientific method merely to
obtain a match.

## Report the evidence honestly

A passing fresh-clone CI run means the declared outputs were regenerated and
matched the committed references according to `honyx.json`. It is standardized
rerun evidence, not independent scientific review, proof that the method is
correct, or proof that no relevant decision was omitted.

If the full analysis does not fit the configured runner, use a larger or
self-hosted runner. If only a subset is checked, label the badge and README as
subset verification.

Read `references/verification-policy.md` before making a reproduction claim.
