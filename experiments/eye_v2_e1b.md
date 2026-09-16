# eye_v2 E1b preregistration

Decision owner: the operator. Budget: 40 minutes from first inspection.
This document is frozen with SHA-256 before implementation or data evaluation.
Text hashes use LF UTF-8 without BOM; compressed input hashes use exact bytes.
No network simulation, neuron drive, fitting, git writes, or changes to the
existing eye, retinotopy, or world modules are permitted.

## Question and data

Are published column assignments consistent with local graph wiring?
Use read_assignments and join_columns on the supplied FAFB v783 graph and
column_assignment.csv.gz. Expected join: 45,528 cells, 31 assignment types,
1,581 hemisphere-qualified column keys. Fail closed on a mismatch with these
counts or on graph/publication type or side disagreements. No other anatomical
data or external project code is used. The E1 coverage and report are context.
Only strictly positive raw count edges enter; signed data and sign never weight
the prediction. CSR rows are presynaptic and columns postsynaptic.

## Holdout and estimator

Order assigned cells by graph index. NumPy default_rng(3801) permutes this
population once; array_split into five groups defines disjoint folds of sizes
differing by at most one. Each cell is held out exactly once (about 20% per
fold). All cells in the target's fold are unavailable as coordinate donors,
including the target itself and any self-loop. Donors may be any of the 31
assigned types. No held-out coordinates enter the estimator.

For each held-out cell, use assigned, non-held-out, same-hemisphere neighbors.
Predict p and q separately by the count-weighted lower median: the smallest
coordinate whose cumulative weight is at least half the total. No rounding,
nearest-column projection, or fitting follows. The resulting integer pair
need not be an occupied column. Pool incoming and outgoing counts for the
primary prediction; reciprocal edges contribute both counts. Also evaluate
incoming-only and outgoing-only predictions independently.

Count opposite-hemisphere assigned neighbors and their synapses separately,
both before and after the fold exclusion; they never enter prediction.
Directional edge incidences are counted separately, including in pooled totals.
Cells without eligible positive weight are unpredictable and stay in all
fraction denominators. Their distance is positive infinity for the primary
median and mean; also report finite-only median and mean for interpretation.
JSON represents nonfinite summaries as null with an explicit nonfinite flag.

## Metrics and controls

Hex distance is (abs(delta_p)+abs(delta_q)+abs(delta_p+delta_q))/2.
Pool held-out cells across folds, without averaging fold medians. Report count,
predictable/unpredictable, median distance, mean distance, d<=1 and d<=2 counts
and fractions, overall and per assignment type, for all three directions.
Save per-cell folds, predictions, distances, and excluded cross-side counts.

Control: default_rng(3802), five successive independent permutations of paired
(p,q) among assigned cells within each hemisphere (left then right). Types,
IDs, graph, hemisphere, and fold membership remain fixed. In each replicate
both donor coordinates and target reference coordinates use that permuted
assignment; use precisely the same estimator and metric denominators.
Do not permute p and q independently or restrict permutations within type.

The sole numerical gate, on pooled bidirectional full-run values, is:
real median d < minimum of the five permutation median d values AND
real d<=2 fraction >= 0.5. If true report "map wiring-consistent"; otherwise
report "not shown". Undefined comparisons cannot pass. No per-type or
directional threshold is an additional gate; no p-value is inferred from five
permutations. This is consistency, not independent validation: the publication
assignments may themselves have been derived from wiring. Holding out cells
here does not remove possible dependence in how the original map was built.

## Sequential-ID descriptive comparison

The legacy eye produces azimuth, not (p,q), so its actual output is not
comparable in hex distance. Use a declared crude surrogate for all assigned
types: within each type and hemisphere, sort exact body IDs and map rank r
linearly to that hemisphere's published p minimum and maximum, rounding with
floor(x+0.5); q=0. For a singleton use the rounded midpoint. Apply the same
holdouts and estimator to these pseudo-assignments and score against those
pseudo-assignments. Also report direct surrogate-to-publication hex error.
This is not an execution or reproduction of the legacy eye. It has no gate.
The numerical gate alone cannot logically exclude every possible ID mapping.

## Quick mode and evidence

Quick mode scores only fold zero targets of L1, Mi1, T4a, retaining the full
31-type donor population and full fold-zero exclusion. Run all five controls
but never issue the full numerical verdict from quick mode. Full mode scores
five folds and all 31 types. Save quick outputs only in the authorized raw
directory; full results go to the four authorized summary records.

Use the prescribed Windows CPython 3.12 and supplied dependency chain, locale
C, bytecode disabled, pytest plugin autoload disabled and -p no:cacheprovider.
Synthetic hex-grid/CSR tests must detect wrong direction, weights, distance,
held-out leakage, cross-side leakage, ignored unpredictable denominators,
broken folds, broken paired permutation, and incorrect gate boundaries.
An intentional failing pytest probe must produce one failure and exit 1.
Record actual pass/fail counts and exits, source and file hashes, git status,
runtime, software versions, and deviations. Recheck frozen hashes after work.
No alternative environment is acceptance evidence. If the budget prevents
completion, report partial status. Summary records together must be <=5 MB.
Audit excludes its own recursive hash and states that exclusion explicitly.
All deliverables use English, LF and UTF-8 without BOM, with no machine paths.
