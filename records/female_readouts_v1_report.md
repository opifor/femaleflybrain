# Female readout baselines

FAIL-CLOSED: historical vpoDN/pC1 equality failed. Descriptive tables only; no behavioral decision.

## Status note (added after review)

The lane declared FAIL-CLOSED because six jump-kernel seed values did not reproduce the historical records bit for bit. The shiu-kernel comparison reproduced all 160 historical vpoDN and pC1 values exactly, so every shiu-kernel table in this report stands as delivered. The jump kernel is descriptive only and the repository does not guarantee its bitwise reproducibility (README, fast backend section: aggregation changes floating-point addition order for jump voltage updates; docs/experiments.md: paired seeds do not imply bitwise reproducibility on the CUDA chain); the preregistration's exact-equality condition for jump overreached that guarantee. The jump columns therefore remain labelled an open anomaly (integer spike differences in a near-saturated regime, ignition 0.70-1.0), and the cheapest next step is a single repeat of the FAFB jump run to separate run-to-run divergence from a session or driver difference. Two reading notes from the audit: FAFB CB1484's 1.40 Hz comes from one of its six cells (8.25 Hz) and CB2364's 0.44 Hz from two cells; in BANC under song the A2-candidate group reaches 147.9 Hz and AVLP083's two cells sit at 181.5 and 53.6 Hz, so group means hide single-cell drive.

## Preregistration (verbatim)

# female_readouts_v1: descriptive baseline reading columns

Version: 1. Freeze this text with SHA-256, hash_basis: lf, before any run.
FAFB v783 (build/graph_female.npz) and BANC v888 (build/graph_banc.npz)
are used intact. This is a preregistered descriptive measurement, with no
confirmatory threshold, behavioral decision, gain change or calibration.

## Unchanged execution

Call runner.run directly with the existing Protocol defaults; do not copy
its simulation loop. Use CUDA fast_gpu float32 and unchanged Parameters.
Reuse two_female.select_groups for the five original groups, checking them
against dictionary API selections and the original saved identities.
FAFB SAG is the exact AN_SMP_2/AN_FLA_SMP_2/ANXXX983 union. BANC SAG is
the dictionary ANXXX983 selection. BANC pC1 requires
superclass=central_brain_intrinsic; this is not a global graph filter.
Only JO-A, JO-B and SAG are driven, in their original order, including
zero-rate targets. Additional dictionary populations are read-only.

Conditions: virgin_song, mated_song, virgin_silence, mated_silence.
Virgin SAG: tonic 50 Hz Poisson; mated SAG: 0 Hz. Song amplitude 1,
pulse mixture 0.7; silence has zero waveform. Seeds 0 through 9, each
condition and kernel from rest. Primary kernel shiu; jump is descriptive.
Run both kernels through the existing runner if the 40-minute task budget
permits. Incomplete coverage is partial, never a complete result.
Quick: female only, seeds 0,1, six windows, four warm-up windows.
Full: both graphs, four conditions, ten seeds, twenty 50 ms windows,
first four excluded and last sixteen measured; dt=0.2 ms, 250 steps/window.
Quick is preliminary and is run before full; it is not acceptance evidence
for equality to the full historical records.

The unchanged song and ear implement 22050 Hz sampling, 35 ms pulse IPI,
4 ms Hann pulses with 250 Hz carrier, and 150 Hz sine song, with continuous
sample clock and phase. Fourth-order Butterworth bands are JO-A 100-500 Hz
and JO-B 500-2500 Hz; sosfiltfilt padlen=27 per window. Each 5 ms slice
uses 180*clip(band RMS/RMS_FULL,0,1) Hz. Record RMS_FULL, JO_MAX_HZ=180,
scale=1.0 and unchanged Shiu W_syn. No additional input or background drive.

## Readouts and observation

The fixed 16-group denominator is: vpoDN, pC1 (pooled a-e), vpoEN, vpoIN,
AVLP008, DNp13/pMN1, oviDN, vpoEN-input:CB1484, vpoEN-input:CB2364,
vpoEN-input:CB1383, vpoEN-input:WED104, vpoEN-input-top10,
vpoEN-gate:AVLP083, AMMC-B1-candidate, AMMC-B1-candidate-graph,
A2-candidate. AVLP008 uses the existing vpoDN-GABA-input dictionary entry.
All other additional names use flybench.dictionary.groups directly.
No aliases are invented. Save selected counts, graph indices, body IDs,
types, selectors and status for each graph. An empty group is absent,
with null rates and empty cell arrays, and remains in every table denominator.
Overlapping groups are not a partition and must not be summed.

A temporary Python return-event profiler reads existing run_batch results
only when called directly by runner.run. It copies selected integer spike
counts after each 5 ms slice, without changing any function, simulator,
state, random generator, drive, hook or dictionary definition. Restore the
previous profiler in finally; reject an already active profiler. Check exact
slice coverage by kernel/condition/window/slice. Store raw selected-cell
counts and original runner windows under build/records-raw/female_readouts_v1/.
The extra populations are not passed to the simulator as drive targets.

## Planned summaries and checks

For every graph, kernel, condition and group, report mean Hz/cell +/- SE
across seed means (sample SD/sqrt(n), n=10 full). Cell means in JSON average
all measured windows and seeds, with body IDs aligned to frozen indices.
Group rates follow the runner's slice-to-window arithmetic so the original
vpoDN/pC1 comparisons can be exact. Cell rates use integer spike totals
divided by measured seconds. No warm-up samples enter summaries.

Silence band: separately for mated_silence and virgin_silence, group mean
<=1 Hz AND every cell's across-seed mean <=3 Hz. Report both numbers,
whether the band holds, and whether all measured counts are zero. A
nonzero rate inside the band is distinguished from exact zero. Absent
groups have no band classification. This describes the scope to measure
suppression below a baseline and makes no physiological decision.

Report seed-paired song minus silence within each state and virgin minus
mated within each stimulus, for every group/kernel/graph, mean +/- paired
SE and all seed differences; pair by seed identity. No difference threshold.
Ignition is the fraction of measured seed-windows whose network mean is
strictly >30 Hz/neuron, separately by condition; also report the analogous
group-mean >30 Hz/cell fraction as a descriptive readout diagnostic.

For both kernels and all four conditions and ten seeds, require exact
vpoDN/pC1 equality to records/female_no_v1_experiment.json (FAFB) and
records/two_female_v1_experiment.json (BANC). Check historical FAFB summaries
embedded in two_female as well. Require exact equality of the observer's
vpoDN/pC1 seed means to the same-run runner output. Any mismatch is
FAIL-CLOSED, with the failed comparisons retained in checks.json. Check
protected input hashes before and after execution, and verify raw-to-summary
reconstruction. Synthetic tests cover selection, absent handling, warm-up,
strict ignition, paired statistics, exact equality failure and observation
without changed runner results. Run a deliberate pytest failure probe.

Compact records together stay below 5 MB; raw arrays/windows remain in build.
The report embeds this preregistration verbatim and is rendered from saved
JSON. UTF-8 without BOM, LF, English. No restricted source trees are read;
only the operator-supplied dependency directory is used by the runtime.
No git write commands. No machine paths or personal names in artifacts.
Graph population, annotation and sign-source differences limit comparison;
BANC includes ventral nerve cord populations. Anatomy alone does not assign
function to the diagnostic entries. There is no male graph execution.
these readouts do not establish hearing, refusal or mating
the ear is not calibrated


## Execution and selectors

Preregistration SHA-256 (LF): `d396254eb8062673eeac243f265bc5566526c1dd157fa8f22df9b8b2956a1d8c`.
Full execution including I/O: 143.537 s. CUDA fast_gpu float32; two graphs, two kernels, four conditions, ten seeds (160 trials).
Cell arrays follow the body IDs and indices in populations.groups; raw NPZ axes are kernel, condition, window, 5 ms slice, selected cell, seed.

