# Cell dictionary

The dictionary answers which graph rows belong to a named input, readout,
motor, state or modulatory population. Names describe source annotations;
functional evidence comes from the linked literature. Dataset keys are `male`
(MaleCNS v1.0), `female` (FAFB v783 Shiu population), and `banc` (BANC v888).
Counts describe the Phase 2 graph populations, not a complete biological census.

## Build and use

```sh
python -m flybench.dictionary.build --data build --out build
```

This creates `build/dictionary_{male,female,banc}.json`. Every entry contains
`name`, `dataset`, `selector`, `count`, `role`, `literature`, `confidence`,
`notes`, `source`, `status`, the first five body IDs, side and NT distributions,
and counts by matched source type. The report also records the exact graph
SHA-256 and its source metadata. Empty-string distribution keys mean missing
annotations. Body IDs remain integers; the API returns indices instead.

```python
from flybench.graph.schema import load
from flybench.dictionary import groups, drive_targets

graph = load("build/graph_female.npz")
readouts = groups("female", graph=graph)  # Simulator(..., groups=readouts)
targets = drive_targets("female", "JO-A", graph=graph)  # Drive(targets, 100)
```

Without `graph=`, the API loads `graph_<dataset>.npz` from `data_dir=`, otherwise
`FLYBENCH_DATA`, otherwise the current directory's `build/`. For this package,
`FLYBENCH_DATA` points to the directory of built graphs. The graph builders use
that variable for raw input instead; pass an explicit directory when switching.
There are no embedded machine paths. Reuse the same graph in the simulator and
dictionary: indices from another snapshot are not interchangeable. Calls do not
cache graphs. Groups overlap, especially ORN subtypes and receptor proxies.

`groups` retains absent groups as empty int64 arrays. `drive_targets` raises
`ValueError` for absent groups or read-only diagnostic populations and
`KeyError` for unknown names. Other groups support perturbation experiments.
Missing graph files and required
annotation columns raise errors rather than becoming silent empty results.

## Matching contract and limitations

`flybench.graph.select.where` evaluates anchored, case-sensitive type regexes,
side and exact superclass with AND semantics. Exact NT and class postfilters
extend that operation because the graph selector does not expose them. The
serialized selector always lists all five fields; null means unrestricted.
Counts include both sides and unknown side unless a side filter is supplied.

- `exact` means a literal type, explicit alias or stated label match, not
  causal proof of the assigned behavioural role.
- `family` pools named subtypes; it need not reproduce a genetic driver.
- `proxy` uses an indirect or incompletely established identity.
- `absent` means zero matching annotations in this graph, not absence from
  the animal. Brain-only FAFB cannot establish a VNC motor census.

