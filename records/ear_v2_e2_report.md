# E2 passive B1 relay report

The joint synthetic-proxy fit satisfies H1, H3 and H4 simultaneously.
This is conditional compatibility of an underidentified passive model, not a
biological calibration or approval to run E5. E1 bank not fitted; E1 G3/G5 open.
H2 biological jitter is **unassessed**; deterministic model jitter is 0 ms.

## Evidence and freeze

Ledger 1.2 appends R3_009--R3_012, evidence class
VERIFIED_OPERATOR_FULLTEXT, with the supplied verbatim quotations and note
"read by the operator in the PMC full text, 2026-09-16". No independent
full-text verification is claimed. R3_003 remains null. All prior entries
and metadata except ledger_version are unchanged, checked against HEAD.
Source: Azevedo & Wilson 2017, doi:10.1016/j.neuron.2017.09.004,
https://pmc.ncbi.nlm.nih.gov/articles/PMC5771506/.

Preregistration SHA-256: `68d0540cd8429f4b06de513b93678f7138fc11f255dd24cc9a0fb73d1a0fd24c`.
Ledger 1.2 SHA-256: `1904fc036534e37f65142d3d7bbd7ae1bd0b48fe01707bdbbef70127c7d64e5e`.
Task A preceded the preregistration freeze; both hashes preceded model code.

## Gates

| Gate | Status | Evidence |
| --- | --- | --- |
| E2-G1 | passed | Prefix bit equality; regular and irregular chunk errors 0 |
| E2-G2 | passed | 10%-peak latency 1.960001440 ms; target 1.96 +/- 0.30 |
| E2-G3 | passed | WT block/control 0.800000; target 0.80 +/- 0.12 |
| E2-G4 | passed | shakB block/control 0.220000; target 0.22 +/- 0.08 |
| E2-G5 | passed (structural) | Maximum increments 0.00459515, 0.00230024, 0.00115079 mV; halving dt halves increments |
| E2-G6 | passed (descriptive) | 100--600 Hz forced phase locking; R-squared 1.0 at every frequency |

G5 aligned trajectory error <=3.38e-14 mV. The numerical continuity fixture
aligns delay to 1.66 ms on all three sample grids, isolating the continuous
membrane update from fractional-delay interpolation. Actual fit delay remains
1.659430584 ms. No threshold, reset, spike generator or noise exists.
No spikes is a model definition, not independent reproduction of 17 recordings.

## Joint fit and sensitivity

| Parameter | Selected | Retained grid range |
| --- | ---: | --- |
| g_gap | 0.986061794 | 0.05 to 20 |
| g_chem | 0.340021308 | 0.00952380952 to 11.25 |
| beta | 0.78 | 0.78 to 0.78 |
| d_ms | 1.65943058 | 0.581357082 to 1.95698304 |
| tau_m_ms | 4.28180972 | 0.5 to 10 |
| tau_syn_ms | 1.48340872 | 1 to 2 |

Conductances are nominal nS with fixed leak 1 nS; d and taus are ms.
R and C physiological constants: not in ledger. Nominal C equals tau_m pF
under the arbitrary leak gauge. JO unit step maps to nominal 1 mV.
Absolute mV amplitude is held out; only latency and matched peak ratios fit.
Chemical block retains 1-beta=0.22; electrical contribution to steady driving
current is g_gap/(g_gap+g_chem)=0.74358974. Electric feedback is retained.
Objective 2.09226e-25; optimizer success True.
All four conditions are evaluated; WT-only fit calls raise ValueError.

There are 675 grid candidates; 225 satisfy objective <= joint minimum + 1.
Ranges are grid sensitivity, **NOT confidence intervals**. They are marginal
extrema, not a Cartesian box of jointly acceptable values. beta=[0.78,0.78]
reflects coarse grid spacing and the loss cutoff, not exact biological
identification; nearby efficiencies were not densely profiled. Three targets
cannot identify six parameters. Wide conductance/tau/delay ranges expose this.
tau_syn is a free design parameter bounded 1--2 ms, not a ledger measurement.

H3 and H4 jointly passed: **yes**. The specific "E2 fit fails -> no E5" trigger
is not activated. E5 readiness remains unestablished because the E1 condition
and absolute amplitude calibration remain unresolved.

## Frequency diagnostic

| Hz | Amplitude (nominal mV) | Phase (rad, wrapped) | R-squared |
| --- | ---: | ---: | ---: |
| 100 | 0.35295013 | -2.12800600 | 1.000000 |
| 200 | 0.18681244 | 2.83552054 | 1.000000 |
| 300 | 0.12395816 | 1.70201264 | 1.000000 |
| 400 | 0.09252702 | 0.61499967 | 1.000000 |
| 500 | 0.07380482 | -0.45528924 | 1.000000 |
| 600 | 0.06139367 | -1.51787646 | 1.000000 |

This is the deterministic forced response to unit sine input, not a fit to
published tuning curves. No frequency result entered the optimization.
Release is max(V_B1,0) with fixed unit slope; no release scale was scanned.
E1 r_graded channel input is supported and tested with a synthetic array;
the E1 bank itself was neither imported nor executed.

## Acceptance and access

Prescribed CPython 3.12.14, numpy 2.4.2,
scipy 1.17.1, Windows; task-prescribed dependency chain,
locale C, bytecode and pytest plugin autoload disabled. No environment
workaround: these are acceptance-chain results, not substitute-environment
partial evidence. Pytest: **19 passed**, exit **0**. Intentional failure:
**1 failed**, exit **1**. Count lines and process exit codes were both read.
Raw logs and reproducible drivers are in build/records-raw/ear_v2_e2_*.

build/ did not exist at initial inspection; it now contains only authorized
raw artifacts. The runner installed import/file guards before scientific
dependencies and pytest: four prohibited import attempts raised ImportError;
three npz/parquet/feather probes raised ValueError before opening files.
No graph file was read; no prohibited package was loaded. Audit lists initial
content reads and runtime open attempts (including unsuccessful pyc probes).
No main-repository build access or protected source/archive inspection.
Only the explicitly supplied dependency site-packages was used from the
otherwise excluded location; this is the task's interpreter-chain exception.

HEAD remains 84bce06, branch lane-e2; no git add/commit/push. Scope and
git diff --check pass. Summary artifacts are below 2 MB; exact bytes and
UTF-8/BOM checks are recorded in ear_v2_e2_audit.json.

## Limitations and deviations

No fit target/tolerance changed after freeze. No scientific gate failed.
Stimulus amplitude, duration, blockade window and original latency estimator
are not in ledger for the fitted comparison. The unit step, long window and
10%-peak estimator are preregistered observation assumptions, not recovered
experimental metadata. Reported spreads are not silently labeled SD or SEM;
the requested numerical gate widths are used without that conversion.
The continuity fixture's common-grid delay alignment is disclosed above.
No graph, network simulation, noise, E1 biological fit or E5 integration was
attempted. The model omits active mechanisms from the source paper by design.
