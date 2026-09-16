# Two-body world

The world separates sensory evidence, persistent neural state, motor commands,
observed motion, and interaction outcomes. Contact is an interaction outcome;
neither contact nor vpoDN activity is an acceptance decision. This is a motor
map, not a measurement. No real-graph courtship run is claimed here.

```python
from flybench.graph import load
from flybench.world.loop import Brain, Loop

male = Brain(load("build/graph_male.npz"), "male", seed=3)
female = Brain(load("build/graph_female.npz"), "female", seed=4)
world = Loop(male, female, seed=7)
records = world.run(10)
report = {"metadata": world.metadata, "records": records}
```

`Brain` uses `sim.fast_gpu`, defaults to CUDA, and supports `device="cpu"`
for synthetic acceptance. Each brain can use its own graph or the same graph;
the simulator and state must be distinct. Dictionary indices are always
resolved against that brain's graph. Missing groups are recorded and have zero
readout/drive; no replacement population is silently selected. Such absence
can prevent walking, hearing, or singing and must be reviewed before a real run.

## Observable boundary

Arena stores only two immutable bodies (x, y in mm, heading in radians, signed
forward speed in mm/s), arena size, and an acoustic waveform. Observation exposes:

- Distance in mm and signed relative bearing in radians.
- Other body's signed forward speed and contact (`distance <= 2 mm`).
- Delivered sound samples, empty for the male receiver.

Bodies, observations, and arena use slots, with no attribute dictionary. There
are no neural rates, mating labels, acceptance variables, controller references,
or log references in these objects. A brain receives only an immutable
observation. The coordinator reads each brain's own outputs to construct its
motor command and the external audit log; those logs never feed the peer brain.
Direct hidden-state changes cannot affect a peer's sensory drive until the
changed brain produces an observable action. This is an interface separation,
not a security sandbox against arbitrary Python introspection.

## Geometry and retina

Coordinates use x right, y up. Positive bearing and heading changes turn left
(counterclockwise); an object on the right has negative bearing. The male starts
at arena centre facing +x. A seeded angle places the female exactly 6 mm ahead
within +/-30 degrees; her heading is uniform on [-pi, pi). Movement uses the
new heading. A wall clamps position and resets speed to zero, without reflection.
Bodies can overlap; contact is reported without a collision or mating rule.

The silhouette is an ellipse centred on bearing and zero elevation, with angular
semiaxes `atan2(body_width/2, distance)` and `atan2(body_height/2, distance)`.
It is visible when its centre is within the horizontal field. At zero separation
both semiaxes are pi/2. L1 and L2 each have one synthetic row at elevation zero:
the planar world has no vertical motion. Vertical visibility is still bounded
by the 210-degree field. Rasterization tests column centres inside the ellipse.

For each L1/L2 family and each anatomical side independently, sort by numeric
body ID and assign rank r of n to `(r+0.5)/n * 150 degrees`. Right-eye cells
receive positive azimuths (left visual field); left-eye cells receive negative
azimuths (right visual field). Unknown sides receive no column. This ordering is
deterministic synthetic retinotopy, not measured anatomical visual angles.
Each exact assignment is included in metadata. Contrast is object minus ground,
clipped to [0,1]; both L1 and L2 receive the same positive geometric proxy.

## Timing and sound

Every 50 ms, both observations are captured before either brain runs. Scent and
vision stay fixed over that window; the imported ear produces ten 5 ms JO drive
bins. Inputs add at overlapping targets. The local single-trial rate adapter
bridges backend sampling `[time,target]` and reporting `[target,trial]` without
changing simulator source. It does not support the batched run API. State, delay
ring, refractory counters, absolute step, and RNG persist across bins/windows.

Motor readouts are per-neuron means over the full 50 ms. Left/right DNa02 means
are formed separately. Turn is `(right-left)/450 * pi` rad/s, without clipping.
Forward motion is `10*clip(DNa01/450)-5*clip(MDN/450)`, multiplied by
`1-clip(DNp09/450)`; these clips are [0,1].