MaleCNS has no `P1_*` primary types in this snapshot. The P1 proxy is a frozen
13-type subset of `pC1_*`: official `fruDsx=coexpress_high` and
`dimorphism=male-specific`. It contains **46 cells**. Lower coexpression,
potentially male-specific, dsx-only, pC1x and ambiguous `pC1_2a/2b` cells are
excluded. This is not a P1a driver identity. The raw official annotation join,
source hash and per-type counts are in `build/dictionary_annotation_evidence.json`;
`build/verify_dictionary_annotations.py` reproduces it with `FLYBENCH_DATA`
pointing to the directory containing `body-annotations.feather`. The graphs
themselves do not retain fruDsx/dimorphism, so this is a snapshot-specific
annotation-derived allowlist, not a runtime genetic filter. The source is the
[official MaleCNS annotation release](https://male-cns.janelia.org/download/).

Or47b and Or67d use ORN_VA1v and ORN_DA1 glomerular proxies. The separate
`Or*` entry requires literal receptor-labelled types and is absent here. The
ORN family includes non-Or olfactory classes; individual ORN entries do not
claim receptor expression. `D_ORN` is excluded rather than silently reinterpreted.

FAFB SAG uses the requested `SpsP` candidate proxy (7 cells), without claiming
cell-for-cell SAG identity. BANC uses the published ANXXX983 alias (2 cells).
Male SpsP is not presumed SAG. The corresponding
[BANC analysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC13518251/)
identifies ANXXX983 as SAG and links it to reproductive-tract state.

Male `wing_motor` is a finite named steering/power MN subset because its graph
has no wing-motor class. BANC instead uses `class=wing_motor_neuron` AND
`superclass=motor`. Named ps1/i1/iii1/b3 entries use motor superclass to avoid
unrelated brain types; BANC spells ps1 `PS1`. This family is not a song-only
motor population. Serotonin and octopamine are NT-label proxies with no added
confidence threshold. Octopamine is not the complete Tdc2 population because
Tdc2 also labels tyraminergic neurons.

JO-A/B excludes `-unclear`; LC10c includes its -1/-2 subtypes but not unclassified
LC10. TN1A pools TN1a subtypes but excludes TN1c. MBON excludes `-like` and
comma-joined ambiguous labels, including BANC `MBON25,MBON34`. The mAL type
family is broader than functional mAL drivers. aIPg and female homologues of
song-related types do not inherit male behavioural claims merely by name.
Gr32a, ppk23/25, pCd and vAB3 are not replaced by broad anatomical populations.

The finite selectors require review when source annotations change. Reports
retain matched types and graph hashes so an update can be compared explicitly.
The source datasets are CC-BY 4.0; retain original data-author attribution.

## Measured summary

All selectors were executed on the three local Phase 2 graphs. The table below
omits the 54 individual glomerular ORN entries; their measurements are included
in the full table and JSON. Zero is displayed as `absent`.

| Group | MaleCNS | FAFB | BANC |
| --- | ---: | ---: | ---: |
| JO-A | 26 | 94 | 30 |
| JO-B | 75 | 296 | 235 |
| ORN | 2635 | 2278 | 2018 |
| Or* | absent | absent | absent |
| Or47b | 130 | 94 | 90 |
| Or67d | 204 | 127 | 86 |
| Gr32a | absent | absent | absent |
| ppk23 | absent | absent | absent |
| ppk25 | absent | absent | absent |
| L1 | 1776 | 1775 | 100 |
| L2 | 1779 | 1728 | 59 |
| R1-R6 | 1394 | 7938 | absent |
| LC10a | 275 | 237 | 224 |
| LC10b | 95 | 83 | 89 |
| LC10c | 255 | 203 | 166 |
| LC10d | 214 | 188 | 182 |
| AOTU019 | 2 | 2 | 2 |
| AOTU025 | 2 | 2 | 2 |
| P1 | 46 | absent | absent |
| pC1a | absent | 2 | 2 |
| pC1b | absent | 2 | 2 |
| pC1c | absent | 2 | 2 |
| pC1d | absent | 2 | 2 |
| pC1e | absent | 2 | 2 |
| pIP10 | 2 | absent | absent |
| vPR6 | 8 | absent | absent |
| vMS11 | 14 | absent | 6 |
| pMP2 | 2 | absent | absent |
| dPR1 | 2 | absent | absent |
| TN1A | 22 | absent | absent |
| vpoDN | absent | 2 | 2 |
| vpoEN | 4 | 4 | 6 |
| vpoIN | 5 | 6 | 4 |
| AMMC-B1-candidate | 12 | 39 | 38 |
| AMMC-B1-candidate-graph | 11 | 23 | 26 |
| A2-candidate | absent | 4 | 2 |
| vpoDN-GABA-input | absent | 10 | 8 |
| aLN-m | 2 | 2 | 2 |
| SAG | absent | 7 | 2 |
| oviDN | absent | 6 | 6 |
| DNp13/pMN1 | 2 | 2 | 2 |
| pCd | absent | absent | absent |
| aIPg | 56 | absent | absent |
| mAL | 159 | 107 | 108 |
| vAB3 | absent | absent | absent |
| DNa01 | 2 | 2 | 2 |
| DNa02 | 2 | 2 | 2 |
| DNp09 | 2 | 2 | 2 |
| MDN | 4 | 4 | 4 |
| DNg100 | 2 | 2 | 2 |
| DNb08 | 4 | 4 | 4 |
| wing_motor | 48 | absent | 62 |
| ps1_MN | 2 | absent | 2 |
| i1_MN | 2 | absent | 2 |
| iii1_MN | 2 | absent | 2 |
| b3_MN | 2 | absent | 2 |
| PAM | 316 | 307 | 277 |
| PPL1 | 16 | 16 | 13 |
| serotonin | 48 | 1021 | 1540 |
| octopamine | 101 | 72 | 1968 |
| KC | 4064 | 5177 | 4403 |
| MBON | 87 | 89 | 92 |
| APL | 2 | 2 | 1 |

## Verification

```sh
python -m pytest -q -p no:cacheprovider tests/test_dictionary.py
```

Synthetic tests exercise AND filters, negative near-matches, empty groups,
index/body-ID distinction, distributions, file resolution and JSON output.
Real smoke tests run whenever the corresponding repository `build/graph_*.npz`
exists, otherwise skip. FAFB JO-A/JO-B and MaleCNS P1 must be nonempty.
FAFB vpoDN is **2 cells**, recorded as an observation with no count assertion.
Use `-s -k real_graph_smoke` to display that observation. Existing reports are
compared against recomputed selections. Enable `FLYBENCH_DICTIONARY_FAIL_PROBE=1`
and run only `test_harness_failure_probe` to require a deliberate failure and
exit 1; unset it before acceptance. Execution evidence is recorded in
`build/dictionary_validation.json`.

## Full measured selector table

| Group | Dataset | Selector (AND) | Count | Confidence | Source |
| --- | --- | --- | ---: | --- | --- |
| JO-A | male | `{"type_re": "^JO-A(?:[1-4](?:_[abc])?)?$"}` | 26 | family | [Auditory responses of Johnston's organ neurons (2013): A/B Johnston's-organ populations respond to sound.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3734059/) |
| JO-B | male | `{"type_re": "^JO-B(?:[1-4](?:_[abc])?)?$"}` | 75 | family | [Auditory responses of Johnston's organ neurons (2013): A/B Johnston's-organ populations respond to sound.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3734059/) |
| ORN | male | `{"type_re": "^ORN(?:_[A-Za-z0-9]+)?$"}` | 2635 | family | [Systematic morphology of identified ORNs (2021): olfactory receptor neurons project to named glomeruli.](https://elifesciences.org/articles/69896) |
| Or* | male | `{"type_re": "^Or[0-9]+[a-z]+$"}` | 0 (absent) | family | [Systematic morphology of identified ORNs (2021): receptor genes identify olfactory sensory classes.](https://elifesciences.org/articles/69896) |
| Or47b | male | `{"type_re": "^ORN_VA1v$"}` | 130 | proxy | [Systematic morphology of identified ORNs (2021): Or47b ORNs innervate VA1v.](https://elifesciences.org/articles/69896) |
| Or67d | male | `{"type_re": "^ORN_DA1$"}` | 204 | proxy | [Systematic morphology of identified ORNs (2021): Or67d ORNs innervate DA1.](https://elifesciences.org/articles/69896) |
| Gr32a | male | `{"type_re": "^Gr32a$"}` | 0 (absent) | exact | [Thistle et al. (2012), contact chemoreceptors: contact chemosensory pathways contribute to mate recognition.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3365544/) |
| ppk23 | male | `{"type_re": "^ppk23$"}` | 0 (absent) | exact | [Thistle et al. (2012), contact chemoreceptors: contact chemosensory pathways contribute to mate recognition.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3365544/) |
| ppk25 | male | `{"type_re": "^ppk25$"}` | 0 (absent) | exact | [Vijayan et al. (2014), ppk25 pheromone neurons: contact chemosensory pathways contribute to mate recognition.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3967927/) |
| L1 | male | `{"type_re": "^L1$"}` | 1776 | exact | [Matsliah et al. (2024), visual-system parts list: lamina neurons relay early visual input.](https://doi.org/10.1038/s41586-024-07981-1) |
| L2 | male | `{"type_re": "^L2$"}` | 1779 | exact | [Matsliah et al. (2024), visual-system parts list: lamina neurons relay early visual input.](https://doi.org/10.1038/s41586-024-07981-1) |
| R1-R6 | male | `{"type_re": "^R1-(?:R)?6$"}` | 1394 | family | [Matsliah et al. (2024), visual-system parts list: outer photoreceptors provide visual input.](https://doi.org/10.1038/s41586-024-07981-1) |
| LC10a | male | `{"type_re": "^LC10a$"}` | 275 | exact | [Sten et al. (2021), arousal gates visual processing: LC10a participates in visual pursuit.](https://doi.org/10.1038/s41586-021-03714-w) |
| LC10b | male | `{"type_re": "^LC10b$"}` | 95 | exact | [Matsliah et al. (2024), visual-system parts list: LC types are visual projection neurons.](https://doi.org/10.1038/s41586-024-07981-1) |
| LC10c | male | `{"type_re": "^LC10c(?:-[12])?$"}` | 255 | family | [Matsliah et al. (2024), visual-system parts list: LC types are visual projection neurons.](https://doi.org/10.1038/s41586-024-07981-1) |
| LC10d | male | `{"type_re": "^LC10d$"}` | 214 | exact | [Matsliah et al. (2024), visual-system parts list: LC types are visual projection neurons.](https://doi.org/10.1038/s41586-024-07981-1) |
| AOTU019 | male | `{"type_re": "^AOTU019$"}` | 2 | exact | [Schlegel et al. (2024), whole-brain cell typing: atlas identifies anterior optic tubercle cell types.](https://doi.org/10.1038/s41586-024-07686-5) |
| AOTU025 | male | `{"type_re": "^AOTU025$"}` | 2 | exact | [Schlegel et al. (2024), whole-brain cell typing: atlas identifies anterior optic tubercle cell types.](https://doi.org/10.1038/s41586-024-07686-5) |
| P1 | male | `{"type_re": "^(?:pC1_1a&#124;pC1_1b&#124;pC1_2a&#124;pC1_2b&#124;pC1_2c&#124;pC1_3a&#124;pC1_3b&#124;pC1_3c&#124;pC1_5b&#124;pC1_6b&#124;pC1_15a&#124;pC1_16a&#124;pC1_16b)$", "superclass": "cb_intrinsic"}` | 46 | proxy | [Hoopfer et al. (2015), P1 and persistent social state: P1 activation promotes persistent social arousal.](https://elifesciences.org/articles/11346) |
| pC1a | male | `{"type_re": "^pC1a$"}` | 0 (absent) | exact | [Deutsch et al. (2020), persistent female internal state: female pC1 subtypes participate in social state circuits.](https://elifesciences.org/articles/59502) |
| pC1b | male | `{"type_re": "^pC1b$"}` | 0 (absent) | exact | [Deutsch et al. (2020), persistent female internal state: female pC1 subtypes participate in social state circuits.](https://elifesciences.org/articles/59502) |
| pC1c | male | `{"type_re": "^pC1c$"}` | 0 (absent) | exact | [Deutsch et al. (2020), persistent female internal state: female pC1 subtypes participate in social state circuits.](https://elifesciences.org/articles/59502) |
| pC1d | male | `{"type_re": "^pC1d$"}` | 0 (absent) | exact | [Deutsch et al. (2020), persistent female internal state: female pC1 subtypes participate in social state circuits.](https://elifesciences.org/articles/59502) |
| pC1e | male | `{"type_re": "^pC1e$"}` | 0 (absent) | exact | [Deutsch et al. (2020), persistent female internal state: female pC1 subtypes participate in social state circuits.](https://elifesciences.org/articles/59502) |
| pIP10 | male | `{"type_re": "^pIP10$"}` | 2 | exact | [von Philipsborn et al. (2011), control of courtship song: identified descending/VNC circuits participate in male song.](https://doi.org/10.1016/j.neuron.2011.01.011) |
| vPR6 | male | `{"type_re": "^vPR6$"}` | 8 | exact | [von Philipsborn et al. (2011), control of courtship song: identified descending/VNC circuits participate in male song.](https://doi.org/10.1016/j.neuron.2011.01.011) |
| vMS11 | male | `{"type_re": "^vMS11$"}` | 14 | exact | [von Philipsborn et al. (2011), control of courtship song: identified descending/VNC circuits participate in male song.](https://doi.org/10.1016/j.neuron.2011.01.011) |
| pMP2 | male | `{"type_re": "^pMP2$"}` | 2 | exact | [Lillvis et al. (2024), nested song circuits: identified descending/VNC circuits participate in male song.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| dPR1 | male | `{"type_re": "^dPR1$"}` | 2 | exact | [Lillvis et al. (2024), nested song circuits: identified descending/VNC circuits participate in male song.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| TN1A | male | `{"type_re": "^TN1a(?:_[a-i])?$"}` | 22 | family | [Lillvis et al. (2024), nested song circuits: identified descending/VNC circuits participate in male song.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| vpoDN | male | `{"type_re": "^(?:DNp37&#124;vpoDN)$"}` | 0 (absent) | exact | [Marin et al. (2025), descending/ascending comparison: vpoDN (DNp37) controls female vaginal plate opening.](https://doi.org/10.1038/s41586-025-08925-z) |
| vpoEN | male | `{"type_re": "^vpoEN$"}` | 4 | exact | [Wang et al. (2021), female sexual receptivity circuits: excitatory/inhibitory song pathways regulate female receptivity.](https://doi.org/10.1038/s41586-020-2972-7) |
| vpoIN | male | `{"type_re": "^vpoIN$"}` | 5 | exact | [Wang et al. (2021), female sexual receptivity circuits: excitatory/inhibitory song pathways regulate female receptivity.](https://doi.org/10.1038/s41586-020-2972-7) |
| AMMC-B1-candidate | male | `{"type_re": "^(?:CB1078&#124;CB1542&#124;SAD053)$"}` | 12 | proxy | annotation crosswalk, external report, REPORTED; [E3 evidence](../records/dictionary_e3_report.md) |
| AMMC-B1-candidate-graph | male | `{"type_re": "^(?:CB1076&#124;CB1125&#124;CB2789)$"}` | 11 | proxy | graph connectivity, lane k2; [E3 evidence](../records/dictionary_e3_report.md) |
| A2-candidate | male | `{"type_re": "^CB1817[ab]$"}` | 0 (absent) | proxy | graph connectivity, lane k2; [E3 evidence](../records/dictionary_e3_report.md) |
| vpoDN-GABA-input | male | `{"type_re": "^AVLP008$"}` | 0 (absent) | proxy | graph connectivity, lane k2; [E3 evidence](../records/dictionary_e3_report.md) |
| aLN-m | male | `{"type_re": "^WED191$"}` | 2 | proxy | annotation crosswalk, external report, REPORTED; [E3 evidence](../records/dictionary_e3_report.md) |
| SAG | male | `{"type_re": "^SAG$"}` | 0 (absent) | exact | [BANC, distributed brain-and-cord control circuits: ANXXX983/SAG carries reproductive-tract state toward pC1.](https://doi.org/10.1038/s41586-026-10735-w) |
| oviDN | male | `{"type_re": "^oviDN(?:[ab](?:_[ab])?)?$"}` | 0 (absent) | family | [Marin et al. (2025), descending/ascending comparison: oviDN pathways participate in oviposition.](https://doi.org/10.1038/s41586-025-08925-z) |
| DNp13/pMN1 | male | `{"type_re": "^(?:DNp13&#124;pMN1)$"}` | 2 | exact | [Marin et al. (2025), descending/ascending comparison: DNp13/pMN1 drives female ovipositor extrusion and has sex-specific VNC targets.](https://doi.org/10.1038/s41586-025-08925-z) |
| pCd | male | `{"type_re": "^pCd(?:[0-9]+[a-z]?)?$"}` | 0 (absent) | family | [Deutsch et al. (2020), persistent female internal state: persistent courtship state involves pCd.](https://elifesciences.org/articles/59502) |
| aIPg | male | `{"type_re": "^aIPg(?:[0-9]+&#124;_m[1-4])?$"}` | 56 | family | [Social state alters vision (2024): aIPg links female aggression and visual processing.](https://doi.org/10.1038/s41586-024-08255-6) |
| mAL | male | `{"type_re": "^mAL(?:[0-9]+[A-I]?[0-9]?&#124;[BCD][1-6]&#124;_[mf][0-9]+[abc]?)?$"}` | 159 | family | [Clowney et al. (2015), excitation/inhibition and mate choice: mAL inhibition contributes to mate choice.](https://pmc.ncbi.nlm.nih.gov/articles/PMC4695383/) |
| vAB3 | male | `{"type_re": "^vAB3$"}` | 0 (absent) | exact | [Clowney et al. (2015), excitation/inhibition and mate choice: ascending pheromone pathways excite courtship circuitry.](https://pmc.ncbi.nlm.nih.gov/articles/PMC4695383/) |
| DNa01 | male | `{"type_re": "^DNa01$"}` | 2 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| DNa02 | male | `{"type_re": "^DNa02$"}` | 2 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| DNp09 | male | `{"type_re": "^DNp09$"}` | 2 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| MDN | male | `{"type_re": "^MDN$"}` | 4 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| DNg100 | male | `{"type_re": "^DNg100$"}` | 2 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| DNb08 | male | `{"type_re": "^DNb08$"}` | 4 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| wing_motor | male | `{"type_re": "^(?:DLMn\\ a,\\ b&#124;DLMn\\ c\\-f&#124;DVMn\\ 1a\\-c&#124;DVMn\\ 2a,\\ b&#124;DVMn\\ 3a,\\ b&#124;b1\\ MN&#124;b2\\ MN&#124;b3\\ MN&#124;i1\\ MN&#124;i2\\ MN&#124;iii1\\ MN&#124;iii3\\ MN&#124;ps1\\ MN&#124;ps2\\ MN&#124;tp1\\ MN&#124;tp2\\ MN&#124;tpn\\ MN)$", "superclass": "vnc_motor"}` | 48 | proxy | [Marin et al. (2025), descending/ascending comparison: wing motor neurons are targets of descending/VNC circuits.](https://doi.org/10.1038/s41586-025-08925-z) |
| ps1_MN | male | `{"type_re": "^(?:ps1 MN&#124;PS1)$", "superclass": "vnc_motor"}` | 2 | exact | [Lillvis et al. (2024), nested song circuits: named wing motor neurons participate in wing control.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| i1_MN | male | `{"type_re": "^i1(?: MN)?$", "superclass": "vnc_motor"}` | 2 | exact | [Lillvis et al. (2024), nested song circuits: named wing motor neurons participate in wing control.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| iii1_MN | male | `{"type_re": "^iii1(?: MN)?$", "superclass": "vnc_motor"}` | 2 | exact | [Lillvis et al. (2024), nested song circuits: named wing motor neurons participate in wing control.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| b3_MN | male | `{"type_re": "^b3(?: MN)?$", "superclass": "vnc_motor"}` | 2 | exact | [Lillvis et al. (2024), nested song circuits: named wing motor neurons participate in wing control.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| PAM | male | `{"type_re": "^PAM(?:[0-9]{2})?$"}` | 316 | family | [Li et al. (2020), mushroom-body connectome: dopaminergic mushroom-body inputs support reinforcement learning.](https://elifesciences.org/articles/62576) |
| PPL1 | male | `{"type_re": "^PPL1(?:[0-9]{2})?$"}` | 16 | family | [Li et al. (2020), mushroom-body connectome: dopaminergic mushroom-body inputs support reinforcement learning.](https://elifesciences.org/articles/62576) |
| serotonin | male | `{"type_re": "^.*$", "nt": "serotonin"}` | 48 | proxy | [Schlegel et al. (2024), whole-brain cell typing: source NT annotations identify serotonergic candidates.](https://doi.org/10.1038/s41586-024-07686-5) |
| octopamine | male | `{"type_re": "^.*$", "nt": "octopamine"}` | 101 | proxy | [Octopaminergic descending neurons (2024): octopaminergic neurons modulate locomotor and other circuits.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11064449/) |
| KC | male | `{"type_re": "^KC(?:ab(?:-(?:ap1&#124;[cmps]))?&#124;a'b'(?:-(?:ap[12]&#124;m))?&#124;apbp-(?:ap[12]&#124;m)&#124;g(?:-(?:[dm]&#124;s[1-4]))?)?$"}` | 4064 | family | [Li et al. (2020), mushroom-body connectome: Kenyon cells provide mushroom-body representations for learning.](https://elifesciences.org/articles/62576) |
| MBON | male | `{"type_re": "^MBON[0-9]{2}$"}` | 87 | family | [Li et al. (2020), mushroom-body connectome: mushroom-body output neurons carry learned output.](https://elifesciences.org/articles/62576) |
| APL | male | `{"type_re": "^APL$"}` | 2 | exact | [Amin et al. (2020), localized mushroom-body inhibition: APL provides feedback inhibition to Kenyon cells.](https://elifesciences.org/articles/56954) |
| ORN_D | male | `{"type_re": "^ORN_D$"}` | 28 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DA1 | male | `{"type_re": "^ORN_DA1$"}` | 204 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DA2 | male | `{"type_re": "^ORN_DA2$"}` | 48 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DA3 | male | `{"type_re": "^ORN_DA3$"}` | 34 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DA4l | male | `{"type_re": "^ORN_DA4l$"}` | 33 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DA4m | male | `{"type_re": "^ORN_DA4m$"}` | 35 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DC1 | male | `{"type_re": "^ORN_DC1$"}` | 32 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DC2 | male | `{"type_re": "^ORN_DC2$"}` | 22 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DC3 | male | `{"type_re": "^ORN_DC3$"}` | 35 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DC4 | male | `{"type_re": "^ORN_DC4$"}` | 23 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL1 | male | `{"type_re": "^ORN_DL1$"}` | 83 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL2d | male | `{"type_re": "^ORN_DL2d$"}` | 15 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL2v | male | `{"type_re": "^ORN_DL2v$"}` | 23 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL3 | male | `{"type_re": "^ORN_DL3$"}` | 103 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL4 | male | `{"type_re": "^ORN_DL4$"}` | 62 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL5 | male | `{"type_re": "^ORN_DL5$"}` | 43 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM1 | male | `{"type_re": "^ORN_DM1$"}` | 74 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM2 | male | `{"type_re": "^ORN_DM2$"}` | 54 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM3 | male | `{"type_re": "^ORN_DM3$"}` | 63 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM4 | male | `{"type_re": "^ORN_DM4$"}` | 32 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM5 | male | `{"type_re": "^ORN_DM5$"}` | 35 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM6 | male | `{"type_re": "^ORN_DM6$"}` | 58 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DP1l | male | `{"type_re": "^ORN_DP1l$"}` | 33 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DP1m | male | `{"type_re": "^ORN_DP1m$"}` | 31 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_V | male | `{"type_re": "^ORN_V$"}` | 55 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA1d | male | `{"type_re": "^ORN_VA1d$"}` | 132 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA1v | male | `{"type_re": "^ORN_VA1v$"}` | 130 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA2 | male | `{"type_re": "^ORN_VA2$"}` | 83 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA3 | male | `{"type_re": "^ORN_VA3$"}` | 30 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA4 | male | `{"type_re": "^ORN_VA4$"}` | 34 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA5 | male | `{"type_re": "^ORN_VA5$"}` | 16 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA6 | male | `{"type_re": "^ORN_VA6$"}` | 63 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA7l | male | `{"type_re": "^ORN_VA7l$"}` | 29 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA7m | male | `{"type_re": "^ORN_VA7m$"}` | 24 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VC1 | male | `{"type_re": "^ORN_VC1$"}` | 29 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VC2 | male | `{"type_re": "^ORN_VC2$"}` | 32 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VC3 | male | `{"type_re": "^ORN_VC3$"}` | 34 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VC4 | male | `{"type_re": "^ORN_VC4$"}` | 38 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VC5 | male | `{"type_re": "^ORN_VC5$"}` | 31 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VL1 | male | `{"type_re": "^ORN_VL1$"}` | 82 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VL2a | male | `{"type_re": "^ORN_VL2a$"}` | 98 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VL2p | male | `{"type_re": "^ORN_VL2p$"}` | 45 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM1 | male | `{"type_re": "^ORN_VM1$"}` | 33 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM2 | male | `{"type_re": "^ORN_VM2$"}` | 41 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM3 | male | `{"type_re": "^ORN_VM3$"}` | 43 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM4 | male | `{"type_re": "^ORN_VM4$"}` | 78 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM5d | male | `{"type_re": "^ORN_VM5d$"}` | 84 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM5v | male | `{"type_re": "^ORN_VM5v$"}` | 34 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM6 | male | `{"type_re": "^ORN_VM6$"}` | 0 (absent) | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM6l | male | `{"type_re": "^ORN_VM6l$"}` | 14 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM6m | male | `{"type_re": "^ORN_VM6m$"}` | 25 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM6v | male | `{"type_re": "^ORN_VM6v$"}` | 34 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM7d | male | `{"type_re": "^ORN_VM7d$"}` | 36 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM7v | male | `{"type_re": "^ORN_VM7v$"}` | 25 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| JO-A | female | `{"type_re": "^JO-A(?:[1-4](?:_[abc])?)?$"}` | 94 | family | [Auditory responses of Johnston's organ neurons (2013): A/B Johnston's-organ populations respond to sound.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3734059/) |
| JO-B | female | `{"type_re": "^JO-B(?:[1-4](?:_[abc])?)?$"}` | 296 | family | [Auditory responses of Johnston's organ neurons (2013): A/B Johnston's-organ populations respond to sound.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3734059/) |
| ORN | female | `{"type_re": "^ORN(?:_[A-Za-z0-9]+)?$"}` | 2278 | family | [Systematic morphology of identified ORNs (2021): olfactory receptor neurons project to named glomeruli.](https://elifesciences.org/articles/69896) |
| Or* | female | `{"type_re": "^Or[0-9]+[a-z]+$"}` | 0 (absent) | family | [Systematic morphology of identified ORNs (2021): receptor genes identify olfactory sensory classes.](https://elifesciences.org/articles/69896) |
| Or47b | female | `{"type_re": "^ORN_VA1v$"}` | 94 | proxy | [Systematic morphology of identified ORNs (2021): Or47b ORNs innervate VA1v.](https://elifesciences.org/articles/69896) |
| Or67d | female | `{"type_re": "^ORN_DA1$"}` | 127 | proxy | [Systematic morphology of identified ORNs (2021): Or67d ORNs innervate DA1.](https://elifesciences.org/articles/69896) |
| Gr32a | female | `{"type_re": "^Gr32a$"}` | 0 (absent) | exact | [Thistle et al. (2012), contact chemoreceptors: contact chemosensory pathways contribute to mate recognition.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3365544/) |
| ppk23 | female | `{"type_re": "^ppk23$"}` | 0 (absent) | exact | [Thistle et al. (2012), contact chemoreceptors: contact chemosensory pathways contribute to mate recognition.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3365544/) |
| ppk25 | female | `{"type_re": "^ppk25$"}` | 0 (absent) | exact | [Vijayan et al. (2014), ppk25 pheromone neurons: contact chemosensory pathways contribute to mate recognition.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3967927/) |
| L1 | female | `{"type_re": "^L1$"}` | 1775 | exact | [Matsliah et al. (2024), visual-system parts list: lamina neurons relay early visual input.](https://doi.org/10.1038/s41586-024-07981-1) |
| L2 | female | `{"type_re": "^L2$"}` | 1728 | exact | [Matsliah et al. (2024), visual-system parts list: lamina neurons relay early visual input.](https://doi.org/10.1038/s41586-024-07981-1) |
| R1-R6 | female | `{"type_re": "^R1-(?:R)?6$"}` | 7938 | family | [Matsliah et al. (2024), visual-system parts list: outer photoreceptors provide visual input.](https://doi.org/10.1038/s41586-024-07981-1) |
| LC10a | female | `{"type_re": "^LC10a$"}` | 237 | exact | [Sten et al. (2021), arousal gates visual processing: LC10a participates in visual pursuit.](https://doi.org/10.1038/s41586-021-03714-w) |
| LC10b | female | `{"type_re": "^LC10b$"}` | 83 | exact | [Matsliah et al. (2024), visual-system parts list: LC types are visual projection neurons.](https://doi.org/10.1038/s41586-024-07981-1) |
| LC10c | female | `{"type_re": "^LC10c(?:-[12])?$"}` | 203 | family | [Matsliah et al. (2024), visual-system parts list: LC types are visual projection neurons.](https://doi.org/10.1038/s41586-024-07981-1) |
| LC10d | female | `{"type_re": "^LC10d$"}` | 188 | exact | [Matsliah et al. (2024), visual-system parts list: LC types are visual projection neurons.](https://doi.org/10.1038/s41586-024-07981-1) |
| AOTU019 | female | `{"type_re": "^AOTU019$"}` | 2 | exact | [Schlegel et al. (2024), whole-brain cell typing: atlas identifies anterior optic tubercle cell types.](https://doi.org/10.1038/s41586-024-07686-5) |
| AOTU025 | female | `{"type_re": "^AOTU025$"}` | 2 | exact | [Schlegel et al. (2024), whole-brain cell typing: atlas identifies anterior optic tubercle cell types.](https://doi.org/10.1038/s41586-024-07686-5) |
| P1 | female | `{"type_re": "^P1(?:_[0-9]+[a-z]?)?$"}` | 0 (absent) | proxy | [Hoopfer et al. (2015), P1 and persistent social state: P1 activation promotes persistent social arousal.](https://elifesciences.org/articles/11346) |
| pC1a | female | `{"type_re": "^pC1a$"}` | 2 | exact | [Deutsch et al. (2020), persistent female internal state: female pC1 subtypes participate in social state circuits.](https://elifesciences.org/articles/59502) |
| pC1b | female | `{"type_re": "^pC1b$"}` | 2 | exact | [Deutsch et al. (2020), persistent female internal state: female pC1 subtypes participate in social state circuits.](https://elifesciences.org/articles/59502) |
| pC1c | female | `{"type_re": "^pC1c$"}` | 2 | exact | [Deutsch et al. (2020), persistent female internal state: female pC1 subtypes participate in social state circuits.](https://elifesciences.org/articles/59502) |
| pC1d | female | `{"type_re": "^pC1d$"}` | 2 | exact | [Deutsch et al. (2020), persistent female internal state: female pC1 subtypes participate in social state circuits.](https://elifesciences.org/articles/59502) |
| pC1e | female | `{"type_re": "^pC1e$"}` | 2 | exact | [Deutsch et al. (2020), persistent female internal state: female pC1 subtypes participate in social state circuits.](https://elifesciences.org/articles/59502) |
| pIP10 | female | `{"type_re": "^pIP10$"}` | 0 (absent) | exact | [von Philipsborn et al. (2011), control of courtship song: identified descending/VNC circuits participate in male song.](https://doi.org/10.1016/j.neuron.2011.01.011) |
| vPR6 | female | `{"type_re": "^vPR6$"}` | 0 (absent) | exact | [von Philipsborn et al. (2011), control of courtship song: identified descending/VNC circuits participate in male song.](https://doi.org/10.1016/j.neuron.2011.01.011) |
| vMS11 | female | `{"type_re": "^vMS11$"}` | 0 (absent) | exact | [von Philipsborn et al. (2011), control of courtship song: identified descending/VNC circuits participate in male song.](https://doi.org/10.1016/j.neuron.2011.01.011) |
| pMP2 | female | `{"type_re": "^pMP2$"}` | 0 (absent) | exact | [Lillvis et al. (2024), nested song circuits: identified descending/VNC circuits participate in male song.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| dPR1 | female | `{"type_re": "^dPR1$"}` | 0 (absent) | exact | [Lillvis et al. (2024), nested song circuits: identified descending/VNC circuits participate in male song.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| TN1A | female | `{"type_re": "^TN1a(?:_[a-i])?$"}` | 0 (absent) | family | [Lillvis et al. (2024), nested song circuits: identified descending/VNC circuits participate in male song.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| vpoDN | female | `{"type_re": "^(?:DNp37&#124;vpoDN)$"}` | 2 | exact | [Marin et al. (2025), descending/ascending comparison: vpoDN (DNp37) controls female vaginal plate opening.](https://doi.org/10.1038/s41586-025-08925-z) |
| vpoEN | female | `{"type_re": "^vpoEN$"}` | 4 | exact | [Wang et al. (2021), female sexual receptivity circuits: excitatory/inhibitory song pathways regulate female receptivity.](https://doi.org/10.1038/s41586-020-2972-7) |
| vpoIN | female | `{"type_re": "^CB1385$"}` | 6 | exact | [Wang et al. (2021), female sexual receptivity circuits: excitatory/inhibitory song pathways regulate female receptivity.](https://doi.org/10.1038/s41586-020-2972-7) |
| AMMC-B1-candidate | female | `{"type_re": "^(?:CB1078&#124;CB1542&#124;SAD053)$"}` | 39 | proxy | annotation crosswalk, external report, REPORTED; [E3 evidence](../records/dictionary_e3_report.md) |
| AMMC-B1-candidate-graph | female | `{"type_re": "^(?:CB1076&#124;CB1125&#124;CB2789)$"}` | 23 | proxy | graph connectivity, lane k2; [E3 evidence](../records/dictionary_e3_report.md) |
| A2-candidate | female | `{"type_re": "^CB1817[ab]$"}` | 4 | proxy | graph connectivity, lane k2; [E3 evidence](../records/dictionary_e3_report.md) |
| vpoDN-GABA-input | female | `{"type_re": "^AVLP008$"}` | 10 | proxy | graph connectivity, lane k2; [E3 evidence](../records/dictionary_e3_report.md) |
| aLN-m | female | `{"type_re": "^CB3880$"}` | 2 | proxy | annotation crosswalk, external report, REPORTED; [E3 evidence](../records/dictionary_e3_report.md) |
| SAG | female | `{"type_re": "^(?:SAG&#124;SpsP)$"}` | 7 | proxy | [BANC, distributed brain-and-cord control circuits: ANXXX983/SAG carries reproductive-tract state toward pC1.](https://doi.org/10.1038/s41586-026-10735-w) |
| oviDN | female | `{"type_re": "^oviDN(?:[ab](?:_[ab])?)?$"}` | 6 | family | [Marin et al. (2025), descending/ascending comparison: oviDN pathways participate in oviposition.](https://doi.org/10.1038/s41586-025-08925-z) |
| DNp13/pMN1 | female | `{"type_re": "^(?:DNp13&#124;pMN1)$"}` | 2 | exact | [Marin et al. (2025), descending/ascending comparison: DNp13/pMN1 drives female ovipositor extrusion and has sex-specific VNC targets.](https://doi.org/10.1038/s41586-025-08925-z) |
| pCd | female | `{"type_re": "^pCd(?:[0-9]+[a-z]?)?$"}` | 0 (absent) | family | [Deutsch et al. (2020), persistent female internal state: persistent courtship state involves pCd.](https://elifesciences.org/articles/59502) |
| aIPg | female | `{"type_re": "^aIPg(?:[0-9]+&#124;_m[1-4])?$"}` | 0 (absent) | family | [Social state alters vision (2024): aIPg links female aggression and visual processing.](https://doi.org/10.1038/s41586-024-08255-6) |
| mAL | female | `{"type_re": "^mAL(?:[0-9]+[A-I]?[0-9]?&#124;[BCD][1-6]&#124;_[mf][0-9]+[abc]?)?$"}` | 107 | family | [Clowney et al. (2015), excitation/inhibition and mate choice: mAL inhibition contributes to mate choice.](https://pmc.ncbi.nlm.nih.gov/articles/PMC4695383/) |
| vAB3 | female | `{"type_re": "^vAB3$"}` | 0 (absent) | exact | [Clowney et al. (2015), excitation/inhibition and mate choice: ascending pheromone pathways excite courtship circuitry.](https://pmc.ncbi.nlm.nih.gov/articles/PMC4695383/) |
| DNa01 | female | `{"type_re": "^DNa01$"}` | 2 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| DNa02 | female | `{"type_re": "^DNa02$"}` | 2 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| DNp09 | female | `{"type_re": "^DNp09$"}` | 2 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| MDN | female | `{"type_re": "^MDN$"}` | 4 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| DNg100 | female | `{"type_re": "^DNg100$"}` | 2 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| DNb08 | female | `{"type_re": "^DNb08$"}` | 4 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| wing_motor | female | `{"type_re": "^.*$", "superclass": "motor", "cell_class": "wing_motor_neuron"}` | 0 (absent) | family | [Marin et al. (2025), descending/ascending comparison: wing motor neurons are targets of descending/VNC circuits.](https://doi.org/10.1038/s41586-025-08925-z) |
| ps1_MN | female | `{"type_re": "^(?:ps1 MN&#124;PS1)$", "superclass": "motor"}` | 0 (absent) | exact | [Lillvis et al. (2024), nested song circuits: named wing motor neurons participate in wing control.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| i1_MN | female | `{"type_re": "^i1(?: MN)?$", "superclass": "motor"}` | 0 (absent) | exact | [Lillvis et al. (2024), nested song circuits: named wing motor neurons participate in wing control.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| iii1_MN | female | `{"type_re": "^iii1(?: MN)?$", "superclass": "motor"}` | 0 (absent) | exact | [Lillvis et al. (2024), nested song circuits: named wing motor neurons participate in wing control.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| b3_MN | female | `{"type_re": "^b3(?: MN)?$", "superclass": "motor"}` | 0 (absent) | exact | [Lillvis et al. (2024), nested song circuits: named wing motor neurons participate in wing control.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| PAM | female | `{"type_re": "^PAM(?:[0-9]{2})?$"}` | 307 | family | [Li et al. (2020), mushroom-body connectome: dopaminergic mushroom-body inputs support reinforcement learning.](https://elifesciences.org/articles/62576) |
| PPL1 | female | `{"type_re": "^PPL1(?:[0-9]{2})?$"}` | 16 | family | [Li et al. (2020), mushroom-body connectome: dopaminergic mushroom-body inputs support reinforcement learning.](https://elifesciences.org/articles/62576) |
| serotonin | female | `{"type_re": "^.*$", "nt": "serotonin"}` | 1021 | proxy | [Schlegel et al. (2024), whole-brain cell typing: source NT annotations identify serotonergic candidates.](https://doi.org/10.1038/s41586-024-07686-5) |
| octopamine | female | `{"type_re": "^.*$", "nt": "octopamine"}` | 72 | proxy | [Octopaminergic descending neurons (2024): octopaminergic neurons modulate locomotor and other circuits.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11064449/) |
| KC | female | `{"type_re": "^KC(?:ab(?:-(?:ap1&#124;[cmps]))?&#124;a'b'(?:-(?:ap[12]&#124;m))?&#124;apbp-(?:ap[12]&#124;m)&#124;g(?:-(?:[dm]&#124;s[1-4]))?)?$"}` | 5177 | family | [Li et al. (2020), mushroom-body connectome: Kenyon cells provide mushroom-body representations for learning.](https://elifesciences.org/articles/62576) |
| MBON | female | `{"type_re": "^MBON[0-9]{2}$"}` | 89 | family | [Li et al. (2020), mushroom-body connectome: mushroom-body output neurons carry learned output.](https://elifesciences.org/articles/62576) |
| APL | female | `{"type_re": "^APL$"}` | 2 | exact | [Amin et al. (2020), localized mushroom-body inhibition: APL provides feedback inhibition to Kenyon cells.](https://elifesciences.org/articles/56954) |
| ORN_D | female | `{"type_re": "^ORN_D$"}` | 31 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DA1 | female | `{"type_re": "^ORN_DA1$"}` | 127 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DA2 | female | `{"type_re": "^ORN_DA2$"}` | 39 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DA3 | female | `{"type_re": "^ORN_DA3$"}` | 30 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DA4l | female | `{"type_re": "^ORN_DA4l$"}` | 40 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DA4m | female | `{"type_re": "^ORN_DA4m$"}` | 40 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DC1 | female | `{"type_re": "^ORN_DC1$"}` | 39 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DC2 | female | `{"type_re": "^ORN_DC2$"}` | 20 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DC3 | female | `{"type_re": "^ORN_DC3$"}` | 33 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DC4 | female | `{"type_re": "^ORN_DC4$"}` | 22 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL1 | female | `{"type_re": "^ORN_DL1$"}` | 69 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL2d | female | `{"type_re": "^ORN_DL2d$"}` | 14 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL2v | female | `{"type_re": "^ORN_DL2v$"}` | 18 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL3 | female | `{"type_re": "^ORN_DL3$"}` | 79 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL4 | female | `{"type_re": "^ORN_DL4$"}` | 52 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL5 | female | `{"type_re": "^ORN_DL5$"}` | 42 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM1 | female | `{"type_re": "^ORN_DM1$"}` | 68 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM2 | female | `{"type_re": "^ORN_DM2$"}` | 54 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM3 | female | `{"type_re": "^ORN_DM3$"}` | 61 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM4 | female | `{"type_re": "^ORN_DM4$"}` | 40 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM5 | female | `{"type_re": "^ORN_DM5$"}` | 42 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM6 | female | `{"type_re": "^ORN_DM6$"}` | 52 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DP1l | female | `{"type_re": "^ORN_DP1l$"}` | 24 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DP1m | female | `{"type_re": "^ORN_DP1m$"}` | 32 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_V | female | `{"type_re": "^ORN_V$"}` | 67 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA1d | female | `{"type_re": "^ORN_VA1d$"}` | 97 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA1v | female | `{"type_re": "^ORN_VA1v$"}` | 94 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA2 | female | `{"type_re": "^ORN_VA2$"}` | 67 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA3 | female | `{"type_re": "^ORN_VA3$"}` | 29 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA4 | female | `{"type_re": "^ORN_VA4$"}` | 31 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA5 | female | `{"type_re": "^ORN_VA5$"}` | 12 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA6 | female | `{"type_re": "^ORN_VA6$"}` | 60 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA7l | female | `{"type_re": "^ORN_VA7l$"}` | 16 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA7m | female | `{"type_re": "^ORN_VA7m$"}` | 22 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VC1 | female | `{"type_re": "^ORN_VC1$"}` | 26 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VC2 | female | `{"type_re": "^ORN_VC2$"}` | 29 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VC3 | female | `{"type_re": "^ORN_VC3$"}` | 31 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VC4 | female | `{"type_re": "^ORN_VC4$"}` | 23 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VC5 | female | `{"type_re": "^ORN_VC5$"}` | 25 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VL1 | female | `{"type_re": "^ORN_VL1$"}` | 80 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VL2a | female | `{"type_re": "^ORN_VL2a$"}` | 71 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VL2p | female | `{"type_re": "^ORN_VL2p$"}` | 27 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM1 | female | `{"type_re": "^ORN_VM1$"}` | 25 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM2 | female | `{"type_re": "^ORN_VM2$"}` | 37 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM3 | female | `{"type_re": "^ORN_VM3$"}` | 37 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM4 | female | `{"type_re": "^ORN_VM4$"}` | 75 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM5d | female | `{"type_re": "^ORN_VM5d$"}` | 67 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM5v | female | `{"type_re": "^ORN_VM5v$"}` | 23 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM6 | female | `{"type_re": "^ORN_VM6$"}` | 0 (absent) | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM6l | female | `{"type_re": "^ORN_VM6l$"}` | 21 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM6m | female | `{"type_re": "^ORN_VM6m$"}` | 33 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM6v | female | `{"type_re": "^ORN_VM6v$"}` | 26 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM7d | female | `{"type_re": "^ORN_VM7d$"}` | 33 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM7v | female | `{"type_re": "^ORN_VM7v$"}` | 26 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| JO-A | banc | `{"type_re": "^JO-A(?:[1-4](?:_[abc])?)?$"}` | 30 | family | [Auditory responses of Johnston's organ neurons (2013): A/B Johnston's-organ populations respond to sound.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3734059/) |
| JO-B | banc | `{"type_re": "^JO-B(?:[1-4](?:_[abc])?)?$"}` | 235 | family | [Auditory responses of Johnston's organ neurons (2013): A/B Johnston's-organ populations respond to sound.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3734059/) |
| ORN | banc | `{"type_re": "^ORN(?:_[A-Za-z0-9]+)?$"}` | 2018 | family | [Systematic morphology of identified ORNs (2021): olfactory receptor neurons project to named glomeruli.](https://elifesciences.org/articles/69896) |
| Or* | banc | `{"type_re": "^Or[0-9]+[a-z]+$"}` | 0 (absent) | family | [Systematic morphology of identified ORNs (2021): receptor genes identify olfactory sensory classes.](https://elifesciences.org/articles/69896) |
| Or47b | banc | `{"type_re": "^ORN_VA1v$"}` | 90 | proxy | [Systematic morphology of identified ORNs (2021): Or47b ORNs innervate VA1v.](https://elifesciences.org/articles/69896) |
| Or67d | banc | `{"type_re": "^ORN_DA1$"}` | 86 | proxy | [Systematic morphology of identified ORNs (2021): Or67d ORNs innervate DA1.](https://elifesciences.org/articles/69896) |
| Gr32a | banc | `{"type_re": "^Gr32a$"}` | 0 (absent) | exact | [Thistle et al. (2012), contact chemoreceptors: contact chemosensory pathways contribute to mate recognition.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3365544/) |
| ppk23 | banc | `{"type_re": "^ppk23$"}` | 0 (absent) | exact | [Thistle et al. (2012), contact chemoreceptors: contact chemosensory pathways contribute to mate recognition.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3365544/) |
| ppk25 | banc | `{"type_re": "^ppk25$"}` | 0 (absent) | exact | [Vijayan et al. (2014), ppk25 pheromone neurons: contact chemosensory pathways contribute to mate recognition.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3967927/) |
| L1 | banc | `{"type_re": "^L1$"}` | 100 | exact | [Matsliah et al. (2024), visual-system parts list: lamina neurons relay early visual input.](https://doi.org/10.1038/s41586-024-07981-1) |
| L2 | banc | `{"type_re": "^L2$"}` | 59 | exact | [Matsliah et al. (2024), visual-system parts list: lamina neurons relay early visual input.](https://doi.org/10.1038/s41586-024-07981-1) |
| R1-R6 | banc | `{"type_re": "^R1-(?:R)?6$"}` | 0 (absent) | family | [Matsliah et al. (2024), visual-system parts list: outer photoreceptors provide visual input.](https://doi.org/10.1038/s41586-024-07981-1) |
| LC10a | banc | `{"type_re": "^LC10a$"}` | 224 | exact | [Sten et al. (2021), arousal gates visual processing: LC10a participates in visual pursuit.](https://doi.org/10.1038/s41586-021-03714-w) |
| LC10b | banc | `{"type_re": "^LC10b$"}` | 89 | exact | [Matsliah et al. (2024), visual-system parts list: LC types are visual projection neurons.](https://doi.org/10.1038/s41586-024-07981-1) |
| LC10c | banc | `{"type_re": "^LC10c(?:-[12])?$"}` | 166 | family | [Matsliah et al. (2024), visual-system parts list: LC types are visual projection neurons.](https://doi.org/10.1038/s41586-024-07981-1) |
| LC10d | banc | `{"type_re": "^LC10d$"}` | 182 | exact | [Matsliah et al. (2024), visual-system parts list: LC types are visual projection neurons.](https://doi.org/10.1038/s41586-024-07981-1) |
| AOTU019 | banc | `{"type_re": "^AOTU019$"}` | 2 | exact | [Schlegel et al. (2024), whole-brain cell typing: atlas identifies anterior optic tubercle cell types.](https://doi.org/10.1038/s41586-024-07686-5) |
| AOTU025 | banc | `{"type_re": "^AOTU025$"}` | 2 | exact | [Schlegel et al. (2024), whole-brain cell typing: atlas identifies anterior optic tubercle cell types.](https://doi.org/10.1038/s41586-024-07686-5) |
| P1 | banc | `{"type_re": "^P1(?:_[0-9]+[a-z]?)?$"}` | 0 (absent) | proxy | [Hoopfer et al. (2015), P1 and persistent social state: P1 activation promotes persistent social arousal.](https://elifesciences.org/articles/11346) |
| pC1a | banc | `{"type_re": "^pC1a$"}` | 2 | exact | [Deutsch et al. (2020), persistent female internal state: female pC1 subtypes participate in social state circuits.](https://elifesciences.org/articles/59502) |
| pC1b | banc | `{"type_re": "^pC1b$"}` | 2 | exact | [Deutsch et al. (2020), persistent female internal state: female pC1 subtypes participate in social state circuits.](https://elifesciences.org/articles/59502) |
| pC1c | banc | `{"type_re": "^pC1c$"}` | 2 | exact | [Deutsch et al. (2020), persistent female internal state: female pC1 subtypes participate in social state circuits.](https://elifesciences.org/articles/59502) |
| pC1d | banc | `{"type_re": "^pC1d$"}` | 2 | exact | [Deutsch et al. (2020), persistent female internal state: female pC1 subtypes participate in social state circuits.](https://elifesciences.org/articles/59502) |
| pC1e | banc | `{"type_re": "^pC1e$"}` | 2 | exact | [Deutsch et al. (2020), persistent female internal state: female pC1 subtypes participate in social state circuits.](https://elifesciences.org/articles/59502) |
| pIP10 | banc | `{"type_re": "^pIP10$"}` | 0 (absent) | exact | [von Philipsborn et al. (2011), control of courtship song: identified descending/VNC circuits participate in male song.](https://doi.org/10.1016/j.neuron.2011.01.011) |
| vPR6 | banc | `{"type_re": "^vPR6$"}` | 0 (absent) | exact | [von Philipsborn et al. (2011), control of courtship song: identified descending/VNC circuits participate in male song.](https://doi.org/10.1016/j.neuron.2011.01.011) |
| vMS11 | banc | `{"type_re": "^vMS11$"}` | 6 | exact | [von Philipsborn et al. (2011), control of courtship song: identified descending/VNC circuits participate in male song.](https://doi.org/10.1016/j.neuron.2011.01.011) |
| pMP2 | banc | `{"type_re": "^pMP2$"}` | 0 (absent) | exact | [Lillvis et al. (2024), nested song circuits: identified descending/VNC circuits participate in male song.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| dPR1 | banc | `{"type_re": "^dPR1$"}` | 0 (absent) | exact | [Lillvis et al. (2024), nested song circuits: identified descending/VNC circuits participate in male song.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| TN1A | banc | `{"type_re": "^TN1a(?:_[a-i])?$"}` | 0 (absent) | family | [Lillvis et al. (2024), nested song circuits: identified descending/VNC circuits participate in male song.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| vpoDN | banc | `{"type_re": "^(?:DNp37&#124;vpoDN)$"}` | 2 | exact | [Marin et al. (2025), descending/ascending comparison: vpoDN (DNp37) controls female vaginal plate opening.](https://doi.org/10.1038/s41586-025-08925-z) |
| vpoEN | banc | `{"type_re": "^vpoEN$"}` | 6 | exact | [Wang et al. (2021), female sexual receptivity circuits: excitatory/inhibitory song pathways regulate female receptivity.](https://doi.org/10.1038/s41586-020-2972-7) |
| vpoIN | banc | `{"type_re": "^CB1385$"}` | 4 | exact | [Wang et al. (2021), female sexual receptivity circuits: excitatory/inhibitory song pathways regulate female receptivity.](https://doi.org/10.1038/s41586-020-2972-7) |
| AMMC-B1-candidate | banc | `{"type_re": "^(?:CB1078&#124;CB1542&#124;SAD053)$"}` | 38 | proxy | annotation crosswalk, external report, REPORTED; [E3 evidence](../records/dictionary_e3_report.md) |
| AMMC-B1-candidate-graph | banc | `{"type_re": "^(?:CB1076&#124;CB1125&#124;CB2789)$"}` | 26 | proxy | graph connectivity, lane k2; [E3 evidence](../records/dictionary_e3_report.md) |
| A2-candidate | banc | `{"type_re": "^CB1817[ab]$"}` | 2 | proxy | graph connectivity, lane k2; [E3 evidence](../records/dictionary_e3_report.md) |
| vpoDN-GABA-input | banc | `{"type_re": "^AVLP008$"}` | 8 | proxy | graph connectivity, lane k2; [E3 evidence](../records/dictionary_e3_report.md) |
| aLN-m | banc | `{"type_re": "^CB3880$"}` | 2 | proxy | annotation crosswalk, external report, REPORTED; [E3 evidence](../records/dictionary_e3_report.md) |
| SAG | banc | `{"type_re": "^ANXXX983$"}` | 2 | exact | [BANC, distributed brain-and-cord control circuits: ANXXX983/SAG carries reproductive-tract state toward pC1.](https://doi.org/10.1038/s41586-026-10735-w) |
| oviDN | banc | `{"type_re": "^oviDN(?:[ab](?:_[ab])?)?$"}` | 6 | family | [Marin et al. (2025), descending/ascending comparison: oviDN pathways participate in oviposition.](https://doi.org/10.1038/s41586-025-08925-z) |
| DNp13/pMN1 | banc | `{"type_re": "^(?:DNp13&#124;pMN1)$"}` | 2 | exact | [Marin et al. (2025), descending/ascending comparison: DNp13/pMN1 drives female ovipositor extrusion and has sex-specific VNC targets.](https://doi.org/10.1038/s41586-025-08925-z) |
| pCd | banc | `{"type_re": "^pCd(?:[0-9]+[a-z]?)?$"}` | 0 (absent) | family | [Deutsch et al. (2020), persistent female internal state: persistent courtship state involves pCd.](https://elifesciences.org/articles/59502) |
| aIPg | banc | `{"type_re": "^aIPg(?:[0-9]+&#124;_m[1-4])?$"}` | 0 (absent) | family | [Social state alters vision (2024): aIPg links female aggression and visual processing.](https://doi.org/10.1038/s41586-024-08255-6) |
| mAL | banc | `{"type_re": "^mAL(?:[0-9]+[A-I]?[0-9]?&#124;[BCD][1-6]&#124;_[mf][0-9]+[abc]?)?$"}` | 108 | family | [Clowney et al. (2015), excitation/inhibition and mate choice: mAL inhibition contributes to mate choice.](https://pmc.ncbi.nlm.nih.gov/articles/PMC4695383/) |
| vAB3 | banc | `{"type_re": "^vAB3$"}` | 0 (absent) | exact | [Clowney et al. (2015), excitation/inhibition and mate choice: ascending pheromone pathways excite courtship circuitry.](https://pmc.ncbi.nlm.nih.gov/articles/PMC4695383/) |
| DNa01 | banc | `{"type_re": "^DNa01$"}` | 2 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| DNa02 | banc | `{"type_re": "^DNa02$"}` | 2 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| DNp09 | banc | `{"type_re": "^DNp09$"}` | 2 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| MDN | banc | `{"type_re": "^MDN$"}` | 4 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| DNg100 | banc | `{"type_re": "^DNg100$"}` | 2 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| DNb08 | banc | `{"type_re": "^DNb08$"}` | 4 | exact | [BANC, distributed brain-and-cord control circuits: descending pathways provide locomotor-related readouts.](https://doi.org/10.1038/s41586-026-10735-w) |
| wing_motor | banc | `{"type_re": "^.*$", "superclass": "motor", "cell_class": "wing_motor_neuron"}` | 62 | family | [Marin et al. (2025), descending/ascending comparison: wing motor neurons are targets of descending/VNC circuits.](https://doi.org/10.1038/s41586-025-08925-z) |
| ps1_MN | banc | `{"type_re": "^(?:ps1 MN&#124;PS1)$", "superclass": "motor"}` | 2 | exact | [Lillvis et al. (2024), nested song circuits: named wing motor neurons participate in wing control.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| i1_MN | banc | `{"type_re": "^i1(?: MN)?$", "superclass": "motor"}` | 2 | exact | [Lillvis et al. (2024), nested song circuits: named wing motor neurons participate in wing control.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| iii1_MN | banc | `{"type_re": "^iii1(?: MN)?$", "superclass": "motor"}` | 2 | exact | [Lillvis et al. (2024), nested song circuits: named wing motor neurons participate in wing control.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| b3_MN | banc | `{"type_re": "^b3(?: MN)?$", "superclass": "motor"}` | 2 | exact | [Lillvis et al. (2024), nested song circuits: named wing motor neurons participate in wing control.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452343/) |
| PAM | banc | `{"type_re": "^PAM(?:[0-9]{2})?$"}` | 277 | family | [Li et al. (2020), mushroom-body connectome: dopaminergic mushroom-body inputs support reinforcement learning.](https://elifesciences.org/articles/62576) |
| PPL1 | banc | `{"type_re": "^PPL1(?:[0-9]{2})?$"}` | 13 | family | [Li et al. (2020), mushroom-body connectome: dopaminergic mushroom-body inputs support reinforcement learning.](https://elifesciences.org/articles/62576) |
| serotonin | banc | `{"type_re": "^.*$", "nt": "serotonin"}` | 1540 | proxy | [Schlegel et al. (2024), whole-brain cell typing: source NT annotations identify serotonergic candidates.](https://doi.org/10.1038/s41586-024-07686-5) |
| octopamine | banc | `{"type_re": "^.*$", "nt": "octopamine"}` | 1968 | proxy | [Octopaminergic descending neurons (2024): octopaminergic neurons modulate locomotor and other circuits.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11064449/) |
| KC | banc | `{"type_re": "^KC(?:ab(?:-(?:ap1&#124;[cmps]))?&#124;a'b'(?:-(?:ap[12]&#124;m))?&#124;apbp-(?:ap[12]&#124;m)&#124;g(?:-(?:[dm]&#124;s[1-4]))?)?$"}` | 4403 | family | [Li et al. (2020), mushroom-body connectome: Kenyon cells provide mushroom-body representations for learning.](https://elifesciences.org/articles/62576) |
| MBON | banc | `{"type_re": "^MBON[0-9]{2}$"}` | 92 | family | [Li et al. (2020), mushroom-body connectome: mushroom-body output neurons carry learned output.](https://elifesciences.org/articles/62576) |
| APL | banc | `{"type_re": "^APL$"}` | 1 | exact | [Amin et al. (2020), localized mushroom-body inhibition: APL provides feedback inhibition to Kenyon cells.](https://elifesciences.org/articles/56954) |
| ORN_D | banc | `{"type_re": "^ORN_D$"}` | 15 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DA1 | banc | `{"type_re": "^ORN_DA1$"}` | 86 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DA2 | banc | `{"type_re": "^ORN_DA2$"}` | 17 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DA3 | banc | `{"type_re": "^ORN_DA3$"}` | 8 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DA4l | banc | `{"type_re": "^ORN_DA4l$"}` | 22 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DA4m | banc | `{"type_re": "^ORN_DA4m$"}` | 37 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DC1 | banc | `{"type_re": "^ORN_DC1$"}` | 42 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DC2 | banc | `{"type_re": "^ORN_DC2$"}` | 16 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DC3 | banc | `{"type_re": "^ORN_DC3$"}` | 34 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DC4 | banc | `{"type_re": "^ORN_DC4$"}` | 22 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL1 | banc | `{"type_re": "^ORN_DL1$"}` | 29 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL2d | banc | `{"type_re": "^ORN_DL2d$"}` | 19 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL2v | banc | `{"type_re": "^ORN_DL2v$"}` | 25 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL3 | banc | `{"type_re": "^ORN_DL3$"}` | 16 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL4 | banc | `{"type_re": "^ORN_DL4$"}` | 20 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DL5 | banc | `{"type_re": "^ORN_DL5$"}` | 26 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM1 | banc | `{"type_re": "^ORN_DM1$"}` | 76 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM2 | banc | `{"type_re": "^ORN_DM2$"}` | 49 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM3 | banc | `{"type_re": "^ORN_DM3$"}` | 32 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM4 | banc | `{"type_re": "^ORN_DM4$"}` | 49 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM5 | banc | `{"type_re": "^ORN_DM5$"}` | 34 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DM6 | banc | `{"type_re": "^ORN_DM6$"}` | 44 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DP1l | banc | `{"type_re": "^ORN_DP1l$"}` | 32 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_DP1m | banc | `{"type_re": "^ORN_DP1m$"}` | 10 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_V | banc | `{"type_re": "^ORN_V$"}` | 72 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA1d | banc | `{"type_re": "^ORN_VA1d$"}` | 69 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA1v | banc | `{"type_re": "^ORN_VA1v$"}` | 90 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA2 | banc | `{"type_re": "^ORN_VA2$"}` | 69 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA3 | banc | `{"type_re": "^ORN_VA3$"}` | 56 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA4 | banc | `{"type_re": "^ORN_VA4$"}` | 38 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA5 | banc | `{"type_re": "^ORN_VA5$"}` | 15 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA6 | banc | `{"type_re": "^ORN_VA6$"}` | 54 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA7l | banc | `{"type_re": "^ORN_VA7l$"}` | 1 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VA7m | banc | `{"type_re": "^ORN_VA7m$"}` | 28 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VC1 | banc | `{"type_re": "^ORN_VC1$"}` | 30 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VC2 | banc | `{"type_re": "^ORN_VC2$"}` | 23 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VC3 | banc | `{"type_re": "^ORN_VC3$"}` | 36 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VC4 | banc | `{"type_re": "^ORN_VC4$"}` | 42 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VC5 | banc | `{"type_re": "^ORN_VC5$"}` | 24 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VL1 | banc | `{"type_re": "^ORN_VL1$"}` | 102 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VL2a | banc | `{"type_re": "^ORN_VL2a$"}` | 45 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VL2p | banc | `{"type_re": "^ORN_VL2p$"}` | 29 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM1 | banc | `{"type_re": "^ORN_VM1$"}` | 29 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM2 | banc | `{"type_re": "^ORN_VM2$"}` | 43 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM3 | banc | `{"type_re": "^ORN_VM3$"}` | 49 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM4 | banc | `{"type_re": "^ORN_VM4$"}` | 50 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM5d | banc | `{"type_re": "^ORN_VM5d$"}` | 67 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM5v | banc | `{"type_re": "^ORN_VM5v$"}` | 39 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM6 | banc | `{"type_re": "^ORN_VM6$"}` | 2 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM6l | banc | `{"type_re": "^ORN_VM6l$"}` | 30 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM6m | banc | `{"type_re": "^ORN_VM6m$"}` | 14 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM6v | banc | `{"type_re": "^ORN_VM6v$"}` | 31 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM7d | banc | `{"type_re": "^ORN_VM7d$"}` | 30 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |
| ORN_VM7v | banc | `{"type_re": "^ORN_VM7v$"}` | 45 | exact | [Systematic morphology of identified ORNs (2021): glomerular labels distinguish olfactory input classes.](https://elifesciences.org/articles/69896) |

## E3 additions (2026-09-16)

`AMMC-B1-candidate` is the primary population: annotation membership from the
external crosswalk takes priority over connectivity ranking. Its reported
aPN1/AMMC-B1 members are CB1078 and CB1542, plus SAD053. The external report was
supplied as a task summary without its original root-ID list or bibliographic
identifier; REPORTED is not independently verified biological identity. The
atlas literature link supplies context, not proof of this crosswalk.
`AMMC-B1-candidate-graph` is a separate secondary sensitivity population from
lane k2. The lists are disjoint in all three snapshots and must not be merged.

A2-candidate is read-only. CB1817a/b is a graph-connectivity hypothesis;
the modern AMMC-A2 type remains UNRESOLVED, and literal AMMC-A2 matches no cells
in any snapshot. This population is not a drive or hook target. `drive_targets` rejects it with
ValueError ("read-only diagnostic population") before loading a graph.

The female/BANC vpoIN selector is now `^CB1385$`. Legacy selector `^vpoIN$`:
"0 cells in FAFB v783 and BANC v888; renamed 2026-09-16".
The six-cell, L3/R3 observation applies to FAFB; BANC has four, L2/R2.
D1 retains the original MaleCNS `^vpoIN$` selector: five cells (L2/R3). `vpoDN-GABA-input` selects AVLP008 separately
and does not establish an annotation synonym for vpoIN.

The source report links female CB3880 to male WED191 as aLN(m); both populations
contain two GABA-labelled cells. BANC CB3880 also has two. The separate reported
vPN1 types AVLP761m/762m/763m select eleven male cells and no female/BANC cells;
this observation adds no vPN1 dictionary key.

New definitions expose `evidence_class` and `read_only` in their serialized
metadata. Existing definitions default to empty evidence class and false
read-only status; vpoIN carries the E3 crosswalk evidence class.

| Population | Selector | FAFB v783 | BANC v888 | MaleCNS v1.0 | Evidence class |
| --- | --- | ---: | ---: | ---: | --- |
| AMMC-B1-candidate | `^(?:CB1078&#124;CB1542&#124;SAD053)$` | 39 | 38 | 12 | annotation crosswalk, external report, REPORTED |
| AMMC-B1-candidate-graph | `^(?:CB1076&#124;CB1125&#124;CB2789)$` | 23 | 26 | 11 | graph connectivity, lane k2 |
| A2-candidate | `^CB1817[ab]$` | 4 | 2 | 0 | graph connectivity, lane k2 |
| vpoIN | `^CB1385$ (female/BANC); ^vpoIN$ (male)` | 6 | 4 | 5 | annotation crosswalk, external report, REPORTED |
| vpoDN-GABA-input | `^AVLP008$` | 10 | 8 | 0 | graph connectivity, lane k2 |
| aLN-m | `^CB3880$ (female/BANC); ^WED191$ (male)` | 2 | 2 | 2 | annotation crosswalk, external report, REPORTED |

Counts not explicitly supplied by the brief are labelled observed baselines in
the tests; supplied expectations remain fixed. NT labels are not overwritten:
FAFB CB1385 includes one unknown NT and AVLP008 includes three; BANC's
secondary B1 population includes one dopamine-labelled and one unknown cell.
See [the E3 evidence report](../records/dictionary_e3_report.md) for counts,
side distributions, synapses, provenance limits and acceptance status.

## vpoEN inputs (E3b)

The ten `vpoEN-input:<type>` entries and `vpoEN-input-top10` are read-only
diagnostic populations for the E5 reading column. The fixed type list follows
the FAFB direct-input ranking in
[vpoen_inputs_v1](../records/vpoen_inputs_v1_report.md), including its
"Sign convention notes (added after review)". It is not reranked per dataset.
Each definition has `group="vpoen-input"`, `confidence="exact"`,
`read_only=True`. Rank-only entries use
`evidence_class="records/vpoen_inputs_v1_report.md"`; the four crosswalk entries
below and the BANC/MaleCNS union use
`evidence_class="annotation crosswalk, external report 19, REPORTED"`.
The added group metadata is serialized only for these new entries; existing
definitions retain their original fields and values. The atlas source link
provides annotation context, while the local record supplies rank evidence.
The base note on every entry is: "anatomical input rank in vpoen_inputs_v1;
not a drive target; function unknown". `drive_targets` raises `ValueError`
for every new entry, including when its population is absent.

Selectors match exact, case-sensitive labels with these dataset-specific aliases:

| Selector | Female | BANC | Male |
| --- | --- | --- | --- |
| vpoEN-input:CB2364 | `^CB2364$` | `^CB2364$` | `^WED001$` |
| vpoEN-input:CB1383 | `^CB1383$` | `^CB1383$` | `^WED055_b$` |
| vpoEN-input:CB1614 | `^CB1614$` | `^CB1614$` | `^AVLP005$` |
| vpoEN-input:AN_AVLP_8 | `^AN_AVLP_8$` | `^AN17B016$` | `^AN17B016$` |

Crosswalk notes state: "per-dataset alias from external report 19 (VFB alternative
name + connectivity similarity); not cell-level homology; an alias never merges
two FAFB types". The supplied report is REPORTED evidence, not an independently
verified cell-level homology. CB1484/CB1869 receive no WED118 alias because that
label groups both FAFB types. CB2108/CB2449 receive no WED063_a/b alias because
cell counts disagree (20 vs 11); CB2108 has no individual input entry. WED104
is literal in all three graphs and needs no alias.

Zero means absent in this snapshot, not biological absence. The female union
is unchanged; BANC/MaleCNS retain all ten literal types and add only the opened
aliases. Counts include cells with no direct edge to vpoEN: for example, male
AVLP005 has eight graph cells but six direct input cells in
[the rank report, line 651](../records/vpoen_inputs_v1_report.md#L651).
The union is not a drive decision or a functional classification.

`A2-candidate` already selects `^CB1817[ab]$`, covering both CB1817a and
CB1817b. Its definition is unchanged; no `A2-candidate-path` is needed.
The existing B1 lists, vpoIN and SAG definitions are also unchanged.

Measurements use positive CSR counts, with presynaptic rows. Cell `sign`
and NT distributions are separate: FAFB uses `shiu2024-parquet`, while BANC
and MaleCNS use `shiu2024`. Cross-graph signs are not like-for-like evidence.
See [E3b evidence](../records/dictionary_e3b_report.md) for L/R counts, NT,
signs, direct JO-A/JO-B inputs, direct vpoEN/vpoIN/vpoDN outputs and hashes.

The following rows supplement the existing full measured selector table.

| Group | Dataset | Selector (AND) | Count | Confidence | Source |
| --- | --- | --- | ---: | --- | --- |
| vpoEN-input:CB1484 | female | `{"type_re": "^(?:CB1484)$"}` | 6 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB2364 | female | `{"type_re": "^CB2364$"}` | 8 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB1383 | female | `{"type_re": "^CB1383$"}` | 6 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:WED104 | female | `{"type_re": "^(?:WED104)$"}` | 2 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:AN_AVLP_8 | female | `{"type_re": "^AN_AVLP_8$"}` | 2 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB2633 | female | `{"type_re": "^(?:CB2633)$"}` | 4 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:PVLP021 | female | `{"type_re": "^(?:PVLP021)$"}` | 4 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB1869 | female | `{"type_re": "^(?:CB1869)$"}` | 3 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB2449 | female | `{"type_re": "^(?:CB2449)$"}` | 6 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB1614 | female | `{"type_re": "^CB1614$"}` | 2 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input-top10 | female | `{"type_re": "^(?:CB1484&#124;CB2364&#124;CB1383&#124;WED104&#124;AN_AVLP_8&#124;CB2633&#124;PVLP021&#124;CB1869&#124;CB2449&#124;CB1614)$"}` | 43 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB1484 | banc | `{"type_re": "^(?:CB1484)$"}` | 0 (absent) | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB2364 | banc | `{"type_re": "^CB2364$"}` | 8 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB1383 | banc | `{"type_re": "^CB1383$"}` | 4 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:WED104 | banc | `{"type_re": "^(?:WED104)$"}` | 1 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:AN_AVLP_8 | banc | `{"type_re": "^AN17B016$"}` | 2 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB2633 | banc | `{"type_re": "^(?:CB2633)$"}` | 2 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:PVLP021 | banc | `{"type_re": "^(?:PVLP021)$"}` | 4 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB1869 | banc | `{"type_re": "^(?:CB1869)$"}` | 0 (absent) | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB2449 | banc | `{"type_re": "^(?:CB2449)$"}` | 7 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB1614 | banc | `{"type_re": "^CB1614$"}` | 5 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input-top10 | banc | `{"type_re": "^(?:CB1484&#124;CB2364&#124;CB1383&#124;WED104&#124;AN_AVLP_8&#124;CB2633&#124;PVLP021&#124;CB1869&#124;CB2449&#124;CB1614&#124;AN17B016)$"}` | 33 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB1484 | male | `{"type_re": "^(?:CB1484)$"}` | 0 (absent) | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB2364 | male | `{"type_re": "^WED001$"}` | 10 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB1383 | male | `{"type_re": "^WED055_b$"}` | 8 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:WED104 | male | `{"type_re": "^(?:WED104)$"}` | 2 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:AN_AVLP_8 | male | `{"type_re": "^AN17B016$"}` | 2 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB2633 | male | `{"type_re": "^(?:CB2633)$"}` | 4 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:PVLP021 | male | `{"type_re": "^(?:PVLP021)$"}` | 4 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB1869 | male | `{"type_re": "^(?:CB1869)$"}` | 0 (absent) | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB2449 | male | `{"type_re": "^(?:CB2449)$"}` | 0 (absent) | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input:CB1614 | male | `{"type_re": "^AVLP005$"}` | 8 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
| vpoEN-input-top10 | male | `{"type_re": "^(?:CB1484&#124;CB2364&#124;CB1383&#124;WED104&#124;AN_AVLP_8&#124;CB2633&#124;PVLP021&#124;CB1869&#124;CB2449&#124;CB1614&#124;WED001&#124;WED055_b&#124;AVLP005&#124;AN17B016)$"}` | 38 | exact | [Schlegel et al. (2024), whole-brain cell typing: annotation context only; rank evidence is vpoen_inputs_v1.](https://doi.org/10.1038/s41586-024-07686-5) |
### E3c: AVLP083 diagnostic gate

`vpoEN-gate:AVLP083` selects `^AVLP083$` in all three datasets, with
`read_only=True`, `group="vpoen-gate"` and `confidence="exact"`. Its evidence
is [vpoen_inputs_v1](../records/vpoen_inputs_v1_report.md); the atlas link
is annotation context only. This anatomical intermediate is not a drive
target; function is unknown. E3c did not change the E3b top-ten definitions;
the later E5 crosswalk changes are documented above.
CB1614 receives no new entry; its FAFB output to vpoIN is remeasured as 59
synapses. See [E3c measurements](../records/dictionary_e3c_report.md).

| Group | Selector | Female cells | BANC cells | Male cells | Confidence |
| --- | --- | ---: | ---: | ---: | --- |
| vpoEN-gate:AVLP083 | `^AVLP083$` | 2 | 2 | 1 | exact |
