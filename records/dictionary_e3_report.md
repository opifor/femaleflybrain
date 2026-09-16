# Dictionary E3 evidence (2026-09-16)

Graph measurements use positive CSR `count` values; rows are presynaptic.
No simulation, experiment, ear or hook implementation was changed.
Reproduce with `python -B build/records-raw/dictionary_e3/dictionary_e3_measure.py` using the
task-specified Python 3.12 interpreter and dependency PYTHONPATH.
No restricted source tree was inspected; only the explicitly supplied
dependency directory is used by the Python runtime. No git writes were run.

## Snapshot identity

| Dataset | File | SHA-256 |
| --- | --- | --- |
| female | graph_female.npz | `35e5c3b4cca86b27392a144a4d6bcb37de2f3f97f29d71f5c0a5c20b1cd593b8` |
| banc | graph_banc.npz | `e403ff72a0666d4335f77a2cb03ddb3ce94159dc2f681cd41384fb9c5e965e49` |
| male | graph_male.npz | `6afa6161b593b03cfa0f6027b697d5b1ff37afa5028c870f8012122f87d03a3d` |

## Selectors and counts

| Population | Selector | FAFB v783 | BANC v888 | MaleCNS v1.0 | Evidence class |
| --- | --- | ---: | ---: | ---: | --- |
| AMMC-B1-candidate | `^(?:CB1078&#124;CB1542&#124;SAD053)$` | 39 | 38 | 12 | annotation crosswalk, external report, REPORTED |
| AMMC-B1-candidate-graph | `^(?:CB1076&#124;CB1125&#124;CB2789)$` | 23 | 26 | 11 | graph connectivity, lane k2 |
| A2-candidate | `^CB1817[ab]$` | 4 | 2 | 0 | graph connectivity, lane k2 |
| vpoIN | `^CB1385$ (female/BANC); ^vpoIN$ (male)` | 6 | 4 | 5 | annotation crosswalk, external report, REPORTED |
| vpoDN-GABA-input | `^AVLP008$` | 10 | 8 | 0 | graph connectivity, lane k2 |
| aLN-m | `^CB3880$ (female/BANC); ^WED191$ (male)` | 2 | 2 | 2 | annotation crosswalk, external report, REPORTED |

| Population | Graph | Count | L | R | M | Unknown | JO-A input synapses | JO-B input synapses |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| AMMC-B1-candidate | female | 39 | 20 | 19 | 0 | 0 | 1 | 649 |
| AMMC-B1-candidate | banc | 38 | 21 | 17 | 0 | 0 | 95 | 3102 |
| AMMC-B1-candidate | male | 12 | 6 | 6 | 0 | 0 | 1 | 795 |
| AMMC-B1-candidate-graph | female | 23 | 11 | 12 | 0 | 0 | 4 | 889 |
| AMMC-B1-candidate-graph | banc | 26 | 13 | 13 | 0 | 0 | 0 | 606 |
| AMMC-B1-candidate-graph | male | 11 | 6 | 5 | 0 | 0 | 0 | 970 |
| A2-candidate | female | 4 | 2 | 2 | 0 | 0 | 266 | 0 |
| A2-candidate | banc | 2 | 0 | 2 | 0 | 0 | 1104 | 4 |
| A2-candidate | male | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| vpoIN | female | 6 | 3 | 3 | 0 | 0 | 0 | 0 |
| vpoIN | banc | 4 | 2 | 2 | 0 | 0 | 0 | 0 |
| vpoIN | male | 5 | 2 | 3 | 0 | 0 | 0 | 0 |
| vpoDN-GABA-input | female | 10 | 5 | 5 | 0 | 0 | 0 | 0 |
| vpoDN-GABA-input | banc | 8 | 4 | 4 | 0 | 0 | 0 | 0 |
| vpoDN-GABA-input | male | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| aLN-m | female | 2 | 0 | 0 | 2 | 0 | 1 | 51 |
| aLN-m | banc | 2 | 1 | 1 | 0 | 0 | 0 | 45 |
| aLN-m | male | 2 | 0 | 0 | 2 | 0 | 0 | 21 |

## Two-edge bottlenecks

For each simple directed cell path u -> m -> t (three distinct cells),
the bottleneck is min(count[u,m], count[m,t]); report the maximum over
all such paths. This is neither summed flow nor physiological efficacy.
No NT/sign filter is applied. Zero means no eligible path. Ties choose
the lexicographically greatest numeric body-ID tuple. Two interpretations
are retained: candidate -> any intermediate -> vpoEN, and JO-A/B ->
candidate -> vpoEN. Exact witnesses and path counts are in the JSON.

