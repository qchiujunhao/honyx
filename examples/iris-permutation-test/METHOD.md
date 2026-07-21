# Iris petal-length group difference test

## Scientific question

Does petal length differ among the three Iris species represented in the
corrected UCI dataset?

This analysis evaluates association between species labels and petal length. It
does not establish that species identity causally produces a measurement change.

## Input and row scope

The declared input is the corrected UCI `bezdekIris.data` file described in
`SOURCE.md`. Every nonempty record represents one observed plant and contains:

1. sepal length in centimeters;
2. sepal width in centimeters;
3. petal length in centimeters;
4. petal width in centimeters;
5. species label.

Use all complete nonempty records. Do not collapse duplicate measurements or
aggregate records before testing. Ignore wholly empty records as file formatting.
Reject nonempty records with a missing field, non-finite measurement, unexpected
species label, or incorrect number of fields.

## Method

1. Parse petal length as the response and species as a three-level categorical
   predictor.
2. Calculate each species' sample size, arithmetic mean, sample standard
   deviation, minimum, and maximum petal length.
3. Calculate the ordinary one-way ANOVA F statistic from between-group and
   within-group sums of squares.
4. Calculate eta squared as between-group sum of squares divided by total sum of
   squares.
5. Hold observed petal lengths fixed and randomly permute species labels 20,000
   times using Python's `random.Random` with seed 1936.
6. Recalculate the F statistic for every permutation.
7. Define an exceedance as a permuted F statistic greater than or equal to the
   observed F statistic.
8. Calculate the Monte Carlo p-value as `(1 + exceedances) / (1 + 20000)`.
9. Write group summaries, degrees of freedom, sums of squares, F, eta squared,
   permutation settings, exceedance count, and p-value to
   `results/analysis.json`.

The add-one correction prevents a zero reported p-value and makes the smallest
possible value `1 / 20001` for this run.

## Parameters fixed for this Method version

- response: petal length;
- grouping variable: species;
- expected groups: setosa, versicolor, and virginica;
- permutations: 20,000;
- random seed: 1936;
- tail: permuted F greater than or equal to observed F;
- missing/malformed records: reject;
- duplicate handling: retain every nonempty source row.

Changing the response variable, group definition, F statistic, permutation
mechanism, tail rule, p-value correction, row scope, or record handling creates a
different Method version. Increasing the permutation count or changing the seed
changes the numerical procedure and must be declared as a new version or an
explicit sensitivity Run.

## Assumptions and limitations

- The F statistic summarizes separation of group means relative to within-group
  variation. The permutation p-value relies on label exchangeability under the
  null hypothesis.
- The source contains 50 records for each species, but this package does not
  establish how the plants were sampled or whether observations are independent.
- The p-value resolution is limited by the fixed number of permutations.
- A small p-value does not measure effect magnitude; eta squared and group
  summaries are reported separately.
- The analysis does not classify new plants and does not adjust for sepal or
  petal-width measurements.

## Canonical execution

Run from the package root:

```bash
python3 src/analyze.py
```

The implementation requires only Python's standard library and does not access
the network during analysis.

