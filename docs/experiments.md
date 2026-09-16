# Experiments

The experiment layer runs paired seeds from rest on a female brain alone.
No arena, male, behavioural feedback, or gain calibration is present.
The preregistration is read before simulation, stored verbatim, and SHA256
fingerprinted in each record. Version 1 execution parameters are implemented
by `Protocol`; changes to hypotheses or execution choices require a new
protocol version before collecting data. Quick runs are preliminary.

```sh
python -m flybench.experiment.runner --quick
python -m flybench.experiment.runner
python -m pytest -q -p no:cacheprovider tests/test_experiment.py tests/test_ear_song.py
```

The CLI requires `build/graph_female.npz` with FAFB v783 metadata,
Shiu connectivity, and `shiu2024-parquet` signs; it runs CUDA `fast_gpu`
float32 batches. Each condition starts every seed from rest. The 50 ms window
contains ten consecutive 5 ms calls, retaining voltage, conductance, delay,
refractory state and each seed's Torch generator. At dt=0.2 ms this is 250
steps per window. Both kernels use the same target order and seed list.
All JO-A, JO-B and SAG targets stay present even at zero rate.

`BatchRates` bridges the existing backend's scalar drive interface: sampling
broadcasts a target rate vector across time steps, while result assignment
broadcasts a column vector across trials. Rates are checked against grid
capacity. No simulation kernel is copied or modified. CPU and CUDA tests
check exact sampled and delivered rates against independent seeded draws,
including continuation and both supported time steps.

The song carries absolute sample time and carrier phase across windows;
22050 Hz gives alternating 1102/1103-sample windows. The pulse envelope is
4 ms Hann, repeated every 35 ms, with a continuous 250 Hz carrier. The sine
carrier is 150 Hz. For each 50 ms waveform, the ear separately applies fourth
order Butterworth filters with `sosfiltfilt(padlen=27)` in 100-500 Hz and
500-2500 Hz bands. Ten nearest-sample slices map band RMS to clipped rates.
RMS_FULL uses a full-amplitude, pure pulse, one-second reference, filtered as
one second. Filter state is not carried across windows; the specified
zero-phase filtering uses the entire current window.

Sources supplied for the synthesis specification: von Philipsborn (2011),
Neuron 69:509; Clemens/Murthy (2018), Nature Communications (carriers);
Zhou (2015), eLife 4:e08477 (IPI).
These are synthesis choices, not brain measurements.

Dictionary version 1 supplies JO-A and JO-B. The experiment pools exact
pC1a-e types and selects DNp37 for vpoDN. Its SAG population is the union
of exact AN_SMP_2, AN_FLA_SMP_2 and ANXXX983 labels, as preregistered;
this overrides the dictionary's female SpsP proxy without altering it.
Missing required groups and overlapping drive populations are errors.
Selected counts, graph indices and body IDs are retained in records.

Quick output: `build/female_no_v1_quick_experiment.json` and
`build/female_no_v1_quick_report.md`. Full output:
`records/female_no_v1_experiment.json` and `records/female_no_v1_report.md`.
JSON schema version 1 is checked by `record.validate`: complete paired trial
coverage, window counts, readouts, drive slices and finite JSON values.
Each trial records every window's output and every 5 ms slice's requested,
sampled and delivered mean drive Hz per group cell. Requested drive is uniform
within each group. Delivered means sampled inputs coincident with an actual
spike, following the simulator contract; output rates also count network spikes.
Graph hash, sign/version metadata, dictionary source hash, experiment source
hashes, physical parameters, timing, seeds, GPU and library versions are stored.

Reports are generated only by rereading saved JSON. They include the exact
preregistration, condition-by-seed results, condition mean ± SE, paired
differences and their sample-SD SE. Primary support requires strictly positive
mean difference greater than twice SE. Zero difference with zero SE is not
supported. Jump comparisons and ignition are descriptive. Ignition is the
fraction of measured seed-windows above 30 Hz per network neuron; warm-up
windows are excluded. All readouts use the last 16 windows in full runs and
last two in quick runs. No inference about mating behaviour follows directly
from these isolated neuronal outputs.

