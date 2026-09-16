# ear_v2 E1 report

PARTIAL: independent graded front end and synthetic validation delivered; biological JO calibration is blocked by missing subtype tuning entries. Scientific gates below retain not-passed outcomes.

## Selected conditional fixture results

| Gate | Target | Measured | Status |
| --- | --- | --- | --- |
| G1 | shared prefix bit-equal | True | passed |
| G2 | max difference <1e-9; equal phase | max error 0; signed 0; phase equal True | passed |
| G3 | 5 <= tau_up < tau_down <= 20 ms; R2 >=0.8 | up 7.750 ms (R2 0.596); down 22.355 ms (R2 0.627) | not passed |
| G4 | peak10/peak1: 36 ms >=0.9; 10 ms <0.9 | 36 ms: 0.98818; 10 ms: 0.81250 | passed |
| G5 | continuous sustained/peak < pulse sustained/peak | continuous 0.65094; pulsed 0.05743 | not passed |
| G6 | JO target peaks within 15%; A/B overlap below 500 Hz; no F | not in ledger; synthetic peaks 150,300,600,900 Hz; F absent | unassessed |
| G7 | compound 600 Hz/DC >0.05 | 0.03978 | not passed |

Passing synthetic diagnostics is not acceptance evidence for a calibrated JO/CAP model. G1/G2 are implementation properties. G3/G4/G5/G7 use a declared synthetic four-channel fixture; G6 cannot be assessed biologically.

Selected tau_sub=5 ms, tau_div=10 ms; objective=21.6916. Original 30/50 ms defaults remain unchanged. Channel omega/Q/G were not fitted: targets are not in ledger. Fixed fixture Q=G=1, centers 150/300/600/900 Hz.

Grid sensitivity (objective <= minimum+1): {'definition': 'objective <= minimum + 1; NOT a confidence interval', 'tau_sub_ms': [5, 50], 'tau_div_ms': [10, 10], 'candidate_count': 5}. These are not statistical confidence intervals; no biological spread or sample size is available for the extracted timescale constraints.

Recovery fit: tau=17.089 ms, R2=0.994, valid=True; engineering [20,40] ms tolerance satisfied=False. The pulse-ratio gate is not equivalent to this timescale test.

G3 fits compound graded envelopes rather than CAP traces. Separate up/down taus are not in ledger. Poor R2, out-of-range taus or incorrect ordering are retained as not passed. G5's duty-cycle-dependent ratio can fail despite visible within-tone adaptation. G7 averages channels with different phases, allowing cancellation of the second harmonic; per-channel harmonics are retained in metrics. No gate definition was relaxed after testing.

Initial 30/50 ms results: G3=False, G4=True, G5=False, G7=False. Complete initial and selected diagnostics are in ear_v2_e1_metrics.json.

## Tests and provenance

Pytest: {'passed': 27, 'skipped': 1, 'xfailed': 3}, exit 0; intentional harness probe: {'failed': 1}, exit 1. Expected hypothesis failures are xfailed and missing G6 is skipped, not counted as passed. The first development run exposed G7 as an ordinary assertion failure; it was changed to the preregistered visible xfail policy, without changing its threshold or averaging rule.

Preregistration SHA-256: `c053c84283c74facad59e0b546322b8d1224ad4c4284b511c6d3acdebb0f8b69`. Ledger SHA-256: `e972119894af09fef6bd32e0d0c000a3397156e68f5461b455cb6eac61b81e01`. Ledger source bytes matched on copy. Snapshot has 58 measurements and 9 datasets; no independent re-verification.

Environment: {'python': '3.12.14', 'python_implementation': 'CPython', 'os': 'Windows', 'architecture': 'AMD64', 'numpy': '2.4.2', 'scipy': '1.17.1', 'pytest': '9.1.1', 'interpreter_chain': 'user-prescribed Python 3.12 and dependency-only PYTHONPATH', 'environment_difference': None, 'locale': {'LC_ALL': 'C', 'LANG': 'C', 'PYTHONUTF8': '1'}, 'bytecode_disabled': True, 'pytest_plugin_autoload_disabled': True}. Locale is pinned for subprocess evidence. Test and fit ran through the prescribed interpreter/dependency chain; no environment workaround. No torch or network simulation was used.

Measured runner wall time 3.848 s; grid 2.149 s; freeze-to-finish 298.875 s. Initial inspection time was not separately instrumented. The 45-minute budget was not exhausted.

## Limitations and delivery boundaries

JO subtype centers, subtype identities, bandwidths and gains are not in ledger; no biological bank or channel fit is claimed. Numeric CAP pulse curves, separate directional tau estimates, absolute JO rates, rate ceilings/refractory intervals and inter-mode conversion are not in ledger. Graded-unit scale remains arbitrary and mode-specific. Null unresolved values remain null.

The specified ledger pulse example uses 16 ms pulses; the preregistered nonoverlapping diagnostic uses 4 ms Hann pulses, 300 Hz and 4 mm/s with 10/36 ms onset IPIs. These design choices are not reported physiological measurements. Continuous/pulse equal RMS is analytic, with realized finite-window RMS reported separately; there is no trial normalization.

No prohibited source tree or archive was opened or searched. Only authorized third-party imports used the dependency path. No git add/commit/push and no existing source edits. No model-based biological calibration substituted for absent evidence.

Reproduce from repository root: set the user-prescribed Python dependency environment, disable bytecode writes, then run `<prescribed-python> build/records-raw/ear_v2_e1_run.py`. The raw driver runs the intentional-failure probe, targeted pytest, fixed grid, and artifacts in that order. Raw traces and logs are intentionally under the ignored build directory; retain them separately for reproduction.

Summary artifact sizes and BOM/scope verification are recorded in ear_v2_e1_audit.json.