| Graph | B1 list | Candidate -> middle -> vpoEN | JO -> candidate -> vpoEN | Direct candidate -> vpoEN synapses |
| --- | --- | ---: | ---: | ---: |
| female | AMMC-B1-candidate | 44 | 3 | 16 |
| female | AMMC-B1-candidate-graph | 29 | 0 | 0 |
| banc | AMMC-B1-candidate | 34 | 3 | 27 |
| banc | AMMC-B1-candidate-graph | 14 | 2 | 5 |
| male | AMMC-B1-candidate | 43 | 4 | 9 |
| male | AMMC-B1-candidate-graph | 33 | 5 | 17 |

## CB1076 versus CB1078 target overlap

Rank target types by summed outgoing positive synapses across all source
cells of each type. Exclude unnamed target types; retain self-types.
Sort ties by Unicode code-point type name, take exactly 20, intersect
the type sets. Full rankings and weights are in the measurements JSON.

| Graph | Shared top-20 types | Count |
| --- | --- | ---: |
| female | CB1383 | 1 |
| banc | AN01A055, CB1948, SAD021_c | 3 |
| male | WED055_b | 1 |

## Verified claims and limitations

- Primary B1 brief counts 39/38/12 and secondary brief counts 23/26 match.
  Male secondary 11 is an observation, not a supplied acceptance value.
- FAFB CB1078=26 and CB1542=11, total 37 (L19/R18), match the report.
  Adding SAD053 gives 39 (L20/R19). Original external root IDs were not
  supplied, so their mapping to SAD053 could not be independently checked.
  The two selected FAFB SAD053 cells are acetylcholine-labelled, with
  JO-A input 0 and JO-B input 244 synapses, confirming that graph signature.
- All three B1 intersections are empty; the two lists remain separate.
- A2 counts 4 FAFB and 2 BANC match; BANC has one CB1817a and one CB1817b,
  both R. Male count is 0; literal AMMC-A2 is absent in all three graphs.
- Legacy ^vpoIN$ is absent in FAFB/BANC. CB1385 is 6 (L3/R3) in FAFB,
  4 (L2/R2) in BANC, and absent in MaleCNS. The reported six is not a
  cross-dataset constant. D1 retains five male literal vpoIN cells (L2/R3).
- FAFB AVLP008 -> DNp37=265 and -> pC1 family (^pC1)=237 match the report.
  BANC values are 93 and 94; male values are zero. FAFB AVLP008 has seven
  GABA and three unknown NT annotations; a uniform GABA label is unverified.
- aLN-m has two GABA cells in every graph: CB3880 female/BANC, WED191 male.
  Female and male sides are M/M; BANC sides are L/R. Homology is REPORTED.
- vPN1 report types have 11 male cells (4/5/2 by AVLP761m/762m/763m),
  L6/R5, and zero female/BANC cells. No unrequested dictionary key was added.
- FAFB top-20 overlap is exactly one type, CB1383, as reported. This does
  not prove absence of all possible forms of connectivity similarity.
- All supplied numeric expectations are preserved. Unspecified counts
  have separately labelled observed regression constants in the tests.
  D1 explicitly expects vpoIN counts 6/4/5; all match.

## Acceptance and handoff

- probe: exit 1; 1 failed in 0.13s.
- suite: exit 0; 294 passed, 18 skipped, 3 xfailed, 1 warning in 87.83s (0:01:27).
- The same task-specified Python 3.12 interpreter and dependency directory were used.
  The repository root is prepended to PYTHONPATH for direct script imports.
  LC_ALL=C and LANG=C; external pytest plugin autoload, bytecode and cache disabled.
  Combined stdout/stderr and exit codes are retained under build/records-raw/dictionary_e3/.
- Regenerate snapshots: `python -B tests/fixtures/graph/generate.py --dictionary-snapshots`.
  Generated dictionary JSON lives in tests/fixtures/graph/; existing build exports remain unchanged.
  Snapshot SHA-256 hashes and generator identity are in dictionary_e3_integrity.json.
- A2 drive rejection passes for present and absent populations in all datasets.
  Existing keys are retained; only female/BANC vpoIN selectors change from HEAD.
- No supplied acceptance count was replaced by an observation. Skips/xfails are not passes.
- Original report root IDs remain unavailable; biological crosswalk identity is REPORTED.
