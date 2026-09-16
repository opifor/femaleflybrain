# ear_v2 E1 round-3 report

The complete 180-point rectified_state grid was evaluated under the frozen round-3
amendment. Family candidates minimize the unchanged G3/recovery objective before
the cross-family gate-count and parameter-count selection. No G4/G5/G7 fit occurred.
G6 is conditional target placement; full biological tuning and anatomy remain unassessed.

## Family winners

| Family | G1 | G2 | G3 | G4 | G5 | G6 | G7 | Count | Objective |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| energy_feedback | passed | passed | not passed | passed | not passed | passed (conditional) | passed | 5/7 | 1.423241628 |
| asymmetric_energy | passed | passed | not passed | passed | not passed | passed (conditional) | passed | 5/7 | 160.093578754 |
| rectified_state | passed | passed | not passed | passed | not passed | passed (conditional) | passed | 5/7 | 0.149724784 |

Selected parameters: `{"family": "energy_feedback", "tau_sub_ms": 5, "tau_div_ms": 10, "strength": 1}`.
Config defaults remain the round-2 winner. The new sigma field defaults to 1.0
and is used only by rectified_state. Four parameters are fitted in rectified_state,
three in asymmetric_energy and two in energy_feedback; tau_sub=5 ms is fixed.
A tied gate count retains the simpler round-2 winner.

## G3 and recovery

| Family | Up tau ms | Up R2 | Down tau ms | Down R2 | Recovery tau ms | Recovery R2 |
| --- | --- | --- | --- | --- | --- | --- |
| energy_feedback | 7.482862 | 0.871708 | 32.504043 | 0.861807 | 21.465670 | 0.990662 |
| asymmetric_energy | 7.845393 | 0.906720 | 200.000000 | 0.904971 | 54.685175 | 0.989963 |
| rectified_state | 7.640765 | 0.829393 | 25.637145 | 0.813048 | 29.078486 | 0.980042 |

G3 requires valid fits, R2 >= 0.8, nonzero transient and 5 <= up < down <= 20 ms.
Fit validity and transient amplitudes are retained for every grid point in the JSON.
The asymmetric_energy down fit reaches the 200 ms bound and is invalid despite
its R2. Both other down fits exceed 20 ms. Recovery is an objective component
and separate diagnostic, not an additional gate.

## G5 and duty-cycle diagnostics

Each pair below is continuous / pulsed. T1 and T2 are **diagnostic, not a gate**.
G5 remains the full-window late mean / early peak, with continuous < pulsed.
T1 masks both pulsed windows to sampled Hann > 0; continuous is unchanged.
T2 uses the late full-window peak / early full-window peak for both conditions.

| Family | Official G5 C / P | T1 C / P (diagnostic, not a gate) | T2 C / P (diagnostic, not a gate) |
| --- | --- | --- | --- |
| energy_feedback | 0.629185 / 0.065149 | 0.629185 / 0.493368 | 0.734157 / 0.985657 |
| asymmetric_energy | 0.609786 / 0.061471 | 0.609786 / 0.465933 | 0.705831 / 0.911723 |
| rectified_state | 0.272466 / 0.058244 | 0.272466 / 0.503261 | 0.313652 / 0.933345 |

Nominal duty cycle is 4/36 = 11.111111%; sampled full-trial
Hann-positive occupancy is 11.047619%. The last 100 ms contains
174/2205 active samples; the first 50 ms contains 174.
Analytic RMS is 0.571952526; realized RMS is
0.571952526 / 0.574235779
(relative difference 0.399203%).
No realized-trial normalization was applied. T1 excludes inactive input samples but
also excludes filter ringing outside the Hann support; it is not a pure state estimate.
T2 removes averaging dilution while retaining peak sensitivity. Rectified-state
T1 is 0.272466 / 0.503261 whereas the official ratio is 0.272466 / 0.058244;
T2 continuous values are below pulsed values in all three families. This reversal
of numerical ordering demonstrates sensitivity to the observation statistic;
it supplies no replacement gate or isolated mechanistic conclusion.

