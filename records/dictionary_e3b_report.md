# Dictionary E3b evidence (2026-09-17)

Eleven read-only diagnostic definitions follow the FAFB vpoEN direct-input
top ten in [vpoen_inputs_v1](vpoen_inputs_v1_report.md). Their group is
`vpoen-input`, confidence is `exact`, and evidence_class names that record.
The atlas source link supplies annotation context only. Exact refers to
literal annotation selection, not established function or drive suitability.
Every new entry says: "anatomical input rank in vpoen_inputs_v1; not a drive
target; function unknown". No experiment or biological simulation was run;
the requested pytest suite retains its existing small simulator unit tests.

## Method and provenance

All three supplied graph archives were measured in the task-specified Python
3.12 environment and dependency directory, without an environment workaround.
CSR rows are presynaptic; direct synapses sum positive `count`, never signed
`data`. JO-A/JO-B and vpoEN/vpoIN/vpoDN use the unchanged dictionary selectors.
All literal-type cells are selected, not only those connected to vpoEN.
The union deduplicates cells; its rows overlap the individual entries.
Empty-string NT or side labels are missing annotations. Absent means no
literal label in the snapshot, not biological absence. No aliases were added.

Cell sign comes directly from the graph `sign` array. FAFB sign_rule is
`shiu2024-parquet`; BANC and MaleCNS use `shiu2024`. Sign is a presynaptic
cell property (`data = sign[src] * count`), not inferred from NT or an
individual strongest-path witness. Sign distributions count cells; the JSON
also retains outgoing vpoEN synapses split by source sign without cancellation.
These graphs have different sign sources and population scopes, so their
sign distributions and raw totals are not like-for-like physiological evidence.
BANC excludes 4,344,932 synapses under its population contract. Chemical
synapses only; electrical synapses are absent. Anatomy does not predict response.

Source attribution: FAFB/FlyWire and Shiu et al. (2024), BANC source authors
(2026), and MaleCNS source authors; source data are CC-BY-4.0. Original source
metadata remains in the refreshed dictionary snapshots.

## A2 coverage and cross-dataset labels

The existing `A2-candidate` regex is exactly `^CB1817[ab]$` in all datasets.
It includes both CB1817a and CB1817b (FAFB two of each, BANC one of each;
MaleCNS neither). No new A2-candidate-path entry was added. Its unresolved
functional identity and read-only status remain unchanged.

M6's M1_top20 shared list contains six of the requested ten types: CB2364,
CB1383, WED104, PVLP021, CB2449 and CB1614. CB2633 also exists in BANC but
is below its top twenty (M1 rank 39 including unnamed types). CB1484,
AN_AVLP_8 and CB1869 have no literal BANC match. M6 rank overlap alone is
not an absence test; these statements were checked against the graph.
MaleCNS contains WED104, CB2633 and PVLP021; the other seven labels are absent.

## Measurements

In the tables, every population except the existing A2-candidate is newly
defined. The ten individual names use the prefix `vpoEN-input:`. Counts,
sides, NT and sign distributions describe all selected cells. A count of
zero has explicit status `absent` in the measurements JSON and snapshots.