| Group | FAFB count | BANC count | FAFB selector | BANC selector |
|---|---:|---:|---|---|
| vpoDN | 2 | 2 | `{"type_re": "^(?:DNp37&#124;vpoDN)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` | `{"type_re": "^(?:DNp37&#124;vpoDN)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` |
| pC1 | 10 | 10 | `[{"type_re": "^pC1a$", "side": null, "superclass": null, "nt": null, "cell_class": null}, {"type_re": "^pC1b$", "side": null, "superclass": null, "nt": null, "cell_class": null}, {"type_re": "^pC1c$", "side": null, "superclass": null, "nt": null, "cell_class": null}, {"type_re": "^pC1d$", "side": null, "superclass": null, "nt": null, "cell_class": null}, {"type_re": "^pC1e$", "side": null, "superclass": null, "nt": null, "cell_class": null}]` | `[{"type_re": "^pC1a$", "side": null, "superclass": null, "nt": null, "cell_class": null}, {"type_re": "^pC1b$", "side": null, "superclass": null, "nt": null, "cell_class": null}, {"type_re": "^pC1c$", "side": null, "superclass": null, "nt": null, "cell_class": null}, {"type_re": "^pC1d$", "side": null, "superclass": null, "nt": null, "cell_class": null}, {"type_re": "^pC1e$", "side": null, "superclass": null, "nt": null, "cell_class": null}]` |
| vpoEN | 4 | 6 | `{"type_re": "^vpoEN$", "side": null, "superclass": null, "nt": null, "cell_class": null}` | `{"type_re": "^vpoEN$", "side": null, "superclass": null, "nt": null, "cell_class": null}` |
| vpoIN | 6 | 4 | `{"type_re": "^CB1385$", "side": null, "superclass": null, "nt": null, "cell_class": null}` | `{"type_re": "^CB1385$", "side": null, "superclass": null, "nt": null, "cell_class": null}` |
| AVLP008 | 10 | 8 | `{"type_re": "^AVLP008$", "side": null, "superclass": null, "nt": null, "cell_class": null}` | `{"type_re": "^AVLP008$", "side": null, "superclass": null, "nt": null, "cell_class": null}` |
| DNp13/pMN1 | 2 | 2 | `{"type_re": "^(?:DNp13&#124;pMN1)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` | `{"type_re": "^(?:DNp13&#124;pMN1)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` |
| oviDN | 6 | 6 | `{"type_re": "^oviDN(?:[ab](?:_[ab])?)?$", "side": null, "superclass": null, "nt": null, "cell_class": null}` | `{"type_re": "^oviDN(?:[ab](?:_[ab])?)?$", "side": null, "superclass": null, "nt": null, "cell_class": null}` |
| vpoEN-input:CB1484 | 6 | 0 | `{"type_re": "^(?:CB1484)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` | `{"type_re": "^(?:CB1484)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` |
| vpoEN-input:CB2364 | 8 | 8 | `{"type_re": "^(?:CB2364)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` | `{"type_re": "^(?:CB2364)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` |
| vpoEN-input:CB1383 | 6 | 4 | `{"type_re": "^(?:CB1383)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` | `{"type_re": "^(?:CB1383)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` |
| vpoEN-input:WED104 | 2 | 1 | `{"type_re": "^(?:WED104)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` | `{"type_re": "^(?:WED104)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` |
| vpoEN-input-top10 | 43 | 31 | `{"type_re": "^(?:CB1484&#124;CB2364&#124;CB1383&#124;WED104&#124;AN_AVLP_8&#124;CB2633&#124;PVLP021&#124;CB1869&#124;CB2449&#124;CB1614)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` | `{"type_re": "^(?:CB1484&#124;CB2364&#124;CB1383&#124;WED104&#124;AN_AVLP_8&#124;CB2633&#124;PVLP021&#124;CB1869&#124;CB2449&#124;CB1614)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` |
| vpoEN-gate:AVLP083 | 2 | 2 | `{"type_re": "^AVLP083$", "side": null, "superclass": null, "nt": null, "cell_class": null}` | `{"type_re": "^AVLP083$", "side": null, "superclass": null, "nt": null, "cell_class": null}` |
| AMMC-B1-candidate | 39 | 38 | `{"type_re": "^(?:CB1078&#124;CB1542&#124;SAD053)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` | `{"type_re": "^(?:CB1078&#124;CB1542&#124;SAD053)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` |
| AMMC-B1-candidate-graph | 23 | 26 | `{"type_re": "^(?:CB1076&#124;CB1125&#124;CB2789)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` | `{"type_re": "^(?:CB1076&#124;CB1125&#124;CB2789)$", "side": null, "superclass": null, "nt": null, "cell_class": null}` |
| A2-candidate | 4 | 2 | `{"type_re": "^CB1817[ab]$", "side": null, "superclass": null, "nt": null, "cell_class": null}` | `{"type_re": "^CB1817[ab]$", "side": null, "superclass": null, "nt": null, "cell_class": null}` |

BANC pC1 also requires central_brain_intrinsic. Counts include every selected cell, including cells without a direct vpoEN edge. All 16 groups remain in the denominator; absent is not a zero-rate measurement. Groups overlap.

## female: condition means

Hz/cell +/- SE across ten seeds; warm-up excluded.

| Kernel | Group | virgin_song | mated_song | virgin_silence | mated_silence |
|---|---|---:|---:|---:|---:|
| shiu | vpoDN | 38.9375 +/- 1.37579 | 0 +/- 0 | 39.125 +/- 1.32484 | 0 +/- 0 |
| shiu | pC1 | 27.375 +/- 0.976637 | 0 +/- 0 | 27.4625 +/- 0.922152 | 0 +/- 0 |
| shiu | vpoEN | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | vpoIN | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | AVLP008 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | DNp13/pMN1 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | oviDN | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | vpoEN-input:CB1484 | 1.39583 +/- 0.164482 | 1.45833 +/- 0.158358 | 0 +/- 0 | 0 +/- 0 |
| shiu | vpoEN-input:CB2364 | 0.4375 +/- 0.100993 | 0.453125 +/- 0.0972997 | 0 +/- 0 | 0 +/- 0 |
| shiu | vpoEN-input:CB1383 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | vpoEN-input:WED104 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | vpoEN-input-top10 | 0.276163 +/- 0.0358003 | 0.287791 +/- 0.0353251 | 0 +/- 0 | 0 +/- 0 |
| shiu | vpoEN-gate:AVLP083 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | AMMC-B1-candidate | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | AMMC-B1-candidate-graph | 0.0380435 +/- 0.00830177 | 0.0380435 +/- 0.00830177 | 0 +/- 0 | 0 +/- 0 |
| shiu | A2-candidate | 8.53125 +/- 0.369902 | 8.4375 +/- 0.357824 | 0 +/- 0 | 0 +/- 0 |
| jump | vpoDN | 137.25 +/- 23.1264 | 135.812 +/- 25.5182 | 132.312 +/- 26.3609 | 0 +/- 0 |
| jump | pC1 | 3.325 +/- 2.06502 | 0 +/- 0 | 0.7125 +/- 0.298172 | 0 +/- 0 |
| jump | vpoEN | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| jump | vpoIN | 43.6667 +/- 2.12055 | 48.0417 +/- 2.73001 | 43.8542 +/- 3.06631 | 0 +/- 0 |
| jump | AVLP008 | 0.475 +/- 0.15568 | 0.125 +/- 0.0768295 | 0.55 +/- 0.41508 | 0 +/- 0 |
| jump | DNp13/pMN1 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| jump | oviDN | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| jump | vpoEN-input:CB1484 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| jump | vpoEN-input:CB2364 | 2.21875 +/- 1.07519 | 1.07812 +/- 0.719599 | 0.4375 +/- 0.284129 | 0 +/- 0 |
| jump | vpoEN-input:CB1383 | 87.0625 +/- 5.14381 | 99.0417 +/- 3.53529 | 88.1042 +/- 4.86235 | 0 +/- 0 |
| jump | vpoEN-input:WED104 | 76.125 +/- 23.1788 | 30.3125 +/- 7.96054 | 117.625 +/- 33.255 | 0 +/- 0 |
| jump | vpoEN-input-top10 | 31.8314 +/- 1.56623 | 31.0552 +/- 1.35661 | 35.6366 +/- 1.41635 | 0 +/- 0 |
| jump | vpoEN-gate:AVLP083 | 0 +/- 0 | 0 +/- 0 | 9.8125 +/- 9.13919 | 0 +/- 0 |
| jump | AMMC-B1-candidate | 0.025641 +/- 0.0223083 | 0.0961538 +/- 0.0408226 | 0.00961538 +/- 0.00684094 | 0 +/- 0 |
| jump | AMMC-B1-candidate-graph | 5.68478 +/- 1.19519 | 5.57065 +/- 1.28813 | 5.21196 +/- 0.817567 | 0 +/- 0 |
| jump | A2-candidate | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |

