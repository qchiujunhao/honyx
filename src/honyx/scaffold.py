from __future__ import annotations

import json
from pathlib import Path


MANIFEST = {
    "schema_version": "0.1",
    "method": {
        "id": "example-summary",
        "version": "1.0.0",
        "title": "Example numeric summary",
        "question": "What are the count, sum, and mean of the declared values?",
        "document": "METHOD.md",
    },
    "run": {
        "entrypoint": ["python3", "src/analyze.py"],
        "resources": [{"path": "src", "role": "Reference implementation"}],
        "inputs": [
            {"id": "values", "path": "inputs/values.json", "role": "Numeric values"}
        ],
        "outputs": [
            {
                "id": "summary",
                "path": "results/summary.json",
                "role": "Computed numeric summary",
                "comparison": {"type": "json"},
            }
        ],
    },
    "verification": {"timeout_seconds": 60},
}

METHOD = """# Example numeric summary

## Question

What are the count, sum, and arithmetic mean of the declared numeric values?

## Inputs

`inputs/values.json` contains a JSON object with a `values` array of numbers.

## Method

Count the values, calculate their sum, and divide the sum by the count to obtain
the arithmetic mean. Reject an empty array.

## Outputs

`results/summary.json` contains `count`, `sum`, and `mean`.
"""

RESULT = """# Result

The example input contains three values with a sum of 6 and an arithmetic mean
of 2. Re-run the canonical entrypoint to regenerate the machine-readable result.
"""

ANALYZE = '''from __future__ import annotations

import json
from pathlib import Path


values = json.loads(Path("inputs/values.json").read_text(encoding="utf-8"))["values"]
if not values:
    raise ValueError("values must not be empty")
result = {"count": len(values), "sum": sum(values), "mean": sum(values) / len(values)}
output = Path("results/summary.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
'''


def initialize_package(target: Path) -> list[Path]:
    target.mkdir(parents=True, exist_ok=True)
    files = {
        "honyx.json": json.dumps(MANIFEST, indent=2) + "\n",
        "METHOD.md": METHOD,
        "RESULT.md": RESULT,
        "inputs/values.json": json.dumps({"values": [1, 2, 3]}, indent=2) + "\n",
        "src/analyze.py": ANALYZE,
        "results/summary.json": json.dumps(
            {"count": 3, "mean": 2.0, "sum": 6}, indent=2, sort_keys=True
        )
        + "\n",
    }
    existing = [target / path for path in files if (target / path).exists()]
    if existing:
        names = ", ".join(path.relative_to(target).as_posix() for path in existing)
        raise FileExistsError(f"refusing to overwrite existing files: {names}")

    created: list[Path] = []
    for relative_path, content in files.items():
        destination = target / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        created.append(destination)
    return created

