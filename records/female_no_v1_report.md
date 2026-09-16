# Experiment report

## Preregistration (verbatim)

# female_no_v1: she can say no

Version: 1. Preregistered before any experimental simulation.
Female brain alone: no arena and no male. Synthesized courtship song enters
JO-A/JO-B; reproductive state enters SAG. Readouts are vpoDN and pC1.

Graph: build/graph_female.npz, FAFB v783, Shiu 2024 exported edges,
sign rule shiu2024-parquet. Record the graph SHA256.
Dictionary version 1, with a protocol-specific SAG selector:
JO-A, JO-B; SAG = ^(?:AN_SMP_2|AN_FLA_SMP_2|ANXXX983)$ (union of present
types); pC1 = pC1a-e; vpoDN = DNp37. Record selected counts and identities.

Conditions: virgin_song, mated_song, virgin_silence, mated_silence.
Virgin: tonic 50 Hz Poisson SAG input in every window; mated: 0 Hz.
Song: a=1, m=0.7, a*(m*pulse+(1-m)*sine). Silence: zero waveform.
Keep all zero-rate drive targets so paired random draws are preserved.
Seeds: 0 through 9, identical in every condition and kernel, each from rest.
Primary kernel: shiu. Secondary kernel: jump, descriptive only:
"kernel does the difference matter".

Timing: 50 ms windows, 20 windows (1 second total), first 4 windows warm-up,
last 16 windows measured. Group output is mean Hz per cell across measured
windows. dt=0.2 ms, 250 steps per window. Quick execution uses seeds 0,1,
6 windows, first 4 warm-up; quick verdicts are preliminary, not primary evidence.

Song: sample rate 22050 Hz; pulse IPI 35 ms, width 4 ms, Hann window,
250 Hz carrier; sine song 150 Hz. Carry sample clock and carrier phase across
windows. Amplitude is bounded by 0..1.
Ear: fourth-order Butterworth bandpasses, JO-A 100-500 Hz, JO-B 500-2500 Hz;
sosfiltfilt padlen=27 on each 50 ms window. Every 5 ms slice gives
180*clip(band RMS/RMS_FULL,0,1) Hz. RMS_FULL is JO-A band RMS of a full-amplitude
1 second pulse train, computed once at import and recorded.
Sources supplied for synthesis: von Philipsborn 2011, Neuron 69:509;
Clemens/Murthy 2018, Nature Communications (carriers);
Zhou 2015, eLife 4:e08477 (IPI).
These are synthesis choices, not brain measurements.

Predictions (registered before data):
P1 "she can say no": vpoDN virgin_song > mated_song.
P2 "she hears": vpoDN virgin_song > virgin_silence.
P3 "state reaches receptivity cells": pC1 virgin_song > mated_song.
For each primary prediction, compute ten paired seed differences and their
mean and SE (sample SD / sqrt(10)). Mean difference > 2 SE means supported;
otherwise not supported. No absolute-value or one-sided sign replacement.
P4 descriptive, no confirmatory verdict: mated_song versus mated_silence
for both readouts; jump minus shiu for each condition and both readouts;
total network Hz/neuron per condition, and fraction of measured windows
with total network rate >30 Hz/neuron.

CHOSEN: amplitude 1, pulse mixture 0.7 (pulse-weighted natural song);
dt 0.2 ms; JO_MAX_HZ 180; union of the three specified SAG candidate types;
scale 1.0 using Shiu W_syn, no additional gain and no calibration.
Report the result whatever its direction. These neuronal readouts do not
establish behavioural refusal or mating in an isolated brain simulation.


## Recorded execution

Protocol SHA256: 9b1e9032b3c3d9e07197a784aeafca1dbba1c7586a585fa1c365ac4b87cb0805. Graph SHA256: 35e5c3b4cca86b27392a144a4d6bcb37de2f3f97f29d71f5c0a5c20b1cd593b8.
Mode: full; elapsed: 64.395 s. Units: Hz per cell.

