# Honyx

Honyx publishes the **`reproducible-analysis` skill**: a skill for coding agents
that turns a finished analysis into a GitHub repo that is **reproducible,
shareable, and self-showcasing**.

When triggered at the end of an analysis, the skill captures the *final result
pipeline* — not the exploration — as an ordered set of steps whose declared
outputs regenerate from the raw inputs. A fresh GitHub Actions clone verifies the
reproduction (the verdict comes from a neutral machine, not the agent), and a
generated site showcases the steps, scripts, and result visualizations. Sharing
is just a GitHub repo URL.

## What's in this repo

- `plugins/honyx/` — the publishable Codex plugin and the `reproducible-analysis`
  skill. The skill is self-contained: its runtime scaffolding lives in
  `skills/reproducible-analysis/assets/` (`check.py`, `build_site.py`,
  `reproduce.yml`, and manifest/orchestrator templates).
- `examples/pipeline-demo/` — a full worked example of what the skill produces: a
  multi-step pipeline, a `honyx.json` manifest, reference outputs, and the
  generated showcase. It is a demonstration, not the repo's product.
- `SCOPE.md` — the converged design blueprint (supersedes `DESIGN.md`).

## See the example reproduce itself

The example regenerates its outputs from the raw input the way CI does — with
only raw inputs on the field, so nothing can reuse a committed answer:

```bash
cd examples/pipeline-demo
mv results reference-outputs      # keep only raw inputs
bash run.sh                       # regenerate every intermediate and output
python3 check.py results reference-outputs   # -> REPRODUCTION OK
python3 build_site.py             # rebuild the showcase into site/index.html
```

In a real repo this runs on every push via `reproduce.yml`, publishing a badge
and the showcase site.

## Design

`SCOPE.md` is the current blueprint. `DESIGN.md` records the earlier, broader
vision and is retained for reference only. The Python package under `src/honyx`
and `tests/` predates the skill-centric form and is slated for removal.