pIP10 mean divided by `1000/refractory_ms`, clipped to [0,1], controls male
amplitude. CHOSEN pulse and sine motor proxies are ps1_MN and i1_MN;
`pulse/(pulse+sine)` controls the imported Song mixture. Both zero means silence.
Song retains its absolute sample clock. The female emits no sound (`song_hz=0`).
The male's new waveform is attenuated by falloff at the pre-movement distance
and delivered to the female in the next window. The first window is silent.
This explicit one-window delay avoids a same-window algebraic feedback loop.
Imported Song uses 22050 samples/s, 250/150 Hz pulse/sine carriers, 35 ms pulse
interval, and a 4 ms envelope. Imported ear uses its existing JO-A/JO-B filters
and JO_MAX_HZ=180; neither module is modified or recalibrated here.

## CHOSEN constants

All new numeric and group choices live in `world/constants.py` and are copied
into report metadata. Simulator parameters, graph dataset, brain/geometry seeds,
missing groups, retina assignment, ear bands and ceiling are recorded as well.

| Constant | Value | Meaning |
| --- | --- | --- |
| WINDOW_MS / EAR_BIN_MS | 50 / 5 ms | World window / acoustic bin |
| ARENA_MM | 40 mm | Square side |
| INITIAL_DISTANCE_MM | 6 mm | Initial separation |
| INITIAL_HALF_ANGLE | pi/6 rad | Placement half-angle |
| CONTACT_MM | 2 mm | Inclusive contact threshold |
| SCENT_D0_MM | 5 mm | Scent and sound amplitude falloff scale |
| SMELL_MAX_HZ / CONTACT_MAX_HZ | 180 / 180 Hz | Sensory ceilings |
| EYE_MAX_HZ / CONTRAST | 180 Hz / 1 | Positive contrast proxy |
| HORIZONTAL_FOV / VERTICAL_FOV | 300 / 210 degrees | Eye field |
| BODY_WIDTH_MM / BODY_HEIGHT_MM | 1 / 2 mm | Silhouette dimensions |
| MOTOR_SCALE_HZ | 450 Hz | Motor normalization |
| MAX_TURN_RAD_S | pi rad/s | Turn gain at 450 Hz difference |
| MAX_FORWARD_MM_S / MAX_REVERSE_MM_S | 10 / 5 mm/s | Translation gains |
| PULSE_GROUP / SINE_GROUP | ps1_MN / i1_MN | Song mode proxies |
| CONTACT_GROUP | ppk23 | Contact-only sensory group |

Volatile scent is `SMELL_MAX_HZ/(1+(distance/5)^2)`, delivered to Or47b for
both receivers as a generic conspecific proxy. In the male this stands in for
female scent; no mating-state-dependent chemistry is invented. The full Or47b
dictionary entry, including its `proxy` confidence label, is retained. Contact
drive exists only during contact. No sex or reproductive state is a sensory field.

## Records and acceptance

Each record contains end-of-window positions/headings/speeds, distance and
contact; start-of-window observations; motor commands; sensory drive dictionaries,
delivered waveform RMS and scent Hz for both bodies; female vpoDN/pC1 means;
male P1/pIP10/LC10a/DNa02 and lateral DNa02 means; emitted song RMS, amplitude,
mixture and female silence. pC1 is the union of dictionary pC1a through pC1e.
Reports are JSON serializable; retaining full waveforms favours auditability over
log size. The caller persists `metadata` together with `records`.

Run `python -m pytest -q -p no:cacheprovider tests/test_world.py`.
The suite checks geometry, soft walls, retinal laterality, distance falloff,
motor direction/stop/reverse, heterogeneous drive, hidden-state isolation, and
ten-window stateful synthetic runs. A split 5+5 run matches a continuous 10-run;
sound propagation has an independently calculated RMS oracle. Enable
`FLYBENCH_FAIL_PROBE=1` and select `test_harness_failure_probe` to require one
failure and exit 1. Real graphs and full courtship validation belong to the
orchestrator, not this acceptance run.
