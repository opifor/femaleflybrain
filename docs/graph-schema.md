# Graph schema v1

The graph is a compressed NumPy `.npz` archive, readable with
`numpy.load(path, allow_pickle=False)`. There are no object arrays or pickles.
`flybench.graph.load(path)` returns a mapping and decodes `meta` to a dictionary.
Rows are presynaptic; columns are postsynaptic. Neuron IDs are sorted ascending,
unique, and preserved as int64 (never routed through floating point).

| Key | dtype / shape | Meaning |
| --- | --- | --- |
| `indptr` | int32, N+1 | CSR row offsets |
| `indices` | int32, E | Sorted postsynaptic indices within each row |
| `count` | int32, E | Positive, unscaled raw synapse counts, summed per ordered pair |
| `data` | int32, E | Exactly `sign[src] * count`; explicit zero-valued edges remain |
| `body_id` | int64, N | Dataset-specific body/root IDs |
| `sign` | int8, N | +1, -1, or 0 from the recorded rule or Shiu parquet |
| `type` | Unicode string, N | Primary type; missing values become `""` |
| `side` | Unicode string, N | L, R, M, or `""`; left/right/midline normalized |
| `nt` | Unicode string, N | Normalized NT; unknown labels retained; missing becomes `""` |
| `nt_conf` | float32, N | Source confidence, when available; unavailable = NaN |
| `superclass`, `class` | Unicode string, N | Source classification, missing = `""` |
| `meta` | Unicode scalar | JSON object described below |

No weight normalization is performed. The simulator applies `w_syn` later.
Repeated ordered pairs (including FlyWire neuropil rows) are summed in int64;
overflow beyond int32 is rejected. Self-loops and isolated annotated neurons
are retained. `min_syn` is an integer >= 1, default 1, applied **after** summing
duplicates. Zero-sign edges are never eliminated because of their sign.
The population remains fixed when changing `min_syn`.

## Population contract and the raw-segment distinction

The population is explicit and independent of `min_syn`:

- MaleCNS: `body-annotations.status == "Traced"` by default. Python `status`
  accepts a string or sequence; `--status Traced Orphan` and repeated `--status`
  select multiple statuses. Missing status is not selected by default.
- FAFB `source="shiu"` (default): IDs in `Completeness_783.csv` (`Unnamed: 0`
  column), including nodes with no outgoing edges. Counts come exclusively from
  `Connectivity_783.parquet` (`Presynaptic_ID`, `Postsynaptic_ID`, `Connectivity`).
  ID columns are FlyWire root IDs, not the parquet's index columns. Codex
  neurons/classification/consolidated types supply annotations by root ID;
  missing annotations stay empty. `--shiu-data` optionally supplies a separate
  directory for the two Shiu files; otherwise they reside under `--data`.
- FAFB `source="codex"`: union of Codex annotation IDs; connections from
  `connections_princeton.csv.gz`. The real export already excludes pairs with
  fewer than five synapses. `min_syn=1` cannot restore those missing pairs.
- BANC: `proofread` OR `roughly_proofread` TRUE, excluding status strings
  containing NOT_A_NEURON, GLIA, TOO_SMALL or UNROOTED, and `super_class=glia`.
  Identity is `banc_888_id`, not a later `root_id` mapping.

Edges with either endpoint outside the selected population are dropped and
accounted for. Default `min_syn=1` retains every positive pair within it.

## NT and sign provenance

Immutable rule names and versions are recorded separately (`sign_rule_version="1"`):

| Rule | ACh | GABA | Glutamate | Dopamine / serotonin / octopamine | Other / missing |
| --- | ---: | ---: | ---: | ---: | ---: |
| `shiu2024` (default) | +1 | -1 | -1 | +1 | 0 |
| `monoamine-zero` | +1 | -1 | -1 | 0 | 0 |

