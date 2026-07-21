# Per-group measurement summary

## Scientific question

What are the number of observations and arithmetic mean of the numeric
measurements in each declared experimental group?

## Input

`inputs/measurements.csv` contains one observation per row with the following
columns:

- `group`: a non-empty group identifier;
- `value`: a finite numeric measurement.

## Method

1. Parse every row as one observation.
2. Reject missing group identifiers, non-numeric values, and non-finite values.
3. Partition observations by exact group identifier.
4. For each group, count observations and calculate the arithmetic mean.
5. Sort groups lexicographically in the output so presentation does not depend on
   input order.

No observations are removed and no missing values are imputed.

## Output

`results/summary.json` contains a `groups` object. Each group has `count` and
`mean` fields. The file also reports the total number of observations.

## Scope and limitations

The method is descriptive. It does not estimate uncertainty, test group
differences, identify outliers, or support weighted observations. Adding any of
those operations would constitute a different method.

