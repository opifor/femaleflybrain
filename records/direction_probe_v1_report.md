# Direction probe v1

Status: COMPLETE

Differences are paired Hz/neuron, mean +/- SE; classes use fixed effect bounds.
Zero SE is expected with constant deterministic input and no random drive.
A silent K0 creates a firing-rate floor: equivalence cannot refute inhibitory connectivity.
Grid note (added after review): the three ceilings collapse the 18 gamma-by-ceiling points to 8 distinct flux levels per arm, and the ten seeds are deterministic replicates (seed_columns_identical is true in every condition), so the 18/18 count describes 8 distinct experiments and a zero SE is arithmetic, not sampling evidence.

| gamma | ceiling | arm | vpoEN delta +/- SE | class | vpoDN delta +/- SE | class | ignition | max target loss |
|---:|---|---|---|---|---|---|---:|---:|
| 0.01 | uncapped | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.120271 |
| 0.01 | uncapped | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.0676522 |
| 0.03 | uncapped | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.233776 |
| 0.03 | uncapped | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.157855 |
| 0.1 | uncapped | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.365823 |
| 0.1 | uncapped | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.300677 |
| 0.3 | uncapped | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.518667 |
| 0.3 | uncapped | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.440992 |
| 1 | uncapped | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.664495 |
| 1 | uncapped | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.588073 |
| 3 | uncapped | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.767727 |
| 3 | uncapped | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.713355 |
| 0.01 | 1/2.2 | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.120271 |
| 0.01 | 1/2.2 | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.0676522 |
| 0.03 | 1/2.2 | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.233776 |
| 0.03 | 1/2.2 | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.157855 |
| 0.1 | 1/2.2 | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.365823 |
| 0.1 | 1/2.2 | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.300677 |
| 0.3 | 1/2.2 | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.518667 |
| 0.3 | 1/2.2 | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.440992 |
| 1 | 1/2.2 | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.571285 |
| 1 | 1/2.2 | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.496116 |
| 3 | 1/2.2 | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.571285 |
| 3 | 1/2.2 | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.496116 |
| 0.01 | 1/5 | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.120271 |
| 0.01 | 1/5 | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.0676522 |
| 0.03 | 1/5 | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.233776 |
| 0.03 | 1/5 | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.157855 |
| 0.1 | 1/5 | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.365823 |
| 0.1 | 1/5 | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.300677 |
| 0.3 | 1/5 | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.461037 |
| 0.3 | 1/5 | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.389376 |
| 1 | 1/5 | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.461037 |
| 1 | 1/5 | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.389376 |
| 3 | 1/5 | K1 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.461037 |
| 3 | 1/5 | K2 | 0 +/- 0.0 | equivalence-zero | 0 +/- 0.0 | equivalence-zero | 0 | 0.389376 |

## D1--D5

