#!/usr/bin/env python3
"""Compare regenerated outputs against the reference outputs.

Output declarations are read from honyx.json. The reference directory holds the
committed outputs that were moved aside before the pipeline re-ran, so a passing
comparison means the outputs were regenerated from raw inputs, not reused.

Usage: python3 check.py <generated_dir> <reference_dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

DEFAULT_TOLERANCE = 1e-9


def numbers_match(a: object, b: object, tol: float) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(numbers_match(a[k], b[k], tol) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(numbers_match(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= tol
    return a == b


def main() -> int:
    generated_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results")
    reference_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("reference-outputs")
    manifest = json.loads(Path("honyx.json").read_text(encoding="utf-8"))

    failures: list[str] = []
    for output in manifest["outputs"]:
        rel = output["path"]
        compare = output.get("compare", "exact")
        generated = generated_dir / rel
        reference = reference_dir / rel

        if not generated.exists():
            failures.append(f"{rel}: not regenerated")
            continue
        if compare == "exists":
            print(f"[ok] {rel}: regenerated (exists)")
            continue
        if compare == "numeric":
            tol = float(output.get("tolerance", DEFAULT_TOLERANCE))
            try:
                gen_value = json.loads(generated.read_text(encoding="utf-8"))
                ref_value = json.loads(reference.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                failures.append(f"{rel}: could not read JSON ({exc})")
                continue
            if numbers_match(gen_value, ref_value, tol):
                print(f"[ok] {rel}: numeric match (tol={tol})")
            else:
                failures.append(f"{rel}: numeric mismatch vs reference")
            continue
        # exact byte comparison
        if generated.read_bytes() == reference.read_bytes():
            print(f"[ok] {rel}: byte-identical")
        else:
            failures.append(f"{rel}: bytes differ from reference")

    if failures:
        print("\nREPRODUCTION FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("\nREPRODUCTION OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
