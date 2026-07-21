# Model fitting acceptance check

- final row count used by the accepted test: 150 nonempty records
- included/excluded row-scope evidence: all 150 nonempty source records included; one wholly empty trailing record treated as file formatting; no scientific observation excluded
- endpoint, baseline, and control decision: not applicable; all three species are comparison groups
- endpoint-scope sensitivity results: not applicable
- response and predictor definitions: petal length in centimeters; three-level categorical species label
- mixture component-label validation and ratio-token order: not applicable
- transformations and duplicate/replicate handling: no response transformation; prefix removed only from output labels; every nonempty record retained without deduplication or collapse
- candidate models and selection result: one predeclared ordinary one-way F statistic; no candidate selection
- optimization/evaluation domain: all 150 declared records; 20,000 label permutations over the same fixed response values
- final quantity type and extraction rule: observed F statistic and add-one-corrected Monte Carlo permutation p-value using random seed 1936
- whether any substitute was used: no
- why the answer matches the requested scientific quantity: it directly evaluates whether between-species mean separation in petal length is large relative to within-species variation and estimates the configured randomization-tail probability

## Acceptance evidence

- Technical integrity: the input has 150 well-formed nonempty records, the output is valid nontrivial JSON, and all values are finite.
- Internal consistency: three groups each contain 50 records; their counts sum to 150; between and within sums of squares sum to the reported total; eta squared equals between divided by total; the reported p-value equals `1 / 20001` because exceedances are zero.
- Independent calculation: R reproduced group counts, means, sample standard deviations, degrees of freedom, sums of squares, and the observed F statistic.
- Plausibility: the very large F statistic is consistent with group means separated by several centimeters while within-group sample standard deviations are below 0.6 cm. The reported effect magnitude and permutation result agree in direction.
- Branch discipline: no rescue branch, alternate row scope, or substitute statistic was used.

The result is accepted as a fixed-method computational result. Acceptance does
not establish the source sampling design, causal interpretation, or universal
scientific validity.

