# male_route_v1

## Test

Rates are Hz/neuron; ignition is a window fraction; active is a percent over the measured-period union.
Values are mean +/- SE across 20 seeds, with windows averaged within seed. Quick is excluded.

| Network | Drive | pIP10 | P1 | Network | Ignition | Active % | Or47b sampled Hz |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| intact | zero | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| intact | scent240 | 7.625 +/- 0.323 | 0.076087 +/- 0.00895 | 5.68879 +/- 0.00319 | 0 +/- 0 | 7.6419 +/- 0.00765 | 240.146 +/- 0.302 |
| intact | scent960 | 10.2812 +/- 0.224 | 0.369565 +/- 0.00994 | 6.40007 +/- 0.00334 | 0 +/- 0 | 7.76329 +/- 0.00955 | 959.901 +/- 0.578 |
| p1_lesion | zero | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| p1_lesion | scent240 | 7.1875 +/- 0.296 | 0.0842391 +/- 0.00984 | 5.68562 +/- 0.00333 | 0 +/- 0 | 7.65355 +/- 0.0126 | 240.146 +/- 0.302 |
| p1_lesion | scent960 | 10.9688 +/- 0.2 | 0.366848 +/- 0.00996 | 6.40278 +/- 0.00254 | 0 +/- 0 | 7.7685 +/- 0.00891 | 959.901 +/- 0.578 |
| random_lesion | zero | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| random_lesion | scent240 | 7.75 +/- 0.254 | 0.080163 +/- 0.008 | 5.68106 +/- 0.00338 | 0 +/- 0 | 7.63154 +/- 0.0129 | 240.146 +/- 0.302 |
| random_lesion | scent960 | 10.5312 +/- 0.254 | 0.38587 +/- 0.00997 | 6.39751 +/- 0.00435 | 0 +/- 0 | 7.76741 +/- 0.0122 | 959.901 +/- 0.578 |

Primary 240 Hz inference:

```json
{
  "intact": {
    "mean": 7.625,
    "se": 0.32253620767777047,
    "n": 20
  },
  "p1_lesion": {
    "mean": 7.1875,
    "se": 0.29559540716466165,
    "n": 20
  },
  "random_lesion": {
    "mean": 7.75,
    "se": 0.2540785725964147,
    "n": 20
  },
  "difference_of_differences": {
    "mean": 0.4375,
    "se": 0.46704734629822114,
    "n": 20
  },
  "control_margin": {
    "mean": 1.65,
    "se": 0.4162212531562358,
    "n": 20
  },
  "R0": "supported",
  "R2": "supported",
  "R1": "P1 bypass SUPPORTED"
}
```

Descriptive 960 Hz analysis:

```json
{
  "intact": {
    "mean": 10.28125,
    "se": 0.22431822878035995,
    "n": 20
  },
  "p1_lesion": {
    "mean": 10.96875,
    "se": 0.20009763241977652,
    "n": 20
  },
  "random_lesion": {
    "mean": 10.53125,
    "se": 0.25357233863545253,
    "n": 20
  },
  "difference_of_differences": {
    "mean": -0.6875,
    "se": 0.24793555508172724,
    "n": 20
  },
  "control_margin": {
    "mean": 2.30625,
    "se": 0.34009419651031975,
    "n": 20
  },
  "R0": "supported",
  "R2": "supported",
  "R1": "P1 bypass SUPPORTED"
}
```

## Paths

Exact-length top-ten simple anatomical paths, ranked by minimum unsigned edge synapse count.
Signs do not affect ranking. P1 shares refer only to returned paths. Full IDs and edge weights are in the paths JSON.

