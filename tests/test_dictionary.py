"""Selection boundaries and measured graph smoke checks."""

import json
import os
from pathlib import Path

import numpy as np
import pytest

from flybench.dictionary import drive_targets, groups
from flybench.dictionary.build import audit, build, markdown_table
from flybench.dictionary.entries import DATASETS, P1_TYPES, Selector, entries
from flybench.graph.schema import load


@pytest.fixture
def graph():
    types = ["JO-A", "JO-A1", "JO-A-unclear", "JO-AB", "JO-B", "XJO-A", "JO-B4_b",
             "pC1_1a", "pC1_9a", "pC1_2a/2b", "pC1x_a", "P1-9", "DNp37",
             "ORN_VA1v", "ORN_DA1", "ORN_VA1d", "Or47b", "Gr32a", "",
             "SpsP", "IbSpsP", "ANXXX983", "LC10c-1", "LC10c-2", "LC10_unclear",
             "KCg-m", "KC_bad", "MBON01", "MBON15-like", "MBON25,MBON34",
             "PS1", "PS100", "ps1 MN", "i1 MN", "iii1", "TN1a_a", "TN1c_a"]
    n = len(types)
    return {"body_id": np.arange(1001, 1001 + n, dtype=np.int64),
            "type": np.array(types), "side": np.array(["L", "R", ""] + ["L"] * (n - 3)),
            "superclass": np.array(["cb_intrinsic"] * 30 + ["motor", "motor", "vnc_motor", "vnc_motor", "motor", "vnc_intrinsic", "vnc_intrinsic"]),
            "class": np.array([""] * 30 + ["wing_motor_neuron"] * 5 + [""] * 2),
            "nt": np.array(["acetylcholine"] * 18 + ["serotonin", "octopamine", "tyramine"] + [""] * (n - 21))}


def test_and_filters_and_missing_metadata(graph):
    np.testing.assert_array_equal(Selector(r"^JO-A[1]?$", side="R", superclass="cb_intrinsic").select(graph), [1])
    np.testing.assert_array_equal(Selector(r"^JO-A[1]?$", side="L", superclass="motor").select(graph), [])
    np.testing.assert_array_equal(Selector(nt="serotonin").select(graph), [18])
    np.testing.assert_array_equal(Selector(superclass="motor", cell_class="wing_motor_neuron").select(graph), [30, 31, 34])
    with pytest.raises(ValueError):
        Selector(side="left").select(graph)
    with pytest.raises(KeyError):
        Selector(nt="serotonin").select({k: v for k, v in graph.items() if k != "nt"})
    with pytest.raises(KeyError):
        Selector(superclass="motor").select({k: v for k, v in graph.items() if k != "superclass"})


@pytest.mark.parametrize("dataset", DATASETS)
def test_boundary_matches(graph, dataset):
    selected = groups(dataset, graph=graph)
    expected = {"JO-A": [0, 1], "JO-B": [4, 6], "Or47b": [13], "Or67d": [14],
                "Or*": [16], "Gr32a": [17], "serotonin": [18], "octopamine": [19],
                "LC10c": [22, 23], "KC": [25], "MBON": [27], "vpoDN": [12],
                "TN1A": [35]}
    for name, indices in expected.items():
        np.testing.assert_array_equal(selected[name], indices, err_msg=name)
        assert selected[name].dtype == np.dtype("int64")
    np.testing.assert_array_equal(selected["P1"], [7] if dataset == "male" else [])
    np.testing.assert_array_equal(selected["SAG"], {"male": [], "female": [19], "banc": [21]}[dataset])
    np.testing.assert_array_equal(selected["ps1_MN"], [32] if dataset == "male" else [30])
    np.testing.assert_array_equal(drive_targets(dataset, "JO-A", graph=graph), [0, 1])
    with pytest.raises(ValueError, match="absent"):
        drive_targets(dataset, "ppk25", graph=graph)
    with pytest.raises(KeyError, match="unknown"):
        drive_targets(dataset, "not-a-group", graph=graph)


