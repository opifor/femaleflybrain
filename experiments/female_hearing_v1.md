# female_hearing_v1: the she hears ladder

Version 1. Preregistered before experimental data collection.
Graph: build/graph_female.npz; record SHA256. Kernel: shiu; dt 0.2 ms;
50 ms windows, 20 windows, first 4 warm-up. Backend: fast_gpu batches,
float32. Each condition starts from rest. Virgin SAG: 50 Hz grid Poisson;
mated SAG: 0 Hz. Readouts: vpoDN (2 cells), vpoEN (4), pC1 (10),
network total spikes and mean Hz/neuron, and measured-window fraction above
30 Hz/neuron. Record each readout cell separately and requested, sampled,
and delivered drive. Delivered drive means sampled inputs coincident with
output spikes; total cell firing is also recorded.

Calibration seeds: 0-9. Test seeds: 10-29, in a separate run after an
automatic frozen selection. Calibration never uses test seeds.
Quick: seeds 0,1, six windows with four warm-up, calibration conditions only;
quick results cannot freeze a choice or enter confirmatory results.

Arm (a), calibration: virgin; JO_MAX_HZ in {60,180,360,720}, song and
paired silence at each dose. Report vpoEN and vpoDN song-minus-silence
mean differences and SE. Freeze the LOWEST dose with vpoEN difference >2 SE.
If none passes, select 720 and record "no transfer".

Arm (b), positive control, calibration: no song; direct vpoEN grid Poisson
at {0,60,180,360} Hz, virgin and mated. Report realized vpoEN firing and
vpoDN. Differences are relative to state-matched 0 Hz; selection uses virgin.
Freeze the LOWEST positive dose with vpoDN difference >2 SE; otherwise
select 360 and record "no transfer".

Arm (c), independent sensitivity, calibration seeds 0-9: positive network
edges only multiplied by 1.3; negative edges, external drive and SAG unchanged.
JO_MAX_HZ 180, all four virgin/mated x song/silence conditions, with gain 1.0
controls for the same four conditions and seeds. Report virgin vpoDN
song-minus-silence and network ignition fraction. Identical gain-1 virgin
conditions in arm (a) may be reused by identity, with no duplicate evidence.

Pre-registered test, seeds 10-29 after freezing, the same session:
T1 "she hears at the chosen dose": virgin vpoDN song-minus-silence at
the selected JO dose >2 SE.
T2 "vpoEN relays": virgin vpoDN at selected direct vpoEN dose minus 0 >2 SE.
T3 "state gates the relay": the T2 difference is smaller in mated than
virgin, qualitatively following Wang et al. (2021), Nature. Descriptive only;
report mated-minus-virgin paired difference of differences, no verdict.
T4: gain 1.3, JO 180, virgin song-minus-silence and ignition, descriptive.
Include all four states/song conditions at gains 1.0 and 1.3 for T4 context.

For every contrast, pair by seed and use sample SD of differences divided
by sqrt(n). For T1 and T2, mean paired difference over 20 seeds >2 SE means
"supported"; otherwise "not supported". Strict inequality; zero with zero
SE is not supported. Calibration and pre-registered test stay separate.
No additional dose search, seed exclusion, or tuning after freezing.

Song and ear match female_no_v1: amplitude 1, pulse mixture 0.7, sample rate
22050 Hz; 35 ms pulse IPI, 4 ms Hann pulse, 250 Hz carrier, 150 Hz sine.
Carry song time between windows. Fourth-order bands 100-500 and 500-2500 Hz,
sosfiltfilt padlen 27 per window; ten 5 ms slices map clipped band RMS/RMS_FULL
to JO_MAX_HZ. RMS_FULL is the full-amplitude one-second pure-pulse reference.
JO groups use dictionary version 1; SAG uses exact AN_SMP_2, AN_FLA_SMP_2,
ANXXX983 union; pC1 uses pC1a-e; vpoDN uses DNp37; vpoEN uses dictionary
version 1. All four drive populations remain targeted even at zero rate,
preserving paired random streams. This direct-drive target convention applies
to every arm and differs from female_no_v1's three-population target list.
Group selection and count checks precede simulation.

Budget: stop with partial evidence if total task time exceeds 40 minutes.
Save calibration, frozen decision and test separately with content hashes.
Report all results regardless of direction. These isolated neural outputs
do not establish behavioural hearing, refusal or mating.
