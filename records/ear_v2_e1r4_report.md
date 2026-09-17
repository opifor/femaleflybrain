# ear_v2 E1 round-4 amendment report

G5c measured on the three frozen round-3 winners, without refit or family selection.

Each G5-legacy, T1 and T2 pair is continuous / pulsed. G5c-300 is S / P20/P1 / E20/E1 (diagnostic, not a gate).

| Family | G5-legacy C / P | T1 C / P | T2 C / P | G5c S | P20/P1 | E20/E1 | G5c-300 S / P / E | G5c verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| energy_feedback | 0.629185 / 0.065149 | 0.629185 / 0.493368 | 0.734157 / 0.985657 | 0.487188 | 0.940957 | 0.942902 | 0.502972 / 0.982970 / 0.985299 | passed |
| asymmetric_energy | 0.609786 / 0.061471 | 0.609786 / 0.465933 | 0.705831 / 0.911723 | 0.488387 | 0.812790 | 0.801373 | 0.506724 / 0.898269 / 0.905670 | passed |
| rectified_state | 0.272466 / 0.058244 | 0.272466 / 0.503261 | 0.313652 / 0.933345 | 0.302164 | 0.800708 | 0.834773 | 0.304728 / 0.929834 / 0.923302 | passed |

G1-G4/G6/G7 unchanged from round 3 (not re-run). This refers to family-winner metrics; the prescribed full regression suite remains part of acceptance.
Config defaults and model source are unchanged. G3 thresholds are unchanged; historical G3 misses are not reclassified as passes.

G5-legacy retains its exact formula and historical direction flag, but is descriptive, duty-cycle confounded; not a gate. Without adaptation, a rectangular response at duty D=4/36 gives mean/peak=D*R/R=0.111111, approximately 0.11. Finite Hann windows and filter tails need not yield exactly this value. Historical legacy C > P and T2 C < P hold in all three families; a round-4 G5c direction must come from its actual measurement, not extrapolation from T2.

G5c uses 250 Hz Gabor pulses, printed exp(-(t/sigma)^2), sigma 4.6 ms, phi=0, 16 ms support, 36 ms IPI, 20 pulses and 50 ms initial support onset. Each fixed pulse template and the 0.5 s sine are set to realized absolute peak 4 mm/s; whole-train RMS is not matched. The 200 ms post-train silence starts after the last 36 ms response interval. The final window ends at the virtual next onset, not at the end of the silence. Continuous means use onset-relative [0,10) and [300,400) ms. Pulse integrals are sum(response)/fs. The gate is strictly S < P20/P1; E20/E1 and the 300 Hz Hann variant are diagnostics. The source provides no universal numerical cutoff.

Observable mismatch, declared: this bench averages already rectified graded channels; the paper measures a CAP Hilbert envelope. No Hilbert transform is applied. Fixed 16 ms truncation, sample-centered waveform and sampled peak normalization are declared reconstruction choices, not recovered source code. Main Fig 3h identifies first/twentieth pulses; its exact amplitude estimator is unresolved in report 17. Fig 3j supplies individual-pulse peaks; the gate combines these as an explicit bench reconstruction.

Ledger R3_006 and R3_007 now have status REPORTED, with original numeric values, attribution fields and prior notes retained. Added notes distinguish the prose 5-20 ms range from individual Fig 1e fits exceeding 20 ms, and the approximate 30 ms recovery statement from a fitted constant; Fig 1d is a tuning curve. New rung-3 REPORTED entry R3_C18_PROTOCOL_R4 records Fig 3h/3j, Supp Fig 8a,b/e, Gabor parameters and CAP envelope. n=5 belongs to the supplementary continuous comparison; main Fig 3h uses n=6. Source: report 17 (as read by external research model), DOI 10.1038/s41467-017-02453-9. No independent primary-source audit is claimed. All fit_allowed values and unrelated entries are preserved.

Pytest: 59 passed, 1 skipped, 3 xfailed in 1.48s; exit 0. Harness: 1 failed in 0.05s; exit 1.
Static checks: exact preregistration byte prefix, frozen LF hashes, all existing ledger fields except the two authorized status/notes corrections, unchanged fit policy, unchanged model/fit bytes, and unchanged earlier test source were checked. These checks do not establish Python syntax, numerical behavior or pytest success.

Deviations: input ledger already version 1.2 (retained). The current preregistration prefix is LF and was retained byte-for-byte. The appendix inherited a CRLF description from the round-3 report; byte inspection of this checkout corrects that description, without changing the frozen appendix or its hash. The requested Python launch was blocked by Windows application-control policy; PowerShell created the preregistration freeze before implementation or evaluation. No alternate Python or security bypass was attempted. That blocker applied at freeze time only: the operator then ran the acceptance chain with a different host interpreter (recorded in the metrics environment field), pytest exit 0, and the table above is the measured result.

Reproduction, from repo root with the prescribed interpreter and dependency-only PYTHONPATH, LC_ALL=LANG=C, PYTHONDONTWRITEBYTECODE=1, PYTEST_DISABLE_PLUGIN_AUTOLOAD=1:

```text
<python> build/records-raw/ear_v2_e1r4/run.py
powershell -File build/records-raw/ear_v2_e1r4/finalize.ps1
```

The runner first checks the freeze, runs the intentional-failure probe and prescribed pytest command, then measures the frozen winners and writes raw input/response NPZ arrays. Do not rerun either one-time freeze driver. Raw files are in the ignored build tree and require separate retention. No git mutation, refit, new family, README change or protected source/archive inspection was performed.

Preregistration SHA-256 (hash_basis: lf): `d6f8757a2194b73f24a3f5cd7a3c66a5d5e098713f9f5dfb7b523917c3a65aec`. Full file hashes and scope checks are in ear_v2_e1r4_audit.json.
