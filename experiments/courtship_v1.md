# courtship_v1 preregistration

Frozen before the first real-graph run. This is a motor map, not a measurement;
contact and vpoDN firing are not acceptance or mating decisions.

## World and brains

Use the constants and geometry in docs/world.md unchanged: 50 ms windows,
40 mm square arena, female initially 6 mm ahead within +/-30 degrees,
scent/sound falloff 1/(1+(distance/5 mm)^2), 300 by 210 degree eyes,
and 450 Hz motor normalization. Both bodies move using DNa02 left/right,
DNa01, MDN and the existing DNp09 stop gate. Use fast_gpu, shiu,
float32, dt 0.2 ms, all other Parameters defaults. Persistent independent
brain states, delay rings, refractory counters and random streams continue
between 5 ms auditory bins and windows. Each trial lasts 400 windows (20 s);
discard the first 40 windows from all time averages and correlations.
Seeds 0 through 9 are paired across conditions. Geometry and male brain use
seed s; female brain uses seed 10000+s. Batch columns represent seeds.

Male: build/graph_male.npz, MaleCNS Traced; dictionary male groups. World-only
inputs: Or47b proxy at SMELL_MAX_HZ times falloff, ppk23 proxy at CONTACT_MAX_HZ
only at distance <=2 mm, and L1/L2 silhouette vision. No auditory or state input.
Read P1, pIP10, LC10a, DNa02 left/right, DNa01, MDN, DNp09, pulse/sine proxies
and network total spikes / mean Hz per neuron.

Male song amplitude is clipped pIP10 mean/(1000/refractory_ms); pulse fraction
is ps1_MN/(ps1_MN+i1_MN), with silence when both motor means are zero.
Use unmodified song.py (22050 Hz) and ear.py (JO_MAX_HZ=180), attenuate at
pre-movement distance, deliver to the female next window (first is silent).

Female: build/graph_female.npz, FAFB Shiu export; dictionary female groups.
CHOSEN blind eye, no scent or contact input, as in the prior female protocol.
Only JO-A/B auditory input and SAG state input: virgin 50 Hz, mated 0 Hz.
SAG uses the prior protocol alias union ^(?:AN_SMP_2|AN_FLA_SMP_2|ANXXX983)$.
pC1 is the union of pC1a through pC1e; vpoDN is the dictionary group.
Read vpoDN, pC1, motor groups and network activity. Female produces no sound.
Missing groups remain empty and are disclosed; no replacement is selected.

## Conditions and predictions

Four paired conditions: virgin_live, mated_live, virgin_mute, mated_mute.
Mute zeros the emitted waveform only; male brain, pIP10 readout, motor mode
and amplitude computation continue unchanged.

- C1 he sings: mean male pIP10 >0 Hz in at least 8 of 10 seeds in each live
  condition, and paired delivered RMS virgin_live minus virgin_mute >2 SE.
  Also disclose nonzero delivered RMS seed counts in both live conditions.
- C2 she says no: paired mean vpoDN virgin_live minus mated_live >2 SE.
- C3 descriptive only: paired mean vpoDN virgin_live minus virgin_mute;
  expect no difference because JO-to-vpoEN transfer was absent in female_hearing_v1.
- C4 descriptive only: P1 mean and male ignition fraction per condition;
  ignition is the fraction of measured windows with network mean >30 Hz/neuron.
  Also report female ignition and network means and totals.
- C5 descriptive only: mean and final distance per condition and per-seed
  Spearman correlation between male DNa02_L-DNa02_R and start-window bearing.
  Constant series have undefined correlation, stored as null with a reason.

SE is sample standard deviation of seed-paired differences divided by sqrt(n).
Use strict >2 SE, including at zero SE. No inferential verdict for C3-C5.
Quick (seeds 0,1; 60 windows; same 40-window warmup) is wiring/performance
evidence only, excluded from full verdicts. If projected full execution exceeds
40 minutes, use seeds 0-4 and label partial; C1/C2 full verdicts then remain
unassessed, with paired estimates disclosed. Do not retune any parameter.

## Records and verification

Record each window: both positions/headings/speeds, pre-movement distance and
bearing, end distance, scent Hz, delivered and emitted RMS, ten JO drive bins,
all named readouts, network total spikes and ignition. Full window records and
group cell rates belong in build/records-raw/. Summary JSON contains only
condition-by-seed aggregates, counts, missing groups, graph/source/protocol
hashes, environment versions, elapsed times and raw record hashes. Summary
JSON plus Markdown report in records must be <=10 MB; no machine paths.

Tests verify mute wave with retained pIP10, observable-only male input,
state and female input wiring, seed-specific batch sampling, and verdicts
against fabricated positive, zero and noisy contrasts. An opt-in deliberate
failure proves the pytest harness returns nonzero as well as reporting failure.