def test_audit_distributions_and_absence(graph):
    records = {r["name"]: r for r in audit("male", graph)}
    record = records["JO-A"]
    assert record["count"] == 2
    assert record["example_body_ids"] == [1001, 1002]
    assert record["matched_types"] == {"JO-A": 1, "JO-A1": 1}
    assert record["side_distribution"] == {"L": 1, "R": 1}
    assert record["nt_distribution"] == {"acetylcholine": 2}
    assert records["ppk25"]["status"] == "absent"
    assert records["ppk25"]["example_body_ids"] == []
    assert records["ppk25"]["nt_distribution"] == {}
    assert len(records["ORN"]["example_body_ids"]) == 3
    assert "absent is not evidence" in records["ppk25"]["notes"]


def test_example_limit_and_missing_side_bucket(graph):
    graph["type"][:] = "JO-A"
    record = audit("male", graph)[0]
    assert record["example_body_ids"] == [1001, 1002, 1003, 1004, 1005]
    assert record["side_distribution"][""] == 1


def test_snapshot_export_and_api_paths(graph, tmp_path, monkeypatch):
    graph["meta"] = np.array(json.dumps({"dataset": "test", "schema_version": "1"}))
    np.savez(tmp_path / "graph_male.npz", **graph)
    monkeypatch.setenv("FLYBENCH_DATA", str(tmp_path))
    np.testing.assert_array_equal(groups("male")["JO-A"], [0, 1])
    np.testing.assert_array_equal(drive_targets("male", "JO-A", data_dir=tmp_path), [0, 1])
    report = build("male", out_dir=tmp_path)
    raw = (tmp_path / "dictionary_male.json").read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert json.loads(raw) == report
    assert len(report["graph"]["sha256"]) == 64
    assert report["graph"]["meta"]["dataset"] == "test"
    assert "0 (absent)" in markdown_table([report])
    assert "&#124;" in markdown_table([report])
    with pytest.raises(FileNotFoundError):
        groups("banc", data_dir=tmp_path)


def test_definition_contract():
    for dataset in DATASETS:
        definitions = entries(dataset)
        assert len({entry.name for entry in definitions}) == len(definitions)
        assert {entry.role for entry in definitions} == {"sensory_input", "readout", "motor", "state", "modulatory"}
        assert all(entry.confidence in ("exact", "family", "proxy") for entry in definitions)
        assert all(entry.literature and entry.source.startswith("https://") for entry in definitions)
    assert "pC1_2a/2b" not in P1_TYPES
    assert "pC1_9a" not in P1_TYPES
    with pytest.raises(ValueError):
        groups("unknown", graph={})


def test_simulator_accepts_groups(graph):
    from scipy.sparse import csr_matrix
    from flybench.sim import Simulator

    n = len(graph["body_id"])
    result = Simulator(csr_matrix((n, n)), groups=groups("male", graph=graph)).run(1, seed=1)
    assert result.group_rates_hz["JO-A"] == 0


@pytest.mark.parametrize("dataset", DATASETS)
def test_real_graph_smoke(dataset, record_property):
    path = Path(__file__).resolve().parents[1] / "build" / f"graph_{dataset}.npz"
    if not path.exists():
        pytest.skip(f"optional graph is unavailable: {path.name}")
    graph = load(path)
    selected = groups(dataset, graph=graph)
    if dataset == "female":
        assert len(selected["JO-A"]) > 0
        assert len(selected["JO-B"]) > 0
        # Report the observation; two cells is not an acceptance oracle.
        record_property("vpoDN_count", len(selected["vpoDN"]))
        print(f"FAFB vpoDN observed count: {len(selected['vpoDN'])}")
    if dataset == "male":
        assert len(selected["P1"]) > 0
    # Independently compare written counts with recomputed index populations.
    report_path = Path(__file__).parent / "fixtures" / "graph" / f"dictionary_{dataset}.json"
    assert report_path.exists(), "regenerate dictionary snapshots with fixtures/graph/generate.py"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert {r["name"]: r["count"] for r in report["entries"]} == {k: len(v) for k, v in selected.items()}
        for record in report["entries"]:
            indices = selected[record["name"]]
            assert record["example_body_ids"] == graph["body_id"][indices[:5]].tolist()


@pytest.mark.skipif(os.environ.get("FLYBENCH_DICTIONARY_FAIL_PROBE") != "1", reason="opt-in failure probe")
def test_harness_failure_probe():
    assert False, "deliberate dictionary harness failure"