## Remaining numerical gates

| Family | G1 prefix bit-equal | G2 graded / signed max error | G4 36 / 10 ms | G7 600/300 | 600/DC |
| --- | --- | --- | --- | --- | --- |
| energy_feedback | True | 0.0 / 0.0 | 0.985657 / 0.794593 | 2611.504122 | 0.078716 |
| asymmetric_energy | True | 0.0 / 0.0 | 0.911723 / 0.643601 | 2496.684049 | 0.075688 |
| rectified_state | True | 0.0 / 0.0 | 0.933345 / 0.458883 | 2473.582666 | 0.076750 |

G2 phase arrays are equal. G7 has both phase signs and exact signed-magnitude
reconstruction in all winners; denominator-floor flags are retained in the JSON.
G6 functional peaks: [100.0, 125.0, 225.0, 600.0] Hz; JO-A half-power design edges:
[100.0, 1200.0] Hz; provisional A/B overlap below 500 Hz:
61.0--273.0 Hz; F absent.
These use exactly the round-2 channels and ledger targets.

## Parameters and sensitivity

- energy_feedback: `{"family": "energy_feedback", "tau_sub_ms": 5, "tau_div_ms": 10, "strength": 1}`.
- asymmetric_energy: `{"family": "asymmetric_energy", "tau_sub_ms": 5, "tau_up_ms": 5, "tau_down_ms": 20, "strength": 1}`.
- rectified_state: `{"family": "rectified_state", "tau_sub_ms": 5, "tau_up_ms": 10, "tau_down_ms": 10, "sigma": 0.3, "strength": 3}`.

Rectified-state sensitivity: `{"definition": "objective <= minimum + 1; not a confidence interval", "candidate_count": 2, "ranges": {"tau_up_ms": [10, 10], "tau_down_ms": [10, 10], "sigma": [0.1, 0.3], "strength": [1, 3]}}`.
Round-2 sensitivities are unchanged: energy_feedback tau_div [10,10], strength [1,1];
asymmetric_energy tau_up [5,5], tau_down [20,20], strength [1,1]. Each contains one point.
All use objective <= minimum + 1; not a confidence interval. A boundary minimum
does not establish an optimum outside this grid. No biological sample size or
population uncertainty is inferred. Per-candidate gate counts are in the fit JSON.
Across the new grid, 72 candidates pass five gates and 108 pass four; none pass
G3 or G5. The two sensitivity points share tau_up=tau_down=10 ms and
(sigma,strength)=(0.1,1) or (0.3,3). Their common sigma/strength ratio
makes their normalized temporal shapes scale-equivalent; this does not identify
sigma and strength independently from kinetics. No approximate tie tolerance
was introduced; minimum objective uses the computed floating-point values.

## Comparison with round 2

Both round-2 winners were rerun. Their complete metric dictionaries and objectives
match the frozen round-2 fit JSON exactly. This round adds one family and two G5
diagnostics; it does not change the stimuli, targets, objective or G1--G7 definitions.
The rectified_state winner passes 5 gates versus 5 for energy_feedback.
Its G3 tau differences versus energy_feedback are 0.157903 ms up and
-6.866898 ms down.
All other numerical comparisons are exposed above; no diagnostic is converted to acceptance.

## Verification, provenance and deviations

Pytest: {'passed': 52, 'skipped': 1, 'xfailed': 3}, exit 0.
Intentional-failure harness: {'command': ['<python>', '-m', 'pytest', '-p', 'no:cacheprovider', '-q', 'build/records-raw/ear_v2_e1r3_harness_probe.py'], 'exit_code': 1, 'counts': {'failed': 1}}.
The count lines and exit codes were inspected. The historical scientific xfails
and historical G6 skip remain visible. Existing tests are unchanged; new tests
cover recurrence, both state-update branches, both input modes, bit-equal causal
prefixes, 10 x 5 ms chunks, empty/single/irregular chunks, reset divergence, sigma
validation and diagnostic oracles. Each old family was also compared bit-for-bit
against its HEAD implementation in both input modes across irregular chunks.
All tested graded, signed and phase arrays were identical.

