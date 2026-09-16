# ear_v2 E1 round-2 report

The preregistered two-family experiment is complete. G3 and G5 remain not passed.
G6 passes conditional target placement only; anatomical mapping and full biological
tuning validation remain unassessed. No calibrated JO/CAP or spike-rate acceptance
is claimed. Failed scientific gates are not converted into test passes.

## Family winners

| Family | G1 | G2 | G3 | G4 | G5 | G6 | G7 | Objective | Fitted parameters |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| energy_feedback | passed | passed | not passed | passed | not passed | passed (conditional) | passed | 1.423242 | 2 |
| asymmetric_energy | passed | passed | not passed | passed | not passed | passed (conditional) | passed | 160.093579 | 3 |

Each family winner minimizes the original kinetics objective within its frozen grid.
Both winners pass five gates. The two-parameter energy_feedback family wins the
preregistered complexity tie-break over three-parameter asymmetric_energy.
All 21 candidates, their numerical diagnostics and gate counts are in the fit JSON.
No grid refinement, threshold change after evaluation, or downstream fit occurred.

## Selected conditional model

Parameters: `{"family": "energy_feedback", "tau_sub_ms": 5, "tau_div_ms": 10, "strength": 1}`. Config defaults match this winner.
The fixed 5 ms subtractive time is a design choice. Only tau_div and strength
were fitted for this family; unused asymmetric constants are not fitted values.
Feedback is a spike-independent energy proxy, not an identified calcium mechanism.
The legacy family remains available with explicit round-1 parameters.

G1 prefix bit-equal: True; G2 graded/signed maximum errors: 0.0/0.0; phase equal: True.
G3: up 7.482862 ms, R2=0.871708; down 32.504043 ms, R2=0.861807.
Fits are valid and up<down, but down exceeds 20 ms. The gate remains not passed.
G4 peak10/peak1: 36 ms=0.985657, 10 ms=0.794593.
Separate recovery: tau=21.465670 ms, R2=0.990662; [20,40] ms engineering tolerance passed=True.
G5 sustained/peak: continuous=0.629185, pulsed=0.065149; still reversed.
Finite-window RMS: continuous=0.571952526, pulsed=0.574235779; only analytic energy was matched.
G7 600/300 ratio (or numerical-floor lower bound)=2611.5; 300 Hz below floor=False.
600 Hz/DC=0.078716; both signs and exact magnitude reconstruction passed.
A large 600/300 ratio can result from full-wave suppression of 300 Hz; it is not
equivalent to the original 600/DC gate or a physiological spike criterion.

## Grid sensitivity

- energy_feedback: winner `{"family": "energy_feedback", "tau_sub_ms": 5, "tau_div_ms": 10, "strength": 1}`; sensitivity `{"definition": "objective <= family minimum + 1; not a confidence interval", "candidate_count": 1, "ranges": {"tau_div_ms": [10, 10], "strength": [1, 1]}}`.
- asymmetric_energy: winner `{"family": "asymmetric_energy", "tau_sub_ms": 5, "tau_up_ms": 5, "tau_down_ms": 20, "strength": 1}`; sensitivity `{"definition": "objective <= family minimum + 1; not a confidence interval", "candidate_count": 1, "ranges": {"tau_up_ms": [5, 5], "tau_down_ms": [20, 20], "strength": [1, 1]}}`.

These ranges are grid sensitivity, not confidence intervals. Boundary minima do
not identify an optimum outside the tested grid. No biological replicates or
uncertainty were invented; separate directional physiological constants are absent.

## Ledger and G6

Ledger v1.1 adds 16 records (R6_001--R6_016) to the preserved 58 entries.
All additions are REPORTED and carry the required secondary-reading provenance.
The original has schema_version=1.0 and no ledger_version field; schema is
unchanged and ledger_version=1.1 was added, as declared before fitting.
R6 identifies additions; their biological rung is 3, not reserved rung 6.
Primary sources were not independently inspected. Two earlier pooled statements
(R6_004, R6_013) lack a uniquely assigned DOI in the supplied section and retain
null DOI. Missing modality/figure/n/preparation details remain unextracted.
DOIs with attributed additions: 10.3389/fncir.2017.00046;
10.3389/fphys.2014.00179; 10.1016/j.cub.2018.02.074; 10.7554/eLife.59976.
Adaptation uses the preserved 10.1038/s41467-017-02453-9 entries R3_006/007.

