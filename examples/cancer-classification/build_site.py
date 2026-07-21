#!/usr/bin/env python3
"""Build the showcase site from the verified run.

Adapted from the skill's build_site.py example for THIS analysis's outputs: a
metrics table (not a group table) and two PNG plots embedded as data URIs (not an
inline SVG). Generated from the regenerated outputs so it cannot drift.
"""
from __future__ import annotations

import base64
import html
import json
from pathlib import Path

OUT_DIR = Path("site")

METRIC_ROWS = [
    ("Test accuracy", "accuracy"),
    ("Test precision", "precision"),
    ("Test recall", "recall"),
    ("Test F1", "f1"),
    ("Test ROC AUC", "roc_auc"),
    ("CV ROC AUC (mean)", "cv_roc_auc_mean"),
    ("CV ROC AUC (std)", "cv_roc_auc_std"),
]


def img(path: Path) -> str:
    data = base64.b64encode(path.read_bytes()).decode()
    return f'<img alt="{html.escape(path.stem)}" src="data:image/png;base64,{data}" style="max-width:100%">'


def main() -> None:
    manifest = json.loads(Path("honyx.json").read_text(encoding="utf-8"))
    method = manifest.get("method", {})
    results = Path(manifest.get("results_dir", "results"))
    metrics = json.loads((results / "metrics.json").read_text(encoding="utf-8"))

    metric_html = "".join(
        f"<tr><td>{html.escape(label)}</td><td>{metrics[key]}</td></tr>"
        for label, key in METRIC_ROWS
        if key in metrics
    )

    steps_html = []
    for step in manifest["steps"]:
        source = Path(step["script"]).read_text(encoding="utf-8")
        steps_html.append(
            f"<section class='step'><h3>{html.escape(step['title'])}</h3>"
            f"<p class='path'>{html.escape(step['script'])}</p>"
            f"<pre><code>{html.escape(source)}</code></pre></section>"
        )

    title = html.escape(method.get("title", "Analysis"))
    question = html.escape(method.get("question", ""))
    model = html.escape(str(metrics.get("model", "")))
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem;line-height:1.5}}
pre{{background:#f6f8fa;padding:1rem;overflow-x:auto;border-radius:6px}}
.path{{color:#666;font-family:monospace;margin:.2rem 0}}
table{{border-collapse:collapse;margin:.5rem 0}}td,th{{border:1px solid #ddd;padding:.3rem .7rem;text-align:left}}
.plots{{display:flex;flex-wrap:wrap;gap:1rem}}.plots>div{{flex:1 1 320px}}
.step{{margin:1.5rem 0}}
</style></head><body>
<h1>{title}</h1>
<p><strong>Question:</strong> {question}</p>
<p><strong>Model:</strong> {model} · seed {metrics.get("seed")} ·
   n_train {metrics.get("n_train")} · n_test {metrics.get("n_test")}</p>
<h2>Metrics</h2>
<table><tr><th>Metric</th><th>Value</th></tr>{metric_html}</table>
<h2>Plots</h2>
<div class="plots">
  <div><h3>ROC curve</h3>{img(results / "roc_curve.png")}</div>
  <div><h3>Feature importance</h3>{img(results / "feature_importance.png")}</div>
</div>
<h2>Pipeline</h2>
{''.join(steps_html)}
<hr>
<p><small>Generated from the verified run. CI reproduction on a fresh clone means
the declared metrics regenerate from the raw input in a rebuilt environment — not
that the model is clinically valid.</small></p>
</body></html>
"""
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "index.html").write_text(page, encoding="utf-8")
    print("wrote site/index.html")


if __name__ == "__main__":
    main()
