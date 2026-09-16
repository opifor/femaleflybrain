# Direction probe v1: preregistration

Diagnostic substitution only; female FAFB v783, alone, no world, ear, song,
external drive, parameter tuning, or gain changes. This precedes E4 freezing.
The graph prediction is inhibitory B1-to-vpoEN transfer. E5 will use E2 relay
flux; this experiment maps direction under fixed synthetic flux only.

Shiu, fast_gpu CUDA float32 batch, unchanged Parameters except dt=0.2 ms.
Twenty 50 ms windows; first four warmup, last sixteen measured. Seeds 0--9,
identical ordered trial columns in all arms. Quick: seed 100, uncapped gamma
0.01 and 3, both relay arms plus baseline; quick is excluded from inference.
K0 has no hook and no drive. K1 sources are dictionary AMMC-B1-candidate (39).
K2 sources are AMMC-B1-candidate-graph (23). Use build/dictionary_fafb.json
if present and resolvable; otherwise the female dictionary API, hashing its
definitions, selector and API plus the resolved identities. No other list.

Gamma: 0.01, 0.03, 0.1, 0.3, 1, 3 spike-equivalents/ms.
Ceilings in order: uncapped, 1/2.2, 1/5 ms^-1. Flux=min(gamma, ceiling),
zero for absolute steps 0--999, constant for steps 1000--4999. No multiplicative
ceiling factor. Execute ceiling-major, gamma ascending, K1 then K2. Identical
effective fluxes within an arm reuse one simulation and retain all 18 labels.
There are eight distinct positive fluxes per arm. Baseline runs first.
Budget: 2400 seconds for full simulation; stop at a window boundary if needed,
retain raw partial data, exclude incomplete conditions, mark PARTIAL. Do not
start a condition when the measured prior condition duration exceeds remaining
budget. Uncapped grid therefore has priority.

Readouts: vpoEN (4), vpoDN/DNp37, pC1 union a--e and each subtype,
vpoDN-GABA-input/AVLP008; per-cell and population rates, network Hz/neuron,
fraction of measured windows above 30 network Hz/neuron, window active-cell
fraction and overall measured active-cell fraction. Record source spike counts.
Each seed first averages the sixteen measured windows. Paired arm-minus-K0
differences then give the ten-seed mean and sample SE (ddof=1); cell guards
use each cell's paired ten-seed mean. Quick SE is null, never inferred.

D1 vpoEN and D2 vpoDN: suppression if mean < -1 Hz and no cell delta > +3 Hz;
equivalence-zero if abs(mean)<=1 Hz and no cell abs(delta)>3 Hz;
unexplained increase if mean>+1 Hz. Remaining guard-failure cases are
unclassified (cell heterogeneity), not forced into one of the three classes.
Boundaries are inclusive only for equivalence and guards. SE is descriptive,
never a decision threshold. With no stochastic drive all seeded runs may be
identical; zero SE does not establish biological certainty. A silent baseline
has no negative firing-rate range: absence of suppression then cannot refute
an inhibitory graph sign. Do not add tonic drive to repair that floor.

D3: retain cumulative dropped_flux per target and seed. Denominator is
count-weighted absolute scheduled mass that has actually arrived by the final
step, excluding the final delay-pending bins. Ratio undefined for zero mass.
Any target/seed loss >5% bars saturation interpretation for that target;
report "saturation interpretation barred" and affected identities. Mean
measured ignition fraction >0.5 gives "ignited, not interpretable". Direction
classes remain descriptive but carry this interpretation flag.
D4: compare all warmup per-cell counts with K0 exactly; record B1 spikes and
both installed and scaled outgoing-count invariants. B1 spike count zero is
a measured check, not a promised hook property; if nonzero, ordinary outputs
are inert by contract. No claim that source activity itself is clamped.
D5: compare K1 and K2 direction classes at every labeled grid point.

Sequence: preregistration and SHA256 seal, implementation, synthetic tests
(classes, absolute timing, dictionary sourcing, seed pairing), intentional
pytest failure to verify harness, quick, full, report. Preserve protocol,
graph, dictionary, release.py and implementation hashes, environment versions,
wall time and relative raw paths. All delivery text is English UTF-8 without
BOM and contains no machine paths. Summary records total <=5 MB. No git
mutation, core/hook/dictionary/ear edits, or clean-room-excluded inspection.