| Population | Graph | Count | L | R | M | Unknown | JO-A input | JO-B input | vpoEN output | vpoIN output | vpoDN output |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vpoEN-input:CB1484 | female | 6 | 3 | 3 | 0 | 0 | 23 | 29 | 704 | 1 | 0 |
| vpoEN-input:CB2364 | female | 8 | 4 | 4 | 0 | 0 | 44 | 8 | 563 | 34 | 0 |
| vpoEN-input:CB1383 | female | 6 | 3 | 3 | 0 | 0 | 0 | 1 | 321 | 0 | 0 |
| vpoEN-input:WED104 | female | 2 | 1 | 1 | 0 | 0 | 1 | 3 | 297 | 0 | 0 |
| vpoEN-input:AN_AVLP_8 | female | 2 | 1 | 1 | 0 | 0 | 4 | 0 | 288 | 1 | 0 |
| vpoEN-input:CB2633 | female | 4 | 2 | 2 | 0 | 0 | 0 | 0 | 278 | 3 | 0 |
| vpoEN-input:PVLP021 | female | 4 | 2 | 2 | 0 | 0 | 8 | 10 | 215 | 0 | 0 |
| vpoEN-input:CB1869 | female | 3 | 2 | 1 | 0 | 0 | 17 | 7 | 184 | 1 | 0 |
| vpoEN-input:CB2449 | female | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 140 | 3 | 0 |
| vpoEN-input:CB1614 | female | 2 | 1 | 1 | 0 | 0 | 17 | 0 | 139 | 59 | 0 |
| vpoEN-input-top10 | female | 43 | 23 | 20 | 0 | 0 | 114 | 58 | 3129 | 102 | 0 |
| A2-candidate | female | 4 | 2 | 2 | 0 | 0 | 266 | 0 | 19 | 0 | 0 |
| vpoEN-input:CB1484 | banc | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| vpoEN-input:CB2364 | banc | 8 | 3 | 5 | 0 | 0 | 93 | 0 | 335 | 10 | 0 |
| vpoEN-input:CB1383 | banc | 4 | 2 | 2 | 0 | 0 | 0 | 8 | 92 | 0 | 0 |
| vpoEN-input:WED104 | banc | 1 | 1 | 0 | 0 | 0 | 4 | 1 | 78 | 0 | 0 |
| vpoEN-input:AN_AVLP_8 | banc | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| vpoEN-input:CB2633 | banc | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 21 | 0 | 0 |
| vpoEN-input:PVLP021 | banc | 4 | 2 | 2 | 0 | 0 | 16 | 22 | 55 | 0 | 0 |
| vpoEN-input:CB1869 | banc | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| vpoEN-input:CB2449 | banc | 7 | 5 | 2 | 0 | 0 | 3 | 0 | 62 | 0 | 0 |
| vpoEN-input:CB1614 | banc | 5 | 4 | 1 | 0 | 0 | 1 | 0 | 81 | 1 | 0 |
| vpoEN-input-top10 | banc | 31 | 17 | 14 | 0 | 0 | 117 | 31 | 724 | 11 | 0 |
| A2-candidate | banc | 2 | 0 | 2 | 0 | 0 | 1104 | 4 | 5 | 0 | 0 |
| vpoEN-input:CB1484 | male | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| vpoEN-input:CB2364 | male | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| vpoEN-input:CB1383 | male | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| vpoEN-input:WED104 | male | 2 | 1 | 1 | 0 | 0 | 18 | 12 | 571 | 2 | 0 |
| vpoEN-input:AN_AVLP_8 | male | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| vpoEN-input:CB2633 | male | 4 | 2 | 2 | 0 | 0 | 0 | 3 | 268 | 2 | 0 |
| vpoEN-input:PVLP021 | male | 4 | 2 | 2 | 0 | 0 | 35 | 1 | 315 | 0 | 0 |
| vpoEN-input:CB1869 | male | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| vpoEN-input:CB2449 | male | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| vpoEN-input:CB1614 | male | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| vpoEN-input-top10 | male | 10 | 5 | 5 | 0 | 0 | 53 | 16 | 1154 | 4 | 0 |
| A2-candidate | male | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

| Population | Graph | NT:cells | Sign:cells |
| --- | --- | --- | --- |
| vpoEN-input:CB1484 | female | {"acetylcholine": 6} | {"1": 6} |
| vpoEN-input:CB2364 | female | {"gaba": 8} | {"-1": 8} |
| vpoEN-input:CB1383 | female | {"gaba": 6} | {"-1": 6} |
| vpoEN-input:WED104 | female | {"gaba": 2} | {"-1": 2} |
| vpoEN-input:AN_AVLP_8 | female | {"gaba": 2} | {"-1": 2} |
| vpoEN-input:CB2633 | female | {"acetylcholine": 4} | {"1": 4} |
| vpoEN-input:PVLP021 | female | {"gaba": 4} | {"-1": 4} |
| vpoEN-input:CB1869 | female | {"acetylcholine": 3} | {"1": 3} |
| vpoEN-input:CB2449 | female | {"acetylcholine": 6} | {"1": 6} |
| vpoEN-input:CB1614 | female | {"gaba": 2} | {"-1": 2} |
| vpoEN-input-top10 | female | {"acetylcholine": 19, "gaba": 24} | {"-1": 24, "1": 19} |
| A2-candidate | female | {"acetylcholine": 4} | {"1": 4} |
| vpoEN-input:CB1484 | banc | {} | {} |
| vpoEN-input:CB2364 | banc | {"gaba": 8} | {"-1": 8} |
| vpoEN-input:CB1383 | banc | {"gaba": 4} | {"-1": 4} |
| vpoEN-input:WED104 | banc | {"gaba": 1} | {"-1": 1} |
| vpoEN-input:AN_AVLP_8 | banc | {} | {} |
| vpoEN-input:CB2633 | banc | {"acetylcholine": 2} | {"1": 2} |
| vpoEN-input:PVLP021 | banc | {"gaba": 4} | {"-1": 4} |
| vpoEN-input:CB1869 | banc | {} | {} |
| vpoEN-input:CB2449 | banc | {"acetylcholine": 7} | {"1": 7} |
| vpoEN-input:CB1614 | banc | {"gaba": 5} | {"-1": 5} |
| vpoEN-input-top10 | banc | {"acetylcholine": 9, "gaba": 22} | {"-1": 22, "1": 9} |
| A2-candidate | banc | {"acetylcholine": 2} | {"1": 2} |
| vpoEN-input:CB1484 | male | {} | {} |
| vpoEN-input:CB2364 | male | {} | {} |
| vpoEN-input:CB1383 | male | {} | {} |
| vpoEN-input:WED104 | male | {"gaba": 2} | {"-1": 2} |
| vpoEN-input:AN_AVLP_8 | male | {} | {} |
| vpoEN-input:CB2633 | male | {"acetylcholine": 4} | {"1": 4} |
| vpoEN-input:PVLP021 | male | {"gaba": 4} | {"-1": 4} |
| vpoEN-input:CB1869 | male | {} | {} |
| vpoEN-input:CB2449 | male | {} | {} |
| vpoEN-input:CB1614 | male | {} | {} |
| vpoEN-input-top10 | male | {"acetylcholine": 4, "gaba": 6} | {"-1": 6, "1": 4} |
| A2-candidate | male | {} | {} |

