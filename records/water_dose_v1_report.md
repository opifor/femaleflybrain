# water_dose_v1 report

Full run, ten seeds; mean +/- SE in Hz. MN9 readout [200,1000) ms.
GRN drive is delivered external-event Hz over the full 1 s.

| Condition | MN9_ref | MN9_other | Delivered GRN drive |
| --- | ---: | ---: | ---: |
| baseline | 0.000 +/- 0.000 | 0.000 +/- 0.000 | 0.000 +/- 0.000 |
| water100 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | 100.894 +/- 1.019 |
| water160 | 13.250 +/- 2.060 | 4.375 +/- 1.197 | 160.794 +/- 1.052 |
| water200 | 34.125 +/- 2.141 | 14.625 +/- 1.103 | 201.361 +/- 1.142 |
| water260 | 56.625 +/- 2.117 | 27.125 +/- 1.972 | 261.761 +/- 1.468 |
| sugar100 | 63.375 +/- 1.817 | 50.375 +/- 1.901 | 100.860 +/- 0.866 |
| sugar200 | 93.875 +/- 2.278 | 65.625 +/- 1.240 | 201.215 +/- 0.928 |

W1: 13.250 +/- 2.060; supported=True.
W2 descriptive order: {'MN9_ref': True, 'MN9_other': True}.
W3: no laterality signal.
This preregistered label means no positive other-minus-ref mismatch signal, not equal sides. Other-minus-ref contrasts at water160/200/260 are -8.875 +/- 1.078, -19.500 +/- 1.137 and -29.500 +/- 1.470 Hz: ref is higher at each active dose.
W4: {'passed': True, 'reference_hz': 63.4, 'band_hz': [53.89, 72.91]}; status=PASS.
W4 is a reproducibility control; graph, parameter and engine hashes also match the prior benchmark.

| Population | Present/requested | IDs | Graph sides | Types |
| --- | --- | --- | --- | --- |
| water | 18/18 | [720575940612950568, 720575940631898285, 720575940606002609, 720575940612579053, 720575940622902535, 720575940616177458, 720575940660292225, 720575940622486922, 720575940613786774, 720575940629852866, 720575940625861168, 720575940613996959, 720575940617857694, 720575940644965399, 720575940625203504, 720575940630553415, 720575940635172191, 720575940634796536] | {'L': 18, 'R': 0, 'M': 0, 'unknown': 0} | ['LB2d', 'LB3'] |
| sugar | 20/21 | [720575940624963786, 720575940630233916, 720575940637568838, 720575940638202345, 720575940617000768, 720575940630797113, 720575940632889389, 720575940621754367, 720575940621502051, 720575940640649691, 720575940639332736, 720575940616885538, 720575940639198653, 720575940617937543, 720575940632425919, 720575940633143833, 720575940612670570, 720575940628853239, 720575940629176663, 720575940611875570] | {'L': 20, 'R': 0, 'M': 0, 'unknown': 0} | ['LB3'] |
| MN9_ref | 1/1 | [720575940660219265] | {'L': 0, 'R': 1, 'M': 0, 'unknown': 0} | ['CB0701'] |
| MN9_other | 1/1 | [720575940618238523] | {'L': 1, 'R': 0, 'M': 0, 'unknown': 0} | ['CB0701'] |

## Limits and provenance

Deviation: sugar has 20/21 source IDs, as in the prior benchmark; missing ID 720575940620900446. No remapping.
Graph labels are reported literally. Historical FAFB left/right reversal and the unverified water pairing prevent an anatomical-side conclusion.
Supplied paper context (qualitative): paper: water activates MN9 at 160 Hz necessity dose; exact water100 value not published.
No parameter or gain changes. An absent other readout cannot establish bilateral silence.
Run wall time: 63.459 s.
Quick wall time: 66.184 s; complete pytest/probe/quick/full chain: 136.429 s.
Acceptance: 10 tests passed, 1 opt-in probe skipped; separate intentional probe returned 1 failed and exit 1. Quick/full completed 14/70 trials with exit 0.
Operational correction before simulation: runner expected 11 passing tests, corrected to the inspected count of 10; no test or hypothesis changed.
Protocol SHA256: 76ec17cba6cfe8e82d18831e6c9c2a73a67b11f8851a9183a4f1f7a9cec958a0.
Graph SHA256: 35e5c3b4cca86b27392a144a4d6bcb37de2f3f97f29d71f5c0a5c20b1cd593b8.
Environment: {"cuda": "12.4", "device": "cuda", "gpu": "NVIDIA GeForce RTX 4090", "numpy": "2.4.2", "python": "3.12.14", "scipy": "1.17.1", "torch": "2.6.0+cu124"}.
Clean room: no sibling project or archive source read; only the explicitly supplied dependency directory used for imports. No git writes.
Raw seed and cell audits: build/records-raw/water_dose_v1_full.json.
Quick, test and execution evidence: records/water_dose_v1_checks.json.