## female: silent baseline

Band: group mean <=1 Hz AND every cell mean <=3 Hz; cell means average seeds and measured windows.

| Kernel | Condition | Group | Group mean Hz | Maximum cell mean Hz | Within band | Exactly zero |
|---|---|---|---:|---:|---|---|
| shiu | virgin_silence | vpoDN | 39.125 | 44 | False | False |
| shiu | virgin_silence | pC1 | 27.4625 | 50.125 | False | False |
| shiu | virgin_silence | vpoEN | 0 | 0 | True | True |
| shiu | virgin_silence | vpoIN | 0 | 0 | True | True |
| shiu | virgin_silence | AVLP008 | 0 | 0 | True | True |
| shiu | virgin_silence | DNp13/pMN1 | 0 | 0 | True | True |
| shiu | virgin_silence | oviDN | 0 | 0 | True | True |
| shiu | virgin_silence | vpoEN-input:CB1484 | 0 | 0 | True | True |
| shiu | virgin_silence | vpoEN-input:CB2364 | 0 | 0 | True | True |
| shiu | virgin_silence | vpoEN-input:CB1383 | 0 | 0 | True | True |
| shiu | virgin_silence | vpoEN-input:WED104 | 0 | 0 | True | True |
| shiu | virgin_silence | vpoEN-input-top10 | 0 | 0 | True | True |
| shiu | virgin_silence | vpoEN-gate:AVLP083 | 0 | 0 | True | True |
| shiu | virgin_silence | AMMC-B1-candidate | 0 | 0 | True | True |
| shiu | virgin_silence | AMMC-B1-candidate-graph | 0 | 0 | True | True |
| shiu | virgin_silence | A2-candidate | 0 | 0 | True | True |
| shiu | mated_silence | vpoDN | 0 | 0 | True | True |
| shiu | mated_silence | pC1 | 0 | 0 | True | True |
| shiu | mated_silence | vpoEN | 0 | 0 | True | True |
| shiu | mated_silence | vpoIN | 0 | 0 | True | True |
| shiu | mated_silence | AVLP008 | 0 | 0 | True | True |
| shiu | mated_silence | DNp13/pMN1 | 0 | 0 | True | True |
| shiu | mated_silence | oviDN | 0 | 0 | True | True |
| shiu | mated_silence | vpoEN-input:CB1484 | 0 | 0 | True | True |
| shiu | mated_silence | vpoEN-input:CB2364 | 0 | 0 | True | True |
| shiu | mated_silence | vpoEN-input:CB1383 | 0 | 0 | True | True |
| shiu | mated_silence | vpoEN-input:WED104 | 0 | 0 | True | True |
| shiu | mated_silence | vpoEN-input-top10 | 0 | 0 | True | True |
| shiu | mated_silence | vpoEN-gate:AVLP083 | 0 | 0 | True | True |
| shiu | mated_silence | AMMC-B1-candidate | 0 | 0 | True | True |
| shiu | mated_silence | AMMC-B1-candidate-graph | 0 | 0 | True | True |
| shiu | mated_silence | A2-candidate | 0 | 0 | True | True |
| jump | virgin_silence | vpoDN | 132.312 | 264.25 | False | False |
| jump | virgin_silence | pC1 | 0.7125 | 4.5 | False | False |
| jump | virgin_silence | vpoEN | 0 | 0 | True | True |
| jump | virgin_silence | vpoIN | 43.8542 | 112.375 | False | False |
| jump | virgin_silence | AVLP008 | 0.55 | 4.875 | False | False |
| jump | virgin_silence | DNp13/pMN1 | 0 | 0 | True | True |
| jump | virgin_silence | oviDN | 0 | 0 | True | True |
| jump | virgin_silence | vpoEN-input:CB1484 | 0 | 0 | True | True |
| jump | virgin_silence | vpoEN-input:CB2364 | 0.4375 | 3.5 | False | False |
| jump | virgin_silence | vpoEN-input:CB1383 | 88.1042 | 170 | False | False |
| jump | virgin_silence | vpoEN-input:WED104 | 117.625 | 224.25 | False | False |
| jump | virgin_silence | vpoEN-input-top10 | 35.6366 | 321.625 | False | False |
| jump | virgin_silence | vpoEN-gate:AVLP083 | 9.8125 | 18.375 | False | False |
| jump | virgin_silence | AMMC-B1-candidate | 0.00961538 | 0.375 | True | False |
| jump | virgin_silence | AMMC-B1-candidate-graph | 5.21196 | 103 | False | False |
| jump | virgin_silence | A2-candidate | 0 | 0 | True | True |
| jump | mated_silence | vpoDN | 0 | 0 | True | True |
| jump | mated_silence | pC1 | 0 | 0 | True | True |
| jump | mated_silence | vpoEN | 0 | 0 | True | True |
| jump | mated_silence | vpoIN | 0 | 0 | True | True |
| jump | mated_silence | AVLP008 | 0 | 0 | True | True |
| jump | mated_silence | DNp13/pMN1 | 0 | 0 | True | True |
| jump | mated_silence | oviDN | 0 | 0 | True | True |
| jump | mated_silence | vpoEN-input:CB1484 | 0 | 0 | True | True |
| jump | mated_silence | vpoEN-input:CB2364 | 0 | 0 | True | True |
| jump | mated_silence | vpoEN-input:CB1383 | 0 | 0 | True | True |
| jump | mated_silence | vpoEN-input:WED104 | 0 | 0 | True | True |
| jump | mated_silence | vpoEN-input-top10 | 0 | 0 | True | True |
| jump | mated_silence | vpoEN-gate:AVLP083 | 0 | 0 | True | True |
| jump | mated_silence | AMMC-B1-candidate | 0 | 0 | True | True |
| jump | mated_silence | AMMC-B1-candidate-graph | 0 | 0 | True | True |
| jump | mated_silence | A2-candidate | 0 | 0 | True | True |

## female: paired differences

Descriptive, no threshold; Hz/cell +/- paired SE.

