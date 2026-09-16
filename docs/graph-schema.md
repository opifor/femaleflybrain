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
| `sign` | int8, N | +1, -1, or 0 from presynaptic NT and rule v1 |
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

These builders produce induced graphs on the supplied annotation populations:

- MaleCNS: all `body-annotations.feather.bodyId` values; no status/type filter.
- FAFB: union of IDs in neurons, classification, and consolidated cell types.
- BANC: all `banc_888_meta.feather.banc_888_id` values; no proofread filter.
  `root_id` can refer to a later segmentation; it is deliberately not the key.

`min_syn=1` removes no connection **within this population**. It does not claim
that every raw segment is a neuron. The supplied MaleCNS full segment graph has
88,384,522 endpoint IDs versus 211,577 annotation IDs. Including all segments
would be a different graph. Edges with either endpoint outside the annotation
population are excluded and explicitly counted in metadata. This is a scope
decision, not a synapse threshold; it is a deviation if “no edge removal” means
all raw segments. No such outside-population edges were found in the supplied
FAFB and BANC inputs. Official published neuron totals refer to more curated
populations and must not be compared as if the selection criteria were identical.

Inputs are not silently supplemented from other versions or comparisons.
`min_syn=1` cannot recover connections already absent from an upstream export.

## NT and sign provenance

Rule name `v1` is immutable: acetylcholine +1; GABA and glutamate -1;
dopamine, serotonin, octopamine, other/unknown/missing labels 0. ACH, GABA, GLUT,
DA, SER, OCT abbreviations are normalized case-insensitively. Histamine,
tyramine and unclear retain their labels and receive 0.

[Shiu et al. (2024)](https://doi.org/10.1038/s41586-024-07763-9) supports the
inhibitory GABA/glutamate assumption. **The requested v1 policy differs from
that paper:** the paper treats dopamine, serotonin and octopamine as excitatory;
flybench deliberately assigns 0. Thus v1 is not an exact reproduction of the
paper's complete NT rule. Any changed assignment requires a new rule version.

- MaleCNS uses `consensus_nt`. `predicted_nt_confidence` is retained only when
  `predicted_nt == consensus_nt`; it is not presented as confidence in a
  different consensus label. Otherwise confidence is NaN.
- FAFB uses `neurons.nt_type` and `nt_type_score`, not the NT column repeated
  across connections. This also supports neurons without outgoing edges.
- BANC uses `neurotransmitter_predicted` and `neurotransmitter_score`.
  `neurotransmitter_verified` is not substituted: it can contain multi-NT labels.

## Metadata

Required provenance: `schema_version`, `dataset`, `version`, `min_syn`,
`sign_rule`, `created_utc` (UTC ISO 8601), `sources` (each file's basename and
SHA-256 of its actual bytes, including gzip compression), `license`,
`population`, and `nt_policy`. There are no absolute machine paths.

Counts: `neuron_count`, `edge_count` (distinct ordered pairs), `synapse_count`,
`nt_distribution`, `type_labeled_fraction`, `input_rows`, `input_synapses`,
`outside_population_rows`, `outside_population_synapses`,
`aggregated_duplicate_rows`, `below_min_syn_edges`, `below_min_syn_synapses`.

`input_synapses = synapse_count + outside_population_synapses + below_min_syn_synapses`.
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

Synthetic fixtures are six-neuron tables under `tests/fixtures/graph/`, with a
seventh, deliberately out-of-population edge endpoint to test accounting. The
sixth neuron is isolated. The fixture generator reads no external data. Feather
and gzip CSV exercise the three builders; a tiny parquet holds independently
specified expected pairs in the Shiu comparison schema.

Run `python -m pytest -q -p no:cacheprovider tests/test_graph.py`. To test failure
propagation, set `FLYBENCH_GRAPH_FAIL_PROBE=1` and run only
`tests/test_graph.py::test_harness_failure_probe`; require both `1 failed` and
exit code 1, then unset the variable before acceptance.

Real builds are separate commands documented in README. This lane's measured
artifacts and independent comparison evidence are in gitignored `build/`.

### Real-data acceptance record (2026-09-16)

User-specified Windows CPython 3.12, with the specified library-only PYTHONPATH;
fresh process per builder, `min_syn=1`. No sandbox or alternate-environment
workaround was used. The output archives were reopened and checked independently.

| Output | Annotation IDs | Edges | Synapses | Typed | Seconds | Peak working set GiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `build/graph_male.npz` | 211,577 | 26,028,386 | 125,365,933 | 77.7523% | 58.16 | 5.071 |
| `build/graph_female.npz` | 139,255 | 3,732,460 | 50,666,648 | 99.3336% | 9.56 | 0.342 |
| `build/graph_banc.npz` | 188,508 | 13,620,865 | 42,309,621 | 62.9936% | 17.16 | 1.291 |

NT distributions (counts of annotation IDs, not synapses):

| NT | MaleCNS | FAFB | BANC |
| --- | ---: | ---: | ---: |
| acetylcholine | 104,173 | 82,298 | 87,059 |
| gaba | 22,186 | 16,017 | 21,686 |
| glutamate | 29,443 | 19,605 | 25,099 |
| dopamine | 396 | 584 | 8,344 |
| serotonin | 48 | 1,021 | 1,936 |
| octopamine | 101 | 72 | 2,303 |
| histamine | 8,024 | 0 | 7,411 |
| tyramine | 0 | 0 | 215 |
| unclear | 22,645 | 0 | 0 |
| missing | 24,561 | 19,658 | 34,455 |

Reference differences and limitations:

- MaleCNS: +44,877 IDs against the 166,700-neuron reference; this graph retains
  every annotation, including glia and non-Traced statuses. The supplied status
  column contains 165,122 `Traced` records. Of 151,856,684 raw rows / 311,833,243
  synapses, 125,828,298 rows / 186,467,310 synapses have an endpoint outside the
  annotation universe. They are explicitly excluded, so this is **partial
  evidence for the literal all-segments/no-edge-removal requirement**.
- FAFB: the neuron total exactly matches 139,255; synapses exceed the rounded
  50-million reference by 666,648 (1.33%). No input synapses were discarded.
  The minimum resulting pair count is 5 despite builder `min_syn=1`; the
  supplied export therefore does not demonstrate retention of counts 1–4.
- BANC: +32,592 annotation IDs against the published 155,916 proofread-plus-
  roughly-proofread reference; this graph intentionally has no proofread filter.
  The local metadata has 150,952 `proofread=TRUE` rows; it is not identical to
  the paper's strict snapshot definition. The union of local `proofread=TRUE`
  and `roughly_proofread=TRUE` has 156,012 IDs (+96 against the publication).
  No input synapses were discarded.

The independent Shiu comparison parquet contains 138,639 endpoint IDs,
15,091,983 pairs and 54,492,922 synapses (minimum count 1). Its completeness
file has 138,639 rows, all marked completed. Against the supplied Codex export:
3,667,935 shared pairs, 11,424,048 Shiu-only pairs, 64,525 Codex-only pairs;
3,275,348 shared pairs have different counts. The sources are not interchangeable
and were not merged or silently substituted. Source hashes, output hashes, and
exact audit results are in `build/graph-audit.json`; the per-build metadata is
also embedded in each NPZ and copied to `build/{male,female,banc}-stdout.json`.

Synthetic acceptance: `26 passed in 1.53s`, exit 0. Deliberate failure probe:
`1 failed in 0.60s`, exit 1. UTF-8/BOM, scope and clean-room read-file evidence:
`build/graph-delivery-checks.json`. No add, commit, or push was run. The parallel
simulation lane's files and README section were not edited by this lane.
