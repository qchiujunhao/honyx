#!/usr/bin/env python3
"""Step 2 — bar chart of pass rate per method (dependency-free SVG)."""
from __future__ import annotations

import json

IN = "results/passrate.json"
OUT = "results/chart.svg"

WIDTH = 400
HEIGHT = 260
PAD = 40
BAR_GAP = 20


def main() -> None:
    methods = json.loads(open(IN, encoding="utf-8").read())["methods"]
    plot_h = HEIGHT - 2 * PAD
    n = len(methods)
    bar_w = (WIDTH - 2 * PAD - (n - 1) * BAR_GAP) / n if n else 0.0

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" font-family="sans-serif">',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="white"/>',
    ]
    for i, m in enumerate(methods):
        h = plot_h * m["pass_rate"]  # pass_rate is already in [0, 1]
        x = PAD + i * (bar_w + BAR_GAP)
        y = HEIGHT - PAD - h
        parts.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" '
            f'height="{h:.2f}" fill="#59a14f"/>'
        )
        parts.append(
            f'<text x="{x + bar_w / 2:.2f}" y="{HEIGHT - PAD + 16:.2f}" '
            f'text-anchor="middle" font-size="13">{m["method"]}</text>'
        )
        parts.append(
            f'<text x="{x + bar_w / 2:.2f}" y="{y - 6:.2f}" '
            f'text-anchor="middle" font-size="12">{m["pass_rate"]:g}</text>'
        )
    parts.append("</svg>")
    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write("\n".join(parts) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
