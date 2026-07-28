# Group mean summary

## Question and result

**What is the mean value in each group?**

| Group | Included rows | Mean |
| --- | ---: | ---: |
| A | 3 | 11.0 |
| B | 3 | 21.0 |
| C | 2 | 31.0 |

The only raw input is `data/measurements.csv`, a small hand-authored
demonstration dataset. Cleaning trims whitespace and excludes blank rows or
rows whose group or numeric value is missing or invalid. The
`C,not-a-number` row is therefore excluded. Valid rows are sorted by group and
value before each arithmetic mean is calculated.

These are descriptive summaries of the supplied rows. The data do not define a
sampling population, so the analysis reports no uncertainty and supports no
causal or population-level conclusion.

## Reproduce

The package uses only the Python standard library:

```bash
reference_root="$(mktemp -d)"
mv results "$reference_root/results"
bash run.sh
python3 check.py results "$reference_root/results"
python3 build_site.py
```

The check compares `summary.json` numerically at absolute tolerance `1e-9` and
requires the SVG chart to be regenerated as a non-empty file. A pass establishes
only that the declared outputs regenerated from the declared input and matched
the committed references.
