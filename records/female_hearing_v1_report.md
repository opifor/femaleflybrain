# female_hearing_v1

All differences are paired Hz/cell, mean +/- SE.

## calibration

| Arm | State | Dose / gain | vpoEN difference | vpoDN difference |
| --- | --- | ---: | ---: | ---: |
| a | virgin | 60 | 0 +/- 0 | 0.0625 +/- 0.0625 |
| a | virgin | 180 | 0 +/- 0 | 0 +/- 0 |
| a | virgin | 360 | 0 +/- 0 | -0.125 +/- 0.242956 |
| a | virgin | 720 | 0 +/- 0 | -0.4375 +/- 0.280284 |
| b | virgin | 0 | 0 +/- 0 | 0 +/- 0 |
| b | virgin | 60 | 59.1875 +/- 1.27765 | 18.125 +/- 0.812233 |
| b | virgin | 180 | 178.156 +/- 2.00664 | 52 +/- 1.23884 |
| b | virgin | 360 | 358.906 +/- 2.57789 | 81.3125 +/- 1.09231 |
| b | mated | 0 | 0 +/- 0 | 0 +/- 0 |
| b | mated | 60 | 59.1875 +/- 1.27765 | 16 +/- 0.679563 |
| b | mated | 180 | 178.156 +/- 2.00664 | 66.125 +/- 0.783954 |
| b | mated | 360 | 358.906 +/- 2.57789 | 105 +/- 0.465847 |
| c | virgin | 1.0 | 0 +/- 0 | 0 +/- 0 |
| c | virgin | 1.3 | 0 +/- 0 | 0.0625 +/- 1.42354 |

Direct-drive realized vpoEN firing (mean +/- SE):
- virgin, 0 Hz: 0 +/- 0
- virgin, 60 Hz: 59.1875 +/- 1.27765
- virgin, 180 Hz: 178.156 +/- 2.00664
- virgin, 360 Hz: 358.906 +/- 2.57789
- mated, 0 Hz: 0 +/- 0
- mated, 60 Hz: 59.1875 +/- 1.27765
- mated, 180 Hz: 178.156 +/- 2.00664
- mated, 360 Hz: 358.906 +/- 2.57789

Frozen selection: {"calibration_seeds": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "calibration_sha256": "f6791a8b6a84e799320bcdc62f204ecd2eef70e508750dfacad0c97950d226ec", "created_utc": "2026-09-16T12:48:48.695925+00:00", "graph_sha256": "35e5c3b4cca86b27392a144a4d6bcb37de2f3f97f29d71f5c0a5c20b1cd593b8", "jo": {"dose": 720, "fallback": true, "rule": "no transfer"}, "protocol_sha256": "dbbe6e754142ef1ff5d0f6449e31a09ea46b0f98b2be924d60a276f696ea3476", "test_seeds": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29], "vpoEN": {"dose": 60, "fallback": false, "rule": "lowest dose with difference > 2 SE"}}

## pre-registered test

| Test | Difference | Verdict |
| --- | ---: | --- |
| T1 | -0.15625 +/- 0.282708 | not supported |
| T2 | 17.8438 +/- 0.595479 | supported |
| T3 | -0.84375 +/- 0.515538 | descriptive |
| T4 | 1.375 +/- 1.11028 | descriptive |

T3 is mated-minus-virgin difference of relay differences; negative supports the descriptive direction.
Mated relay: 17 +/- 0.625986

## Ignition

| Stage | Condition | Fraction >30 Hz/neuron |
| --- | --- | ---: |
| calibration | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 60, "song": false, "state": "virgin"} | 0 |
| calibration | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 60, "song": true, "state": "virgin"} | 0 |
| calibration | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": false, "state": "virgin"} | 0 |
| calibration | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": true, "state": "virgin"} | 0 |
| calibration | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 360, "song": false, "state": "virgin"} | 0 |
| calibration | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 360, "song": true, "state": "virgin"} | 0 |
| calibration | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 720, "song": false, "state": "virgin"} | 0 |
| calibration | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 720, "song": true, "state": "virgin"} | 0 |
| calibration | {"direct_vpoEN_hz": 60, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": false, "state": "virgin"} | 0 |
| calibration | {"direct_vpoEN_hz": 180, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": false, "state": "virgin"} | 0 |
| calibration | {"direct_vpoEN_hz": 360, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": false, "state": "virgin"} | 0 |
| calibration | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": false, "state": "mated"} | 0 |
| calibration | {"direct_vpoEN_hz": 60, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": false, "state": "mated"} | 0 |
| calibration | {"direct_vpoEN_hz": 180, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": false, "state": "mated"} | 0 |
| calibration | {"direct_vpoEN_hz": 360, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": false, "state": "mated"} | 0 |
| calibration | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": true, "state": "mated"} | 0 |
| calibration | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.3, "jo_max_hz": 180, "song": false, "state": "virgin"} | 0 |
| calibration | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.3, "jo_max_hz": 180, "song": true, "state": "virgin"} | 0 |
| calibration | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.3, "jo_max_hz": 180, "song": false, "state": "mated"} | 0 |
| calibration | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.3, "jo_max_hz": 180, "song": true, "state": "mated"} | 0 |
| pre_registered_test | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 720, "song": false, "state": "virgin"} | 0 |
| pre_registered_test | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 720, "song": true, "state": "virgin"} | 0 |
| pre_registered_test | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": false, "state": "virgin"} | 0 |
| pre_registered_test | {"direct_vpoEN_hz": 60, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": false, "state": "virgin"} | 0 |
| pre_registered_test | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": false, "state": "mated"} | 0 |
| pre_registered_test | {"direct_vpoEN_hz": 60, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": false, "state": "mated"} | 0 |
| pre_registered_test | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": true, "state": "virgin"} | 0 |
| pre_registered_test | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.0, "jo_max_hz": 180, "song": true, "state": "mated"} | 0 |
| pre_registered_test | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.3, "jo_max_hz": 180, "song": false, "state": "virgin"} | 0 |
| pre_registered_test | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.3, "jo_max_hz": 180, "song": true, "state": "virgin"} | 0 |
| pre_registered_test | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.3, "jo_max_hz": 180, "song": false, "state": "mated"} | 0 |
| pre_registered_test | {"direct_vpoEN_hz": 0, "excitatory_gain": 1.3, "jo_max_hz": 180, "song": true, "state": "mated"} | 0 |

