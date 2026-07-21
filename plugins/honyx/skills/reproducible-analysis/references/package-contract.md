# Package contract

`honyx.json` is a lightweight manifest read by `check.py` (to compare outputs)
and `build_site.py` (to render the showcase). Keep every path package-relative;
reject absolute paths and parent traversal. See `examples/pipeline-demo/`.

```json
{
  "method": {
    "title": "Human title",
    "question": "Scientific question the pipeline answers"
  },
  "inputs": ["data/measurements.csv"],
  "run": "bash run.sh",
  "results_dir": "results",
  "steps": [
    {"id": "clean", "title": "Clean raw measurements",
     "script": "steps/01_clean.py", "produces": ["results/clean.csv"]},
    {"id": "summarize", "title": "Compute per-group statistics",
     "script": "steps/02_summarize.py", "produces": ["results/summary.json"]},
    {"id": "visualize", "title": "Render group-mean bar chart",
     "script": "steps/03_visualize.py", "produces": ["results/chart.svg"]}
  ],
  "outputs": [
    {"path": "summary.json", "compare": "numeric", "tolerance": 1e-9},
    {"path": "chart.svg", "compare": "exists"}
  ]
}
```

- `inputs` are the **raw** inputs only — the sole files kept on the field when CI
  moves the reference outputs aside. Never list outputs, caches, or intermediates.
- `steps` are ordered and each names one script. They give the showcase its
  structure (process + scripts) and document the real pipeline.
- `outputs` paths are relative to `results_dir`. Each has a comparison:
  - `numeric` — parse JSON and compare **numbers** within `tolerance`. Every
    non-number value (strings, booleans) is compared by **exact equality**, and
    keys/lengths must match. So a machine-dependent string in a compared output —
    a timestamp, absolute path, locale-formatted label, or interpreter version —
    will fail the check with no numeric leeway. Keep such values out of compared
    outputs (or split them into an `exists`-only file).
  - `exact` — byte-identical. Use only for genuinely deterministic text files.
  - `exists` — only require regeneration. Use for plots and other presentation
    artifacts whose bytes differ across machines for spurious rendering reasons;
    compare the data behind them (declared as a separate `numeric` output).

Freeze the environment in `requirements.txt` (pinned) so CI rebuilds it. A
human-readable `README.md` should carry the question, the ordered method, all
result-affecting choices, assumptions, limitations, output meaning, and the CI
badge (stating full-data vs subset reproduction).