- D1/D2: descriptive direction classes above; no gain changes or E5 efficacy claim.
- D3: per-target/per-seed dropped and arrived mass are in the raw NPZ files.
- K0 flux=0: not ignited; no target exceeds 5% loss; barred targets=0; B1 measured spikes={'K1': 0, 'K2': 0}; warmup match=True.
- K1 flux=0.01: not ignited; saturation interpretation barred; barred targets=4; B1 measured spikes={'K1': 0, 'K2': 0}; warmup match=True.
- K2 flux=0.01: not ignited; saturation interpretation barred; barred targets=4; B1 measured spikes={'K1': 0, 'K2': 0}; warmup match=True.
- K1 flux=0.03: not ignited; saturation interpretation barred; barred targets=15; B1 measured spikes={'K1': 0, 'K2': 0}; warmup match=True.
- K2 flux=0.03: not ignited; saturation interpretation barred; barred targets=18; B1 measured spikes={'K1': 0, 'K2': 0}; warmup match=True.
- K1 flux=0.1: not ignited; saturation interpretation barred; barred targets=84; B1 measured spikes={'K1': 0, 'K2': 0}; warmup match=True.
- K2 flux=0.1: not ignited; saturation interpretation barred; barred targets=71; B1 measured spikes={'K1': 0, 'K2': 0}; warmup match=True.
- K1 flux=0.3: not ignited; saturation interpretation barred; barred targets=288; B1 measured spikes={'K1': 0, 'K2': 0}; warmup match=True.
- K2 flux=0.3: not ignited; saturation interpretation barred; barred targets=227; B1 measured spikes={'K1': 0, 'K2': 2260}; warmup match=True.
- K1 flux=1: not ignited; saturation interpretation barred; barred targets=527; B1 measured spikes={'K1': 0, 'K2': 0}; warmup match=True.
- K2 flux=1: not ignited; saturation interpretation barred; barred targets=505; B1 measured spikes={'K1': 0, 'K2': 5410}; warmup match=True.
- K1 flux=3: not ignited; saturation interpretation barred; barred targets=695; B1 measured spikes={'K1': 1630, 'K2': 0}; warmup match=True.
- K2 flux=3: not ignited; saturation interpretation barred; barred targets=782; B1 measured spikes={'K1': 0, 'K2': 10730}; warmup match=True.
- K1 flux=0.454545: not ignited; saturation interpretation barred; barred targets=362; B1 measured spikes={'K1': 0, 'K2': 0}; warmup match=True.
- K2 flux=0.454545: not ignited; saturation interpretation barred; barred targets=317; B1 measured spikes={'K1': 0, 'K2': 3190}; warmup match=True.
- K1 flux=0.2: not ignited; saturation interpretation barred; barred targets=206; B1 measured spikes={'K1': 0, 'K2': 0}; warmup match=True.
- K2 flux=0.2: not ignited; saturation interpretation barred; barred targets=156; B1 measured spikes={'K1': 0, 'K2': 1380}; warmup match=True.
- D4: source neurons may spike; zero installed/scaled outgoing counts establish inert ordinary outputs.
- D5: [{"gamma": 0.01, "ceiling": "uncapped", "flux": 0.01, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 0.03, "ceiling": "uncapped", "flux": 0.03, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 0.1, "ceiling": "uncapped", "flux": 0.1, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 0.3, "ceiling": "uncapped", "flux": 0.3, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 1.0, "ceiling": "uncapped", "flux": 1.0, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 3.0, "ceiling": "uncapped", "flux": 3.0, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 0.01, "ceiling": "1/2.2", "flux": 0.01, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 0.03, "ceiling": "1/2.2", "flux": 0.03, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 0.1, "ceiling": "1/2.2", "flux": 0.1, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 0.3, "ceiling": "1/2.2", "flux": 0.3, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 1.0, "ceiling": "1/2.2", "flux": 0.45454545454545453, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 3.0, "ceiling": "1/2.2", "flux": 0.45454545454545453, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 0.01, "ceiling": "1/5", "flux": 0.01, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 0.03, "ceiling": "1/5", "flux": 0.03, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 0.1, "ceiling": "1/5", "flux": 0.1, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 0.3, "ceiling": "1/5", "flux": 0.2, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 1.0, "ceiling": "1/5", "flux": 0.2, "vpoEN_same": true, "vpoDN_same": true}, {"gamma": 3.0, "ceiling": "1/5", "flux": 0.2, "vpoEN_same": true, "vpoDN_same": true}]

## Provenance

Protocol SHA256: 1f25c7ab1f2ae166a837fc322e3a5f300f52f8b953f4c44698eb6141636e3c53
Graph SHA256: 35e5c3b4cca86b27392a144a4d6bcb37de2f3f97f29d71f5c0a5c20b1cd593b8
Release SHA256: 576dd0c5c34980223b0230bfcfc9ff2377de9358d4e06309ad9ea4f48db6bff9
Wall seconds: 632.751
Dictionary API and resolved population identities are hashed in the JSON record.
No core, hook, dictionary, ear, gain or parameter changes except prescribed dt.
Clean room: excluded trees were not inspected; only the authorized runtime dependency path was supplied externally.
All raw artifact hashes and environment versions are in the JSON.

## Explicit measured conclusions

D1: equivalence-zero.
D2: equivalence-zero.
K0 network rate was 0 Hz/neuron. No readout suppression can be measured below a silent baseline; the inhibitory path-sign prediction remains unresolved by this floor-limited firing-rate contrast.
D3: maximum ignition fraction 0; maximum target/seed dropped fraction 0.76772739. The >5% rule applies to the affected targets only, not to every target in the condition.
Target identities, arrived mass, dropped mass, fractions and per-target interpretation bars: `build/records-raw/direction_probe_v1_full/target_loss.json` (SHA256 `cd4ebbff59e1eacba432607abda1ded89edba75863869ebc7614c34b4fbd2d09`). Zero-arrival targets have undefined fractions and are omitted from this target table; their zero mass remains in the NPZ.
D4: all warmup per-cell counts match K0 exactly; installed and scaled source outgoing counts are zero. Source spike counts are not all zero. This violates a literal source-silence expectation, but is allowed by the release-hook contract: spiking sources have inert ordinary outputs.

