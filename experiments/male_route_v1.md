# male_route_v1 preregistration

Registered before any new simulation or path analysis. Male alone, no world.
Use build/graph_male.npz and the existing male dictionary, with P1=46 and
pIP10=2. Or47b uses exactly the male_decides selector (glomerular ORN proxy).
Shiu kernel, fast_gpu CUDA, unchanged Parameters except dt=0.2 ms as in
male_decides. Run 20 persistent 50 ms windows and discard windows 0..3.
Reset state for each condition. Use batch size one to accommodate seed-specific
random lesion graphs and shared GPU capacity; no parameter selection or tuning.

## Design

TEST seeds 0..19: drive {zero, scent240, scent960} crossed with network
{intact, p1_lesion, random_lesion}, nine conditions per seed. Quick seeds
100,101: {zero, scent960} crossed with {intact, p1_lesion}; excluded from
inference. No calibration or frozen parameter selection exists.
Poisson drive uses the backend's existing Bernoulli discretization. The fixed
target union is Or47b, right-side L1/L2, and P1, including zero-dose targets,
exactly as in male_decides. Only Or47b receives nonzero input. Reinitialize
the same seed for each condition so all conditions consume matching draws.

Lesion outgoing CSR rows only: copy count and signed data arrays, zero both
in lesioned rows, retain all CSR indices and incoming edges from other rows.
Cells remain in the network. Self-edges are outgoing and are also removed.
Random lesions contain 46 distinct non-P1 cells sampled without replacement
using numpy default_rng(seed+1000), independently of simulation randomness.
The same random lesion is reused across doses within a seed. There is NO
superclass matching. Random lesions may include input or readout cells.
Store all lesioned CSR indices and body IDs in raw records.

## Readouts and decisions

Within each seed average the 16 measured-window rates: pIP10, P1, Or47b
firing and realized sampled/delivered Or47b input, network Hz/neuron.
Ignition is the fraction of measured windows strictly above 30 Hz/neuron.
Active percentage is 100 times the fraction of cells with at least one spike
anywhere in the union of the 16 measured windows, not mean window activity.
Summaries use sample SD/sqrt(n) across seeds. Paired inference uses the 20
within-seed differences, never windows as replicates. Strict inequalities.

Let D_N(d) be scent dose d minus zero pIP10 in network N, per seed.
R0: mean D_intact(240) > 2 SE supports replication; otherwise R1/R2 unassessed.
R2: mean D_random(240) > 0.8 mean D_intact(240) supports the simple lesion
control; otherwise R1 is unassessed because the lesion method is suspect.
R1, only after R0/R2 pass: if mean D_P1(240) < 0.5 mean D_intact(240) AND
mean [D_intact(240)-D_P1(240)] > 2 SE of that paired difference-of-differences,
report "route through P1 SUPPORTED". If mean D_P1(240) > 0.8 mean D_intact(240),
report "P1 bypass SUPPORTED". Otherwise report "inconclusive".
Apply the same calculations at 960 as descriptive only, with its own gates.
Report all differences and SE, including the random control difference.

R3 is graph-only, descriptive: enumerate the ten strongest directed simple
paths for each exact length 2,3,4 from Or47b proxy ORNs to pIP10, ranked by
minimum unsigned edge synapse count. Exclude repeated cells. Ignore edge sign
for ranking but retain signed weights in output. Equal-score ties use a
deterministic search order (larger remaining bound, deeper prefix, CSR indices).
Report body IDs, types, edge counts, and P1 membership. P1 share means the
fraction of the returned top-ten paths containing an intermediate P1 cell,
per length and pooled; it is not a census of all possible anatomical paths.
Anatomical path ranking does not establish functional causality.

## Execution and provenance

Order: synthetic pytest and deliberate failing harness probe, quick, TEST,
path analysis, report. Budget 30 minutes; report partial if unfinished and
do not infer from incomplete TEST coverage. Hash this protocol before data.
Record graph, dictionary, relevant source hashes, environment versions,
parameters, wall time, target counts, and raw hashes. Summaries only under
records/male_route_v1_* with total below 10 MB; raw under build/records-raw.
Report headings include Test and Paths, with no calibration heading.
No machine paths in artifacts. Only this repository is inspected; the supplied
dependency import path is used without inspecting adjacent project sources.
No core, dictionary, gain or other lane files are changed. No git writes.
