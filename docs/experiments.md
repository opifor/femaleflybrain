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