| Kernel | Condition | Seed | vpoDN | pC1 | Network | Ignition fraction |
|---|---|---:|---:|---:|---:|---:|
| shiu | virgin_song | 0 | 41.25 | 29.125 | 0.166989 | 0 |
| shiu | virgin_song | 1 | 31.875 | 22.375 | 0.16396 | 0 |
| shiu | virgin_song | 2 | 38.125 | 26.75 | 0.164627 | 0 |
| shiu | virgin_song | 3 | 45 | 31.25 | 0.168468 | 0 |
| shiu | virgin_song | 4 | 43.75 | 30.75 | 0.16827 | 0 |
| shiu | virgin_song | 5 | 35 | 23.75 | 0.16359 | 0 |
| shiu | virgin_song | 6 | 36.875 | 26 | 0.165808 | 0 |
| shiu | virgin_song | 7 | 34.375 | 24.75 | 0.163897 | 0 |
| shiu | virgin_song | 8 | 41.25 | 29.625 | 0.167152 | 0 |
| shiu | virgin_song | 9 | 41.875 | 29.375 | 0.165132 | 0 |
| shiu | mated_song | 0 | 0 | 0 | 0.156053 | 0 |
| shiu | mated_song | 1 | 0 | 0 | 0.156116 | 0 |
| shiu | mated_song | 2 | 0 | 0 | 0.15489 | 0 |
| shiu | mated_song | 3 | 0 | 0 | 0.157414 | 0 |
| shiu | mated_song | 4 | 0 | 0 | 0.156909 | 0 |
| shiu | mated_song | 5 | 0 | 0 | 0.156233 | 0 |
| shiu | mated_song | 6 | 0 | 0 | 0.156341 | 0 |
| shiu | mated_song | 7 | 0 | 0 | 0.156774 | 0 |
| shiu | mated_song | 8 | 0 | 0 | 0.155665 | 0 |
| shiu | mated_song | 9 | 0 | 0 | 0.154547 | 0 |
| shiu | virgin_silence | 0 | 41.25 | 29.125 | 0.011126 | 0 |
| shiu | virgin_silence | 1 | 33.75 | 23.5 | 0.00858344 | 0 |
| shiu | virgin_silence | 2 | 38.125 | 26.75 | 0.00973752 | 0 |
| shiu | virgin_silence | 3 | 45.625 | 31.25 | 0.0111441 | 0 |
| shiu | virgin_silence | 4 | 43.75 | 30.75 | 0.0117121 | 0 |
| shiu | virgin_silence | 5 | 35 | 23.75 | 0.00741133 | 0 |
| shiu | virgin_silence | 6 | 36.25 | 25.75 | 0.0095031 | 0 |
| shiu | virgin_silence | 7 | 34.375 | 24.75 | 0.00726707 | 0 |
| shiu | virgin_silence | 8 | 41.25 | 29.625 | 0.0114416 | 0 |
| shiu | virgin_silence | 9 | 41.875 | 29.375 | 0.0106301 | 0 |
| shiu | mated_silence | 0 | 0 | 0 | 0 | 0 |
| shiu | mated_silence | 1 | 0 | 0 | 0 | 0 |
| shiu | mated_silence | 2 | 0 | 0 | 0 | 0 |
| shiu | mated_silence | 3 | 0 | 0 | 0 | 0 |
| shiu | mated_silence | 4 | 0 | 0 | 0 | 0 |
| shiu | mated_silence | 5 | 0 | 0 | 0 | 0 |
| shiu | mated_silence | 6 | 0 | 0 | 0 | 0 |
| shiu | mated_silence | 7 | 0 | 0 | 0 | 0 |
| shiu | mated_silence | 8 | 0 | 0 | 0 | 0 |
| shiu | mated_silence | 9 | 0 | 0 | 0 | 0 |
| jump | virgin_song | 0 | 0 | 21.375 | 50.0669 | 1 |
| jump | virgin_song | 1 | 141.875 | 0.125 | 47.6125 | 1 |
| jump | virgin_song | 2 | 157.5 | 2.875 | 50.3932 | 1 |
| jump | virgin_song | 3 | 31.875 | 0.875 | 49.4762 | 1 |
| jump | virgin_song | 4 | 208.75 | 5.375 | 51.3271 | 1 |
| jump | virgin_song | 5 | 208.125 | 0 | 51.443 | 1 |
| jump | virgin_song | 6 | 89.375 | 0.625 | 50.8523 | 1 |
| jump | virgin_song | 7 | 163.75 | 0 | 50.9836 | 1 |
| jump | virgin_song | 8 | 179.375 | 4.875 | 46.7807 | 0.9375 |
| jump | virgin_song | 9 | 197.5 | 0.5 | 49.3654 | 1 |
| jump | mated_song | 0 | 203.75 | 0 | 48.0125 | 1 |
| jump | mated_song | 1 | 208.125 | 0 | 50.5208 | 1 |
| jump | mated_song | 2 | 0 | 0 | 50.548 | 1 |
| jump | mated_song | 3 | 192.5 | 0 | 51.7681 | 1 |
| jump | mated_song | 4 | 115 | 0 | 46.9275 | 1 |
| jump | mated_song | 5 | 0 | 0 | 49.0535 | 1 |
| jump | mated_song | 6 | 129.375 | 0 | 50.8824 | 1 |
| jump | mated_song | 7 | 113.75 | 0 | 48.1576 | 1 |
| jump | mated_song | 8 | 196.875 | 0 | 51.1845 | 1 |
| jump | mated_song | 9 | 198.125 | 0 | 48.2976 | 1 |
| jump | virgin_silence | 0 | 0 | 0 | 47.9677 | 1 |
| jump | virgin_silence | 1 | 0.625 | 0.125 | 48.8921 | 1 |
| jump | virgin_silence | 2 | 96.875 | 0 | 52.5138 | 1 |
| jump | virgin_silence | 3 | 195.625 | 2.75 | 45.1942 | 0.9375 |
| jump | virgin_silence | 4 | 208.125 | 0.125 | 48.6939 | 1 |
| jump | virgin_silence | 5 | 208.125 | 0.5 | 46.318 | 1 |
| jump | virgin_silence | 6 | 76.875 | 2.125 | 44.7411 | 0.9375 |
| jump | virgin_silence | 7 | 156.875 | 1.375 | 47.0536 | 0.9375 |
| jump | virgin_silence | 8 | 173.125 | 0 | 47.1119 | 1 |
| jump | virgin_silence | 9 | 208.125 | 0.375 | 52.4779 | 1 |
| jump | mated_silence | 0 | 0 | 0 | 0 | 0 |
| jump | mated_silence | 1 | 0 | 0 | 0 | 0 |
| jump | mated_silence | 2 | 0 | 0 | 0 | 0 |
| jump | mated_silence | 3 | 0 | 0 | 0 | 0 |
| jump | mated_silence | 4 | 0 | 0 | 0 | 0 |
| jump | mated_silence | 5 | 0 | 0 | 0 | 0 |
| jump | mated_silence | 6 | 0 | 0 | 0 | 0 |
| jump | mated_silence | 7 | 0 | 0 | 0 | 0 |
| jump | mated_silence | 8 | 0 | 0 | 0 | 0 |
| jump | mated_silence | 9 | 0 | 0 | 0 | 0 |

