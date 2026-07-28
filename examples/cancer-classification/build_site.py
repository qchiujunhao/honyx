#!/usr/bin/env python3
"""Build the showcase from the regenerated two-path comparison."""
from __future__ import annotations

import html
import json
from pathlib import Path

OUT_DIR = Path("site")
METRICS = [
    ("Accuracy", "accuracy"),
    ("F1", "f1"),
    ("Test ROC AUC", "roc_auc"),
    ("CV ROC AUC", "cv_roc_auc_mean"),
    ("CV ROC AUC std", "cv_roc_auc_std"),
]


def main() -> None:
    manifest = json.loads(Path("honyx.json").read_text(encoding="utf-8"))
    method = manifest["method"]
    results = Path(manifest["results_dir"])
    comparison = json.loads((results / "comparison.json").read_text(encoding="utf-8"))

    model_headers = [
        ("logistic_regression", "Logistic regression"),
        ("random_forest", "Random forest"),
    ]
    metric_rows = "".join(
        "<tr>"
        f"<th>{html.escape(label)}</th>"
        + "".join(
            f"<td>{comparison['paths'][key][metric]}</td>" for key, _ in model_headers
        )
        + "</tr>"
        for label, metric in METRICS
    )

    steps = []
    for step in manifest["steps"]:
        source = Path(step["script"]).read_text(encoding="utf-8")
        steps.append(
            f"<section class='step'><h3>{html.escape(step['title'])}</h3>"
            f"<p class='path'>{html.escape(step['script'])}</p>"
            f"<pre><code>{html.escape(source)}</code></pre></section>"
        )

    title = html.escape(method["title"])
    question = html.escape(method["question"])
    conclusion = html.escape(comparison["conclusion"])
    selected = html.escape(comparison["selected_path"].replace("_", " "))
    headers = "".join(f"<th>{html.escape(label)}</th>" for _, label in model_headers)
    roc = (results / "roc_comparison.svg").read_text(encoding="utf-8")
    drivers = (results / "model_drivers.svg").read_text(encoding="utf-8")

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:980px;margin:2rem auto;padding:0 1rem;line-height:1.5}}
.finding{{background:#eef6ff;border-left:4px solid #4c78a8;padding:1rem}}
pre{{background:#f6f8fa;padding:1rem;overflow-x:auto;border-radius:6px}}
.path{{color:#666;font-family:monospace;margin:.2rem 0}}
table{{border-collapse:collapse;margin:1rem 0}}td,th{{border:1px solid #ddd;padding:.4rem .7rem;text-align:left}}
.figure svg{{max-width:100%;height:auto}}.step{{margin:1.5rem 0}}
</style></head><body>
<h1>{title}</h1>
<p><strong>Question:</strong> {question}</p>
<div class="finding"><strong>Result:</strong> {conclusion}
The path selected by mean cross-validation ROC AUC was {selected}.
Both paths were judged strong at the declared {comparison['strong_auc_threshold']:.2f}
threshold: {str(comparison['both_paths_reach_threshold']).lower()}.</div>
<h2>Path comparison</h2>
<table><tr><th>Metric</th>{headers}</tr>{metric_rows}</table>
<p>CV ROC AUC range: {comparison['cv_roc_auc_range']:.3f};
test ROC AUC range: {comparison['test_roc_auc_range']:.3f}.</p>
<div class="figure">{roc}</div>
<div class="figure">{drivers}</div>
<h2>Final analysis paths</h2>
{''.join(steps)}
<hr>
<p><small>This page was generated from the rerun results. A passing CI check
means the declared outputs matched the committed references; it does not establish
clinical validity or prove these are the only defensible model paths.</small></p>
</body></html>
"""
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "index.html").write_text(page, encoding="utf-8")
    print("wrote site/index.html")


if __name__ == "__main__":
    main()