| Kernel | Group | Left minus right | Mean +/- SE |
|---|---|---|---:|
| shiu | vpoDN | virgin_song - virgin_silence | -0.1875 +/- 0.209372 |
| shiu | pC1 | virgin_song - virgin_silence | -0.0875 +/- 0.117925 |
| shiu | vpoEN | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | vpoIN | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | AVLP008 | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | DNp13/pMN1 | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | oviDN | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | vpoEN-input:CB1484 | virgin_song - virgin_silence | 1.39583 +/- 0.164482 |
| shiu | vpoEN-input:CB2364 | virgin_song - virgin_silence | 0.4375 +/- 0.100993 |
| shiu | vpoEN-input:CB1383 | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | vpoEN-input:WED104 | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | vpoEN-input-top10 | virgin_song - virgin_silence | 0.276163 +/- 0.0358003 |
| shiu | vpoEN-gate:AVLP083 | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | AMMC-B1-candidate | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | AMMC-B1-candidate-graph | virgin_song - virgin_silence | 0.0380435 +/- 0.00830177 |
| shiu | A2-candidate | virgin_song - virgin_silence | 8.53125 +/- 0.369902 |
| shiu | vpoDN | mated_song - mated_silence | 0 +/- 0 |
| shiu | pC1 | mated_song - mated_silence | 0 +/- 0 |
| shiu | vpoEN | mated_song - mated_silence | 0 +/- 0 |
| shiu | vpoIN | mated_song - mated_silence | 0 +/- 0 |
| shiu | AVLP008 | mated_song - mated_silence | 0 +/- 0 |
| shiu | DNp13/pMN1 | mated_song - mated_silence | 0 +/- 0 |
| shiu | oviDN | mated_song - mated_silence | 0 +/- 0 |
| shiu | vpoEN-input:CB1484 | mated_song - mated_silence | 1.45833 +/- 0.158358 |
| shiu | vpoEN-input:CB2364 | mated_song - mated_silence | 0.453125 +/- 0.0972997 |
| shiu | vpoEN-input:CB1383 | mated_song - mated_silence | 0 +/- 0 |
| shiu | vpoEN-input:WED104 | mated_song - mated_silence | 0 +/- 0 |
| shiu | vpoEN-input-top10 | mated_song - mated_silence | 0.287791 +/- 0.0353251 |
| shiu | vpoEN-gate:AVLP083 | mated_song - mated_silence | 0 +/- 0 |
| shiu | AMMC-B1-candidate | mated_song - mated_silence | 0 +/- 0 |
| shiu | AMMC-B1-candidate-graph | mated_song - mated_silence | 0.0380435 +/- 0.00830177 |
| shiu | A2-candidate | mated_song - mated_silence | 8.4375 +/- 0.357824 |
| shiu | vpoDN | virgin_song - mated_song | 38.9375 +/- 1.37579 |
| shiu | pC1 | virgin_song - mated_song | 27.375 +/- 0.976637 |
| shiu | vpoEN | virgin_song - mated_song | 0 +/- 0 |
| shiu | vpoIN | virgin_song - mated_song | 0 +/- 0 |
| shiu | AVLP008 | virgin_song - mated_song | 0 +/- 0 |
| shiu | DNp13/pMN1 | virgin_song - mated_song | 0 +/- 0 |
| shiu | oviDN | virgin_song - mated_song | 0 +/- 0 |
| shiu | vpoEN-input:CB1484 | virgin_song - mated_song | -0.0625 +/- 0.0542378 |
| shiu | vpoEN-input:CB2364 | virgin_song - mated_song | -0.015625 +/- 0.0491353 |
| shiu | vpoEN-input:CB1383 | virgin_song - mated_song | 0 +/- 0 |
| shiu | vpoEN-input:WED104 | virgin_song - mated_song | 0 +/- 0 |
| shiu | vpoEN-input-top10 | virgin_song - mated_song | -0.0116279 +/- 0.00775194 |
| shiu | vpoEN-gate:AVLP083 | virgin_song - mated_song | 0 +/- 0 |
| shiu | AMMC-B1-candidate | virgin_song - mated_song | 0 +/- 0 |
| shiu | AMMC-B1-candidate-graph | virgin_song - mated_song | 0 +/- 0 |
| shiu | A2-candidate | virgin_song - mated_song | 0.09375 +/- 0.140142 |
| shiu | vpoDN | virgin_silence - mated_silence | 39.125 +/- 1.32484 |
| shiu | pC1 | virgin_silence - mated_silence | 27.4625 +/- 0.922152 |
| shiu | vpoEN | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | vpoIN | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | AVLP008 | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | DNp13/pMN1 | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | oviDN | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | vpoEN-input:CB1484 | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | vpoEN-input:CB2364 | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | vpoEN-input:CB1383 | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | vpoEN-input:WED104 | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | vpoEN-input-top10 | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | vpoEN-gate:AVLP083 | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | AMMC-B1-candidate | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | AMMC-B1-candidate-graph | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | A2-candidate | virgin_silence - mated_silence | 0 +/- 0 |
| jump | vpoDN | virgin_song - virgin_silence | 4.9375 +/- 23.6102 |
| jump | pC1 | virgin_song - virgin_silence | 2.6125 +/- 2.18894 |
| jump | vpoEN | virgin_song - virgin_silence | 0 +/- 0 |
| jump | vpoIN | virgin_song - virgin_silence | -0.1875 +/- 3.90688 |
| jump | AVLP008 | virgin_song - virgin_silence | -0.075 +/- 0.401905 |
| jump | DNp13/pMN1 | virgin_song - virgin_silence | 0 +/- 0 |
| jump | oviDN | virgin_song - virgin_silence | 0 +/- 0 |
| jump | vpoEN-input:CB1484 | virgin_song - virgin_silence | 0 +/- 0 |
| jump | vpoEN-input:CB2364 | virgin_song - virgin_silence | 1.78125 +/- 1.17925 |
| jump | vpoEN-input:CB1383 | virgin_song - virgin_silence | -1.04167 +/- 4.61552 |
| jump | vpoEN-input:WED104 | virgin_song - virgin_silence | -41.5 +/- 49.9096 |
| jump | vpoEN-input-top10 | virgin_song - virgin_silence | -3.80523 +/- 2.74947 |
| jump | vpoEN-gate:AVLP083 | virgin_song - virgin_silence | -9.8125 +/- 9.13919 |
| jump | AMMC-B1-candidate | virgin_song - virgin_silence | 0.0160256 +/- 0.0209631 |
| jump | AMMC-B1-candidate-graph | virgin_song - virgin_silence | 0.472826 +/- 1.52721 |
| jump | A2-candidate | virgin_song - virgin_silence | 0 +/- 0 |
| jump | vpoDN | mated_song - mated_silence | 135.812 +/- 25.5182 |
| jump | pC1 | mated_song - mated_silence | 0 +/- 0 |
| jump | vpoEN | mated_song - mated_silence | 0 +/- 0 |
| jump | vpoIN | mated_song - mated_silence | 48.0417 +/- 2.73001 |
| jump | AVLP008 | mated_song - mated_silence | 0.125 +/- 0.0768295 |
| jump | DNp13/pMN1 | mated_song - mated_silence | 0 +/- 0 |
| jump | oviDN | mated_song - mated_silence | 0 +/- 0 |
| jump | vpoEN-input:CB1484 | mated_song - mated_silence | 0 +/- 0 |
| jump | vpoEN-input:CB2364 | mated_song - mated_silence | 1.07812 +/- 0.719599 |
| jump | vpoEN-input:CB1383 | mated_song - mated_silence | 99.0417 +/- 3.53529 |
| jump | vpoEN-input:WED104 | mated_song - mated_silence | 30.3125 +/- 7.96054 |
| jump | vpoEN-input-top10 | mated_song - mated_silence | 31.0552 +/- 1.35661 |
| jump | vpoEN-gate:AVLP083 | mated_song - mated_silence | 0 +/- 0 |
| jump | AMMC-B1-candidate | mated_song - mated_silence | 0.0961538 +/- 0.0408226 |
| jump | AMMC-B1-candidate-graph | mated_song - mated_silence | 5.57065 +/- 1.28813 |
| jump | A2-candidate | mated_song - mated_silence | 0 +/- 0 |
| jump | vpoDN | virgin_song - mated_song | 1.4375 +/- 41.1276 |
| jump | pC1 | virgin_song - mated_song | 3.325 +/- 2.06502 |
| jump | vpoEN | virgin_song - mated_song | 0 +/- 0 |
| jump | vpoIN | virgin_song - mated_song | -4.375 +/- 3.40929 |
| jump | AVLP008 | virgin_song - mated_song | 0.35 +/- 0.206492 |
| jump | DNp13/pMN1 | virgin_song - mated_song | 0 +/- 0 |
| jump | oviDN | virgin_song - mated_song | 0 +/- 0 |
| jump | vpoEN-input:CB1484 | virgin_song - mated_song | 0 +/- 0 |
| jump | vpoEN-input:CB2364 | virgin_song - mated_song | 1.14062 +/- 1.31865 |
| jump | vpoEN-input:CB1383 | virgin_song - mated_song | -11.9792 +/- 6.00686 |
| jump | vpoEN-input:WED104 | virgin_song - mated_song | 45.8125 +/- 25.1597 |
| jump | vpoEN-input-top10 | virgin_song - mated_song | 0.776163 +/- 2.20429 |
| jump | vpoEN-gate:AVLP083 | virgin_song - mated_song | 0 +/- 0 |
| jump | AMMC-B1-candidate | virgin_song - mated_song | -0.0705128 +/- 0.0518575 |
| jump | AMMC-B1-candidate-graph | virgin_song - mated_song | 0.11413 +/- 1.93377 |
| jump | A2-candidate | virgin_song - mated_song | 0 +/- 0 |
| jump | vpoDN | virgin_silence - mated_silence | 132.312 +/- 26.3609 |
| jump | pC1 | virgin_silence - mated_silence | 0.7125 +/- 0.298172 |
| jump | vpoEN | virgin_silence - mated_silence | 0 +/- 0 |
| jump | vpoIN | virgin_silence - mated_silence | 43.8542 +/- 3.06631 |
| jump | AVLP008 | virgin_silence - mated_silence | 0.55 +/- 0.41508 |
| jump | DNp13/pMN1 | virgin_silence - mated_silence | 0 +/- 0 |
| jump | oviDN | virgin_silence - mated_silence | 0 +/- 0 |
| jump | vpoEN-input:CB1484 | virgin_silence - mated_silence | 0 +/- 0 |
| jump | vpoEN-input:CB2364 | virgin_silence - mated_silence | 0.4375 +/- 0.284129 |
| jump | vpoEN-input:CB1383 | virgin_silence - mated_silence | 88.1042 +/- 4.86235 |
| jump | vpoEN-input:WED104 | virgin_silence - mated_silence | 117.625 +/- 33.255 |
| jump | vpoEN-input-top10 | virgin_silence - mated_silence | 35.6366 +/- 1.41635 |
| jump | vpoEN-gate:AVLP083 | virgin_silence - mated_silence | 9.8125 +/- 9.13919 |
| jump | AMMC-B1-candidate | virgin_silence - mated_silence | 0.00961538 +/- 0.00684094 |
| jump | AMMC-B1-candidate-graph | virgin_silence - mated_silence | 5.21196 +/- 0.817567 |
| jump | A2-candidate | virgin_silence - mated_silence | 0 +/- 0 |

