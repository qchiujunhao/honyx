# Iris petal-length group difference result

## Data included

The run used all 150 nonempty plant records in the corrected UCI input. Each of
the three species contributed 50 observations.

## Group summaries

| Species | Count | Mean petal length (cm) | Sample SD (cm) | Range (cm) |
| --- | ---: | ---: | ---: | ---: |
| setosa | 50 | 1.462 | 0.173664 | 1.0–1.9 |
| versicolor | 50 | 4.260 | 0.469911 | 3.0–5.1 |
| virginica | 50 | 5.552 | 0.551895 | 4.5–6.9 |

## Test result

The observed one-way group statistic was:

```text
F(2, 147) = 1180.161182252981
```

Between-group differences accounted for approximately 94.14% of the total
petal-length sum of squares (`eta_squared = 0.9413717190573679`).

Using 20,000 label permutations and random seed 1936, zero permuted statistics
were at least as large as the observed statistic. With the declared add-one
correction:

```text
p = (1 + 0) / (1 + 20000)
  = 0.00004999750012499375
```

At this configured Monte Carlo resolution, the data provide strong evidence that
petal-length distributions are associated with species labels. This does not
establish causation, sampling representativeness, or the size of every pairwise
species contrast.

## Independent numerical check

An independent R one-way ANOVA reproduced the three sample sizes, group means,
sample standard deviations, between-group degrees of freedom (`2`), residual
degrees of freedom (`147`), between-group sum of squares (`437.1028`), residual
sum of squares (`27.2226`), and F statistic (`1180.161`, rounded). R's conventional
parametric tail probability was below `2e-16`; that value is an independent
sanity check and is not substituted for the declared permutation p-value.

## Machine-readable evidence

All reported numerical results are present in `results/analysis.json`. Honyx
regenerates that file from the declared input in a separate workspace and
compares parsed JSON values.

