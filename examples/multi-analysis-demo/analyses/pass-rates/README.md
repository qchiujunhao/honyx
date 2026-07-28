# Pass rates by method

## Question and result

**What fraction of students pass, using score 60 or higher, under each method?**

| Method | Included scores | Pass rate |
| --- | ---: | ---: |
| A | 4 | 0.50 |
| B | 4 | 0.75 |
| C | 4 | 0.75 |

The only raw input is `data/scores.csv`, a small hand-authored demonstration
dataset. Method names are trimmed. Rows with a missing method, missing score, or
non-numeric score are excluded; this removes `A,not-taken`. A score is counted
as passing when it is greater than or equal to the fixed threshold 60. Rates
are rounded to six decimal places and methods are sorted by name.

The rates describe only these supplied rows. There is no defined sampling
population, uncertainty interval, covariate adjustment, or causal comparison,
and the result should not be interpreted as evidence that one method is better.

## Reproduce

The package uses only the Python standard library:

```bash
reference_root="$(mktemp -d)"
mv results "$reference_root/results"
bash run.sh
python3 check.py results "$reference_root/results"
python3 build_site.py
```

The check compares `passrate.json` numerically at absolute tolerance `1e-9` and
requires the SVG chart to be regenerated as a non-empty file. A pass establishes
only that the declared outputs regenerated from the declared input and matched
the committed references.