## Condition summaries

| Kernel | Condition | vpoDN mean ± SE | pC1 mean ± SE | Network mean ± SE | Ignition fraction |
|---|---|---:|---:|---:|---:|
| shiu | virgin_song | 38.9375 ± 1.37579 | 27.375 ± 0.976637 | 0.165789 ± 0.000578994 | 0 |
| shiu | mated_song | 0 ± 0 | 0 ± 0 | 0.156094 ± 0.000278493 | 0 |
| shiu | virgin_silence | 39.125 ± 1.32484 | 27.4625 ± 0.922152 | 0.00985563 ± 0.000519265 | 0 |
| shiu | mated_silence | 0 ± 0 | 0 ± 0 | 0 ± 0 | 0 |
| jump | virgin_song | 137.812 ± 23.3105 | 3.6625 ± 2.06853 | 49.8301 ± 0.496083 | 0.99375 |
| jump | mated_song | 135.75 ± 25.4997 | 0 ± 0 | 49.5353 ± 0.519596 | 1 |
| jump | virgin_silence | 132.438 ± 26.3939 | 0.7375 ± 0.315376 | 48.0964 ± 0.847335 | 0.98125 |
| jump | mated_silence | 0 ± 0 | 0 ± 0 | 0 ± 0 | 0 |

## Paired contrasts

| Prediction / contrast | Difference ± SE | Verdict |
|---|---:|---|
| P1 (vpoDN) | 38.9375 ± 1.37579 | supported |
| P2 (vpoDN) | -0.1875 ± 0.209372 | not supported |
| P3 (pC1) | 27.375 ± 0.976637 | supported |
| P4 shiu vpoDN: mated song minus silence | 0 ± 0 | descriptive |
| P4 jump vpoDN: mated song minus silence | 135.75 ± 25.4997 | descriptive |
| P4 virgin_song vpoDN: jump minus shiu | 98.875 ± 23.6762 | descriptive |
| P4 mated_song vpoDN: jump minus shiu | 135.75 ± 25.4997 | descriptive |
| P4 virgin_silence vpoDN: jump minus shiu | 93.3125 ± 25.8964 | descriptive |
| P4 mated_silence vpoDN: jump minus shiu | 0 ± 0 | descriptive |
| P4 shiu pC1: mated song minus silence | 0 ± 0 | descriptive |
| P4 jump pC1: mated song minus silence | 0 ± 0 | descriptive |
| P4 virgin_song pC1: jump minus shiu | -23.7125 ± 1.93129 | descriptive |
| P4 mated_song pC1: jump minus shiu | 0 ± 0 | descriptive |
| P4 virgin_silence pC1: jump minus shiu | -26.725 ± 0.953575 | descriptive |
| P4 mated_silence pC1: jump minus shiu | 0 ± 0 | descriptive |

## Result

P1: supported; P2: not supported; P3: supported under the preregistered Shiu criterion.
The full paired-seed execution is reported above.
Kernel differences and ignition fractions are descriptive. No calibration was applied.
These isolated-brain neuronal outputs do not demonstrate behavioural refusal or mating.

Adding song to the virgin condition changed vpoDN by -0.1875 ± 0.209372 Hz/cell (paired SE).
The auditory prediction was not supported; reproductive-state effects alone do not establish song-dependent receptivity.
