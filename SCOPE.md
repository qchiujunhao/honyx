# Honyx Scope (converged)

This is the working blueprint. It supersedes the broad vision in `DESIGN.md`.
The old Python package (`src/honyx`, its CLI, schema, and `tests/`) is retained
for reference only and is slated for removal once the skill-centric form below is
validated.

**What this repo is:** a package that *publishes the `reproducible-analysis`
skill* (`plugins/honyx/`). The repo is not itself a reproducible analysis; it
ships the skill and its scaffolding assets, plus `examples/` that demonstrate
what the skill produces. Everything the skill needs at runtime lives in the skill
bundle (`plugins/honyx/skills/reproducible-analysis/assets/`) so it works when
installed on its own.

## One-line goal

Build **one skill**. When an analysis is finished, triggering it turns the final
pipeline into a GitHub repository that is **reproducible, shareable, and
self-showcasing** — with no bespoke platform or framework.

## The three requirements

1. **Reproducible.** After the analysis, capture the *final result pipeline*
   into something that regenerates the reported outputs from declared raw inputs.
2. **Shareable.** Distribution is a GitHub repo — the repo is already a website
   with a URL. No registry, publisher, or hosted service of our own.
3. **Showcased.** The repo website presents the whole process: the ordered
   pipeline steps, the scripts used to produce the final result, and the result
   visualizations. It does **not** show the agent's exploration or dead ends.

## Load-bearing design decisions

- **Verification runs outside the agent.** The agent is the author, never the
  judge. A **fresh GitHub Actions clone** is the clean room, for free: a blank
  runner checks out only what is committed. A green run means "reproduced," and
  the runner asserts it — not the agent.
- **The one discipline that isn't free:** the pipeline must not read the
  committed reference outputs (or committed intermediates) as inputs. Before
  re-running, move the reference outputs aside and keep only the raw inputs; all
  intermediates are regenerated. This is the entire remaining value of the old
  clean-room verifier, compressed into a ~dozens-of-lines check script.
- **Pipeline as explicit ordered steps.** The final method is usually multiple
  scripts (clean → analyze → visualize). "Showcase the process + scripts + viz"
  *is* "represent the steps," so steps are first-class: plain scripts plus an
  orchestrator (`run.sh` / `Makefile`).
- **The showcase is generated from the verified run**, never hand-maintained, so
  the site cannot drift from what actually reproduces (no stale figures).
- **Only the verifier is a fixed shipped script.** `check.py` earns being copied
  verbatim (verification must not be author-improvised) and is genuinely generic
  (it compares only by declared type). The showcase builder is presentation with
  no verification role and is inherently analysis-specific — it ships as an
  adaptable example, not a "generic" drop-in. Don't manufacture rigid scripts for
  work that is intrinsically per-analysis.
- **Compare data, not picture bytes.** Plots are presentation artifacts
  regenerated from verified data; compare the JSON/CSV behind them (numeric
  tolerance), never byte-match PNG/SVG across machines.
- **Freeze the environment at finalize time** (a lockfile), because the moment
  you share, "runs on my machine" is worthless — it must rebuild on a different
  machine / in CI.
- **Data:** small data in-repo; large data via declared URL + hash. Git is bad
  at big data; this is the one leak in "share via GitHub."

## Verification tiers + honest badge

GitHub-hosted free runners are limited (~2–4 vCPU, ~7–16 GB RAM, ~14 GB disk,
**no GPU**, 6 h/job; public repos get unlimited minutes). So the CADENCE is:

- **Light/medium analyses** → CI runs the **full** reproduction.
- **Too big for a free runner** → CI reproduces a **declared representative
  subset** end-to-end (proves the code runs and reproduces on a slice); the full
  run is done on a **self-hosted / larger runner** with the *same* workflow.

The **badge must state what was verified** (full vs subset; free vs self-hosted
runner). A green check on 1% of the data must not read as "full reproduction."
The skill estimates data size / runtime / GPU need at finalize time and picks the
tier automatically.

## Deliverable shape

- **One skill** (reshaped `reproducible-analysis`): finalize the analysis into a
  clean multi-step repo, freeze the environment, declare raw inputs vs generated
  outputs, build the showcase site from the verified run, install the CI
  workflow, and set an honest badge/tier.
- **`check.py`** — the small clean-check script (data-driven from the manifest;
  numeric tolerance for JSON; `exists` for regenerated visualizations).
- **`reproduce.yml`** — a GitHub Actions workflow template:
  `fresh clone → reconstruct env → move reference aside → run pipeline →
  compare outputs → badge + publish Pages`.
- **A minimal working example** demonstrating the full loop end-to-end.

## Explicitly cut from the original design

Registry / publisher / version graph / hosted verification (GitHub covers it);
the 10 verification dimensions; the Method/Implementation/Run/Verification
planes; method-evolution taxonomy; cross-agent transfer; LLM review as a gate;
and most of the Python package.

## Honesty boundaries (what this does NOT guarantee)

- **"The whole process was captured" cannot be guaranteed deterministically.**
  CI proves that *what was captured* reproduces (the solvable half); it cannot
  prove that *nothing was left in the conversation* (undeclared filtering, a
  result-dependent threshold, a manual step). That half is best-effort agent
  audit plus honest disclosure of what remains uncovered.
- **Reproduction ≠ scientific correctness.** A green run only means the outputs
  regenerate from the declared inputs; it says nothing about whether the method
  itself is right.