| Synapses | Rank | Bottleneck | Types (source to target) | Through P1 |
| ---: | ---: | ---: | --- | --- |
| 2 | 1 | 1 | ORN_VA1v -> PPM1201 -> pIP10 | False |
| 3 | 1 | 34 | ORN_VA1v -> MZ_lv2PN -> PVLP217m -> pIP10 | False |
| 3 | 2 | 34 | ORN_VA1v -> MZ_lv2PN -> PVLP217m -> pIP10 | False |
| 3 | 3 | 34 | ORN_VA1v -> MZ_lv2PN -> PVLP217m -> pIP10 | False |
| 3 | 4 | 34 | ORN_VA1v -> MZ_lv2PN -> PVLP217m -> pIP10 | False |
| 3 | 5 | 34 | ORN_VA1v -> MZ_lv2PN -> PVLP217m -> pIP10 | False |
| 3 | 6 | 34 | ORN_VA1v -> MZ_lv2PN -> PVLP217m -> pIP10 | False |
| 3 | 7 | 34 | ORN_VA1v -> MZ_lv2PN -> PVLP217m -> pIP10 | False |
| 3 | 8 | 34 | ORN_VA1v -> MZ_lv2PN -> PVLP217m -> pIP10 | False |
| 3 | 9 | 34 | ORN_VA1v -> MZ_lv2PN -> PVLP217m -> pIP10 | False |
| 3 | 10 | 34 | ORN_VA1v -> MZ_lv2PN -> PVLP217m -> pIP10 | False |
| 4 | 1 | 63 | ORN_VA1v -> MZ_lv2PN -> PVLP149 -> AVLP718m -> pIP10 | False |
| 4 | 2 | 63 | ORN_VA1v -> MZ_lv2PN -> PVLP149 -> AVLP718m -> pIP10 | False |
| 4 | 3 | 63 | ORN_VA1v -> MZ_lv2PN -> PVLP149 -> AVLP718m -> pIP10 | False |
| 4 | 4 | 63 | ORN_VA1v -> MZ_lv2PN -> PVLP149 -> AVLP718m -> pIP10 | False |
| 4 | 5 | 63 | ORN_VA1v -> MZ_lv2PN -> PVLP149 -> AVLP718m -> pIP10 | False |
| 4 | 6 | 63 | ORN_VA1v -> MZ_lv2PN -> PVLP149 -> AVLP718m -> pIP10 | False |
| 4 | 7 | 63 | ORN_VA1v -> MZ_lv2PN -> PVLP149 -> AVLP718m -> pIP10 | False |
| 4 | 8 | 63 | ORN_VA1v -> MZ_lv2PN -> PVLP149 -> AVLP718m -> pIP10 | False |
| 4 | 9 | 63 | ORN_VA1v -> MZ_lv2PN -> PVLP149 -> AVLP718m -> pIP10 | False |
| 4 | 10 | 63 | ORN_VA1v -> MZ_lv2PN -> PVLP149 -> AVLP718m -> pIP10 | False |

Length 2: P1 share 0/1.


Length 3: P1 share 0/10.


Length 4: P1 share 0/10.


## Provenance and limitations

Protocol SHA256: 20a1d9be86cbbe0517bbc64e0816075245dbf45868c3db2d0ddb1340ff2449e3
Graph SHA256: 6afa6161b593b03cfa0f6027b697d5b1ff37afa5028c870f8012122f87d03a3d
Dictionary SHA256: 00e7bdfa0e890d1267ca08a69c0c49a32464a7b38db5c0832ca1f42c596d6473
Environment: {"python": "3.12.14", "numpy": "2.4.2", "scipy": "1.17.1", "torch": "2.6.0+cu124", "cuda": "12.4", "device": "cuda", "gpu": "NVIDIA GeForce RTX 4090"}
Wall seconds: quick=78.254, TEST=818.403, paths=17.292.
Complete: quick=True, TEST=True.
Random control is not superclass matched and can include sensory or readout cells; all lesion IDs are in raw metadata.
Batch size one uses the unchanged fast_gpu backend. Fixed zero-dose targets retain the backend input/refractory convention.
Source hashes, parameters, realized input, per-seed metrics and raw hashes are in the stage JSON files.
Clean room: only this repository was inspected; the supplied dependency import path was used without inspecting adjacent project sources.
No world or behavior was simulated. Anatomical top paths are descriptive; GPU reproducibility is not claimed bitwise.

## Execution checks and deviations

Native-chain synthetic pytest before data: 9 passed, 1 skipped, exit 0.
The deliberate failing probe returned 1 failed, 9 deselected, exit 1.
After the summary-key correction, pytest returned 10 passed, 1 skipped, exit 0.
Evidence audit: 883 checks passed, 0 failed, exit 0. This includes raw hashes,
complete 180-trial TEST coverage, identical sampled input within paired dose/seed,
active-union counts, lesion identities, unchanged core/dictionary source hashes,
and independent sparse walk-count certificates for the strongest path scores.
There is only one two-synapse path, rather than ten; the walk-count census confirms this.
Pooled P1 share among returned strongest paths is 0/21, not a whole-graph path share.

The original summary merged network identity and network rate under one key.
The report rebuilds summaries from unchanged per-seed data using separate keys;
path table formatting was also corrected. The execution source is retained under
build/records-raw/male_route_v1_execution_source.py and matches stage source hashes.
No protocol, simulation parameter, core, dictionary or numerical trial was changed.
No environment workaround, external project inspection or git write was used.
Total recorded quick, TEST and path execution time is 913.949 seconds (15.23 minutes),
excluding implementation, synthetic tests and report verification; the task remained
within the 30-minute budget. All delivered text uses UTF-8 without BOM.

At 240 Hz the P1-lesion response retains 94.26% of the intact paired response;
the random-lesion response retains 101.64%. R0 and R2 pass, and the preregistered
R1 rule supports a P1 bypass in this model. At 960 Hz the corresponding descriptive
retention is 106.69%; this is not a separate confirmatory hypothesis.
