# shiu_benchmarks_v1 preregistration

Frozen before quick or full simulation on 2026-09-16. No parameter fitting.

## Sources and populations

[Shiu et al., Nature 634, 210-219 (2024)](https://doi.org/10.1038/s41586-024-07763-9),
Methods (model calibration), Fig. 1d and Extended Data Fig. 1d (right sugar),
Fig. 3b-e (bitter and Ir94e), Fig. 4a (water), Fig. 5g (JO-CE versus JO-F).
Exact FlyWire IDs are frozen in `SHIU_IDS` in `flybench/experiment/benchmarks.py`,
from the authors' [figures.ipynb](https://github.com/philshiu/Drosophila_brain_model/blob/main/figures.ipynb).
The 21 right sugar GRNs and MN9 720575940660219265 match the supplied example.ipynb.
aBN1 is 720575940630907434. No inferred Gr64f gene selector is substituted.
Groups: sugar 21, water 18, bitter 21, Ir94e 18, JO-CE 70, JO-F 60, MN9 1, aBN1 1.
The v783 graph lacks sugar 720575940620900446, bitter 720575940618600651,
and JO-CE 720575940626307902. Use the present intersection, report these omissions,
and do not remap IDs. An empty required group aborts the run.
JO-A/B use the existing female dictionary selectors, including numbered subtypes.

## Design

FAFB v783, Shiu export, shiu2024-parquet sign rule version 1, all graph edges.
Existing fast_gpu CUDA float32 batch engine, Shiu kernel, unchanged Parameters
except dt=0.2 ms (upstream 0.1 ms). Rest/reset -52 mV, threshold -45 mV,
tau_m 20 ms, tau_s 5 ms, delay 1.8 ms, refractory 2.2 ms, w_syn 0.275 mV,
Poisson voltage scale 250, zero refractory for driven cells. No gain adjustment.
Grid Bernoulli Poisson sampling, existing Torch generator per seed.
Each condition starts from rest, 1000 ms; readouts use [200,1000) ms.
Full seeds 0-9; quick seeds 0-1 with the same duration and conditions.
Quick results are operational checks, excluded from full inference.
The full run starts only after successful quick record validation.

Conditions: baseline; sugar 10/50/100/200 Hz; water 100 Hz;
sugar 100 + bitter 100 Hz; sugar 100 + Ir94e 100 Hz;
JO-CE 100 Hz; JO-F 100 Hz; JO-A 180 Hz; JO-B 180 Hz;
JO-A and JO-B together, each 180 Hz.
Only specified populations receive external drive. Same seed labels are paired;
different target populations need not receive identical random draws.
No dose or population is revised after seeing quick results.

## Predictions and decision rules

For n seeds, SE is sample SD / sqrt(n). A directional contrast is supported
only when its mean is strictly greater than 2 SE; equality does not pass.
B1: MN9 sugar100 > 0 and each paired successive dose difference
(50-10, 100-50, 200-100) > 2 SE; sugar100 minus sugar100+bitter100 > 2 SE.
B1 passes only if all five criteria pass. Water100 > 0 and Ir94e suppression
are separately reported secondary contrasts, not replacements for B1.
B2: aBN1 JO-CE100 > 0 and paired JO-CE100 minus JO-F100 > 2 SE.
The positive-rate predictions also use mean > 2 SE for a conservative gate.
The overall robustness gate requires both B1 and B2. Failure does not identify
a biological absence or uniquely implicate graph, kernel, or input delivery.
No multiplicity correction: these are predefined engineering checks.

B3 is descriptive: every trial reports driven count, per-cell and group-mean
requested, sampled and delivered external-event Hz over all 1 s and the 800 ms
readout interval. Also report actual driven-cell total spike Hz, which can include
network-generated spikes. Delivered means a sampled event coinciding with a spike.
For each JO-A, JO-B, and combined input, rank directly postsynaptic types by summed
raw synapse counts from that input, excluding the driven cells and blank types;
ties use type string code-point order. Keep 20 types, use only their directly
connected cells as the second-order readout, and report which have any nonzero
rate across seeds. Report the untyped incoming synapse count separately.

## Interpretation limits

The paper used v630 and 30 trials; this uses v783, 10 seeds, float32 and a different
sampling backend, dt and readout interval. Three source IDs are missing.
Methods reports approximately 80% of maximal MN9 firing at sugar100; this is not
80% of the refractory ceiling. Report sugar100/sugar200 only as the measured dose
range ratio, not an estimate of a proven maximum. Exact numeric 100 Hz values
are not supplied by the paper text; do not invent digitized values.
Water activation and JO-CE selectivity are directional comparisons.
50 mM sucrose in Fig. 3d/e is a behavioural stimulus, not 50 Hz and not a calibrated
mapping to this model. Bitter and Ir94e are distinct populations.

Records preserve protocol and code hashes, source selector provenance, graph
fingerprint, seedwise rates, drive audits, a Result object and generated tables.
No behavioural or female-hearing pathway conclusion follows solely from this gate.