# Explicit acceptance counts supplied by the E3 brief. Never replace these
# with observations when an acceptance mismatch occurs.
E3_BRIEF_COUNTS = {
    "female": {"AMMC-B1-candidate": 39, "AMMC-B1-candidate-graph": 23,
               "A2-candidate": 4, "vpoIN": 6, "aLN-m": 2},
    "banc": {"AMMC-B1-candidate": 38, "AMMC-B1-candidate-graph": 26,
             "A2-candidate": 2, "vpoIN": 4},
    "male": {"AMMC-B1-candidate": 12, "aLN-m": 2, "vpoIN": 5},
}
# The brief supplies no numeric expectation for these combinations. Freeze
# separately labelled graph observations; they do not invent brief claims.
E3_OBSERVED_COUNTS = {
    "female": {"vpoDN-GABA-input": 10},
    "banc": {"vpoDN-GABA-input": 8, "aLN-m": 2},
    "male": {"AMMC-B1-candidate-graph": 11, "A2-candidate": 0,
             "vpoDN-GABA-input": 0},
}


@pytest.fixture(scope="module", params=DATASETS)
def e3_snapshot(request):
    dataset = request.param
    path = Path(__file__).resolve().parents[1] / "build" / f"graph_{dataset}.npz"
    if not path.exists():
        pytest.skip(f"optional E3 graph unavailable: {path.name}")
    graph = load(path)
    return dataset, graph, groups(dataset, graph=graph)


@pytest.mark.parametrize("name", ["AMMC-B1-candidate", "AMMC-B1-candidate-graph",
                                  "A2-candidate", "vpoIN", "vpoDN-GABA-input", "aLN-m"])
def test_e3_snapshot_counts(e3_snapshot, name):
    dataset, _, selected = e3_snapshot
    expected = E3_BRIEF_COUNTS[dataset] | E3_OBSERVED_COUNTS[dataset]
    assert len(selected[name]) == expected[name], (dataset, name, "E3 count mismatch")


def test_e3_snapshot_boundaries(e3_snapshot):
    dataset, graph, selected = e3_snapshot
    assert np.intersect1d(selected["AMMC-B1-candidate"],
                          selected["AMMC-B1-candidate-graph"]).size == 0
    if dataset in ("female", "banc"):
        assert len(selected["vpoIN"]) > 0
        assert len(Selector(r"^vpoIN$").select(graph)) == 0
    if dataset == "banc":
        assert graph["side"][selected["A2-candidate"]].tolist() == ["R", "R"]
    assert set(graph["nt"][selected["aLN-m"]]) == {"gaba"}


@pytest.mark.parametrize("dataset", DATASETS)
def test_e3_a2_drive_rejected_for_present_and_absent_population(dataset):
    # A present cell prevents an ordinary absence error from masquerading as
    # the diagnostic guard. An absent population must use the same guard.
    for types in (["CB1817a", "CB1817b"], ["unrelated"]):
        graph = {"type": np.array(types), "body_id": np.arange(len(types))}
        with pytest.raises(ValueError, match="read-only diagnostic population"):
            drive_targets(dataset, "A2-candidate", graph=graph)


@pytest.mark.parametrize("dataset", DATASETS)
def test_e3_selector_definitions_and_exact_boundaries(dataset):
    definitions = {entry.name: entry for entry in entries(dataset)}
    patterns = {
        "AMMC-B1-candidate": r"^(?:CB1078|CB1542|SAD053)$",
        "AMMC-B1-candidate-graph": r"^(?:CB1076|CB1125|CB2789)$",
        "A2-candidate": r"^CB1817[ab]$",
        "vpoIN": r"^vpoIN$" if dataset == "male" else r"^CB1385$",
        "vpoDN-GABA-input": r"^AVLP008$",
        "aLN-m": r"^WED191$" if dataset == "male" else r"^CB3880$",
    }
    for name, pattern in patterns.items():
        entry = definitions[name]
        assert entry.selector.type_re == pattern
        assert entry.evidence_class in ("annotation crosswalk, external report, REPORTED",
                                         "graph connectivity, lane k2")
        assert entry.notes
        types = ["CB10780", "CB1076-like", "CB1817c", "CB1385a", "AVLP008-like",
                 "WED191a", "CB38800", "xSAD053", "AMMC-A2", "vpoIN-like"]
        assert entry.selector.select({"type": np.array(types),
                                      "body_id": np.arange(len(types))}).size == 0
    assert definitions["A2-candidate"].read_only
    assert not definitions["AMMC-B1-candidate"].read_only
    assert "0 cells in FAFB v783 and BANC v888; renamed 2026-09-16" in definitions["vpoIN"].notes


