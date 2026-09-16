# Graded visual front end

`flybench.retinotopy.join_columns` joins the supplied FAFB v783 column table
to graph `body_id` using exact integer root IDs. It preserves graph order,
reports unmatched cells and label disagreements, and rejects duplicate IDs or
conflicting column hexes. Columns are keyed by `(hemisphere, column_id)`.
Unassigned cells remain unassigned. No edges or network state are accessed.

The angular transform is a declared convention, uncalibrated.
`EYE_HEX_STEP_DEG=2.0` has no biological source and can be changed with
`eye2.Config(hex_step_deg=...)`. With `u=p+q/2`, `v=sqrt(3)*q/2`, origins are
`u0=min(u)-0.5`, `v0=(min(v)+max(v))/2` over each hemisphere's full assignment
table. Angles are `s*(u-u0)*step`, `(v-v0)*step`, in degrees. `s=+1` for left
hemisphere, `-1` for right; negative azimuth is left field. This laterality is
declared, unverified. Source hexes do not establish optical axes or field limits.

```python
import numpy as np
from flybench.retinotopy import read_assignments, join_columns
from flybench.eye2 import Eye2

with np.load("build/graph_female.npz", allow_pickle=False) as source:
    graph = {k: source[k] for k in ("body_id", "type", "side")}
mapping = join_columns(graph, read_assignments("build/raw_female/column_assignment.csv.gz"))
eye = Eye2(mapping.column_map, input_mode="object_parametric")
response = eye.process([[10, 0, 8, 12, 1]], input_mode="object_parametric")
outer = response.r_graded["outer"]  # (column, sample), never Hz
```

Modes are mandatory at construction and every call. `column_luminance` takes
a time-by-column matrix in [0,1], ordered exactly as `column_map.keys`.
`object_parametric` takes time-by-5 rows: bearing, elevation, full width, full
height (all degrees), contrast in [-1,1]. It explicitly projects one rectangle
per sample: background .5, inside .5+.5*contrast, edges included, no wrapping.
There is no automatic input-mode conversion. Geometry is fixed for an instance.

`r_graded` and `polarity_sign` each contain `outer`, `R7`, `R8` arrays of shape
(column, sample); `r_signed` reconstructs their signed signals. `outer` pools
R1-6 as one name. These names all use the same filter, since measured class
differences are unavailable. They do not assign photoreceptor cells to columns.
`column_ids`, `start_sample` and `input_mode` identify output ordering and time.
`eye_absolute_rate_calibrated=false`, `eye_rate_ceiling_hz=null`.

The sample recurrence is a causal first-order low-pass, subtractive adaptation,
then division by `1+strength*mean_square_state`. Default sample rate 1000/s,
time constants 5/50/100 ms and strength 1 all have no biological source.
Initial states are zero; they persist until explicit `reset()`. Empty calls
preserve state; invalid inputs fail before mutation. Chunk length is only I/O.

E1 tests implementation consistency and an assignment permutation control;
biological gates unassessed. Sequential rank is not a coordinate: the legacy
`eye.py` spreads sorted body IDs at zero elevation, whereas this module retains
published p,q assignments and explicitly labels its angle convention.
No graph-drive or spike interface is provided. Network delivery is a separate
round requiring Akif's seal. See `experiments/eye_v2_e1.md` and the E1 report.
