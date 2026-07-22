#!/usr/bin/env python3
"""Build the landing page for a multi-analysis repo. Copy verbatim; it is generic.

Scans analyses/*/honyx.json, runs each analysis's own build_site.py, collects the
per-analysis showcases under site/<slug>/, and writes site/index.html linking
them. Run from the repo root.
"""
from __future__ import annotations

import html
import json
import shutil
import subprocess
import sys
from pathlib import Path

ANALYSES = Path("analyses")
SITE = Path("site")


def main() -> None:
    SITE.mkdir(exist_ok=True)
    cards = []
    for manifest_path in sorted(ANALYSES.glob("*/honyx.json")):
        analysis = manifest_path.parent
        slug = analysis.name
        method = json.loads(manifest_path.read_text(encoding="utf-8")).get("method", {})

        subprocess.run([sys.executable, "build_site.py"], cwd=analysis, check=True)
        destination = SITE / slug
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(analysis / "site", destination)
        cards.append((slug, method.get("title", slug), method.get("question", "")))

    items = "".join(
        f'<li><a href="{html.escape(slug)}/index.html">{html.escape(title)}</a>'
        f"<p>{html.escape(question)}</p></li>"
        for slug, title, question in cards
    )
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Analyses</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:820px;margin:2rem auto;padding:0 1rem;line-height:1.5}}
ul{{list-style:none;padding:0}}
li{{border:1px solid #ddd;border-radius:8px;padding:1rem;margin:1rem 0}}
li a{{font-size:1.2rem;font-weight:600;text-decoration:none}}
li p{{color:#555;margin:.3rem 0 0}}
</style></head><body>
<h1>Analyses</h1>
<p>Each analysis is an independently reproducible package. CI verifies each on a
fresh clone; the links open each analysis's own showcase.</p>
<ul>{items}</ul>
</body></html>
"""
    (SITE / "index.html").write_text(page, encoding="utf-8")
    print(f"built site/ landing with {len(cards)} analyses")


if __name__ == "__main__":
    main()