# Fixed roadmap values, independent of the production selector allowlist.
E3B_INPUTS = {
    "CB1484": 704, "CB2364": 563, "CB1383": 321, "WED104": 297,
    "AN_AVLP_8": 288, "CB2633": 278, "PVLP021": 215, "CB1869": 184,
    "CB2449": 140, "CB1614": 139,
}
E3B_NAMES = ["vpoEN-input:" + name for name in E3B_INPUTS] + ["vpoEN-input-top10"]


@pytest.fixture
def e3b_graph():
    types = list(E3B_INPUTS) + ["CB1484", "CB1817a", "CB1817b"]
    types += [variant for name in E3B_INPUTS
              for variant in ("x" + name, name + "-like", name.lower(), name + "0")]
    return {"type": np.array(types), "body_id": np.arange(9001, 9001 + len(types)),
            "superclass": np.full(len(types), "cb_intrinsic"),
            "class": np.full(len(types), ""), "nt": np.full(len(types), ""),
            "side": np.full(len(types), "")}


@pytest.mark.parametrize("dataset", DATASETS)
def test_e3b_exact_selection_and_metadata(dataset, e3b_graph):
    alias_types = {"female": [], "banc": ["AN17B016"],
                   "male": ["WED001", "WED055_b", "AVLP005", "AN17B016"]}[dataset]
    for column, values in e3b_graph.items():
        extra = (alias_types if column == "type" else
                 np.arange(10001, 10001 + len(alias_types)) if column == "body_id" else
                 np.full(len(alias_types), "cb_intrinsic" if column == "superclass" else ""))
        e3b_graph[column] = np.concatenate((values, np.asarray(extra, dtype=values.dtype)))
    definitions = {entry.name: entry for entry in entries(dataset)}
    selected = groups(dataset, graph=e3b_graph)
    alias_indices = {
        "female": {}, "banc": {"AN_AVLP_8": [53]},
        "male": {"CB2364": [53], "CB1383": [54],
                 "CB1614": [55], "AN_AVLP_8": [56]},
    }[dataset]
    for i, cell_type in enumerate(E3B_INPUTS):
        expected = alias_indices.get(cell_type, [0, 10] if i == 0 else [i])
        np.testing.assert_array_equal(selected["vpoEN-input:" + cell_type], expected)
    union_expected = list(range(11)) + sorted(i for ids in alias_indices.values() for i in ids)
    np.testing.assert_array_equal(selected["vpoEN-input-top10"], union_expected)
    np.testing.assert_array_equal(selected["A2-candidate"], [11, 12])
    assert "A2-candidate-path" not in definitions
    exclusion_notes = {
        "CB1484": "; no WED118 alias: it groups CB1484 and CB1869 and would silently include CB1869",
        "CB1869": "; no WED118 alias: it groups CB1484 and CB1869",
        "CB2449": "; no CB2108/CB2449 to WED063_a/b aliases: cell counts disagree (20 vs 11)",
        "WED104": "; literal in all three graphs; no alias needed",
    }
    for name in E3B_NAMES:
        entry = definitions[name]
        assert entry.read_only and entry.confidence == "exact"
        assert entry.group == entry.to_dict()["group"] == "vpoen-input"
        cell_type = name.removeprefix("vpoEN-input:")
        # Crosswalk-entry metadata is covered by test_e5_alias_patterns_and_metadata,
        # including datasets that retain the original literal spelling.
        if cell_type not in ("CB2364", "CB1383", "CB1614", "AN_AVLP_8"):
            if name == "vpoEN-input-top10" and dataset != "female":
                assert entry.evidence_class == "annotation crosswalk, external report 19, REPORTED"
                assert "not cell-level homology" in entry.notes
            else:
                assert entry.evidence_class == "records/vpoen_inputs_v1_report.md"
                suffix = exclusion_notes.get(cell_type, "")
                if name == "vpoEN-input-top10":
                    suffix = "; literal union plus only the opened dataset aliases" + "".join(exclusion_notes.values())
                assert entry.notes == "anatomical input rank in vpoen_inputs_v1; not a drive target; function unknown" + suffix
        for graph in (e3b_graph, {"type": np.array(["unrelated"]), "body_id": np.array([1])}):
            with pytest.raises(ValueError, match="read-only diagnostic population"):
                drive_targets(dataset, name, graph=graph)
    assert "group" not in definitions["A2-candidate"].to_dict()