| arm | effective flux | source spikes (sum over 10 seeds, measured 800 ms) | network Hz/neuron | window active fraction | overall active fraction | barred targets |
|---|---:|---:|---:|---:|---:|---:|
| K1 | 0.01 | 0 | 0.0013975144 | 2.885191e-05 | 2.885191e-05 | 4 |
| K2 | 0.01 | 0 | 0.00088358975 | 3.1556777e-05 | 3.6064888e-05 | 4 |
| K1 | 0.03 | 0 | 0.0071859289 | 0.00014741523 | 0.00017311146 | 15 |
| K2 | 0.03 | 0 | 0.0073482209 | 0.00017266065 | 0.00019475039 | 18 |
| K1 | 0.1 | 0 | 0.049670367 | 0.0011211672 | 0.0016806238 | 84 |
| K2 | 0.1 | 0 | 0.036317342 | 0.00068072476 | 0.00078621456 | 71 |
| K1 | 0.3 | 0 | 0.22096055 | 0.004238526 | 0.0061743088 | 288 |
| K2 | 0.3 | 2260 | 0.15620605 | 0.003047483 | 0.0044431942 | 227 |
| K1 | 1 | 0 | 0.66838155 | 0.010312755 | 0.013913834 | 527 |
| K2 | 1 | 5410 | 0.48430636 | 0.0078152612 | 0.010574225 | 505 |
| K1 | 3 | 1630 | 1.2433731 | 0.016360386 | 0.020016013 | 695 |
| K2 | 3 | 10730 | 2.89574 | 0.043226473 | 0.073125167 | 782 |
| K1 | 0.45454545 | 0 | 0.33029126 | 0.005718088 | 0.0079054234 | 362 |
| K2 | 0.45454545 | 3190 | 0.24484452 | 0.0045640116 | 0.0062464386 | 317 |
| K1 | 0.2 | 0 | 0.13552283 | 0.0028044958 | 0.0039166468 | 206 |
| K2 | 0.2 | 1380 | 0.095689164 | 0.001899718 | 0.0026760147 | 156 |

D5: main and secondary list comparison at every labeled point.

| gamma | ceiling | K1 vpoEN | K2 vpoEN | vpoEN same | vpoDN same |
|---:|---|---|---|---|---|
| 0.01 | uncapped | equivalence-zero | equivalence-zero | True | True |
| 0.03 | uncapped | equivalence-zero | equivalence-zero | True | True |
| 0.1 | uncapped | equivalence-zero | equivalence-zero | True | True |
| 0.3 | uncapped | equivalence-zero | equivalence-zero | True | True |
| 1 | uncapped | equivalence-zero | equivalence-zero | True | True |
| 3 | uncapped | equivalence-zero | equivalence-zero | True | True |
| 0.01 | 1/2.2 | equivalence-zero | equivalence-zero | True | True |
| 0.03 | 1/2.2 | equivalence-zero | equivalence-zero | True | True |
| 0.1 | 1/2.2 | equivalence-zero | equivalence-zero | True | True |
| 0.3 | 1/2.2 | equivalence-zero | equivalence-zero | True | True |
| 1 | 1/2.2 | equivalence-zero | equivalence-zero | True | True |
| 3 | 1/2.2 | equivalence-zero | equivalence-zero | True | True |
| 0.01 | 1/5 | equivalence-zero | equivalence-zero | True | True |
| 0.03 | 1/5 | equivalence-zero | equivalence-zero | True | True |
| 0.1 | 1/5 | equivalence-zero | equivalence-zero | True | True |
| 0.3 | 1/5 | equivalence-zero | equivalence-zero | True | True |
| 1 | 1/5 | equivalence-zero | equivalence-zero | True | True |
| 3 | 1/5 | equivalence-zero | equivalence-zero | True | True |

## Execution and acceptance

Quick: seed 100, two uncapped points, both arms and K0, 58.988 seconds; complete, warmup checks passed. Full: 632.751 seconds, 17 unique batches including K0, 36 labeled relay rows, ten matched seeds; no truncation.
Pytest: 15 passed, exit 0. Intentional failure: 1 failed, 14 deselected, exit 1. Outputs and test hash: `records/direction_probe_v1_tests.json`.
Acceptance used the requested Python 3.12 runtime, externally supplied dependency path, and actual CUDA fast_gpu chain; no alternate environment or backend was used.
Reproduce with `python -m pytest -q -p no:cacheprovider tests/test_direction_probe.py`, then `python -m flybench.experiment.direction_probe quick`, then `python -m flybench.experiment.direction_probe full` using the authorized runtime and dependency environment.
Raw acceptance checks: `records/direction_probe_v1_acceptance.json`.
Deviations: no simulation/grid deviations. Missing dictionary_fafb.json used the permitted dictionary API fallback. The preregistration explicitly resolves cell-guard gaps as unclassified and uses absolute per-cell deltas for equivalence; no observed row falls in a gap. Source silence is a failed expectation where spikes occur, not a hook-invariant failure.
Ten seed columns are deterministic replicates in this no-noise design; descriptive SE=0 does not imply ten independent biological observations.
Quick used batch width 1 and full used width 10. At flux 3, quick source counts per trial were K1=162 and K2=1074; full per-trial counts were K1=163 and K2=1073. Cross-batch bitwise equivalence was not established. All full paired contrasts use the same batch width.
No git add, commit or push was run. Only authorized files were written.
