# Verification policy

Keep authoring, review, and verification as separate authorities. You author and
audit; a neutral machine verifies. Your statement that an analysis reproduces
never advances its status — only a CI run does.

## The verifier is a fresh CI clone

A blank GitHub-hosted runner is the clean room, for free. On every push it must:

1. check out only what is committed;
2. reconstruct the environment from the pinned `requirements.txt`;
3. move the reference outputs aside so only raw inputs remain on the field;
4. re-run the pipeline (`run.sh`), regenerating every intermediate and output;
5. compare regenerated outputs against the reference (`check.py`): `numeric` with
   tolerance for data, `exists` for regenerated plots, `exact` only when stable;
6. surface the verdict as the run's pass/fail and a README badge;
7. rebuild and publish the showcase from the regenerated outputs.

The one discipline that a naive `clone && run && diff` misses is step 3: if a
step reads a committed reference output or intermediate as input, a broken step
hides behind a stale answer. Keep only raw inputs; regenerate everything else.

## Match the runner to the work

Free runners are limited (~2–4 vCPU, ~7–16 GB RAM, ~14 GB disk, no GPU, 6 h/job).
Reproduce the full analysis when it fits; otherwise reproduce a declared
representative subset in CI and run the full pipeline on a self-hosted or larger
runner with the same workflow. The badge must state which was verified.

## What a green run does and does not mean

- ✅ The declared outputs regenerate from the declared raw inputs, in a
  reconstructed environment, on a machine that is not the author's.
- ❌ Not proof the method is scientifically correct.
- ❌ Not proof the *whole* process was captured — a clean rerun on committed
  inputs cannot show that source code contains no fixed answer, nor that no step
  was left in the conversation. Stronger evidence would be verifier-owned
  synthetic inputs, input mutation with known relations, a second compatible run,
  or an independent implementation. Report only the level actually tested.