@pytest.mark.parametrize("dataset,patterns", [
    ("female", (r"^CB2364$", r"^CB1383$", r"^CB1614$", r"^AN_AVLP_8$")),
    ("banc", (r"^CB2364$", r"^CB1383$", r"^CB1614$", r"^AN17B016$")),
    ("male", (r"^WED001$", r"^WED055_b$", r"^AVLP005$", r"^AN17B016$")),
])
def test_e5_alias_patterns_and_metadata(dataset, patterns):
    definitions = {entry.name: entry for entry in entries(dataset)}
    for cell_type, pattern in zip(("CB2364", "CB1383", "CB1614", "AN_AVLP_8"), patterns):
        entry = definitions["vpoEN-input:" + cell_type]
        assert entry.selector.type_re == pattern
        assert entry.read_only
        alias_note = ("per-dataset alias from external report 19 (VFB alternative name + "
                      "connectivity similarity); not cell-level homology; an alias never "
                      "merges two FAFB types")
        if pattern == rf"^{cell_type}$":
            # Literal selection in this dataset: the original E3b provenance is unchanged.
            assert entry.evidence_class == "records/vpoen_inputs_v1_report.md"
            assert alias_note not in entry.notes
        else:
            assert entry.evidence_class == "annotation crosswalk, external report 19, REPORTED"
            assert alias_note in entry.notes


@pytest.mark.parametrize("dataset", ["banc", "male"])
def test_e5_ambiguous_aliases_remain_closed(dataset):
    definitions = {entry.name: entry for entry in entries(dataset)}
    graph = {"type": np.array(["WED118", "WED063_a", "WED063_b"]),
             "body_id": np.arange(3)}
    # CB2108 has no pre-existing selector; do not introduce one for this crosswalk.
    assert "vpoEN-input:CB2108" not in definitions
    for cell_type in ("CB1484", "CB1869", "CB2449"):
        entry = definitions["vpoEN-input:" + cell_type]
        assert entry.selector.type_re == rf"^(?:{cell_type})$"
        assert entry.selector.select(graph).size == 0
        assert "no " in entry.notes
    assert definitions["vpoEN-input-top10"].selector.select(graph).size == 0


def test_e5_wed001_selection_is_dataset_specific():
    graph = {"type": np.array(["WED001", "WED001-like", "xWED001", "wed001"]),
             "body_id": np.arange(4)}
    for dataset, expected in (("male", [0]), ("female", [])):
        entry = next(e for e in entries(dataset) if e.name == "vpoEN-input:CB2364")
        np.testing.assert_array_equal(entry.selector.select(graph), expected)
        with pytest.raises(ValueError, match="read-only diagnostic population"):
            drive_targets(dataset, entry.name, graph=graph)


@pytest.mark.parametrize("dataset,extra", [("female", []), ("banc", [10]),
                                          ("male", [10, 11, 12, 13])])
def test_e5_top10_retains_literals_and_adds_only_open_aliases(dataset, extra):
    labels = list(E3B_INPUTS) + ["AN17B016", "WED001", "WED055_b", "AVLP005",
                               "WED118", "WED063_a", "WED063_b", "WED001-like"]
    graph = {"type": np.array(labels), "body_id": np.arange(len(labels))}
    entry = next(e for e in entries(dataset) if e.name == "vpoEN-input-top10")
    np.testing.assert_array_equal(entry.selector.select(graph), list(range(10)) + extra)
    assert entry.read_only
    if dataset != "female":
        assert entry.evidence_class == "annotation crosswalk, external report 19, REPORTED"