## Roadmap consistency

All 10 supplied FAFB direct vpoEN synapse counts match exactly: 704, 563,
321, 297, 288, 278, 215, 184, 140 and 139 in the fixed rank order. Their
union contributes 3,129 synapses; BANC contributes 724 and MaleCNS 1,154.
All 90 direct-output comparisons (10 types x 3 targets x 3 datasets) against
the complete vpoen_inputs_v1_results.json M1 tables match, treating a type
with no M1 row as zero input synapses. No expected value was revised.

The M1 cell column counts contributing cells, whereas dictionary membership
counts every matching cell. In BANC, CB2364 has 8 selected versus 7 contributing,
CB1383 has 4 versus 3, and CB1614 has 5 versus 4. This is a denominator
difference, not a changed roadmap value. The strongest JO path reported by
the roadmap (JO-A -> CB1817a -> CB2364 -> vpoEN) motivates retaining the
existing A2 diagnostic population; no new path search or drive inference
was needed for this dictionary task.

## Reproduction and acceptance

Run with the task-specified CPython and dependency environment, repository
root on PYTHONPATH, LC_ALL=C and LANG=C, PYTHONDONTWRITEBYTECODE=1 and
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1:

```sh
python -m flybench.dictionary.build --data build --out build
python -B tests/fixtures/graph/generate.py --dictionary-snapshots
python -B tests/test_dictionary.py --e3b-measurements
python -m pytest -q -p no:cacheprovider tests/test_dictionary.py tests/test_direction_probe.py tests/test_vpoen_inputs.py
```

The build and fixture generator both completed with exit 0. Only dictionary
snapshot outputs were written under build. The existing fixture generator
was used unchanged. New synthetic tests check exact labels, duplicate-cell
union membership, near-match rejection, metadata, all three definitions,
present/absent drive rejection and directed positive-count measurement.
Real-graph tests compare snapshot metadata and the ten frozen FAFB values.
The deliberate failing probe returned exit 1 and `1 failed in 0.13s`.
The initial suite exposed four missing-metadata errors in the new synthetic
fixture; adding its required superclass/class/NT columns resolved them.
The initial output is retained alongside the final run in the suite JSON.
Final acceptance: exit 0; `74 passed, 1 skipped in 36.80s`. The single skip
is the opt-in deliberate-failure test, which was executed separately above.

Graph, source and snapshot hashes, unchanged existing entry comparisons,
UTF-8/LF checks and numeric comparisons are in dictionary_e3b_integrity.json.
No restricted source tree was inspected. No git write command was run.
All existing definitions, including B1 lists, A2-candidate, vpoIN and SAG,
are preserved. README is unchanged. No environment deviation or numerical
mismatch was observed.

Formatting deviation: the unchanged Windows snapshot writer emits CRLF.
Tracked fixture snapshots were normalized to LF without changing JSON values;
the gitignored build snapshots retain the command's CRLF output because only
the specified build command is authorized to write there. All tracked delivery
files are UTF-8 without BOM and use LF. Build and fixture JSON values are equal;
their byte hashes differ solely due to line endings.
