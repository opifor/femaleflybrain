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