def e3b_measure(graph, selected):
    """Measure raw directed synapses without sign cancellation or simulation."""
    from flybench.dictionary.build import distribution
    from scipy.sparse import csr_matrix

    n = len(graph["body_id"])
    counts = csr_matrix((graph["count"], graph["indices"], graph["indptr"]), shape=(n, n))
    rows = {}
    for name in E3B_NAMES + ["A2-candidate"]:
        indices = selected[name]
        rows[name] = {
            "count": len(indices), "status": "present" if len(indices) else "absent",
            "sides": distribution(graph["side"][indices]),
            "nt": distribution(graph["nt"][indices]),
            "sign": distribution(graph["sign"][indices]),
            "types": distribution(graph["type"][indices]),
            "body_ids": graph["body_id"][indices].tolist(),
            "jo_a_synapses": int(counts[selected["JO-A"]][:, indices].sum()),
            "jo_b_synapses": int(counts[selected["JO-B"]][:, indices].sum()),
            "outputs": {target: int(counts[indices][:, selected[target]].sum())
                        for target in ("vpoEN", "vpoIN", "vpoDN")},
            "vpoen_sign_synapses": {
                str(sign): int(counts[indices[graph["sign"][indices] == sign]][:, selected["vpoEN"]].sum())
                for sign in (-1, 0, 1)},
        }
    return rows


def test_e3b_measure_direction_and_sign(e3b_graph):
    from scipy.sparse import csr_matrix

    n = len(e3b_graph["body_id"])
    # Reverse edge 91 must not contaminate JO-A input 7; negative source
    # signs must not turn raw outgoing count 11 into -11 or remove it.
    matrix = csr_matrix(([7, 91, 11, 13, 17], ([11, 0, 0, 0, 0], [0, 11, 12, 13, 14])), shape=(n, n))
    graph = dict(e3b_graph, count=matrix.data, indices=matrix.indices, indptr=matrix.indptr,
                 side=np.array(["L"] * n), nt=np.array(["gaba"] * n), sign=np.full(n, -1))
    selected = groups("female", graph=graph)
    selected.update({"JO-A": np.array([11]), "JO-B": np.array([15]),
                     "vpoEN": np.array([12]), "vpoIN": np.array([13]), "vpoDN": np.array([14])})
    row = e3b_measure(graph, selected)["vpoEN-input:CB1484"]
    assert row["jo_a_synapses"] == 7 and row["jo_b_synapses"] == 0
    assert row["outputs"] == {"vpoEN": 11, "vpoIN": 13, "vpoDN": 17}
    assert row["sign"] == {"-1": 2}
    assert row["vpoen_sign_synapses"] == {"-1": 11, "0": 0, "1": 0}


def test_e3b_roadmap_synapses_and_snapshot_metadata(e3_snapshot):
    dataset, graph, selected = e3_snapshot
    rows = e3b_measure(graph, selected)
    report = json.loads((Path(__file__).parent / "fixtures" / "graph" /
                         f"dictionary_{dataset}.json").read_text(encoding="utf-8"))
    exported = {entry["name"]: entry for entry in report["entries"]}
    for name in E3B_NAMES:
        assert exported[name]["read_only"] is True
        assert exported[name]["group"] == "vpoen-input"
        assert exported[name]["count"] == rows[name]["count"]
    if dataset == "female":
        assert {cell_type: rows["vpoEN-input:" + cell_type]["outputs"]["vpoEN"]
                for cell_type in E3B_INPUTS} == E3B_INPUTS
    # top10 is the literal FAFB list plus only the opened per-dataset aliases (report 19).
    opened_aliases = {"female": [], "banc": ["AN17B016"],
                      "male": ["WED001", "WED055_b", "AVLP005", "AN17B016"]}[dataset]
    np.testing.assert_array_equal(selected["vpoEN-input-top10"],
                                  np.flatnonzero(np.isin(graph["type"], list(E3B_INPUTS) + opened_aliases)))


def write_e3b_measurements():
    """Reproduce the delivery measurements with the task's Python environment."""
    from flybench.dictionary.build import sha256

    measured = {}
    for dataset in ("female", "banc", "male"):
        path = Path("build") / f"graph_{dataset}.npz"
        graph = load(path)
        measured[dataset] = {
            "graph_file": path.name, "sha256": sha256(path),
            "sign_rule": graph["meta"]["sign_rule"],
            "rows": e3b_measure(graph, groups(dataset, graph=graph)),
        }
        print(dataset, {name: row["count"] for name, row in measured[dataset]["rows"].items()}, flush=True)
        del graph
    destination = Path("records/dictionary_e3b_measurements.json")
    destination.write_text(json.dumps(measured, indent=2) + "\n", encoding="utf-8", newline="\n")


