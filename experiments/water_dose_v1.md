# water_dose_v1 preregistration

Frozen before graph inspection or simulation on 2026-09-16. No calibration,
parameter fitting, gain changes, or post-result population replacement.

## Inputs and design

Use build/graph_female.npz, FAFB v783, shiu connectivity and
shiu2024-parquet sign rule version 1. Import water (18 source IDs) and sugar
(21 source IDs) from SHIU_IDS in flybench/experiment/benchmarks.py.
Audit present and missing IDs and L/R/M/unknown side counts. The existing
benchmark already reports sugar 720575940620900446 missing (20/21): preserve
the same present intersection, explicitly record this deviation from the
requested 21/21 expectation, and never invent a replacement. Empty input aborts.

MN9_ref is 720575940660219265. MN9_other is every graph cell with exactly the
same nonempty type label and the opposite L/R side. Report IDs and side labels;
do not reverse historical FAFB labels. If reference side/type is unknown or no
opposite match exists, report other as absent, never zero. Multiple matches are
averaged per seed, with individual cell rates retained in raw records.

Use the identical fast_gpu CUDA float32 Shiu kernel and Parameters(dt=0.2)
as shiu_benchmarks_v1: rest/reset -52, threshold -45 mV, tau_m 20, tau_s 5,
delay 1.8, refractory 2.2 ms, w_syn 0.275, drive_scale 250; zero refractory
in driven cells and one Torch generator per seed. Each condition starts at rest,
runs 1000 ms, and reads [200,1000) ms. No engine changes.
Conditions in order: baseline; water100, water160, water200, water260;
sugar100, sugar200. Full seeds 0-9; quick seeds 0-1, otherwise identical.
Execution order: synthetic pytest and intentional-failure harness probe,
quick, full, report. Quick validates operation and frozen hashes, not hypotheses.

## Decisions

Report mean +/- sample SD/sqrt(n). Contrasts pair matching seeds. Strict mean
greater than 2 SE is supported; equality fails. No multiplicity correction.
W1: water160 minus baseline for MN9_ref exceeds 2 SE.
W2: descriptive strict mean order water260 > water160 > water100, separately
for ref and other; absent other is not evaluable. Water200 remains reported.
W3: compute other minus ref for each water dose; any supported positive
contrast yields "laterality mismatch SUSPECTED". If both readouts are exactly
zero at every water dose and every seed, "pathway silent at all tested doses".
Otherwise "no laterality signal" (lack of signal does not establish equivalence).
Absent other yields "not evaluable: MN9_other absent", never a silence claim.
W4: full sugar100 ref mean lies within inclusive 63.4 * [0.85,1.15] Hz.
Outside this band is FAIL-CLOSED, and biological interpretation is withheld.
Matching graph, parameter and existing engine hashes are checked against the
benchmark record as additional provenance evidence; W4 alone is not identity proof.

## Reporting and limits

Record protocol and graph SHA256, engine/code hashes, ID counts, side counts,
environment versions, wall time and seedwise rates. Raw per-cell drive audits
include requested, sampled, delivered and total spike Hz for full 1 s and the
800 ms readout. Summary table uses full-second delivered external GRN drive;
baseline drive is zero. Summary records total less than 10 MB; raw data under
build/records-raw. UTF-8 without BOM; no machine-specific paths in artifacts.

Supplied paper context: Shiu et al. (2024), doi:10.1038/s41586-024-07763-9,
water sweep 20-260 Hz, necessity dose 160 Hz, separate inputs selected to produce
40 Hz MN9 for sugar/water comparison. Qualitative report comparison only:
"paper: water activates MN9 at 160 Hz necessity dose; exact water100 value not published".
The paper normally reads contralateral MN9 and warns of historical FAFB
left/right reversal. The upstream sugar pairing does not validate water pairing.
Graph-side labels are descriptive and do not independently settle anatomical side.
No biological absence conclusion follows from an unresponsive model readout.
Budget 25 minutes; shared GPU may affect wall time. No staging, commit or push.
