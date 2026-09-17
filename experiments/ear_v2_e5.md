# ear_v2_e5: two-arm descriptive sign-resolution reading

Version: 1. Freeze this text before execution with SHA-256.
hash_basis: lf
a2_arm: read_only (identity unverified)
aliases: per-dataset (reported)
kernel: shiu (jump descriptive)
individual: one of {fafb, banc}
Claim class: descriptive, no calibration.

## Question

Two female connectomes under the same JO-A/JO-B drive (graph edges only;
no added hook or BatchRates drive): what does the skewed E/I convergence
onto vpoEN read as? The same A2-candidate population (CB1817a/b) feeds
vpoEN's largest excitatory input (CB1484, FAFB 704 synapses) and largest
inhibitory input (CB2364, 563 synapses). The supplied anatomical roadmap
reports CB1817a -> CB1484 83 (+) and CB1817a -> CB2364 583 (+), roughly
7:1 toward the inhibitory input. This anatomical ratio is distinct from
the descriptive firing-rate ratio below. This is a sign-resolution question:
"excitation never arrived" versus "arrived and was cancelled" requires
reading CB1484 and CB2364 together, not vpoEN's own rate alone.
Each individual carries its own baseline. FAFB columns are expected silent
at rest; BANC CB2364, AVLP083 and A2-candidate are expected active under song.

## Unchanged execution

Drive is the unchanged runner drive to JO-A, JO-B and SAG; no additional drive target.
The operator clarified that the original runner's BatchRates adapter is permitted;
the prohibition applies to additional drive targets and added adapters or hooks.

Reuse female_no_v1/female_readouts_v1: call female_readouts.observed_run,
which calls the unchanged runner.run; never copy the simulation loop.
The existing runner internally uses BatchRates solely for its original
JO-A, JO-B and SAG drive and always runs shiu then jump. No new BatchRates
target, injected drive, simulator hook, gain or calibration is introduced.
The passive return-event observer is reused unchanged. No function is replaced.
Quick: female only, seeds 0-1, six 50 ms windows, first four warm-up.
Full: FAFB v783 and BANC v888, seeds 0-9, twenty 50 ms windows, first four
warm-up, dt=0.2 ms; CUDA fast_gpu float32 and unchanged Parameters/W_syn.
Conditions: virgin_song, mated_song, virgin_silence, mated_silence.
The only two stimulus arms are baseline=silence and song. Lesion arms:
not run; requires operator seal.
Virgin SAG is 50 Hz Poisson; mated SAG is zero. Song amplitude=1,
mixture=0.7; silence has zero waveform. Preserve original target ordering,
zero-rate targets, song clock, 22050 Hz sampling, 35 ms pulse IPI,
4 ms Hann pulses/250 Hz carrier, 150 Hz sine, fourth-order JO-A 100-500 Hz
and JO-B 500-2500 Hz bands, padlen=27, 5 ms slices, scale=1.0,
180*clip(band RMS/RMS_FULL,0,1) Hz. Record RMS_FULL and JO_MAX_HZ=180.
No kernel, ear, dictionary or graph changes. No external references.
Execution order is freeze, quick, full FAFB, full BANC. The unchanged
runner includes descriptive jump immediately after shiu for each graph;
it cannot defer all jump execution without altering its control flow.

## Readouts and observation

Fixed eleven-group denominator (overlapping groups must not be summed):
vpoEN, vpoEN-input:CB1484, vpoEN-input:CB2364, vpoEN-input:CB1383,
vpoEN-input:WED104, vpoEN-input:AN_AVLP_8, vpoEN-gate:AVLP083,
A2-candidate, vpoDN, vpoIN, vpoDN-GABA-input (AVLP008).
Use the current dictionary API, save selectors, indices, body IDs, cell
counts, types and status. Empty groups are absent with null rates, never zero.
pC1 is an additional equality-control readout outside the eleven denominator.
Preserve the original FAFB SAG union and BANC pC1 superclass filter.
The authoritative dictionary snapshot is entries.py plus serialized current
per-dataset entries saved before execution. LF SHA-256 of entries.py:
e5f280ee1c389daa34d7981a0cfe0e188786acc0db5d4176655ee27ea9a40234.
Legacy dictionary_female.json LF SHA-256:
bd309bf4123292e4eff8dcac1385275bf8908a6790646fe19e63ccd1bf50eabd.
Legacy dictionary_banc.json LF SHA-256:
96fb99d17d5c0eaef5c9882bc65f481c46982a38699d6f619ce2b0c5b790e0bd.
Legacy exports supply original drive identities, not new diagnostic selectors.
FAFB diagnostic labels remain literal. BANC AN_AVLP_8 -> AN17B016 is
via alias, REPORTED. CB2364 -> WED001, CB1383 -> WED055_b and
CB1614 -> AVLP005 apply to male only; no male graph is run.
An alias is not established cell-level homology. A2-candidate remains read-only.

## Planned summaries and checks

Each summary row records individual in {fafb,banc}, condition, kernel,
group, fixed count, mean Hz/cell +/- SE across seed means, and conditional_on.
FAFB conditional_on: "FAFB v783 sign source shiu2024-parquet; uncalibrated front end".
BANC conditional_on: "BANC sign source shiu2024".
Separate individual tables and judgments; retain raw integer spike counts,
runner windows and seed/cell means. Warm-up is excluded. Reuse the existing
slice-to-window arithmetic, paired differences and raw reconstruction checks.
Pre-registered directional expectations, with no decision threshold:
FAFB song -> CB1484>0, CB2364>0, vpoEN=0: activity in first-hop input
populations need not yield vpoEN spikes; cancellation versus insufficient
excitation cannot be distinguished by these rates. BANC song -> the
inhibitory-side populations CB2364 and AVLP083 and upstream A2-candidate
are active, vpoEN=0. CB1484 is absent in BANC, so this individual cannot
fully test the two-sided hypothesis. Absent means absent selection, not
biological absence. No rate or causal efficacy follows from anatomy alone.
FAFB descriptive E/I ratio is defined here as CB2364 mean Hz / CB1484 mean Hz
(inhibitory/excitatory ordering despite the requested E/I label), per condition
and kernel. Zero denominator -> undefined (JSON null). No ratio threshold.
Exact historical equality is required only for shiu vpoDN/pC1, each seed and
condition, against female_readouts_v1 and original female_no_v1/two_female_v1.
Jump is descriptive with no historical bitwise equality requirement.
Any shiu mismatch is FAIL-CLOSED. Require exact observer-to-runner equality,
slice coverage, raw-to-summary reconstruction and unchanged input hashes.
Run relevant pytest with -q -p no:cacheprovider and a deliberate failure probe;
read both exit code and pass/fail summary. System Python 3.11 is the chain.
Sign claims come from sign_flow, never from firing-rate signs or NT guesses.
At a silent baseline no number is described as having decreased.

## Scope and delivery

a descriptive reading of an uncalibrated front end on two female connectomes; not a measurement of the female's hearing.
No behavioral claim, physiological rate calibration or causal intervention.
BANC population/sign-source scope differs from FAFB. Separate conditional
judgments are mandatory. Compact records remain below 5 MB; raw arrays stay
under build/records-raw/ear_v2_e5/. Freeze all protected inputs before quick,
including this preregistration, current dictionary snapshots, graphs,
historical records, reused observer/runner and task orchestration script.
Report is rendered from saved JSON and embeds this preregistration verbatim.
English, UTF-8 without BOM, LF; no personal names or machine paths in artifacts.
No git mutation. Full simulation budget <=15 minutes, total task <=40 minutes.
