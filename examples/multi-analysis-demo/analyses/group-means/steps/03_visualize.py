#!/usr/bin/env python3
"""Step 3 — render a bar chart of group means as a dependency-free SVG.

The chart is a presentation artifact regenerated from results/summary.json.
Reproducibility is checked on the data (summary.json), not on the SVG bytes.
"""
from __future__ import annotations

import json

IN = "results/summary.json"
OUT = "results/chart.svg"

WIDTH = 400
HEIGHT = 260
PAD = 40
BAR_GAP = 20


def main() -> None:
    with open(IN, encoding="utf-8") as handle:
        summary = json.load(handle)
    groups = summary["groups"]

    max_mean = max((g["mean"] for g in groups), default=1.0) or 1.0
    plot_h = HEIGHT - 2 * PAD
    n = len(groups)
    bar_w = (WIDTH - 2 * PAD - (n - 1) * BAR_GAP) / n if n else 0.0

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" font-family="sans-serif">',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="white"/>',
    ]
    for i, g in enumerate(groups):
        h = plot_h * (g["mean"] / max_mean)
        x = PAD + i * (bar_w + BAR_GAP)
        y = HEIGHT - PAD - h
        parts.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" '
            f'height="{h:.2f}" fill="#4c78a8"/>'
        )
        parts.append(
            f'<text x="{x + bar_w / 2:.2f}" y="{HEIGHT - PAD + 16:.2f}" '
            f'text-anchor="middle" font-size="13">{g["group"]}</text>'
        )
        parts.append(
            f'<text x="{x + bar_w / 2:.2f}" y="{y - 6:.2f}" '
            f'text-anchor="middle" font-size="12">{g["mean"]:g}</text>'
        )
    parts.append("</svg>")

    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write("\n".join(parts) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
