# shiu_benchmarks_v1 report

Source: [Shiu et al. 2024](https://doi.org/10.1038/s41586-024-07763-9).

Rates are Hz, mean +/- SE across ten seeds, measured after 200 ms.
Paper comparisons are qualitative unless explicitly numeric; no figure digitization was performed.

| Condition | MN9 | aBN1 | Shiu comparison |
| --- | ---: | ---: | --- |
| baseline | 0.000 +/- 0.000 | 0.000 +/- 0.000 | 0 Hz baseline (Methods) |
| sugar10 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | dose response (Fig. 1d/Extended Data Fig. 1d) |
| sugar50 | 14.500 +/- 1.627 | 0.000 +/- 0.000 | dose response (Fig. 1d/Extended Data Fig. 1d) |
| sugar100 | 63.375 +/- 1.817 | 0.000 +/- 0.000 | ~80% of maximal MN9 (Methods) |
| sugar200 | 93.875 +/- 2.278 | 0.000 +/- 0.000 | dose response (Fig. 1d/Extended Data Fig. 1d) |
| water100 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | MN9 activation (Fig. 4a) |
| sugar100_bitter100 | 4.500 +/- 0.972 | 0.000 +/- 0.000 | suppression (Fig. 3b) |
| sugar100_Ir94e100 | 8.750 +/- 1.222 | 0.000 +/- 0.000 | weaker suppression (Fig. 3c) |
| JO-CE100 | 0.000 +/- 0.000 | 26.875 +/- 0.678 | robust aBN1 (Fig. 5g) |
| JO-F100 | 0.000 +/- 0.000 | 0.625 +/- 0.384 | little/no aBN1 (Fig. 5g) |
| JO-A180 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | descriptive audit |
| JO-B180 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | descriptive audit |
| JO-AB180 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | descriptive audit |

Sugar100/sugar200 measured-range ratio: 0.6750998668442078; not a proven maximum.

## Populations

| Group | Present | Missing source IDs |
| --- | ---: | --- |
| sugar | 20 | [720575940620900446] |
| MN9 | 1 | [] |
| bitter | 20 | [720575940618600651] |
| Ir94e | 18 | [] |
| water | 18 | [] |
| JO-CE | 69 | [720575940626307902] |
| JO-F | 60 | [] |
| aBN1 | 1 | [] |
| JO-A | 94 | [] |
| JO-B | 296 | [] |

## Preregistered decisions

| Check | Paired contrast, Hz | Supported (>2 SE) |
| --- | ---: | --- |
| B1: sugar_positive | 63.375 +/- 1.817 | True |
| B1: dose_50_minus_10 | 14.500 +/- 1.627 | True |
| B1: dose_100_minus_50 | 48.875 +/- 2.382 | True |
| B1: dose_200_minus_100 | 30.500 +/- 2.556 | True |
| B1: bitter_suppression | 58.875 +/- 2.224 | True |
| B2: CE_positive | 26.875 +/- 0.678 | True |
| B2: CE_minus_F | 26.250 +/- 0.745 | True |
| secondary: water_positive | 0.000 +/- 0.000 | False |
| secondary: Ir94e_suppression | 54.625 +/- 2.493 | True |

Gate: True; individual gates: {'B1': True, 'B2': True}.

## B3 drive audit

Full-second rates, averaged across driven cells then seeds. Per-cell and per-trial records also include the measurement interval.

| Condition | Group (cells) | Requested | Sampled | Delivered | Total spikes |
| --- | --- | ---: | ---: | ---: | ---: |
| sugar10 | sugar (20) | 10.000 +/- 0.000 | 10.160 +/- 0.262 | 10.160 +/- 0.262 | 10.160 +/- 0.262 |
| sugar50 | sugar (20) | 50.000 +/- 0.000 | 50.775 +/- 0.509 | 50.775 +/- 0.509 | 50.775 +/- 0.509 |
| sugar100 | sugar (20) | 100.000 +/- 0.000 | 100.860 +/- 0.866 | 100.860 +/- 0.866 | 100.875 +/- 0.865 |
| sugar200 | sugar (20) | 200.000 +/- 0.000 | 201.215 +/- 0.928 | 201.215 +/- 0.928 | 201.290 +/- 0.933 |
| water100 | water (18) | 100.000 +/- 0.000 | 100.894 +/- 1.019 | 100.894 +/- 1.019 | 100.911 +/- 1.017 |
| sugar100_bitter100 | sugar (20) | 100.000 +/- 0.000 | 100.660 +/- 0.942 | 100.660 +/- 0.942 | 100.675 +/- 0.948 |
| sugar100_bitter100 | bitter (20) | 100.000 +/- 0.000 | 100.170 +/- 0.821 | 100.170 +/- 0.821 | 100.170 +/- 0.821 |
| sugar100_Ir94e100 | sugar (20) | 100.000 +/- 0.000 | 100.420 +/- 0.517 | 100.420 +/- 0.517 | 100.440 +/- 0.518 |
| sugar100_Ir94e100 | Ir94e (18) | 100.000 +/- 0.000 | 100.122 +/- 0.894 | 100.122 +/- 0.894 | 101.639 +/- 0.898 |
| JO-CE100 | JO-CE (69) | 100.000 +/- 0.000 | 99.926 +/- 0.403 | 99.926 +/- 0.403 | 99.926 +/- 0.403 |
| JO-F100 | JO-F (60) | 100.000 +/- 0.000 | 100.067 +/- 0.426 | 100.067 +/- 0.426 | 100.067 +/- 0.426 |
| JO-A180 | JO-A (94) | 180.000 +/- 0.000 | 179.855 +/- 0.493 | 179.855 +/- 0.493 | 179.855 +/- 0.493 |
| JO-B180 | JO-B (296) | 180.000 +/- 0.000 | 180.203 +/- 0.254 | 180.203 +/- 0.254 | 180.203 +/- 0.254 |
| JO-AB180 | JO-A (94) | 180.000 +/- 0.000 | 179.849 +/- 0.624 | 179.849 +/- 0.624 | 179.849 +/- 0.624 |
| JO-AB180 | JO-B (296) | 180.000 +/- 0.000 | 180.284 +/- 0.207 | 180.284 +/- 0.207 | 180.284 +/- 0.207 |

## JO second-order targets

| Input | Type | Raw synapses | Cells | Hz | Any active seed |
| --- | --- | ---: | ---: | ---: | --- |
| JO-A | DNg24 | 215 | 2 | 39.250 +/- 0.320 | True |
| JO-A | CB1231 | 189 | 16 | 1.430 +/- 0.033 | True |
| JO-A | CB1817a | 182 | 2 | 16.812 +/- 0.378 | True |
| JO-A | DNg29 | 181 | 2 | 40.938 +/- 0.569 | True |
| JO-A | CB0104 | 146 | 2 | 50.250 +/- 0.408 | True |
| JO-A | CB3882 | 139 | 1 | 68.750 +/- 0.697 | True |
| JO-A | CB0956 | 130 | 7 | 1.054 +/- 0.077 | True |
| JO-A | CB0307 | 128 | 2 | 23.625 +/- 0.182 | True |
| JO-A | CB1538 | 127 | 6 | 2.729 +/- 0.085 | True |
| JO-A | CB3911 | 124 | 1 | 59.250 +/- 0.917 | True |
| JO-A | AN_multi_33 | 110 | 2 | 30.125 +/- 0.306 | True |
| JO-A | CB0591 | 103 | 3 | 9.958 +/- 0.191 | True |
| JO-A | DNge130 | 98 | 2 | 28.000 +/- 0.224 | True |
| JO-A | CB0261 | 96 | 2 | 0.625 +/- 0.186 | True |
| JO-A | CB3877 | 95 | 3 | 12.375 +/- 0.412 | True |
| JO-A | DNp01 | 95 | 2 | 29.625 +/- 0.267 | True |
| JO-A | DNp02 | 93 | 2 | 23.625 +/- 0.320 | True |
| JO-A | CB0443 | 91 | 2 | 21.625 +/- 0.191 | True |
| JO-A | CB1817b | 84 | 2 | 0.062 +/- 0.062 | True |
| JO-A | CB3876 | 80 | 1 | 0.375 +/- 0.267 | True |
| JO-B | CB2556 | 639 | 7 | 30.232 +/- 0.198 | True |
| JO-B | CB1076 | 429 | 8 | 13.484 +/- 0.151 | True |
| JO-B | CB1038 | 338 | 9 | 18.597 +/- 0.081 | True |
| JO-B | CB2789 | 302 | 4 | 34.531 +/- 0.243 | True |
| JO-B | SAD052 | 258 | 4 | 12.281 +/- 0.094 | True |
| JO-B | DNg29 | 245 | 2 | 64.188 +/- 0.552 | True |
| JO-B | SAD053 | 244 | 2 | 53.312 +/- 0.639 | True |
| JO-B | CB1427 | 213 | 8 | 2.562 +/- 0.220 | True |
| JO-B | CB1078 | 210 | 14 | 0.107 +/- 0.029 | True |
| JO-B | CB2034 | 209 | 6 | 20.083 +/- 0.202 | True |
| JO-B | CB1231 | 197 | 15 | 3.650 +/- 0.131 | True |
| JO-B | CB1542 | 195 | 6 | 0.125 +/- 0.034 | True |
| JO-B | WED025 | 188 | 6 | 20.146 +/- 0.213 | True |
| JO-B | DNge145 | 173 | 4 | 16.938 +/- 0.357 | True |
| JO-B | CB2162 | 171 | 4 | 30.500 +/- 0.299 | True |
| JO-B | CB2664 | 169 | 7 | 1.393 +/- 0.095 | True |
| JO-B | CB3876 | 166 | 1 | 81.125 +/- 0.902 | True |
| JO-B | CB1138 | 164 | 8 | 13.047 +/- 0.132 | True |
| JO-B | CB0033 | 163 | 2 | 79.625 +/- 0.408 | True |
| JO-B | CB0758 | 158 | 4 | 24.031 +/- 0.164 | True |
| JO-AB | CB2556 | 646 | 7 | 29.196 +/- 0.313 | True |
| JO-AB | CB1076 | 429 | 8 | 12.453 +/- 0.163 | True |
| JO-AB | DNg29 | 426 | 2 | 81.500 +/- 0.680 | True |
| JO-AB | CB1231 | 386 | 16 | 7.602 +/- 0.144 | True |
| JO-AB | CB1038 | 338 | 9 | 18.444 +/- 0.164 | True |
| JO-AB | CB2789 | 306 | 4 | 34.812 +/- 0.247 | True |
| JO-AB | DNg24 | 294 | 2 | 27.812 +/- 1.103 | True |
| JO-AB | SAD052 | 258 | 4 | 13.031 +/- 0.132 | True |
| JO-AB | CB0956 | 246 | 7 | 10.571 +/- 0.213 | True |
| JO-AB | CB3876 | 246 | 1 | 73.500 +/- 1.970 | True |
| JO-AB | SAD053 | 244 | 2 | 47.000 +/- 0.557 | True |
| JO-AB | CB2664 | 220 | 7 | 2.054 +/- 0.097 | True |
| JO-AB | CB3911 | 214 | 1 | 94.625 +/- 0.792 | True |
| JO-AB | CB1427 | 213 | 8 | 2.375 +/- 0.152 | True |
| JO-AB | CB2034 | 212 | 6 | 19.063 +/- 0.227 | True |
| JO-AB | CB1078 | 211 | 14 | 0.143 +/- 0.024 | True |
| JO-AB | CB1538 | 208 | 6 | 12.292 +/- 0.317 | True |
| JO-AB | CB1542 | 195 | 6 | 0.062 +/- 0.062 | True |
| JO-AB | WED025 | 188 | 6 | 20.167 +/- 0.272 | True |
| JO-AB | CB0478 | 186 | 2 | 46.750 +/- 0.491 | True |

Untyped synapse totals: JO-A=11, JO-B=26, JO-AB=37.

## Limits and provenance

v783 replaces paper v630; three source IDs are absent. dt=0.2 rather than 0.1 ms; ten rather than thirty repeats; float32 Torch GPU sampling; first 200 ms excluded. No parameters were tuned.
Bitter and Ir94e are distinct. The 50 mM experiment is behavioural and is not reproduced by a calibrated concentration-to-rate conversion.
Passing controls would support this graph/kernel/input combination for these routes, but would not prove the biological absence of JO-A/B to vpoEN transfer. A failed control also does not identify a unique cause.
Runtime: 80.46 s. Graph SHA256: `35e5c3b4cca86b27392a144a4d6bcb37de2f3f97f29d71f5c0a5c20b1cd593b8`.
Protocol SHA256: `e95446d667dbcc711edf2f6d7aafe9373f362729c9ab6346dd14f1718d274d1d`.
Clean room: no sibling project or archive source was read. Only the explicitly supplied dependency directory was used for imports. No git staging, commit or push.

## Frozen preregistration

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