@pytest.mark.parametrize("dataset", DATASETS)
def test_e3c_gate_definition_boundaries_and_read_only(dataset):
    definition = next(e for e in entries(dataset) if e.name == "vpoEN-gate:AVLP083")
    assert definition.selector.type_re == r"^AVLP083$"
    assert definition.read_only is True
    assert definition.group == "vpoen-gate"
    assert definition.confidence == "exact"
    assert definition.evidence_class == "records/vpoen_inputs_v1_report.md"
    labels = ["AVLP083", "AVLP083", "AVLP083-like", "xAVLP083", "avlp083", "AVLP0830"]
    graph = {"type": np.array(labels), "body_id": np.arange(len(labels))}
    np.testing.assert_array_equal(definition.selector.select(graph), [0, 1])
    for labels in (["AVLP083"], ["unrelated"]):
        with pytest.raises(ValueError, match="read-only diagnostic population"):
            drive_targets(dataset, definition.name,
                          graph={"type": np.array(labels), "body_id": np.arange(len(labels))})


def e3c_measure(graph, selected):
    """Raw directed counts, independent of signed weights and path flow."""
    from flybench.dictionary.build import distribution
    from scipy.sparse import csr_matrix

    n = len(graph["body_id"])
    counts = csr_matrix((graph["count"], graph["indices"], graph["indptr"]), shape=(n, n))
    indices = selected["vpoEN-gate:AVLP083"]
    return {
        "count": len(indices), "status": "present" if len(indices) else "absent",
        "sides": distribution(graph["side"][indices]),
        "nt": distribution(graph["nt"][indices]),
        "sign": distribution(graph["sign"][indices]),
        "body_ids": graph["body_id"][indices].tolist(),
        "inputs": {source: int(counts[selected[source]][:, indices].sum())
                   for source in ("JO-A", "JO-B", "AMMC-B1-candidate", "AMMC-B1-candidate-graph")},
        "outputs": {target: int(counts[indices][:, selected[target]].sum())
                    for target in ("vpoEN", "vpoIN", "vpoDN")},
        "b1_by_type": {str(label): int(counts[np.flatnonzero(graph["type"] == label)][:, indices].sum())
                       for label in ("CB1078", "CB1542", "SAD053", "CB1076", "CB1125", "CB2789")},
        "cb1614_vpoin_synapses": int(counts[selected["vpoEN-input:CB1614"]][:, selected["vpoIN"]].sum()),
    }


def test_e3c_snapshot_matches_literal_population(e3_snapshot):
    dataset, graph, selected = e3_snapshot
    indices = np.flatnonzero(graph["type"] == "AVLP083")
    np.testing.assert_array_equal(selected["vpoEN-gate:AVLP083"], indices)
    snapshot = json.loads((Path(__file__).parent / "fixtures" / "graph" /
                           f"dictionary_{dataset}.json").read_text(encoding="utf-8"))
    record = next(e for e in snapshot["entries"] if e["name"] == "vpoEN-gate:AVLP083")
    from flybench.dictionary.build import distribution
    assert record["count"] == len(indices)
    assert record["read_only"] is True
    assert record["group"] == "vpoen-gate"
    assert record["side_distribution"] == distribution(graph["side"][indices])
    assert record["nt_distribution"] == distribution(graph["nt"][indices])
    assert record["example_body_ids"] == graph["body_id"][indices[:5]].tolist()
    row = e3c_measure(graph, selected)
    if dataset == "female":
        assert row["outputs"]["vpoEN"] == 124
        assert row["cb1614_vpoin_synapses"] == 59


def test_e3c_measure_direction_and_raw_counts():
    from scipy.sparse import csr_matrix

    matrix = csr_matrix(([7, 91, 11, 13, 17, 19, 23, 59],
                         ([1, 0, 0, 0, 0, 5, 6, 7], [0, 1, 2, 3, 4, 0, 0, 3])), shape=(8, 8))
    graph = dict(body_id=np.arange(8), type=np.array(["AVLP083", "JO-A", "vpoEN", "vpoIN",
                 "vpoDN", "CB1078", "CB1076", "CB1614"]), side=np.full(8, "L"),
                 nt=np.full(8, "gaba"), sign=np.full(8, -1), count=matrix.data,
                 indices=matrix.indices, indptr=matrix.indptr)
    selected = {name: np.array([i]) for name, i in
                (("vpoEN-gate:AVLP083", 0), ("JO-A", 1), ("vpoEN", 2), ("vpoIN", 3),
                 ("vpoDN", 4), ("AMMC-B1-candidate", 5), ("AMMC-B1-candidate-graph", 6),
                 ("vpoEN-input:CB1614", 7))}
    selected["JO-B"] = np.array([], dtype=np.int64)
    row = e3c_measure(graph, selected)
    assert row["inputs"] == {"JO-A": 7, "JO-B": 0, "AMMC-B1-candidate": 19,
                             "AMMC-B1-candidate-graph": 23}
    assert row["outputs"] == {"vpoEN": 11, "vpoIN": 13, "vpoDN": 17}
    assert row["cb1614_vpoin_synapses"] == 59