Elapsed seconds: {"calibration": 162.0540607999974, "test": 116.12365549999959}

The gain-1 sensitivity controls include all four state/song conditions. Identical configurations are reused within a stage. Quick data are excluded.
No behavioural conclusion follows from these isolated neuronal readouts.

## Preregistration

# female_hearing_v1: the she hears ladder

Version 1. Preregistered before experimental data collection.
Graph: build/graph_female.npz; record SHA256. Kernel: shiu; dt 0.2 ms;
50 ms windows, 20 windows, first 4 warm-up. Backend: fast_gpu batches,
float32. Each condition starts from rest. Virgin SAG: 50 Hz grid Poisson;
mated SAG: 0 Hz. Readouts: vpoDN (2 cells), vpoEN (4), pC1 (10),
network total spikes and mean Hz/neuron, and measured-window fraction above
30 Hz/neuron. Record each readout cell separately and requested, sampled,
and delivered drive. Delivered drive means sampled inputs coincident with
output spikes; total cell firing is also recorded.

Calibration seeds: 0-9. Test seeds: 10-29, in a separate run after an
automatic frozen selection. Calibration never uses test seeds.
Quick: seeds 0,1, six windows with four warm-up, calibration conditions only;
quick results cannot freeze a choice or enter confirmatory results.

Arm (a), calibration: virgin; JO_MAX_HZ in {60,180,360,720}, song and
paired silence at each dose. Report vpoEN and vpoDN song-minus-silence
mean differences and SE. Freeze the LOWEST dose with vpoEN difference >2 SE.
If none passes, select 720 and record "no transfer".

Arm (b), positive control, calibration: no song; direct vpoEN grid Poisson
at {0,60,180,360} Hz, virgin and mated. Report realized vpoEN firing and
vpoDN. Differences are relative to state-matched 0 Hz; selection uses virgin.
Freeze the LOWEST positive dose with vpoDN difference >2 SE; otherwise
select 360 and record "no transfer".

Arm (c), independent sensitivity, calibration seeds 0-9: positive network
edges only multiplied by 1.3; negative edges, external drive and SAG unchanged.
JO_MAX_HZ 180, all four virgin/mated x song/silence conditions, with gain 1.0
controls for the same four conditions and seeds. Report virgin vpoDN
song-minus-silence and network ignition fraction. Identical gain-1 virgin
conditions in arm (a) may be reused by identity, with no duplicate evidence.

Pre-registered test, seeds 10-29 after freezing, the same session:
T1 "she hears at the chosen dose": virgin vpoDN song-minus-silence at
the selected JO dose >2 SE.
T2 "vpoEN relays": virgin vpoDN at selected direct vpoEN dose minus 0 >2 SE.
T3 "state gates the relay": the T2 difference is smaller in mated than
virgin, qualitatively following Wang et al. (2021), Nature. Descriptive only;
report mated-minus-virgin paired difference of differences, no verdict.
T4: gain 1.3, JO 180, virgin song-minus-silence and ignition, descriptive.
Include all four states/song conditions at gains 1.0 and 1.3 for T4 context.

For every contrast, pair by seed and use sample SD of differences divided
by sqrt(n). For T1 and T2, mean paired difference over 20 seeds >2 SE means
"supported"; otherwise "not supported". Strict inequality; zero with zero
SE is not supported. Calibration and pre-registered test stay separate.
No additional dose search, seed exclusion, or tuning after freezing.

Song and ear match female_no_v1: amplitude 1, pulse mixture 0.7, sample rate
22050 Hz; 35 ms pulse IPI, 4 ms Hann pulse, 250 Hz carrier, 150 Hz sine.
Carry song time between windows. Fourth-order bands 100-500 and 500-2500 Hz,
sosfiltfilt padlen 27 per window; ten 5 ms slices map clipped band RMS/RMS_FULL
to JO_MAX_HZ. RMS_FULL is the full-amplitude one-second pure-pulse reference.
JO groups use dictionary version 1; SAG uses exact AN_SMP_2, AN_FLA_SMP_2,
ANXXX983 union; pC1 uses pC1a-e; vpoDN uses DNp37; vpoEN uses dictionary
version 1. All four drive populations remain targeted even at zero rate,
preserving paired random streams. This direct-drive target convention applies
to every arm and differs from female_no_v1's three-population target list.
Group selection and count checks precede simulation.

Budget: stop with partial evidence if total task time exceeds 40 minutes.
Save calibration, frozen decision and test separately with content hashes.
Report all results regardless of direction. These isolated neural outputs
do not establish behavioural hearing, refusal or mating.

