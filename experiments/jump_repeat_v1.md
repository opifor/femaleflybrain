# jump_repeat_v1: full-protocol within-session repeatability

Version 2; registered before execution. no calibration; descriptive
Source HEAD: 2817d540673b0100ac1c5e007c2dc09036f69f13. hash_basis: lf.
The SHA-256 of this complete LF-normalized text and all simulation inputs is
saved in records/jump_repeat_v1_freeze.json before the first run. Binary NPZ
hashes use original bytes. No self-referential hash is inserted into this text.

Use the intact FAFB v783 female graph, female_no_v1 Protocol.read defaults,
CUDA fast_gpu float32 and the unchanged runner.run. Reuse
female_readouts.observed_run and two_female.select_groups without copying or
adapting the simulation loop, AST, kernel, observer, ear, dictionary or drive.
Four conditions, seeds 0-9 batched together, shiu then jump, twenty 50 ms
windows, dt=0.2 ms, windows 4-19 measured. Same graph and groups as historical.

Run the complete protocol three consecutive times in one Python process,
then once in each of three new Python processes, sequentially on this same
machine/session/driver. Six full runs; no quick or selective simulator runs.
The full batch replaces the initial four-pair single-seed proposal. Four
conditions x ten seeds x two groups gives 80 seed values per kernel per
repeat (160 across both kernels), not 160 per kernel. Retain every value.

Read vpoDN and pC1 rates with the existing slice/window arithmetic. Save
integer counts per selected cell, seed, 5 ms slice and all twenty windows,
with graph indices/body IDs and original runner records under
build/records-raw/jump_repeat_v1/. Compare raw arrays by shape/dtype/bytes;
compare float64 rates exactly, with no tolerance. Historical comparisons
use female_no_v1_experiment.json; readouts comparisons use the female
summary in female_readouts_v1_experiment.json, cross-checked against its
checks.json datasets.female.historical.comparisons. Old raw counts are not
assumed available: baseline spike deltas are inferred from rate x 0.8 s x
group size, rounded to integer, and explicitly labelled as inferred.

For each kernel report six-by-six repeat equality matrices (raw and rates),
all differing condition/seed/group identities, baseline comparisons,
pairwise changed-bin counts, L1 and maximum-bin spike differences, signed
total differences, and ignition fractions strictly above 30 Hz per cell
or neuron over measured windows. Full row matrix: condition/seed/kernel,
historical, readouts, inproc1-3, separate1-3. Reconstruct summaries from saved
raw data and require observer-to-runner equality and complete coverage.

Classify jump and shiu separately:
- run-to-run divergent: any repeat pair differs in selected raw counts or rates.
- session-stable, historical-divergent: all repeats agree, but at least one
  historical or readouts seed value differs.
- fully reproducible: all repeat raw counts and rates agree and all saved
  historical/readouts seed values agree.

These classes concern observed counts and rates, not internal voltage or
exact spike timestamps. Divergence is not bitwise reproducible on this
execution chain; floating-point/atomic summation order is a candidate
mechanism, not an isolated causal finding. Stable historical divergence is
consistent with session/driver/build differences but cannot distinguish them.
Shiu is an expected equal control; a difference is retained descriptively.
No behavioral inference, gain adjustment or calibration. Historical
disagreement is an outcome, not a reason to discard a completed experiment.

Freeze before runs and verify inputs before/after; synthetic small tests and
an opt-in deliberate failing pytest probe validate the comparison harness.
Use the supplied Python/dependency chain and pytest -p no:cacheprovider.
Allow approximately seven minutes for simulation within a 25-minute task
budget; incomplete execution is partial with the repeat count retained.
English, UTF-8 without BOM, LF. No git writes, external service writes,
restricted-tree inspection, machine paths or personal names in artifacts.
