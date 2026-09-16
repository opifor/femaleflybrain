# male_decides_v1 preregistration

Registered before simulation. Male alone, no world or contact. Graph:
`build/graph_male.npz`; fast_gpu CUDA batch, Shiu kernel, dt 0.2 ms,
20 persistent windows of 50 ms; discard the first four. All other Parameters
defaults are unchanged. Reset state per condition; independent seed columns.

## Inputs and readouts

Poisson drive uses the existing backend's Bernoulli time discretization.
A: dictionary Or47b glomerular proxy (ORN_VA1v), 30, 60, 120, 240, 480,
960 Hz; no vision. B: 30, 60, 120, 240 Hz to all L1/L2 with graph side R,
not silhouette columns (CHOSEN); no smell. C: direct P1, 0, 30, 60, 120 Hz.
Use a fixed union of input targets across conditions, including zero drive,
so paired seeds have matching random draws. Only specified targets get input.

Read P1 (expected 46), pIP10 (2), LC10a (275), DNa02 L/R, DNa01, MDN,
Or47b proxy, L1/L2, network mean Hz/neuron, network total spikes and total
Hz. Ignition is the fraction of measured windows with network mean strictly
greater than 30 Hz/neuron. Also report firing for the first 20 target types
in each of the ORN, L1 and L2 populations, in Unicode code-point order;
if fewer exist report all. Here target types mean directly driven populations,
not postsynaptic partners. Retain window summaries in build/records-raw only.

## Calibration and freezing

Seeds 0–9 only. Average the 16 measured windows within each seed, then
calculate mean and sample SD/sqrt(n) across seeds. Ignition fraction is
averaged over seeds. A ignition threshold is the first ascending dose whose
fraction is strictly greater than 0.5 (or absent). Select the lowest A dose
with P1 mean > 2 SE and ignition <= 0.5. If none, choose 960 Hz, explicitly
marked fallback and not evidence of a nonigniting dose. B selects the lowest
dose with LC10a mean > 2 SE. C selects the lowest dose with pIP10 mean > 2 SE,
including zero. B/C have no specified successful fallback: if none qualifies,
freeze the choice as absent and mark that held-out prediction unassessed.
Persist and hash frozen choices before any held-out execution.

## Held-out tests

Seeds 10–29 only; no retuning. Paired differences use within-seed measured
means and SE across the 20 differences, never windows as replicates.
M1: selected smell minus zero, P1 > 2 SE. M2: selected vision minus zero,
LC10a > 2 SE; DNa02 R−L is descriptive. M3: selected direct P1 minus zero,
pIP10 > 2 SE. Strict mean > 2 SE means supported, otherwise not supported.
M4: ignition for every test condition, calibration smell threshold, and P1
and ignition under combined selected smell plus vision; all descriptive.
Also report paired combined P1 difference and SE. No behavioral claim follows.

## Execution and evidence

Order: quick (seeds 100,101; zero and highest A/B/C doses, excluded from
inference), calibration, freeze, held-out test, report. Budget: 40 minutes.
Stop and report partial if execution cannot complete. Record protocol, graph,
dictionary and source hashes; environment versions, target counts, raw hashes
and wall times. Calibration and test have separate report headings. Summary
records only, <=10 MB; raw output under build/records-raw. No machine paths.
Synthetic tests cover strict freeze boundaries, ignition threshold and seed
partition; an opt-in deliberate failure checks the pytest exit chain.
