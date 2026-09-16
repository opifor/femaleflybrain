# Dictionary E3c evidence (2026-09-17)

The single new diagnostic definition is `vpoEN-gate:AVLP083`, selecting
`^AVLP083$` in female, BANC and male graphs. It follows the E3b serialization
pattern with group `vpoen-gate`, exact annotation confidence, read-only status,
and evidence class `records/vpoen_inputs_v1_report.md`. The atlas citation is
annotation context, not functional evidence. It is not a drive target;
function is unknown. CB1614 has no new entry. All 128 preceding definitions
and the E3b top-ten union remain unchanged.

## Method and measurements

Measurements use the supplied CPython 3.12 and dependency environment.
Positive CSR `count` values are summed with presynaptic rows, without sign
cancellation. Existing JO, B1 and vpo selectors are authoritative. All cells
with the exact AVLP083 label are included. NT and sign are separate graph
annotations; no aliases or functional identities are inferred.

| Graph | Cells | L | R | NT | JO-A in | JO-B in | vpoEN out | vpoIN out | vpoDN out | B1 primary in | B1 graph in | CB1614 to vpoIN |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| female | 2 | 1 | 1 | gaba:2 | 2 | 0 | 124 | 3 | 0 | 4 | 26 | 59 |
| banc | 2 | 1 | 1 | gaba:2 | 1 | 0 | 76 | 1 | 0 | 32 | 0 | 1 |
| male | 1 | 0 | 1 | gaba:1 | 0 | 0 | 107 | 2 | 0 | 2 | 12 | 0 |

There are no midline or unknown-side AVLP083 cells in these snapshots.
All AVLP083 cells have sign -1. FAFB uses `shiu2024-parquet`; BANC and
MaleCNS use `shiu2024`, so sign provenance differs across graphs.

| Graph | CB1078 | CB1542 | SAD053 | CB1076 | CB1125 | CB2789 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| female | 1 | 2 | 1 | 26 | 0 | 0 |
| banc | 29 | 2 | 1 | 0 | 0 | 0 |
| male | 0 | 1 | 1 | 12 | 0 | 0 |

The first three columns belong to the primary B1 list; the last three belong
to the graph list. Their direct input totals are not three-edge path strengths.
The FAFB CB1614 to vpoIN observation is exactly 59 synapses, consistent with
E3b. Male CB1614 has no literal population; zero is not biological absence.

## Roadmap consistency

FAFB AVLP083 is rank 12 among direct vpoEN inputs, with 124 synapses; it stays
outside the frozen top ten. Direct totals and path strengths have different
denominators. Re-enumerating simple two-edge paths through AVLP083 reproduces
4,392 paths, summed bottlenecks 36,546 and maximum 41 in FAFB; BANC gives
4,309 paths, summed bottlenecks 20,330 and maximum 29. The measurement helper
checks all three graphs against the unchanged roadmap M2 records and hashes.
Summed bottlenecks reuse edges and are not capacity-constrained flow.

Roadmap witnesses ending `AVLP083 -> vpoEN` were checked at their original
body IDs against CSR edges, literal types and forward presynaptic signs.
In particular, `CB1206 -> AVLP083 -> vpoEN` has counts 57 and 41, signs `+-`,
and minimum 41 in FAFB. Its BANC counterpart has counts 58 and 29, signs `+-`,
and minimum 29. Full verified witnesses and cell IDs are in the measurements
JSON. No new three-edge search or drive recommendation was made.

Source attribution and population limitations follow the E3b report:
FAFB/FlyWire and Shiu et al. (2024), BANC source authors (2026), and MaleCNS
source authors, with CC-BY-4.0 source data. BANC excludes 4,344,932 synapses
under its population contract. Raw totals have unequal scopes; individual,
sex and annotation differences limit comparison. Chemical synapses only;
electrical synapses are absent. Anatomy does not predict network response.

## Reproduction and acceptance

Use the task-specified interpreter and dependencies, with repository root
on PYTHONPATH, `LC_ALL=C`, `LANG=C`, `PYTHONDONTWRITEBYTECODE=1`, and
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`:

```sh
python -m flybench.dictionary.build --data build --out build
python -B tests/fixtures/graph/generate.py --dictionary-snapshots
python -B tests/test_dictionary.py --e3c-measurements
python -m pytest -q -p no:cacheprovider tests/test_dictionary.py tests/test_vpoen_inputs.py
```

The fixture generator is unchanged. New tests cover exact selection,
near-match rejection, present and absent read-only rejection in all three
datasets, fixture population and metadata agreement, and directed unsigned
counts with asymmetric synthetic edges. The deliberate dictionary failure
probe uses `FLYBENCH_DICTIONARY_FAIL_PROBE=1` and returns exit 1 with one
failed test. The normal suite skips that opt-in probe. Suite output and
exit codes are retained in `dictionary_e3c_suite.json`. Final acceptance:
exit 0, `66 passed, 1 skipped in 48.68s`. The deliberate probe produced
`1 failed in 0.15s`, exit 1.

No experiment or biological simulation was run; the explicitly requested
acceptance suite includes its existing small simulator unit test. No git
write command was run. No restricted source tree was inspected; only the
specified runtime dependency directory was used. No environment workaround
or numerical mismatch was observed.

Formatting deviation: the unchanged Windows build writer emits CRLF.
Only the authorized build command wrote under build, so those snapshots
retain its output. Tracked fixtures and delivery files are normalized to
LF, UTF-8 without BOM. Integrity uses `hash_basis: "lf"` for text files;
graph archive hashes retain their original binary basis. Build and fixture
JSON values and LF-normalized bytes are compared. Integrity excludes its
own self-hash.