## female: ignition

Fraction of measured seed-windows with mean strictly >30 Hz/neuron (network) or Hz/cell (group).

| Kernel | Population | virgin_song | mated_song | virgin_silence | mated_silence |
|---|---|---:|---:|---:|---:|
| shiu | network | 0 | 0 | 0 | 0 |
| shiu | vpoDN | 0.60625 | 0 | 0.6125 | 0 |
| shiu | pC1 | 0.38125 | 0 | 0.38125 | 0 |
| shiu | vpoEN | 0 | 0 | 0 | 0 |
| shiu | vpoIN | 0 | 0 | 0 | 0 |
| shiu | AVLP008 | 0 | 0 | 0 | 0 |
| shiu | DNp13/pMN1 | 0 | 0 | 0 | 0 |
| shiu | oviDN | 0 | 0 | 0 | 0 |
| shiu | vpoEN-input:CB1484 | 0 | 0 | 0 | 0 |
| shiu | vpoEN-input:CB2364 | 0 | 0 | 0 | 0 |
| shiu | vpoEN-input:CB1383 | 0 | 0 | 0 | 0 |
| shiu | vpoEN-input:WED104 | 0 | 0 | 0 | 0 |
| shiu | vpoEN-input-top10 | 0 | 0 | 0 | 0 |
| shiu | vpoEN-gate:AVLP083 | 0 | 0 | 0 | 0 |
| shiu | AMMC-B1-candidate | 0 | 0 | 0 | 0 |
| shiu | AMMC-B1-candidate-graph | 0 | 0 | 0 | 0 |
| shiu | A2-candidate | 0 | 0 | 0 | 0 |
| jump | network | 0.99375 | 1 | 0.98125 | 0 |
| jump | vpoDN | 0.73125 | 0.6875 | 0.69375 | 0 |
| jump | pC1 | 0.03125 | 0 | 0.00625 | 0 |
| jump | vpoEN | 0 | 0 | 0 | 0 |
| jump | vpoIN | 0.91875 | 0.95625 | 0.8375 | 0 |
| jump | AVLP008 | 0 | 0 | 0 | 0 |
| jump | DNp13/pMN1 | 0 | 0 | 0 | 0 |
| jump | oviDN | 0 | 0 | 0 | 0 |
| jump | vpoEN-input:CB1484 | 0 | 0 | 0 | 0 |
| jump | vpoEN-input:CB2364 | 0 | 0 | 0 | 0 |
| jump | vpoEN-input:CB1383 | 0.9875 | 1 | 0.98125 | 0 |
| jump | vpoEN-input:WED104 | 0.55 | 0.3125 | 0.6 | 0 |
| jump | vpoEN-input-top10 | 0.5625 | 0.5625 | 0.7875 | 0 |
| jump | vpoEN-gate:AVLP083 | 0 | 0 | 0.05625 | 0 |
| jump | AMMC-B1-candidate | 0 | 0 | 0 | 0 |
| jump | AMMC-B1-candidate-graph | 0 | 0 | 0 | 0 |
| jump | A2-candidate | 0 | 0 | 0 | 0 |

## banc: condition means

Hz/cell +/- SE across ten seeds; warm-up excluded.

| Kernel | Group | virgin_song | mated_song | virgin_silence | mated_silence |
|---|---|---:|---:|---:|---:|
| shiu | vpoDN | 8.6875 +/- 0.856197 | 0 +/- 0 | 10.25 +/- 1.02571 | 0 +/- 0 |
| shiu | pC1 | 12.7625 +/- 0.785823 | 0 +/- 0 | 13 +/- 0.823694 | 0 +/- 0 |
| shiu | vpoEN | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | vpoIN | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | AVLP008 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | DNp13/pMN1 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | oviDN | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | vpoEN-input:CB1484 | absent | absent | absent | absent |
| shiu | vpoEN-input:CB2364 | 44.625 +/- 0.3534 | 44.2656 +/- 0.255208 | 0 +/- 0 | 0 +/- 0 |
| shiu | vpoEN-input:CB1383 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | vpoEN-input:WED104 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | vpoEN-input-top10 | 14.0968 +/- 0.111842 | 14.0685 +/- 0.0787065 | 0 +/- 0 | 0 +/- 0 |
| shiu | vpoEN-gate:AVLP083 | 117.562 +/- 6.9375 | 121.75 +/- 6.03362 | 0 +/- 0 | 0 +/- 0 |
| shiu | AMMC-B1-candidate | 1.16447 +/- 0.0692094 | 1.17434 +/- 0.0737263 | 0 +/- 0 | 0 +/- 0 |
| shiu | AMMC-B1-candidate-graph | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| shiu | A2-candidate | 147.938 +/- 1.10259 | 147.812 +/- 0.818885 | 0 +/- 0 | 0 +/- 0 |
| jump | vpoDN | 0 +/- 0 | 0 +/- 0 | 4.125 +/- 1.17556 | 0 +/- 0 |
| jump | pC1 | 3.6375 +/- 0.587618 | 0.5375 +/- 0.154841 | 5.0125 +/- 0.516213 | 0 +/- 0 |
| jump | vpoEN | 46.4583 +/- 0.664638 | 47.9583 +/- 1.08822 | 36.8125 +/- 2.33978 | 0 +/- 0 |
| jump | vpoIN | 244.969 +/- 8.02184 | 254.688 +/- 7.41883 | 157.156 +/- 14.3316 | 0 +/- 0 |
| jump | AVLP008 | 51.125 +/- 1.71192 | 54.875 +/- 2.45785 | 36.6094 +/- 3.37523 | 0 +/- 0 |
| jump | DNp13/pMN1 | 0 +/- 0 | 0 +/- 0 | 0.0625 +/- 0.0625 | 0 +/- 0 |
| jump | oviDN | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| jump | vpoEN-input:CB1484 | absent | absent | absent | absent |
| jump | vpoEN-input:CB2364 | 232.594 +/- 2.01546 | 237.406 +/- 2.21953 | 14.2344 +/- 1.22178 | 0 +/- 0 |
| jump | vpoEN-input:CB1383 | 30.5938 +/- 2.57881 | 40.5938 +/- 4.71346 | 15.75 +/- 1.66745 | 0 +/- 0 |
| jump | vpoEN-input:WED104 | 0 +/- 0 | 0 +/- 0 | 42.25 +/- 5.14647 | 0 +/- 0 |
| jump | vpoEN-input-top10 | 102.815 +/- 1.54622 | 106.79 +/- 2.4733 | 27.1129 +/- 2.11312 | 0 +/- 0 |
| jump | vpoEN-gate:AVLP083 | 384.75 +/- 3.99674 | 389.062 +/- 3.58703 | 311.5 +/- 18.9858 | 0 +/- 0 |
| jump | AMMC-B1-candidate | 2.16447 +/- 0.147583 | 2.25987 +/- 0.167734 | 0 +/- 0 | 0 +/- 0 |
| jump | AMMC-B1-candidate-graph | 5.76442 +/- 0.286088 | 5.14904 +/- 0.735067 | 6.01442 +/- 0.430458 | 0 +/- 0 |
| jump | A2-candidate | 303.688 +/- 3.09352 | 306.562 +/- 2.27503 | 0 +/- 0 | 0 +/- 0 |