Environment: `{"python": "3.12.14", "numpy": "2.4.2", "scipy": "1.17.1", "pytest": "9.1.1", "platform": "Windows", "machine": "AMD64", "locale": "C", "bytecode": false, "plugin_autoload": false, "prescribed_chain": true}`.
Fit runner wall time: 120.125 s. All 180 grid points completed within the 45-minute budget.
The prescribed interpreter and dependency-only PYTHONPATH were used directly;
no environment workaround was used. Evidence is from the requested execution chain.
Reproduce from repo root after setting that environment and LC_ALL=LANG=C,
PYTHONDONTWRITEBYTECODE=1 and PYTEST_DISABLE_PLUGIN_AUTOLOAD=1:
`<python> build/records-raw/ear_v2_e1r3_run.py`, then
`<python> build/records-raw/ear_v2_e1r3_finalize.py`.
The run script invokes `<python> -m pytest -p no:cacheprovider -q tests/test_ear2.py`.
The freeze script is a one-time construction step; do not rerun it.

Deviations and input-state differences:
- Round-2 drivers were absent. The reconstructed round-3 drivers are under the
  authorized build/records-raw directory, not at repo root; execution is from root.
- The supplied checkout already has ledger v1.2. Every v1.1 measurement and the
  complete fit policy match the local v1.1 git blob. No later entries were used.
  Full-ledger v1.1 byte equality is false; current ledger bytes remain unchanged.
- Git autocrlf made the initial preregistration CRLF. Its local byte prefix is
  preserved exactly; historical LF round-1/2 hashes are separately verified.
  The initial strict historical-byte check rejected this difference before any
  preregistration write or model change. No preregistered text was revised.
- An initial parent-directory AGENTS.md filename search exceeded the intended
  discovery scope; it returned unrelated instruction-file names only. No returned
  file was opened, and no protected source or archive contents were inspected.

Clean room: no protected source or archive was opened; the authorized dependency
path was used only for imports. The main working tree was not opened or modified.
Git operations were read-only; no add, commit or push. No network simulation,
graph, world or dictionary processing. No ledger edits. fit_allowed=false is preserved.
New delivery text is English UTF-8 without BOM. Raw artifacts need separate retention.

## Hashes

- round1_sha256: `c053c84283c74facad59e0b546322b8d1224ad4c4284b511c6d3acdebb0f8b69`.
- round2_sha256: `f4b29a780558f148c9cf3a35390dc0d247f3ddc1850974858d516f50d464b064`.
- historical_round12_sha256: `3d477af62ddc609153897e45890364487172e1f3552e3d0b1d227b090bc13681`.
- round12_sha256: `60f55ad3f3c4f5d0da40251728e5bb4eac5826160ee503ff69324d5d50f1e1b3`.
- round3_sha256: `e611cd74154a1c936cb9b06c73efe22fe232a2744b30a9c88917219e47b6dde8`.
- combined_sha256: `f525f2abbcc53551eb2243d9f53dd2975e4e7b2375752c7b1d4a19102254d927`.
- ledger_v11_sha256: `8bd44ce467b72c0aa792f2bb2dc2d1fa9340f266141fe96ac75950811eae750f`.
- ledger_current_sha256: `b43ae2c8b8b2db0edb019e13fde696cbe65eb77512fa39f761718905ad08e6ca`.

File hashes, git status, scope checks, byte-prefix preservation and sizes are in
ear_v2_e1r3_audit.json. The audit excludes its own hash to avoid self-reference.
