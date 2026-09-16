# eye_v2 E1 preregistration

Frozen before implementation and gate evaluation on 2026-09-17. Budget: 60
minutes from first inspection. No network simulation, neuron drive, fitting,
git writes, or edits to the legacy eye or world. SHA-256 is recorded before
implementation. Only the supplied FAFB v783 copies and design note are used.

## Mapping and coverage

Join column_assignment.root_id to graph.body_id as exact integers. Reject
duplicate root IDs and conflicting (hemisphere, column_id) hex coordinates.
Retain unmatched counts and label disagreements; never invent missing hexes.
Column keys include hemisphere. Use the full assignment file to freeze the
coordinate origin; expose only columns with at least one graph-matched cell.
Coverage uses graph type and side as denominator, counts assigned by exact ID,
and separately records assignment-file type/hemisphere coverage and mismatches.
Report all graph types, and flag absent assignment types among visual intrinsic
and retinal categories from visual_neuron_types as an operational columnar
candidate inventory, not a complete anatomical classification. Also report
every graph type beginning R, L, Mi, Tm, T4, T5, C or T followed by digits as
a naming-based candidate; distinguish these two inventory sources explicitly.
No inference from soma coordinates, connectivity, or ID order.

No hex-to-angle transform is supplied in the inspected data schemas or note.
EYE_HEX_STEP_DEG=2.0 is a design constant: no biological source.
For axial p,q, u=p+q/2 and v=sqrt(3)*q/2. Within each hemisphere of the FULL
assignment table, u0=min(u)-0.5 and v0=(min(v)+max(v))/2. Angles in degrees:
azimuth=s*(u-u0)*step; elevation=(v-v0)*step. s=+1 for left hemisphere and
-1 for right. Negative azimuth means left visual field. Thus left field maps
to right hemisphere by declared, unverified convention. This is a declared
convention, uncalibrated. No source-based optical axis, field boundary,
interommatidial angle, or contralateral biological mapping is asserted.

## Contract and equations

Explicit modes: column_luminance, a finite time-by-column matrix in [0,1],
and object_parametric, a time-by-5 matrix of bearing_deg, elevation_deg,
width_deg, height_deg, contrast. Width/height are positive full extents;
contrast is in [-1,1]. One axis-aligned rectangle per sample, no angular
wrapping. Luminance is background 0.5 outside, 0.5+0.5*contrast inside,
including edges. This rasterization is an explicit part of object mode,
not an implicit conversion between input modes. Instances reject mode changes.

Output has one (column, sample) graded magnitude array and polarity array per
named class outer (R1-6 pooled), R7, R8. All three use identical filters:
no measured class differences are available. These are abstract channels,
not assignments of R1-6 cells or evidence that each column has all classes.
eye_absolute_rate_calibrated=false; eye_rate_ceiling_hz=null. No spike API.
Sampling rate 1000 samples/s, low-pass tau=5 ms, subtractive adaptation tau=50
ms, divisive adaptation tau=100 ms, strength=1; all have no biological source.
First-order low-pass f=a*f_prev+(1-a)*x, b=a_sub*b_prev+(1-a_sub)*f,
u=f-b, d=a_div*d_prev+(1-a_div)*f*f; signed output u/(1+strength*d).
Each a=exp(-1000/(sample_rate_hz*tau_ms)). Magnitude=abs(signed), polarity=sign(u).
All states initially zero, continuous across calls, reset only explicitly.
Empty chunks do not advance state; invalid input is rejected before mutation.
Window length only controls I/O. No biological parameter fitting.

## Frozen gates and negative controls

G1: seed 2801, 200 samples uniform [0,1] over all mapped columns; two signals
share 100 samples and have independently drawn suffixes. Every class's graded
and polarity prefix must be bit-equal, including processing the prefix alone.
Lookahead or trial normalization would violate this gate.

G2: seed 2802, 200 samples, whole versus chunks with boundaries
[0,1,1,7,23,24,80,131,199,200]. Maximum graded and signed error <1e-9;
polarity equal and start_sample correct. State reset per chunk would fail.
Both modes are tested, with object trajectories over mapped column centers.

G3: target each mapped column's azimuth in turn, full width=4*step (tolerance
2*step), elevation=0, height=2*(max(abs(elevation))+step), contrast=1.
From a fresh zero state, exactly the columns with |azimuth-theta|<=2*step
must have greater first-sample graded response than the background-only
trial; all other columns must equal background bit-for-bit. Require zero
false positives and zero false negatives across all targets. This is spatial
self-consistency, not map accuracy. Also test finite-height rectangles on
synthetic coordinates to detect discarded elevation or width/height swaps.

G4: every mapped left-hemisphere azimuth >0 and right-hemisphere azimuth <0;
objects centered at signed midrange with width equal to that hemisphere's
azimuth span plus one step must increase only that hemisphere's response.
Require nonempty responses on both sides and zero cross-side increases.
Biological laterality remains declared, unverified.

G5: seed 2805, uniformly permute coordinate pairs across fixed column keys,
including hemispheres; project the same G3 targets through the corrupted
map and score against the ORIGINAL frozen key-to-angle table. At least one
G3 false positive and one false negative must occur. Per-target affected
column counts and summed first-sample responses must remain identical to
the intact map (sum tolerance 1e-12). This catches a vacuous spatial oracle.

Biological gates unassessed: the supplied evidence has no visual recording
targets. No biological pass is inferred from G1-G5. Synthetic tests also use
independent recurrence and exact integer join oracles, invalid/duplicate data,
reset, empty calls, and nonmutation after rejected inputs. A separate intentional
pytest failure must show both one failure and exit 1 before acceptance.

## Evidence and reporting

Freeze preregistration, all four compressed source files and graph hashes.
Use prescribed Python/dependency chain, locale C, no bytecode, no plugin
autoload, pytest -p no:cacheprovider. No environment fallback. Store scripts,
raw mapping, gate details and logs only under build/records-raw/eye_v2_e1/.
Five summary records total <=5 MB; English UTF-8 without BOM, no machine paths.
Report verbatim preregistration, full coverage table, G1-G5, biological status,
all design constants and source limitations, scope note, test counts/exits,
hashes, git status, and deviations. An audit omits its own recursive hash and
records that exclusion. No external literature claims or downloads are added.
Next step: network delivery is a separate round requiring its own pre-registration and decision.