## banc: silent baseline

Band: group mean <=1 Hz AND every cell mean <=3 Hz; cell means average seeds and measured windows.

| Kernel | Condition | Group | Group mean Hz | Maximum cell mean Hz | Within band | Exactly zero |
|---|---|---|---:|---:|---|---|
| shiu | virgin_silence | vpoDN | 10.25 | 10.375 | False | False |
| shiu | virgin_silence | pC1 | 13 | 32 | False | False |
| shiu | virgin_silence | vpoEN | 0 | 0 | True | True |
| shiu | virgin_silence | vpoIN | 0 | 0 | True | True |
| shiu | virgin_silence | AVLP008 | 0 | 0 | True | True |
| shiu | virgin_silence | DNp13/pMN1 | 0 | 0 | True | True |
| shiu | virgin_silence | oviDN | 0 | 0 | True | True |
| shiu | virgin_silence | vpoEN-input:CB1484 | absent | absent | absent | absent |
| shiu | virgin_silence | vpoEN-input:CB2364 | 0 | 0 | True | True |
| shiu | virgin_silence | vpoEN-input:CB1383 | 0 | 0 | True | True |
| shiu | virgin_silence | vpoEN-input:WED104 | 0 | 0 | True | True |
| shiu | virgin_silence | vpoEN-input-top10 | 0 | 0 | True | True |
| shiu | virgin_silence | vpoEN-gate:AVLP083 | 0 | 0 | True | True |
| shiu | virgin_silence | AMMC-B1-candidate | 0 | 0 | True | True |
| shiu | virgin_silence | AMMC-B1-candidate-graph | 0 | 0 | True | True |
| shiu | virgin_silence | A2-candidate | 0 | 0 | True | True |
| shiu | mated_silence | vpoDN | 0 | 0 | True | True |
| shiu | mated_silence | pC1 | 0 | 0 | True | True |
| shiu | mated_silence | vpoEN | 0 | 0 | True | True |
| shiu | mated_silence | vpoIN | 0 | 0 | True | True |
| shiu | mated_silence | AVLP008 | 0 | 0 | True | True |
| shiu | mated_silence | DNp13/pMN1 | 0 | 0 | True | True |
| shiu | mated_silence | oviDN | 0 | 0 | True | True |
| shiu | mated_silence | vpoEN-input:CB1484 | absent | absent | absent | absent |
| shiu | mated_silence | vpoEN-input:CB2364 | 0 | 0 | True | True |
| shiu | mated_silence | vpoEN-input:CB1383 | 0 | 0 | True | True |
| shiu | mated_silence | vpoEN-input:WED104 | 0 | 0 | True | True |
| shiu | mated_silence | vpoEN-input-top10 | 0 | 0 | True | True |
| shiu | mated_silence | vpoEN-gate:AVLP083 | 0 | 0 | True | True |
| shiu | mated_silence | AMMC-B1-candidate | 0 | 0 | True | True |
| shiu | mated_silence | AMMC-B1-candidate-graph | 0 | 0 | True | True |
| shiu | mated_silence | A2-candidate | 0 | 0 | True | True |
| jump | virgin_silence | vpoDN | 4.125 | 4.25 | False | False |
| jump | virgin_silence | pC1 | 5.0125 | 25.75 | False | False |
| jump | virgin_silence | vpoEN | 36.8125 | 110.5 | False | False |
| jump | virgin_silence | vpoIN | 157.156 | 212.5 | False | False |
| jump | virgin_silence | AVLP008 | 36.6094 | 152.75 | False | False |
| jump | virgin_silence | DNp13/pMN1 | 0.0625 | 0.125 | True | False |
| jump | virgin_silence | oviDN | 0 | 0 | True | True |
| jump | virgin_silence | vpoEN-input:CB1484 | absent | absent | absent | absent |
| jump | virgin_silence | vpoEN-input:CB2364 | 14.2344 | 112.375 | False | False |
| jump | virgin_silence | vpoEN-input:CB1383 | 15.75 | 36.375 | False | False |
| jump | virgin_silence | vpoEN-input:WED104 | 42.25 | 42.25 | False | False |
| jump | virgin_silence | vpoEN-input-top10 | 27.1129 | 295.25 | False | False |
| jump | virgin_silence | vpoEN-gate:AVLP083 | 311.5 | 312 | False | False |
| jump | virgin_silence | AMMC-B1-candidate | 0 | 0 | True | True |
| jump | virgin_silence | AMMC-B1-candidate-graph | 6.01442 | 145.625 | False | False |
| jump | virgin_silence | A2-candidate | 0 | 0 | True | True |
| jump | mated_silence | vpoDN | 0 | 0 | True | True |
| jump | mated_silence | pC1 | 0 | 0 | True | True |
| jump | mated_silence | vpoEN | 0 | 0 | True | True |
| jump | mated_silence | vpoIN | 0 | 0 | True | True |
| jump | mated_silence | AVLP008 | 0 | 0 | True | True |
| jump | mated_silence | DNp13/pMN1 | 0 | 0 | True | True |
| jump | mated_silence | oviDN | 0 | 0 | True | True |
| jump | mated_silence | vpoEN-input:CB1484 | absent | absent | absent | absent |
| jump | mated_silence | vpoEN-input:CB2364 | 0 | 0 | True | True |
| jump | mated_silence | vpoEN-input:CB1383 | 0 | 0 | True | True |
| jump | mated_silence | vpoEN-input:WED104 | 0 | 0 | True | True |
| jump | mated_silence | vpoEN-input-top10 | 0 | 0 | True | True |
| jump | mated_silence | vpoEN-gate:AVLP083 | 0 | 0 | True | True |
| jump | mated_silence | AMMC-B1-candidate | 0 | 0 | True | True |
| jump | mated_silence | AMMC-B1-candidate-graph | 0 | 0 | True | True |
| jump | mated_silence | A2-candidate | 0 | 0 | True | True |

## banc: paired differences

Descriptive, no threshold; Hz/cell +/- paired SE.