For the harness probe, set `FLYBENCH_FAIL_PROBE=1` and run only
`tests/test_experiment.py::test_harness_failure_probe`. It must report one
failure with exit code 1. Remove that variable for acceptance tests.

## female_hearing_v1

The [hearing ladder preregistration](../experiments/female_hearing_v1.md) fixes
JO dose calibration, direct vpoEN positive controls, and positive-edge gain
sensitivity before collection. It uses the existing Shiu fast_gpu engine and
BatchRates adapter without changing the earlier experiment. Run in order:

```sh
python -m flybench.experiment.hearing quick
python -m flybench.experiment.hearing calibration
python -m flybench.experiment.hearing freeze
python -m flybench.experiment.hearing test
python -m flybench.experiment.hearing report
python -m pytest -q -p no:cacheprovider tests/test_hearing.py tests/test_experiment.py
```

Quick seeds 0,1 are preliminary. Calibration uses only seeds 0-9; freeze reads
the saved calibration and selects the lowest dose passing the strict paired
mean >2 SE rule (JO: vpoEN; direct drive: virgin vpoDN). Fallbacks are 720 and
360 Hz with a no-transfer flag. Freeze refuses to overwrite a decision. The
separate test process uses only seeds 10-29 and verifies protocol, graph and
calibration hashes against that decision. T1 and T2 receive verdicts; T3 is
mated-minus-virgin relay difference and T4 is gain-1.3 auditory response,
both descriptive. No dose selection uses held-out data.

Gain scales only positive CSR values before simulator construction. All four
drive groups, including zero-rate vpoEN, remain targeted in every condition
to preserve paired streams. This adds targets relative to female_no_v1 and
therefore changes its random stream and the backend's target refractory
convention; cross-experiment bitwise agreement is not claimed. Full gain
controls cover all four state/song combinations. Identical configurations
within a stage are simulated once and reused by identity.

Each trial stores group and individual vpoEN/vpoDN/pC1 firing, total network
spikes and mean rate, and per-target requested/sampled/delivered drive for
every 5 ms slice. Means and ignition exclude the first four windows.
Outputs are `records/female_hearing_v1_{calibration,frozen,test}.json`;
the JSON report contains a `Result` object. The Markdown report is rendered
from that saved JSON, with calibration and pre-registered test sections.
Quick output and execution evidence are under `build/`.

## shiu_benchmarks_v1

The [preregistered Shiu controls](../experiments/shiu_benchmarks_v1.md) test
sugar-to-MN9 dose response and bitter suppression, JO-CE versus JO-F activation
of aBN1, and external-drive delivery including JO-A/B second-order responses.
Use the existing `build/graph_female.npz` with FAFB v783, the Shiu export and
`shiu2024-parquet` signs. Run, in order:

```text
python -m flybench.experiment.benchmarks --quick
python -m flybench.experiment.benchmarks
python -m pytest -q -p no:cacheprovider tests/test_benchmarks.py
```

Both stages use 1 s trials and exclude the first 200 ms from readouts. Quick
uses seeds 0-1; full uses 0-9. The full command requires a matching quick record.
All neuronal simulation uses the unchanged `fast_gpu` CUDA batch engine.
Shiu's literal source IDs are preserved; missing v783 IDs are reported rather
than replaced. The three absent IDs reduce sugar to 20, bitter to 20 and JO-CE
to 69 cells. Water and Ir94e each contain 18, JO-F 60, and both readouts one.

The [generated report](../records/shiu_benchmarks_v1_report.md) and
[JSON record](../records/shiu_benchmarks_v1_report.json) include a `Result` object,
all 130 seedwise trials, graph/protocol/code fingerprints, exact selector lists,
per-cell drive audits and the top 20 directly postsynaptic types for each JO-A/B
input. The report compares the measured directions with paper figures; it does
not invent exact paper rates or equate 50 mM sucrose with an input frequency.
The approximately 80% maximum in Shiu's Methods is not a refractory-limit claim.

