# Honyx Package Contract 0.1

The package root contains `honyx.json`, human-facing method and result documents,
declared implementation resources, declared inputs, and reference outputs.

```text
analysis-package/
├── honyx.json
├── METHOD.md
├── RESULT.md
├── src/
├── inputs/
└── results/
```

`honyx.json` is the machine entrypoint. All file paths are package-relative. The
v0 verifier rejects absolute paths and `..` traversal.

## Minimal manifest

```json
{
  "schema_version": "0.1",
  "method": {
    "id": "group-summary",
    "version": "1.0.0",
    "title": "Group summary",
    "question": "What is the mean value in each group?",
    "document": "METHOD.md"
  },
  "run": {
    "entrypoint": ["python3", "src/analyze.py"],
    "resources": [
      {"path": "src", "role": "Reference implementation"}
    ],
    "inputs": [
      {"id": "measurements", "path": "inputs/measurements.csv", "role": "Measurements"}
    ],
    "outputs": [
      {
        "id": "summary",
        "path": "results/summary.json",
        "role": "Group statistics",
        "comparison": {"type": "json"}
      }
    ]
  },
  "verification": {"timeout_seconds": 60}
}
```

## Allowlisted verification

The verifier creates a new package-local workspace and copies only paths listed
under `run.resources` and `run.inputs`. It does not copy `run.outputs`. It then
executes `run.entrypoint` from the clean workspace and compares newly generated
outputs with reference outputs retained outside that workspace.

Supported comparison types:

- `exists`: require the output to be generated;
- `exact`: require byte-identical content;
- `json`: compare parsed JSON values, ignoring formatting and object key order.

Successful v0 verification establishes regeneration and output equivalence in
the current software environment. It does not establish environment
reconstruction, scientific correctness, method conformance, or independent
implementation.