Functional peaks are 100/125/225/600 Hz, exactly on the 1 Hz evaluation grid.
JO-A design half-power edges: [100.0, 1200.0] Hz.
Conditional A/B overlap: 61.0--273.0 Hz at >=0.5 own-peak response; F absent.
The 100/125 components are only provisionally B-associated. Functional classes
span anatomical zones. The broad A reported response extent is not a measured
half-power bandwidth: using it as such is an explicit engineering convention.
G6 therefore exits unassessed only for the requested conditional placement test.
Full biological transfer shapes, gain and anatomical correspondence remain unassessed.
The ledger retains 8 Hz, D and F findings; none is forced into this audio bank.

## Comparison with round 1

Round 1 selected tau_sub/tau_div=5/10 ms on a synthetic 150/300/600/900 Hz bank.
Round 2 uses the reported-target conditional bank and an energy feedback state.
G3 R2 improves from 0.596/0.627 to 0.872/0.862 but still misses the time band.
G4 remains passed; recovery now satisfies its separate engineering band.
G5 remains not passed (round 1 ratios 0.65094/0.05743).
G6 conditional placement is newly assessable. G7 now uses the user-requested
600/300>0.5 definition, replacing round-1 600/DC>0.05 in the frozen amendment.
Consequently G7 pass status is not a controlled same-gate comparison.
Both filter bank and adaptation changed; no isolated causal effect is claimed.

## Verification and reproducibility

Final targeted pytest: {'passed': 40, 'skipped': 1, 'xfailed': 3}, exit 0.
Intentional-failure harness: {'exit_code': 1, 'counts': {'failed': 1}}; failed-count and exit both inspected.
The historical round-1 scientific misses remain three visible xfails and its
unidentified-bank G6 remains one skip. All previous passing tests still pass.
New tests cover both families: causal prefixes, regular/irregular/empty chunks,
reset behavior, independent sample recurrence, invalid configuration, signed
reconstruction, and positive/negative synthetic gate oracles. Default regression
checks the selected parameters and actual default execution.
Only tests/test_ear2.py was run; a full suite was not run because other tests
exercise network simulation outside this task. No network simulation was run.
Evidence used the prescribed Python/dependency chain, locale C, disabled bytecode
and disabled plugin autoload. No environment workaround; no environment difference.
Measured fit runner wall time: 11.718 seconds.
For reproduction, set the prescribed dependency environment and run the raw
ear_v2_e1r2_run.py driver from the repository root, then ear_v2_e1r2_finalize.py.
The freeze and ledger scripts are one-time construction steps, not rerun steps.
No prohibited source tree or archive was opened; dependency imports only used
the authorized external dependency path. No git add, commit, push or other git write.
Delivery files are English UTF-8 without BOM. Raw artifacts require separate retention.

## Hashes

- Round-1 preregistration bytes: `c053c84283c74facad59e0b546322b8d1224ad4c4284b511c6d3acdebb0f8b69`.
- Round-2 appendix bytes: `f4b29a780558f148c9cf3a35390dc0d247f3ddc1850974858d516f50d464b064`.
- Combined preregistration: `3d477af62ddc609153897e45890364487172e1f3552e3d0b1d227b090bc13681`.
- Ledger v1.0: `e972119894af09fef6bd32e0d0c000a3397156e68f5461b455cb6eac61b81e01`.
- Ledger v1.1: `8bd44ce467b72c0aa792f2bb2dc2d1fa9340f266141fe96ac75950811eae750f`.

Byte-prefix hashes, existing-ledger equality, BOM, summary sizes, code hashes
and git scope are checked in ear_v2_e1r2_audit.json. The 45-minute budget was
not exhausted; no required fit or test work remains. Scientific misses remain
limitations of the preregistered families, not deferred successful acceptance.