The robustness gate requires every predefined B1 and B2 contrast to exceed
2 SE. Water and Ir94e are secondary checks. This is a v783 directional replication,
with dt=0.2 ms, ten repeats and an 800 ms readout, not exact reconstruction of the
paper's v630, dt=0.1 ms, thirty-repeat calculation. Passing controls do not prove
that a silent hearing pathway is biologically absent.

The measured B1 and B2 gates passed. Sugar100 produced 63.375 +/- 1.817 Hz MN9,
falling to 4.500 +/- 0.972 Hz with bitter100. JO-CE100 produced 26.875 +/- 0.678 Hz
aBN1 versus 0.625 +/- 0.384 Hz for JO-F100. Water100 produced zero MN9 spikes,
so that secondary activation prediction was not reproduced at this dose.
Sugar100/sugar200 was 0.675, below the paper's approximate 0.8 calibration target;
the denominator here is only the measured 200 Hz condition, not a known maximum.
All sampled drive events were delivered in the recorded trials. Each of the
JO-A, JO-B and combined-input top-20 second-order type sets contained 20 active
types (any seed >0 Hz). These controls argue against a global drive failure,
while leaving the cause of the silent vpoEN hearing response unresolved.

Acceptance: benchmark plus reference/fast-backend tests reported 56 passed,
3 skipped (opt-in failure probes), exit 0. The benchmark's intentional-failure
probe reported 1 failed, 7 deselected, exit 1. See the
[delivery checks](../records/shiu_benchmarks_v1_checks.json) and
[native process exits](../records/shiu_benchmarks_v1_execution.json).

## Two-body courtship

The [courtship_v1 preregistration](../experiments/courtship_v1.md) connects
MaleCNS and FAFB brains to the observable-only world. Four paired conditions
cross virgin/mated female SAG state with live/muted male song. Female scent
and vision are disabled. Male sensory inputs come only from geometry; both
bodies move, and emitted male song reaches the female one window later.

Run `python -m flybench.experiment.courtship quick`, then
`python -m flybench.experiment.courtship full` and
`python -m flybench.experiment.courtship report`. If the quick timing projects
more than 40 minutes, `full --partial` uses five seeds with unassessed full
predictions. Quick uses two seeds and 60 windows; full uses ten seeds and
400 windows, always excluding the first 40 windows from summaries.

The experiment-local adapter gives each GPU batch column its own world input;
the simulator and world implementations are unchanged. Run
`python -m pytest -q -p no:cacheprovider tests/test_courtship.py` for wiring,
seed-column and verdict checks. The opt-in `FLYBENCH_FAIL_PROBE=1` probe must
report a failure and exit 1.

Compact summaries and the generated report are in `records/courtship_v1_*`;
window and group-cell data are compressed under `build/records-raw/`.
P1 activity, approach and ignition are descriptive. vpoDN is a neural readout,
not an acceptance or mating decision.

See the [courtship report](../records/courtship_v1_report.md) and
[seed summaries](../records/courtship_v1_full.json) for measured results and
execution limitations. The male ppk23 group is empty in this dictionary;
no substitute contact population is introduced. Paired seeds do not imply
bitwise numerical reproducibility on the recorded CUDA execution chain.

## male_decides_v1

The [preregistered male sensory dose ladder](../experiments/male_decides_v1.md)
isolates smell, right-side L1/L2 vision and direct P1 drive in the male Shiu
network. Calibration seeds 0–9 freeze doses before paired held-out seeds 10–29.
Run `python -m flybench.experiment.male_decides` with stages `quick`,
`calibration`, `freeze`, `test`, then `report`, in that order.

The [report](../records/male_decides_v1_report.md) separates calibration and
held-out predictions. Compact seed summaries and frozen choices reside in
`records/male_decides_v1_*`; window data and target indices remain under
`build/records-raw/`. Rates are per neuron; network total rates and spike
counts are included separately. Ignition is a window fraction, not behavior.
Run `python -m pytest -q -p no:cacheprovider tests/test_male_decides.py`;
the opt-in `FLYBENCH_FAIL_PROBE=1` harness probe must fail with exit 1.
