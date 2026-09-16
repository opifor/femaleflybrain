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