| Kernel | Group | Left minus right | Mean +/- SE |
|---|---|---|---:|
| shiu | vpoDN | virgin_song - virgin_silence | -1.5625 +/- 0.339142 |
| shiu | pC1 | virgin_song - virgin_silence | -0.2375 +/- 0.0800391 |
| shiu | vpoEN | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | vpoIN | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | AVLP008 | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | DNp13/pMN1 | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | oviDN | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | vpoEN-input:CB1484 | virgin_song - virgin_silence | absent |
| shiu | vpoEN-input:CB2364 | virgin_song - virgin_silence | 44.625 +/- 0.3534 |
| shiu | vpoEN-input:CB1383 | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | vpoEN-input:WED104 | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | vpoEN-input-top10 | virgin_song - virgin_silence | 14.0968 +/- 0.111842 |
| shiu | vpoEN-gate:AVLP083 | virgin_song - virgin_silence | 117.562 +/- 6.9375 |
| shiu | AMMC-B1-candidate | virgin_song - virgin_silence | 1.16447 +/- 0.0692094 |
| shiu | AMMC-B1-candidate-graph | virgin_song - virgin_silence | 0 +/- 0 |
| shiu | A2-candidate | virgin_song - virgin_silence | 147.938 +/- 1.10259 |
| shiu | vpoDN | mated_song - mated_silence | 0 +/- 0 |
| shiu | pC1 | mated_song - mated_silence | 0 +/- 0 |
| shiu | vpoEN | mated_song - mated_silence | 0 +/- 0 |
| shiu | vpoIN | mated_song - mated_silence | 0 +/- 0 |
| shiu | AVLP008 | mated_song - mated_silence | 0 +/- 0 |
| shiu | DNp13/pMN1 | mated_song - mated_silence | 0 +/- 0 |
| shiu | oviDN | mated_song - mated_silence | 0 +/- 0 |
| shiu | vpoEN-input:CB1484 | mated_song - mated_silence | absent |
| shiu | vpoEN-input:CB2364 | mated_song - mated_silence | 44.2656 +/- 0.255208 |
| shiu | vpoEN-input:CB1383 | mated_song - mated_silence | 0 +/- 0 |
| shiu | vpoEN-input:WED104 | mated_song - mated_silence | 0 +/- 0 |
| shiu | vpoEN-input-top10 | mated_song - mated_silence | 14.0685 +/- 0.0787065 |
| shiu | vpoEN-gate:AVLP083 | mated_song - mated_silence | 121.75 +/- 6.03362 |
| shiu | AMMC-B1-candidate | mated_song - mated_silence | 1.17434 +/- 0.0737263 |
| shiu | AMMC-B1-candidate-graph | mated_song - mated_silence | 0 +/- 0 |
| shiu | A2-candidate | mated_song - mated_silence | 147.812 +/- 0.818885 |
| shiu | vpoDN | virgin_song - mated_song | 8.6875 +/- 0.856197 |
| shiu | pC1 | virgin_song - mated_song | 12.7625 +/- 0.785823 |
| shiu | vpoEN | virgin_song - mated_song | 0 +/- 0 |
| shiu | vpoIN | virgin_song - mated_song | 0 +/- 0 |
| shiu | AVLP008 | virgin_song - mated_song | 0 +/- 0 |
| shiu | DNp13/pMN1 | virgin_song - mated_song | 0 +/- 0 |
| shiu | oviDN | virgin_song - mated_song | 0 +/- 0 |
| shiu | vpoEN-input:CB1484 | virgin_song - mated_song | absent |
| shiu | vpoEN-input:CB2364 | virgin_song - mated_song | 0.359375 +/- 0.284367 |
| shiu | vpoEN-input:CB1383 | virgin_song - mated_song | 0 +/- 0 |
| shiu | vpoEN-input:WED104 | virgin_song - mated_song | 0 +/- 0 |
| shiu | vpoEN-input-top10 | virgin_song - mated_song | 0.0282258 +/- 0.109368 |
| shiu | vpoEN-gate:AVLP083 | virgin_song - mated_song | -4.1875 +/- 7.45592 |
| shiu | AMMC-B1-candidate | virgin_song - mated_song | -0.00986842 +/- 0.0139129 |
| shiu | AMMC-B1-candidate-graph | virgin_song - mated_song | 0 +/- 0 |
| shiu | A2-candidate | virgin_song - mated_song | 0.125 +/- 0.630531 |
| shiu | vpoDN | virgin_silence - mated_silence | 10.25 +/- 1.02571 |
| shiu | pC1 | virgin_silence - mated_silence | 13 +/- 0.823694 |
| shiu | vpoEN | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | vpoIN | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | AVLP008 | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | DNp13/pMN1 | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | oviDN | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | vpoEN-input:CB1484 | virgin_silence - mated_silence | absent |
| shiu | vpoEN-input:CB2364 | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | vpoEN-input:CB1383 | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | vpoEN-input:WED104 | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | vpoEN-input-top10 | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | vpoEN-gate:AVLP083 | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | AMMC-B1-candidate | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | AMMC-B1-candidate-graph | virgin_silence - mated_silence | 0 +/- 0 |
| shiu | A2-candidate | virgin_silence - mated_silence | 0 +/- 0 |
| jump | vpoDN | virgin_song - virgin_silence | -4.125 +/- 1.17556 |
| jump | pC1 | virgin_song - virgin_silence | -1.375 +/- 0.570088 |
| jump | vpoEN | virgin_song - virgin_silence | 9.64583 +/- 2.10705 |
| jump | vpoIN | virgin_song - virgin_silence | 87.8125 +/- 17.6515 |
| jump | AVLP008 | virgin_song - virgin_silence | 14.5156 +/- 3.53234 |
| jump | DNp13/pMN1 | virgin_song - virgin_silence | -0.0625 +/- 0.0625 |
| jump | oviDN | virgin_song - virgin_silence | 0 +/- 0 |
| jump | vpoEN-input:CB1484 | virgin_song - virgin_silence | absent |
| jump | vpoEN-input:CB2364 | virgin_song - virgin_silence | 218.359 +/- 2.51355 |
| jump | vpoEN-input:CB1383 | virgin_song - virgin_silence | 14.8438 +/- 3.0349 |
| jump | vpoEN-input:WED104 | virgin_song - virgin_silence | -42.25 +/- 5.14647 |
| jump | vpoEN-input-top10 | virgin_song - virgin_silence | 75.7016 +/- 2.5229 |
| jump | vpoEN-gate:AVLP083 | virgin_song - virgin_silence | 73.25 +/- 18.5332 |
| jump | AMMC-B1-candidate | virgin_song - virgin_silence | 2.16447 +/- 0.147583 |
| jump | AMMC-B1-candidate-graph | virgin_song - virgin_silence | -0.25 +/- 0.664699 |
| jump | A2-candidate | virgin_song - virgin_silence | 303.688 +/- 3.09352 |
| jump | vpoDN | mated_song - mated_silence | 0 +/- 0 |
| jump | pC1 | mated_song - mated_silence | 0.5375 +/- 0.154841 |
| jump | vpoEN | mated_song - mated_silence | 47.9583 +/- 1.08822 |
| jump | vpoIN | mated_song - mated_silence | 254.688 +/- 7.41883 |
| jump | AVLP008 | mated_song - mated_silence | 54.875 +/- 2.45785 |
| jump | DNp13/pMN1 | mated_song - mated_silence | 0 +/- 0 |
| jump | oviDN | mated_song - mated_silence | 0 +/- 0 |
| jump | vpoEN-input:CB1484 | mated_song - mated_silence | absent |
| jump | vpoEN-input:CB2364 | mated_song - mated_silence | 237.406 +/- 2.21953 |
| jump | vpoEN-input:CB1383 | mated_song - mated_silence | 40.5938 +/- 4.71346 |
| jump | vpoEN-input:WED104 | mated_song - mated_silence | 0 +/- 0 |
| jump | vpoEN-input-top10 | mated_song - mated_silence | 106.79 +/- 2.4733 |
| jump | vpoEN-gate:AVLP083 | mated_song - mated_silence | 389.062 +/- 3.58703 |
| jump | AMMC-B1-candidate | mated_song - mated_silence | 2.25987 +/- 0.167734 |
| jump | AMMC-B1-candidate-graph | mated_song - mated_silence | 5.14904 +/- 0.735067 |
| jump | A2-candidate | mated_song - mated_silence | 306.562 +/- 2.27503 |
| jump | vpoDN | virgin_song - mated_song | 0 +/- 0 |
| jump | pC1 | virgin_song - mated_song | 3.1 +/- 0.572155 |
| jump | vpoEN | virgin_song - mated_song | -1.5 +/- 0.786165 |
| jump | vpoIN | virgin_song - mated_song | -9.71875 +/- 10.9434 |
| jump | AVLP008 | virgin_song - mated_song | -3.75 +/- 1.49996 |
| jump | DNp13/pMN1 | virgin_song - mated_song | 0 +/- 0 |
| jump | oviDN | virgin_song - mated_song | 0 +/- 0 |
| jump | vpoEN-input:CB1484 | virgin_song - mated_song | absent |
| jump | vpoEN-input:CB2364 | virgin_song - mated_song | -4.8125 +/- 1.62744 |
| jump | vpoEN-input:CB1383 | virgin_song - mated_song | -10 +/- 5.91406 |
| jump | vpoEN-input:WED104 | virgin_song - mated_song | 0 +/- 0 |
| jump | vpoEN-input-top10 | virgin_song - mated_song | -3.97581 +/- 2.14218 |
| jump | vpoEN-gate:AVLP083 | virgin_song - mated_song | -4.3125 +/- 2.9908 |
| jump | AMMC-B1-candidate | virgin_song - mated_song | -0.0953947 +/- 0.159836 |
| jump | AMMC-B1-candidate-graph | virgin_song - mated_song | 0.615385 +/- 0.831847 |
| jump | A2-candidate | virgin_song - mated_song | -2.875 +/- 3.27183 |
| jump | vpoDN | virgin_silence - mated_silence | 4.125 +/- 1.17556 |
| jump | pC1 | virgin_silence - mated_silence | 5.0125 +/- 0.516213 |
| jump | vpoEN | virgin_silence - mated_silence | 36.8125 +/- 2.33978 |
| jump | vpoIN | virgin_silence - mated_silence | 157.156 +/- 14.3316 |
| jump | AVLP008 | virgin_silence - mated_silence | 36.6094 +/- 3.37523 |
| jump | DNp13/pMN1 | virgin_silence - mated_silence | 0.0625 +/- 0.0625 |
| jump | oviDN | virgin_silence - mated_silence | 0 +/- 0 |
| jump | vpoEN-input:CB1484 | virgin_silence - mated_silence | absent |
| jump | vpoEN-input:CB2364 | virgin_silence - mated_silence | 14.2344 +/- 1.22178 |
| jump | vpoEN-input:CB1383 | virgin_silence - mated_silence | 15.75 +/- 1.66745 |
| jump | vpoEN-input:WED104 | virgin_silence - mated_silence | 42.25 +/- 5.14647 |
| jump | vpoEN-input-top10 | virgin_silence - mated_silence | 27.1129 +/- 2.11312 |
| jump | vpoEN-gate:AVLP083 | virgin_silence - mated_silence | 311.5 +/- 18.9858 |
| jump | AMMC-B1-candidate | virgin_silence - mated_silence | 0 +/- 0 |
| jump | AMMC-B1-candidate-graph | virgin_silence - mated_silence | 6.01442 +/- 0.430458 |
| jump | A2-candidate | virgin_silence - mated_silence | 0 +/- 0 |

