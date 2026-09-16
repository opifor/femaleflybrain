# ear_v2 E1 preregistration

Frozen before implementation, 2026-09-16. Budget: 45 minutes from first
repository inspection. Pure signal processing; no network simulation.
The SHA-256 of this file is recorded separately before implementation.

## Evidence and scope

Use only supplied ledger C18 measurements R3_006 (5--20 ms intensity
adaptation range), R3_007 (approximately 30 ms recovery), and R3_008
(pulse response curve not transcribed). DOI: 10.1038/s41467-017-02453-9.
These are extracellular compound action potentials in virgin female
Canton-S flies, not individual JO rates or graded membrane measurements.
Comparison of graded envelopes to CAP kinetics is a provisional observation
mapping, not a calibrated CAP model. User authorization permits this limited
fit despite the source snapshot's default fit_allowed=false metadata.
No independent source verification or additional literature extraction.

Inspection of all 58 measurement entries found no JO subtype tuning centers,
bandwidths, or gains. Those targets are **not in ledger**. B1 curves are not JO
subtype tuning. No biological default channels will be invented. A generic
four-channel synthetic fixture (150, 300, 600, 900 Hz, Q=1, G=1) tests the
implementation only; these are design choices, not biological measurements.
JO calibration must fail closed until explicit ledger tuning entries exist.
No F channel is included. A/B identity and overlap remain unassessed.

## Input, output, and model

Sampling rate is flybench.song.SAMPLE_RATE = 22050 Hz. Input is a finite,
one-dimensional waveform explicitly expressed as particle_velocity_mm_s or
arista_displacement_um. Each instance is bound to exactly one mode. No
conversion exists between modes; conversion requests raise ValueError.
No trial RMS normalization. No automatic conversion of Song amplitudes.
Output r_graded has shape (channel, sample), arbitrary graded units, never Hz.
A separate phase_sign array preserves the sign immediately before full-wave
rectification; r_signed = phase_sign * r_graded is reconstructible.

Immutable configuration constants:
jo_absolute_rate_calibrated=false; jo_rate_ceiling_hz=null;
jo_refractory_ms=null; allow_uncalibrated_spike_drive=false.
Null means unresolved, not zero. No Poisson operation or output clipping.

For each channel H(s)=G*(omega/Q)*s/(s*s+(omega/Q)*s+omega*omega).
Prewarp omega=2*fs*tan(pi*f/fs), then use the bilinear transform.
Persistent filter state is followed by persistent subtractive adaptation:
b[n]=a_sub*b[n-1]+(1-a_sub)*filtered[n]; u=filtered-b.
Rectify v=abs(u), preserving sign(u) separately. Divisive adaptation:
d[n]=a_div*d[n-1]+(1-a_div)*v[n]; r=v/(1+d).
a=exp(-1/(fs*tau)); initial tau_sub=30 ms, tau_div=50 ms are design
initializations, not measurements. The denominator's unit offset is a fixed
arbitrary graded-unit convention, not a physical amplitude calibration.
All states start at zero only at construction or explicit reset.
No stimulus classification or pulse/sine routing. Fifty milliseconds is only
an I/O window; five milliseconds is only a logging bin. All processing uses
individual waveform samples. Rounded absolute sample boundaries avoid drift.

## Gates and stimuli

G1: deterministic RNG seed 1801, 100 ms Gaussian signal with a shared 50 ms
prefix and altered suffix. Prefix r_graded and phase_sign must be bit-equal;
also compare a prefix processed alone. A noncausal lookahead would break this.

G2: a 50 ms seed-1802 waveform in one call versus ten consecutive 5 ms
chunks, boundaries round(k*0.005*fs). Maximum difference <1e-9 in graded and
signed responses; phase signs identical. Also test empty, one-sample, and
irregular chunks on a longer trial. State reset between chunks must break it.

G3: synthetic 80--1000 Hz multisine, spacing 20 Hz, independent uniform
phases from seed 1803, 16 phase realizations. Its analytic RMS is one before
the explicitly prescribed physical level (1 or 4 mm/s); no realized-trial
RMS adjustment. Separate 0.5 s step-up and step-down trials switch at 0.25 s.
Average graded response over realizations and synthetic channels; average
into 1 ms analysis bins (not internal model steps). Fit c+a*exp(-t/tau)
on 2--62 ms after switch, tau bounds 1--200 ms. Require R-squared >=0.8,
nonzero transient amplitude >1e-6, both tau in inclusive [5,20] ms,
and tau_up < tau_down. [5,20] is a reported range, not two standard errors.
If fits are inadequate mark not passed, retaining numerical diagnostics.
The direction of asymmetry is user-provided; separate up/down numerical
values and the asymmetry effect size are not in ledger.