def write_e3c_measurements():
    """Reproduce E3c counts and verify existing roadmap cell witnesses."""
    import re
    from flybench.dictionary.build import sha256
    from scipy.sparse import csr_matrix

    report = Path("records/vpoen_inputs_v1_report.md").read_text(encoding="utf-8")
    roadmap = json.loads(Path("records/vpoen_inputs_v1_results.json").read_text(encoding="utf-8"))
    measured = {}
    for dataset in ("female", "banc", "male"):
        path = Path("build") / f"graph_{dataset}.npz"
        graph = load(path)
        row = e3c_measure(graph, groups(dataset, graph=graph))
        row.update(graph_file=path.name, sha256=sha256(path), sign_rule=graph["meta"]["sign_rule"])
        n = len(graph["body_id"])
        counts = csr_matrix((graph["count"], graph["indices"], graph["indptr"]), shape=(n, n))
        selected = groups(dataset, graph=graph)
        targets = set(map(int, selected["vpoEN"]))
        incoming = counts.tocsc()
        paths, flow, maximum = 0, 0, 0
        for middle in selected["vpoEN-gate:AVLP083"]:
            for offset in range(counts.indptr[middle], counts.indptr[middle + 1]):
                target = int(counts.indices[offset])
                if target not in targets or target == middle:
                    continue
                for pre_offset in range(incoming.indptr[middle], incoming.indptr[middle + 1]):
                    source = int(incoming.indices[pre_offset])
                    if source in (middle, target):
                        continue
                    strength = min(int(incoming.data[pre_offset]), int(counts.data[offset]))
                    paths += 1
                    flow += strength
                    maximum = max(maximum, strength)
        row["two_edge_via_avlp083"] = dict(paths=paths, flow=flow, maximum=maximum)
        expected = next(r for r in roadmap["datasets"][dataset]["M2"] if r["type"] == "AVLP083")
        assert row["sha256"] == roadmap["graph_sha256"][dataset]
        assert row["two_edge_via_avlp083"] == {key: expected[key] for key in ("paths", "flow", "maximum")}
        lookup = {int(body): i for i, body in enumerate(graph["body_id"])}
        witnesses = []
        for match in re.finditer(r"([^|\n]+?) \(([+0-]+); min=(\d+); IDs=([\d,]+)\)", report):
            types, signs, minimum, ids = match.groups()
            if " -> AVLP083 -> vpoEN" not in types:
                continue
            bodies = list(map(int, ids.split(",")))
            if not all(body in lookup for body in bodies):
                continue
            vertices = [lookup[body] for body in bodies]
            observed = [int(counts[a, b]) for a, b in zip(vertices, vertices[1:])]
            actual_signs = "".join({-1: "-", 0: "0", 1: "+"}[int(graph["sign"][v])] for v in vertices[:-1])
            assert min(observed) == int(minimum) and actual_signs == signs
            assert [str(graph["type"][v]) or "unnamed" for v in vertices] == types.strip().split(" -> ")
            witness = dict(types=types.strip(), body_ids=bodies, counts=observed,
                           signs=actual_signs, bottleneck=min(observed))
            if witness not in witnesses:
                witnesses.append(witness)
        row["verified_roadmap_witnesses"] = witnesses
        measured[dataset] = row
        print(dataset, json.dumps(row), flush=True)
    Path("records/dictionary_e3c_measurements.json").write_text(
        json.dumps(measured, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__" and "--e3c-measurements" in __import__("sys").argv:
    write_e3c_measurements()
    raise SystemExit(0)


if __name__ == "__main__":
    import sys

    if sys.argv[1:] != ["--e3b-measurements"]:
        raise SystemExit("usage: python tests/test_dictionary.py --e3b-measurements")
    write_e3b_measurements()