## banc: ignition

Fraction of measured seed-windows with mean strictly >30 Hz/neuron (network) or Hz/cell (group).

| Kernel | Population | virgin_song | mated_song | virgin_silence | mated_silence |
|---|---|---:|---:|---:|---:|
| shiu | network | 0 | 0 | 0 | 0 |
| shiu | vpoDN | 0 | 0 | 0.025 | 0 |
| shiu | pC1 | 0.00625 | 0 | 0.00625 | 0 |
| shiu | vpoEN | 0 | 0 | 0 | 0 |
| shiu | vpoIN | 0 | 0 | 0 | 0 |
| shiu | AVLP008 | 0 | 0 | 0 | 0 |
| shiu | DNp13/pMN1 | 0 | 0 | 0 | 0 |
| shiu | oviDN | 0 | 0 | 0 | 0 |
| shiu | vpoEN-input:CB1484 | absent | absent | absent | absent |
| shiu | vpoEN-input:CB2364 | 1 | 1 | 0 | 0 |
| shiu | vpoEN-input:CB1383 | 0 | 0 | 0 | 0 |
| shiu | vpoEN-input:WED104 | 0 | 0 | 0 | 0 |
| shiu | vpoEN-input-top10 | 0 | 0 | 0 | 0 |
| shiu | vpoEN-gate:AVLP083 | 1 | 1 | 0 | 0 |
| shiu | AMMC-B1-candidate | 0 | 0 | 0 | 0 |
| shiu | AMMC-B1-candidate-graph | 0 | 0 | 0 | 0 |
| shiu | A2-candidate | 1 | 1 | 0 | 0 |
| jump | network | 0.88125 | 0.8875 | 0.7 | 0 |
| jump | vpoDN | 0 | 0 | 0.075 | 0 |
| jump | pC1 | 0 | 0 | 0.01875 | 0 |
| jump | vpoEN | 0.98125 | 0.99375 | 0.7625 | 0 |
| jump | vpoIN | 1 | 1 | 0.90625 | 0 |
| jump | AVLP008 | 0.96875 | 0.96875 | 0.64375 | 0 |
| jump | DNp13/pMN1 | 0 | 0 | 0 | 0 |
| jump | oviDN | 0 | 0 | 0 | 0 |
| jump | vpoEN-input:CB1484 | absent | absent | absent | absent |
| jump | vpoEN-input:CB2364 | 1 | 1 | 0 | 0 |
| jump | vpoEN-input:CB1383 | 0.325 | 0.58125 | 0.04375 | 0 |
| jump | vpoEN-input:WED104 | 0 | 0 | 0.5375 | 0 |
| jump | vpoEN-input-top10 | 1 | 1 | 0.50625 | 0 |
| jump | vpoEN-gate:AVLP083 | 1 | 1 | 0.94375 | 0 |
| jump | AMMC-B1-candidate | 0 | 0 | 0 | 0 |
| jump | AMMC-B1-candidate-graph | 0 | 0 | 0 | 0 |
| jump | A2-candidate | 1 | 1 | 0 | 0 |

## Equality, scope and deviations

Exact historical vpoDN/pC1 equality: False. Both kernels, all conditions and seeds; observer-to-runner equality and raw reconstruction are recorded in records/female_readouts_v1_checks.json.
The existing runner.run, simulator, hook, ear and dictionary files are unchanged. Only JO-A, JO-B and SAG received external drive. The return-event observer did not replace a function.
Population scope and sign sources differ; BANC includes ventral nerve cord cells and excludes 4,344,932 synapses outside its construction population. Absent labels do not imply biological absence.
these readouts do not establish hearing, refusal or mating
the ear is not calibrated
Clean room: no restricted source tree was inspected; only the supplied runtime dependency directory was used. No git write commands were executed.
Deviations: The original full CLI stopped after five FAFB jump historical rate mismatches. BANC collection continued through the same frozen runner and observer solely to complete the descriptive tables. The failed equality gate is retained; full historical replication is not accepted. The mismatch cause has not been established.

## Acceptance evidence

Historical equality is FAIL-CLOSED. These completed descriptive tables are not accepted as an exact replication.

| Dataset | Kernel | Equal vpoDN/pC1 seed comparisons | Total |
|---|---|---:|---:|
| female | shiu | 80 | 80 |
| female | jump | 75 | 80 |
| banc | shiu | 80 | 80 |
| banc | jump | 79 | 80 |

| Dataset | Kernel | Condition | Seed | Readout | Historical Hz | Current Hz |
|---|---|---|---:|---|---:|---:|
| female | jump | virgin_song | 4 | vpoDN | 208.75 | 203.125 |
| female | jump | virgin_song | 4 | pC1 | 5.375 | 2 |
| female | jump | mated_song | 0 | vpoDN | 203.75 | 204.375 |
| female | jump | virgin_silence | 3 | vpoDN | 195.625 | 194.375 |
| female | jump | virgin_silence | 3 | pC1 | 2.75 | 2.5 |
| banc | jump | virgin_silence | 0 | pC1 | 9 | 5.875 |

Observer-to-runner equality uses exact comparison, without numerical tolerance. The primary and secondary outputs are both retained. The mismatch cause is unverified; no calibration, gain or protocol adjustment was attempted.
Synthetic pytest: 11 passed, 1 skipped; exit 0. The skip is the opt-in failure probe. Deliberate probe: 1 failed, 11 deselected; exit 1. The initial test invocation had one temporary-directory setup error, corrected before freeze. No environment workaround.
Quick including I/O: 21.960 s; full CLI plus continuation: 143.537 s. The original full CLI exited 1 at the failed gate.