The Python-only legacy alias `v1` retains the old monoamine-zero assignments.
ACH/GABA/GLUT/DA/SER/OCT abbreviations are normalized case-insensitively.
[Shiu 2024 Methods](https://www.nature.com/articles/s41586-024-07763-9)
classifies the three monoamines as excitatory. Histamine, tyramine and unclear
have no observations in the Codex/parquet join: zero is an explicit conservative
extension, **not** a parquet-verified biological assignment.

FAFB Shiu uses `shiu2024-parquet`, version 1: the `Excitatory` column directly
determines each presynaptic neuron's sign. Every outgoing row, including rows
below `min_syn`, participates in the consistency check. Conflicting signs abort
the build. Neurons without outgoing rows receive 0 and are counted explicitly.
`--sign-rule monoamine-zero` is rejected with Shiu source rather than silently
overriding its signs; select Codex to use an NT-derived alternative rule.

MaleCNS NT is `consensus_nt`; confidence is `predicted_nt_confidence` only where
the predicted and consensus labels agree (otherwise NaN). FAFB annotations use
`neurons.nt_type` / `nt_type_score`. BANC uses `neurotransmitter_predicted` /
`neurotransmitter_score`; potentially multi-NT verified labels are not substituted.

## Metadata

Required provenance: `schema_version`, `dataset`, `version`, `min_syn`,
`sign_rule`, `sign_rule_version`, `created_utc` (UTC ISO 8601), `sources` (each file's basename and
SHA-256 of its actual bytes, including gzip compression), `license`,
`population`, and `nt_policy`. There are no absolute machine paths.

Counts: `neuron_count`, `edge_count` (distinct ordered pairs), `synapse_count`,
`nt_distribution`, `type_labeled_fraction`, `input_rows`, `input_synapses`,
`outside_population_rows`, `outside_population_synapses`,
`aggregated_duplicate_rows`, `below_min_syn_edges`, `below_min_syn_synapses`.

`input_synapses = synapse_count + outside_population_synapses + below_min_syn_synapses`.
`dropped` also exposes outside-population rows/synapses and below-threshold synapses.
Dataset-specific metadata records status counts, proofreading filter counts, source
choice, unmatched Codex IDs, sign conflicts and NT/parquet sign distributions.
Counts in `nt_distribution` cover all graph nodes, including isolated nodes.
An empty-string key denotes missing NT. Type coverage is nonempty `type` / N.

`elapsed_seconds` includes input reading, SHA-256, CSR validation, compression,
and array writing; it excludes the small final JSON member append/rename.
`peak_rss_bytes` is the OS process lifetime peak working set on Windows
(peak RSS on Unix), not a Python-only allocation sample. Run each CLI in a fresh
process for comparable measurements; imports are included in memory high water.
Artifacts are atomically replaced after writing a sibling `.partial` archive.

`schema.validate(graph)` checks core dtype, CSR boundary, sign, and exact
signed-count invariants. Builders also reject duplicate annotation IDs, invalid
counts, unknown rule versions, and int32 overflow rather than silently coercing
ambiguous graphs.

## Selection

```python
from flybench.graph import load, where
g = load("build/graph_female.npz")
indices = where(g, type_re=r"^DN", side="L", superclass="descending")
body_ids = g["body_id"][indices]
```

Predicates are ANDed. Regex uses case-sensitive Python `re.search`; superclass
is an exact match. The return value contains increasing CSR indices, not IDs.
Class vocabularies differ across datasets; no cross-dataset taxonomy is invented.

## Sources and reference populations

- [MaleCNS release downloads](https://male-cns.janelia.org/download/) describes
  the weights file as the complete **segment-to-segment** graph.
  [Codex](https://codex.flywire.ai/) reports 166,700 MaleCNS neurons.
- [Dorkenwald et al. (2024)](https://doi.org/10.1038/s41586-024-07558-y):
  139,255 FAFB neurons and approximately 50 million synapses.
- [BANC publication](https://doi.org/10.1038/s41586-026-10735-w): 155,916 is
  proofread **plus roughly proofread**, not strictly proofread alone.
  The paper notes that metadata proofreading flags can postdate the snapshot.
  [BANC Codex](https://codex.flywire.ai/banc) is a living annotation resource.

All three data sources are CC-BY 4.0; cite the original data authors when
redistributing derived graphs. Filename/version labels identify the intended
input release; SHA-256 identifies the actual local export used. The builders
do not claim that a filename proves a release's authenticity.

## Tests and measured builds

Six-neuron synthetic Feather, CSV and parquet fixtures test CSR orientation,
counts, hashes, both rules, status/proofreading filters, source choice and sign
conflict rejection. Run `python -m pytest -q -p no:cacheprovider tests/test_graph.py`.
Set `FLYBENCH_GRAPH_FAIL_PROBE=1` and run only `test_harness_failure_probe` to
verify a deliberate failure returns exit 1; unset before acceptance.

### TUR-2 real-data acceptance (2026-09-16)

User-specified Windows CPython 3.12 and library-only PYTHONPATH; fresh process
per builder, min_syn=1, no alternate-environment workaround. NPZ files and
metadata are in `build/graph_{male,female,banc}.npz` and `build/*-tur2.json`.

| Dataset | Neurons | Edges | Synapses | Typed | Seconds | Peak working set GiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| male | 165,122 | 25,563,197 | 124,025,046 | 98.4224% | 35.99 | 5.065 |
| female | 138,639 | 15,091,983 | 54,492,922 | 99.3667% | 14.74 | 0.747 |
| banc | 137,791 | 12,260,970 | 37,964,689 | 75.7118% | 11.72 | 1.237 |

| NT | MaleCNS | FAFB Shiu | BANC |
| --- | ---: | ---: | ---: |
| missing | 502 | 19,042 | 3,639 |
| acetylcholine | 103,718 | 82,298 | 77,174 |
| dopamine | 392 | 584 | 7,688 |
| gaba | 22,055 | 16,017 | 20,184 |
| glutamate | 29,296 | 19,605 | 21,866 |
| histamine | 5,910 | 0 | 3,522 |
| octopamine | 101 | 72 | 1,968 |
| serotonin | 48 | 1,021 | 1,540 |
| tyramine | 0 | 0 | 210 |
| unclear | 3,100 | 0 | 0 |

MaleCNS status counts: Traced 165,122; Orphan 15,925; Glia 11,864;
Unimportant 10,751; missing 5,472; Assign 1,832; Anchor 611. Traced selection
is 1,578 below the 166,700 Codex reference. Dropped: 126,293,487 raw rows /
187,808,197 synapses, including unannotated segments and non-Traced bodies.

FAFB Shiu: 15,091,983 input rows, minimum count 1; all 54,492,922 synapses retained.
138,639 completeness IDs are 616 below the 139,255 FAFB reference; synapses are
4,492,922 above the rounded 50M reference (the paper also reports 54.5M).
No unmatched Codex neuron IDs, no inconsistent presynaptic signs; 634 nodes have
no outgoing sign evidence and receive 0. Nonempty type coverage differs from
ID matching: matched IDs can have missing labels.

BANC: 150,952 proofread + 5,060 roughly proofread = 156,012 union IDs.
The requested exclusions remove 18,221 union IDs, leaving 137,791, which is
18,125 below the paper's 155,916. The unfiltered union is 96 above the paper.
These are different selection contracts; the target is not forced by relaxing
the requested filter. Dropped: 1,359,895 rows / 4,344,932 synapses.
Within the union, overlapping exclusion-reason counts are UNROOTED 17,515,
TOO_SMALL 816, NOT_A_NEURON 107, GLIA 101 and glia superclass 146.
Codex contains 5,342,446 neuropil rows (minimum row count 1), but its
3,732,460 aggregated ordered pairs have minimum count 5: the upstream
threshold applies to pairs, not individual neuropil rows.

### Codex NT versus Shiu parquet signs (unique presynaptic neurons)

| Codex NT | +1 | -1 |
| --- | ---: | ---: |
| acetylcholine | 82,067 | 231 |
| gaba | 43 | 15,974 |
| glutamate | 199 | 19,406 |
| dopamine | 584 | 0 |
| serotonin | 1,021 | 0 |
| octopamine | 72 | 0 |
| histamine | 0 | 0 |
| tyramine | 0 | 0 |
| unclear | 0 | 0 |
| missing | 12,686 | 5,722 |

Zero observations for histamine/tyramine/unclear provide no sign evidence.
473 ACh/GABA/glutamate labels disagree with the simple NT rule; parquet signs
are retained exactly. The current Codex labels need not reproduce the older
per-synapse prediction procedure used by Shiu.

Acceptance: `38 passed in 2.09s`, exit 0; deliberate probe `1 failed in 0.52s`, exit 1.
Only the allowed data files were read outside this repository; no external
project code, add/commit/push, or simulation-lane edits were used.