G4: ten Hann-windowed 300 Hz, 4 ms pulses, peak scale 4 mm/s, at onset-to-onset
IPIs 36 and 10 ms. First onset 50 ms; measure compound graded maximum in
each onset-to-next-onset interval. Require peak10/peak1 >=0.9 at 36 ms and
<0.9 at 10 ms. This is descriptive, not a digitized CAP target. The ledger's
16 ms pulse protocol cannot be substituted silently for this nonoverlapping
4 ms synthetic diagnostic; the 10 ms onset IPI would overlap 16 ms pulses.
Recovery additionally uses a 250 ms conditioner (300 Hz, scale 4), silence
gaps 0,5,10,20,30,50,80,120 ms and an identical 4 ms probe. Compare probe
peak to an isolated probe, fit c+a*exp(-gap/tau). R-squared >=0.8; [20,40] ms
is a declared engineering tolerance around approximately 30, not uncertainty
from the publication. Recovery is reported alongside G4, not silently equated
with the pulse-ratio criterion.

G5: 0.5 s 300 Hz continuous sine versus 36 ms IPI Hann pulse train. Equal
RMS by analytic waveform energy: sine amplitude derives from the integral
of the 4 ms Hann carrier squared divided by IPI; pulse scale 4 mm/s.
No trial RMS normalization. Report realized finite-window RMS mismatch.
Ratio = mean of compound response in last 100 ms / maximum in first 50 ms.
Require continuous ratio < pulse ratio. Unequal duty cycle affects this
descriptive ratio; it is not an isolated measurement of adaptation strength.

G6: linear bank frequency response on 1 Hz grid 20--2000 Hz: peaks within
15 percent of ledger JO targets; A/B overlap defined as a common frequency
below 500 Hz with both magnitude/own-peak >=0.5. Absent ledger centers and
identities -> biological gate unassessed, even if fixture filter tests pass.
Fixture checks use 1 percent peak tolerance and overlap of first two filters.
F explicitly absent. No hard high-pass at 500 Hz.

G7: 0.5 s 300 Hz sine, amplitude 1 mm/s. Analyze last 0.2 s; 600 Hz Fourier
amplitude of mean graded signal must exceed 0.05 times its DC amplitude;
phase_sign must take both signs and reconstruct signed magnitude exactly.
The doubled component describes a rectified compound response, not spikes.

## Fit and uncertainty

Run pytest before fitting. Scientific hypotheses may be not passed;
pytest uses explicit xfail for unsupported scientific gates, never a silent
passing assertion. Structural, numerical, and contract failures stay failures.
Prove the harness with an intentional failing test and its failed-count line.

Only tau_sub, tau_div and channel omega/Q/G are eligible parameters.
Without JO targets, channel fitting is unassessed, with no fabricated result.
For a reproducible conditional exploration on the synthetic fixture, grid
tau_sub in [5,10,20,30,50] ms and tau_div in [5,10,20,30,50] ms.
For each candidate measure G3 and recovery. Objective: sum of squared
distance of up/down taus outside [5,20], scaled by 15 ms, plus squared
(recovery_tau-30)/10; add 1 when up>=down, and 10 for each invalid fit.
No fitting to G4/G5/G7, downstream neurons, or network output. Report every
grid point and the best (tie resolved by ascending sub then div). The
objective<=minimum+1 parameter ranges are grid sensitivity, NOT confidence
intervals or population uncertainty. No refinement or post-hoc tolerance edits.
Report initial and selected candidate gate values separately. A fixture fit
is partial evidence only and must not become the module's biological default.

## Records and stop conditions

Freeze file and ledger hashes; record Python, dependency versions, platform
without machine paths, seed, commands with portable placeholders, wall time,
test counts and exit codes. Raw arrays, scripts and logs go under
build/records-raw/ear_v2_e1*. Summaries go under records/ear_v2_e1_* and total
at most 2 MB. UTF-8 without BOM; copied ledger must also be byte-identical.
If source has BOM, record the conflict rather than silently changing bytes.
No git mutation. No legacy front-end, core, world, dictionary, or experiment
runner edits. Missing calibration and failed descriptive gates are visible
limitations, never converted into scientific acceptance by green unit tests.
